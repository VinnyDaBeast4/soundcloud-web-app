from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import tempfile
import glob
import zipfile

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>WaveFetch Music Downloader</title>
<style>
  body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #0f0f1a, #1f1235, #ff5500);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .card {
    width: 90%;
    max-width: 540px;
    background: rgba(0,0,0,0.58);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 35px;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
    backdrop-filter: blur(12px);
  }

  .deck {
    font-size: 60px;
    margin-bottom: 10px;
  }

  h1 {
    margin: 10px 0;
    font-size: 36px;
  }

  p {
    color: #d8d8d8;
    font-size: 15px;
    margin-bottom: 25px;
    line-height: 1.5;
  }

  input {
    width: 100%;
    padding: 15px;
    border-radius: 14px;
    border: none;
    outline: none;
    font-size: 14px;
    box-sizing: border-box;
    margin-bottom: 16px;
  }

  button {
    width: 100%;
    padding: 15px;
    border-radius: 14px;
    border: none;
    background: #ff5500;
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
  }

  button:hover {
    background: #ff6a1f;
  }

  .features {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-top: 22px;
  }

  .feature {
    flex: 1;
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 14px;
    font-size: 12px;
    color: #e7e7e7;
  }

  .footer {
    margin-top: 22px;
    font-size: 12px;
    color: #bbbbbb;
  }
</style>
</head>

<body>
  <div class="card">
    <div class="deck">🎧</div>
    <h1>WaveFetch</h1>
    <p>Paste a SoundCloud or YouTube song, playlist, or set link. Single tracks download as MP3. Playlists download as a ZIP folder.</p>

    <input id="url" placeholder="Paste your music link here...">

    <button onclick="download()">Download</button>

    <div class="features">
      <div class="feature">🎵 MP3 Format</div>
      <div class="feature">🖼 Cover Art</div>
      <div class="feature">📦 Playlist ZIP</div>
    </div>

    <div class="footer">Built for fast downloads and Rekordbox organization</div>
  </div>

<script>
function download(){
  const url = document.getElementById("url").value;
  if (!url) return alert("Paste a link first");
  window.location.href = "/download?url=" + encodeURIComponent(url);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/download")
def download():
    url = request.args.get("url")
    if not url:
        return "No URL provided", 400

    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(playlist_title|Single Tracks)s", "%(artist|uploader)s - %(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "writethumbnail": True,
        "ignoreerrors": True,
        "noplaylist": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
        "postprocessor_args": [
            "-id3v2_version", "3"
        ],
        "prefer_ffmpeg": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    mp3_files = glob.glob(os.path.join(temp_dir, "**", "*.mp3"), recursive=True)

    if not mp3_files:
        return "Download failed. No MP3 files found.", 500

    if len(mp3_files) == 1:
        mp3_path = mp3_files[0]
        filename = os.path.basename(mp3_path)
        return send_file(mp3_path, as_attachment=True, download_name=filename)

    zip_path = os.path.join(temp_dir, "WaveFetch_Playlist.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for mp3 in mp3_files:
            arcname = os.path.relpath(mp3, temp_dir)
            zipf.write(mp3, arcname)

    return send_file(zip_path, as_attachment=True, download_name="WaveFetch_Playlist.zip")

if __name__ == "__main__":
    app.run()
