from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import tempfile
import glob
import zipfile
import csv
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>WaveFetch | DJ Music Toolkit</title>
<style>
  body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #080812;
    color: white;
  }

  .hero {
    min-height: 100vh;
    background:
      radial-gradient(circle at top left, rgba(255,85,0,0.45), transparent 35%),
      radial-gradient(circle at bottom right, rgba(111,66,255,0.35), transparent 35%),
      linear-gradient(135deg, #080812, #151528, #1f1235);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
  }

  .container {
    width: 100%;
    max-width: 1050px;
  }

  .top {
    text-align: center;
    margin-bottom: 35px;
  }

  .logo {
    font-size: 62px;
    margin-bottom: 10px;
  }

  h1 {
    font-size: 52px;
    margin: 0;
  }

  .tagline {
    font-size: 18px;
    color: #d6d6d6;
    max-width: 720px;
    margin: 15px auto 0;
    line-height: 1.6;
  }

  .cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
    margin-top: 35px;
  }

  .card {
    background: rgba(0,0,0,0.58);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 26px;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.42);
    backdrop-filter: blur(12px);
  }

  .card h2 {
    margin-top: 0;
    font-size: 28px;
  }

  .free-label {
    color: #ff7a2f;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 1px;
  }

  .pro-label {
    color: #c7a7ff;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 1px;
  }

  textarea, input, select {
    width: 100%;
    padding: 15px;
    border-radius: 14px;
    border: none;
    outline: none;
    font-size: 14px;
    box-sizing: border-box;
    font-family: Arial, sans-serif;
    margin: 10px 0;
  }

  textarea {
    height: 150px;
    resize: vertical;
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

  .pro-button {
    background: linear-gradient(135deg, #7b45ff, #ff5500);
    margin-top: 10px;
  }

  .features {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    margin-top: 18px;
  }

  .feature {
    background: rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 13px;
    color: #e8e8e8;
    font-size: 14px;
  }

  .price {
    font-size: 34px;
    font-weight: bold;
    margin: 15px 0 5px;
  }

  .small {
    color: #bbbbbb;
    font-size: 13px;
    line-height: 1.5;
  }

  .footer {
    text-align: center;
    color: #aaa;
    font-size: 13px;
    margin-top: 28px;
  }

  @media (max-width: 800px) {
    .cards {
      grid-template-columns: 1fr;
    }

    h1 {
      font-size: 40px;
    }
  }
</style>
</head>

<body>
  <section class="hero">
    <div class="container">

      <div class="top">
        <div class="logo">🎧</div>
        <h1>WaveFetch</h1>
        <p class="tagline">
          A DJ music toolkit built for fast downloads, clean metadata, cover art, and future Rekordbox / Serato library prep.
        </p>
      </div>

      <div class="cards">

        <div class="card">
          <div class="free-label">FREE VERSION</div>
          <h2>Download Tracks</h2>
          <p class="small">
            Paste one link or multiple links below. Downloads come out as DJ-ready MP3 files with title, artist, metadata, and cover art.
          </p>

          <textarea id="urls" placeholder="Paste one link per line..."></textarea>

          <button onclick="download()">Download Tracks</button>

          <div class="features">
            <div class="feature">🎵 MP3 Format</div>
            <div class="feature">🖼 Embedded Cover Art</div>
            <div class="feature">🏷 Artist + Title Metadata</div>
            <div class="feature">🎚 Rekordbox / Serato Friendly</div>
          </div>
        </div>

        <div class="card">
          <div class="pro-label">PRO WAITLIST</div>
          <h2>WaveFetch Pro</h2>
          <p class="small">
            Join the early access list for BPM detection, key detection, smart renaming, duplicate cleanup, and DJ library tools.
          </p>

          <div class="price">$19</div>
          <p class="small">Planned one-time early access price</p>

          <form method="POST" action="/waitlist">
            <input type="email" name="email" placeholder="Your email" required>

            <select name="software" required>
              <option value="">What DJ software do you use?</option>
              <option value="Rekordbox">Rekordbox</option>
              <option value="Serato">Serato</option>
              <option value="Traktor">Traktor</option>
              <option value="VirtualDJ">VirtualDJ</option>
              <option value="Other">Other</option>
            </select>

            <button class="pro-button" type="submit">Join Pro Waitlist</button>
          </form>

          <div class="features">
            <div class="feature">🔒 BPM Detection</div>
            <div class="feature">🔒 Key Detection</div>
            <div class="feature">🔒 Smart File Renaming</div>
            <div class="feature">🔒 Duplicate Finder</div>
            <div class="feature">🔒 Batch Folder Organizer</div>
            <div class="feature">🔒 Rekordbox / Serato Prep Tools</div>
          </div>
        </div>

      </div>

      <div class="footer">
        WaveFetch is designed for personal music organization and DJ library preparation.
      </div>

    </div>
  </section>

<script>
function download(){
  const urls = document.getElementById("urls").value;
  if (!urls.trim()) return alert("Paste at least one link first");

  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/download";

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = "urls";
  input.value = urls;

  form.appendChild(input);
  document.body.appendChild(form);
  form.submit();
}
</script>

</body>
</html>
"""

THANK_YOU_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Joined WaveFetch Pro</title>
<style>
  body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #080812, #1f1235, #ff5500);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  .box {
    max-width: 520px;
    background: rgba(0,0,0,0.6);
    padding: 40px;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
  }

  a {
    color: white;
    background: #ff5500;
    padding: 14px 20px;
    border-radius: 14px;
    text-decoration: none;
    display: inline-block;
    margin-top: 20px;
    font-weight: bold;
  }
</style>
</head>
<body>
  <div class="box">
    <h1>You're on the WaveFetch Pro waitlist 🎧</h1>
    <p>Thanks for joining. You’ll be first to know when Pro features are ready.</p>
    <a href="/">Back to WaveFetch</a>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/waitlist", methods=["POST"])
def waitlist():
    email = request.form.get("email", "")
    software = request.form.get("software", "")

    file_exists = os.path.isfile("waitlist.csv")

    with open("waitlist.csv", "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["email", "software", "date_joined"])

        writer.writerow([email, software, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    return render_template_string(THANK_YOU_HTML)

@app.route("/download", methods=["POST"])
def download():
    raw_urls = request.form.get("urls", "")
    urls = [line.strip() for line in raw_urls.splitlines() if line.strip()]

    if not urls:
        return "No URLs provided", 400

    temp_dir = tempfile.mkdtemp()

    for index, url in enumerate(urls, start=1):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, f"{index:03d} - %(artist|uploader)s - %(title)s.%(ext)s"),
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

    mp3_files = glob.glob(os.path.join(temp_dir, "*.mp3"))

    if not mp3_files:
        return "Download failed. No MP3 files found.", 500

    mp3_files.sort()

    if len(mp3_files) == 1:
        mp3_path = mp3_files[0]
        filename = os.path.basename(mp3_path)
        return send_file(mp3_path, as_attachment=True, download_name=filename)

    zip_path = os.path.join(temp_dir, "WaveFetch_Tracks.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for mp3 in mp3_files:
            zipf.write(mp3, os.path.basename(mp3))

    return send_file(zip_path, as_attachment=True, download_name="WaveFetch_Tracks.zip")

if __name__ == "__main__":
    app.run()
