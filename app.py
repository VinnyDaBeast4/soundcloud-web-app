from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Music Downloader</title>
</head>
<body style="font-family:sans-serif;text-align:center;padding:40px;">
<h1>Music Downloader</h1>
<input id="url" placeholder="Paste link here" style="width:300px;padding:10px;">
<br><br>
<button onclick="download()">Download</button>

<script>
function download(){
  const url = document.getElementById("url").value;
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

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file("song.mp3", as_attachment=True)

if __name__ == "__main__":
    app.run()
