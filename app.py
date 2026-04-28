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

  textarea {
    width: 100%;
    height: 150px;
    padding: 15px;
    border-radius: 14px;
    border: none;
    outline: none;
    font-size: 14px;
    box-sizing: border-box;
    resize: vertical;
    font-family: Arial, sans-serif;
    margin: 15px 0;
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
    margin-top: 15px;
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

  .locked {
    opacity: 0.95;
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

        <div class="card locked">
          <div class="pro-label">PRO VERSION</div>
          <h2>DJ Library Prep</h2>
          <p class="small">
            Pro is built for DJs who want cleaner files, faster prep, and organized libraries before importing into Rekordbox or Serato.
          </p>

          <div class="price">$19</div>
          <p class="small">One-time early access price</p>

          <div class="features">
            <div class="feature">🔒 BPM Detection</div>
            <div class="feature">🔒 Key Detection</div>
            <div class="feature">🔒 Smart File Renaming</div>
            <div class="feature">🔒 Duplicate Finder</div>
            <div class="feature">🔒 Batch Folder Organizer</div>
            <div class="feature">🔒 Rekordbox / Serato Prep Tools</div>
          </div>

          <button class="pro-button" onclick="proAlert()">Upgrade to Pro</button>
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

function proAlert(){
  alert("WaveFetch Pro is coming soon. This section will include BPM, key detection, smart renaming, duplicate cleanup, and DJ library organization.");
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

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
