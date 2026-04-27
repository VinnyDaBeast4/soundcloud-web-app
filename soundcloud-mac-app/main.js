const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const os = require('os');
const fs = require('fs');

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 920,
    height: 760,
    minWidth: 760,
    minHeight: 620,
    title: 'SoundCloud Downloader',
    backgroundColor: '#0f1115',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

function desktopPath(folderName) {
  return path.join(os.homedir(), 'Desktop', folderName || 'usb');
}

ipcMain.handle('choose-folder', async () => {
  const result = await dialog.showOpenDialog(win, {
    properties: ['openDirectory', 'createDirectory'],
    defaultPath: path.join(os.homedir(), 'Desktop')
  });

  if (result.canceled || !result.filePaths.length) return null;
  return result.filePaths[0];
});

ipcMain.handle('open-folder', async (_event, folderPath) => {
  const target = folderPath || desktopPath('usb');
  if (!fs.existsSync(target)) fs.mkdirSync(target, { recursive: true });
  await shell.openPath(target);
  return true;
});

ipcMain.on('start-download', (event, options) => {
  const { url, format, outputFolder, playlistMode } = options;

  if (!url || !url.trim()) {
    event.sender.send('download-output', 'ERROR: Paste a SoundCloud link first.\n');
    event.sender.send('download-done', false);
    return;
  }

  const folder = outputFolder && outputFolder.trim() ? outputFolder.trim() : desktopPath('usb');
  if (!fs.existsSync(folder)) fs.mkdirSync(folder, { recursive: true });

  const template = playlistMode
    ? path.join(folder, '%(playlist_title)s', '%(title)s.%(ext)s')
    : path.join(folder, '%(title)s.%(ext)s');

  const args = [
    '-ciw',
    '-x',
    '--audio-format', format || 'mp3',
    '--audio-quality', '0',
    '--embed-thumbnail',
    '--convert-thumbnails', 'jpg',
    '--add-metadata',
    playlistMode ? '--yes-playlist' : '--no-playlist',
    '-o', template,
    url.trim()
  ];

  event.sender.send('download-output', `Saving to: ${folder}\n`);
  event.sender.send('download-output', `Running: yt-dlp ${args.map(a => a.includes(' ') ? `"${a}"` : a).join(' ')}\n\n`);

  const child = spawn('yt-dlp', args, { shell: false });

  child.stdout.on('data', data => {
    event.sender.send('download-output', data.toString());
  });

  child.stderr.on('data', data => {
    event.sender.send('download-output', data.toString());
  });

  child.on('error', err => {
    event.sender.send('download-output', `\nERROR: ${err.message}\n\nMake sure yt-dlp and ffmpeg are installed:\nbrew install yt-dlp ffmpeg\n`);
    event.sender.send('download-done', false);
  });

  child.on('close', code => {
    event.sender.send('download-output', `\nFinished with exit code ${code}.\n`);
    event.sender.send('download-done', code === 0);
  });
});
