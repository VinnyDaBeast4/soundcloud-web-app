from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import tempfile
import glob

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>WaveFetch Music Downloader</title>
</head>
<body style="font-family:sans-serif;text-align:center;padding:40px;">
<h1>WaveFetch Music Downloader</h1>
<p>Paste a SoundCloud or YouTube link below.</p>
<input id="url" placeholder="Paste link here" style="width:400px;padding:10px;">
<br><br>
<button onclick="download()">Download MP3</button>

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

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(temp_dir, "%(artist|uploader)s - %(title)s.%(ext)s"),
        "writethumbnail": True,
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

    mp3_files = glob.glob(os.path.join(temp_dir, "*.mp3"))

    if not mp3_files:
        return "Download failed. No MP3 file found.", 500

    mp3_path = mp3_files[0]
    filename = os.path.basename(mp3_path)

    return send_file(mp3_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run()
