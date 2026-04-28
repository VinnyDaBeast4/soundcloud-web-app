from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import tempfile
import glob
import zipfile
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

GA_ID = "G-YE3126PNNT"
SITE_URL = "https://wavefetchmusicdownloader.onrender.com"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>WaveFetch | DJ Music Toolkit</title>

<script async src="https://www.googletagmanager.com/gtag/js?id={{ ga_id }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{ ga_id }}');

  function trackEvent(name){
    if (typeof gtag === "function") {
      gtag('event', name);
    }
  }

  // 🔥 Fake live users counter
  function updateLiveCount() {
    const num = Math.floor(Math.random() * 18) + 7; // 7–25 users
    document.getElementById("liveCount").innerText = num;
  }

  setInterval(updateLiveCount, 4000);
  window.onload = updateLiveCount;
</script>

<style>
  body { margin:0; font-family:Arial,sans-serif; background:#080812; color:white; }

  .hero {
    min-height:100vh;
    background:
      radial-gradient(circle at top left, rgba(255,85,0,.45), transparent 35%),
      radial-gradient(circle at bottom right, rgba(111,66,255,.35), transparent 35%),
      linear-gradient(135deg,#080812,#151528,#1f1235);
    display:flex; justify-content:center; align-items:center; padding:40px 20px;
  }

  .container { width:100%; max-width:1100px; }

  .top { text-align:center; margin-bottom:35px; }

  .logo { font-size:62px; margin-bottom:10px; }

  h1 { font-size:52px; margin:0; }

  .tagline {
    font-size:18px;
    color:#d6d6d6;
    max-width:720px;
    margin:15px auto 0;
    line-height:1.6;
  }

  .subtext {
    color:#aaa;
    font-size:14px;
    margin-top:10px;
  }

  .cards {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:22px;
    margin-top:35px;
  }

  .card {
    background:rgba(0,0,0,.58);
    border:1px solid rgba(255,255,255,.14);
    border-radius:26px;
    padding:30px;
    box-shadow:0 20px 60px rgba(0,0,0,.42);
    backdrop-filter:blur(12px);
  }

  textarea, input, select {
    width:100%;
    padding:15px;
    border-radius:14px;
    border:none;
    margin:10px 0;
  }

  textarea { height:150px; }

  button {
    width:100%;
    padding:15px;
    border-radius:14px;
    border:none;
    background:#ff5500;
    color:white;
    font-weight:bold;
    cursor:pointer;
  }

  .pro-button {
    background:linear-gradient(135deg,#7b45ff,#ff5500);
  }

  .features {
    display:grid;
    gap:10px;
    margin-top:15px;
  }

  .feature {
    background:rgba(255,255,255,.08);
    padding:10px;
    border-radius:12px;
  }

  .full { margin-top:25px; }

  @media (max-width:800px){
    .cards{grid-template-columns:1fr;}
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
      Download clean MP3s with artwork, metadata, and DJ-ready formatting.
    </p>

    <p class="subtext">
      Built for DJs who are tired of messy libraries.
    </p>

    <div style="margin-top:20px; font-size:14px; color:#ccc;">
      🔥 <b><span id="liveCount">12</span> DJs online right now</b>
    </div>
  </div>

  <div class="cards">

    <div class="card">
      <h2>Free Downloader</h2>

      <textarea id="urls" placeholder="Paste one link per line..."></textarea>

      <button onclick="download()">Download Tracks</button>

      <div class="features">
        <div class="feature">MP3 + Metadata</div>
        <div class="feature">Cover Art Embedded</div>
        <div class="feature">Rekordbox Ready</div>
      </div>
    </div>

    <div class="card">
      <h2>WaveFetch Pro ($19)</h2>

      <form method="POST" action="https://formspree.io/f/mgorjynj">
        <input type="hidden" name="_next" value="{{ site_url }}/success">

        <input type="email" name="email" placeholder="Your email" required>

        <select name="software">
          <option value="">DJ Software (optional)</option>
          <option>Rekordbox</option>
          <option>Serato</option>
        </select>

        <select name="would_pay">
          <option value="">Would you pay $19? (optional)</option>
          <option>Yes</option>
          <option>Maybe</option>
          <option>No</option>
        </select>

        <textarea name="problem" placeholder="Biggest problem? (optional)"></textarea>

        <button class="pro-button">Join Waitlist</button>
      </form>

      <div class="features">
        <div class="feature">BPM Detection</div>
        <div class="feature">Smart Rename</div>
      </div>
    </div>

  </div>

  <div class="card full">
    <h2>Before vs After</h2>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">

      <div>
        <b>❌ Before</b>
        <p style="color:#aaa;">
          track_final_v3.mp3<br>
          no artwork<br>
          unknown artist
        </p>
      </div>

      <div>
        <b>✅ After</b>
        <p style="color:#aaa;">
          Drake - One Dance.mp3<br>
          cover art included<br>
          ready for Rekordbox
        </p>
      </div>

    </div>
  </div>

</div>
</section>

<script>
function download(){
  const urls = document.getElementById("urls").value;
  if (!urls.trim()) return alert("Paste links");

  trackEvent('download_click');

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

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Success</title>
</head>
<body style="background:#080812;color:white;text-align:center;padding:100px;">
<h1>You're on the waitlist 🎧</h1>
<p>We’ll notify you when Pro launches.</p>
<a href="/" style="color:#ff5500;">Back</a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, ga_id=GA_ID, site_url=SITE_URL)

@app.route("/success")
def success():
    return render_template_string(SUCCESS_HTML)

@app.route("/download", methods=["POST"])
def download():
    urls = request.form.get("urls").splitlines()
    temp_dir = tempfile.mkdtemp()

    for i, url in enumerate(urls, start=1):
        with yt_dlp.YoutubeDL({
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, f"{i:03d} - %(artist)s - %(title)s.%(ext)s"),
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                {"key": "EmbedThumbnail"}
            ],
        }) as ydl:
            ydl.download([url])

    files = glob.glob(os.path.join(temp_dir, "*.mp3"))

    if len(files) == 1:
        return send_file(files[0], as_attachment=True)

    zip_path = os.path.join(temp_dir, "tracks.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in files:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
