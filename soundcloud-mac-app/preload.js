const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('downloaderAPI', {
  startDownload: (options) => ipcRenderer.send('start-download', options),
  onOutput: (callback) => ipcRenderer.on('download-output', (_event, data) => callback(data)),
  onDone: (callback) => ipcRenderer.on('download-done', (_event, success) => callback(success)),
  chooseFolder: () => ipcRenderer.invoke('choose-folder'),
  openFolder: (folderPath) => ipcRenderer.invoke('open-folder', folderPath)
});
