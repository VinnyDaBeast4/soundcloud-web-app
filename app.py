from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import tempfile
import glob
import zipfile

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

  function updateLiveCount() {
    const num = Math.floor(Math.random() * 18) + 7;
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
    padding:40px 20px;
  }

  .container { width:100%; max-width:1120px; margin:auto; }

  .top { text-align:center; margin-bottom:35px; }

  .logo { font-size:62px; margin-bottom:10px; }

  h1 { font-size:54px; margin:0; }

  .tagline {
    font-size:18px;
    color:#d6d6d6;
    max-width:760px;
    margin:15px auto 0;
    line-height:1.6;
  }

  .subtext { color:#aaa; font-size:14px; margin-top:10px; }

  .live {
    margin-top:20px;
    font-size:14px;
    color:#ccc;
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

  .pro-card {
    border:1px solid rgba(255,145,0,.45);
    box-shadow:0 20px 80px rgba(255,85,0,.22);
    position:relative;
    overflow:hidden;
  }

  .pro-card:before {
    content:"";
    position:absolute;
    top:-80px;
    right:-80px;
    width:180px;
    height:180px;
    background:rgba(255,85,0,.25);
    border-radius:50%;
    filter:blur(20px);
  }

  .badge {
    display:inline-block;
    padding:7px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:bold;
    background:rgba(255,85,0,.18);
    color:#ffb07a;
    margin-bottom:12px;
  }

  .pro-badge {
    background:linear-gradient(135deg,#7b45ff,#ff5500);
    color:white;
  }

  textarea, input, select {
    width:100%;
    padding:15px;
    border-radius:14px;
    border:none;
    margin:10px 0;
    box-sizing:border-box;
    font-size:14px;
  }

  textarea { height:150px; resize:vertical; }

  button {
    width:100%;
    padding:15px;
    border-radius:14px;
    border:none;
    background:#ff5500;
    color:white;
    font-weight:bold;
    cursor:pointer;
    font-size:15px;
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
    padding:11px;
    border-radius:12px;
    font-size:14px;
  }

  .pro-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-top:15px;
  }

  .pro-feature {
    background:rgba(255,255,255,.08);
    padding:13px;
    border-radius:14px;
    font-size:13px;
    min-height:42px;
  }

  .price {
    font-size:38px;
    font-weight:bold;
    margin:5px 0;
  }

  .small {
    color:#cfcfcf;
    font-size:13px;
    line-height:1.5;
  }

  .full { margin-top:25px; }

  .comparison {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:15px;
  }

  .mini-box {
    background:rgba(255,255,255,.06);
    padding:18px;
    border-radius:16px;
  }

  @media (max-width:800px){
    .cards, .comparison, .pro-grid { grid-template-columns:1fr; }
    h1 { font-size:42px; }
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

    <div class="live">
      🔥 <b><span id="liveCount">12</span> DJs online right now</b>
    </div>
  </div>

  <div class="cards">

    <div class="card">
      <span class="badge">FREE TOOL</span>
      <h2>Free Downloader</h2>
      <p class="small">
        Paste one link or multiple links. WaveFetch gives you clean MP3 files with artwork and metadata.
      </p>

      <textarea id="urls" placeholder="Paste one link per line..."></textarea>

      <button onclick="download()">Download Tracks</button>

      <div class="features">
        <div class="feature">🎵 MP3 Format</div>
        <div class="feature">🖼 Cover Art Embedded</div>
        <div class="feature">🏷 Artist + Title Metadata</div>
        <div class="feature">🎚 Rekordbox / Serato Friendly</div>
      </div>
    </div>

    <div class="card pro-card">
      <span class="badge pro-badge">PRO EARLY ACCESS</span>
      <h2>WaveFetch Pro</h2>

      <div class="price">$19</div>
      <p class="small">One-time early access price for DJs who want faster library prep.</p>

      <form method="POST" action="https://formspree.io/f/mgorjynj" onsubmit="trackEvent('waitlist_signup_click')">
        <input type="hidden" name="_next" value="{{ site_url }}/success">

        <input type="email" name="email" placeholder="Your email" required>

        <select name="software">
          <option value="">DJ Software (optional)</option>
          <option>Rekordbox</option>
          <option>Serato</option>
          <option>Traktor</option>
          <option>VirtualDJ</option>
          <option>Other</option>
        </select>

        <select name="would_pay">
          <option value="">Would you pay $19? (optional)</option>
          <option>Yes</option>
          <option>Maybe</option>
          <option>No</option>
        </select>

        <textarea name="problem" placeholder="Biggest problem with your DJ library? (optional)"></textarea>

        <button class="pro-button">Join Pro Waitlist</button>
      </form>

      <div class="pro-grid">
        <div class="pro-feature">🎚 BPM Detection</div>
        <div class="pro-feature">🎼 Key Detection</div>
        <div class="pro-feature">🧠 Smart Rename</div>
        <div class="pro-feature">📦 Bulk Processing</div>
        <div class="pro-feature">🧹 Duplicate Cleaner</div>
        <div class="pro-feature">🗂 Folder Organizer</div>
        <div class="pro-feature">🏷 Metadata Fixer</div>
        <div class="pro-feature">🚀 DJ-Ready Export</div>
      </div>
    </div>

  </div>

  <div class="card full">
    <h2>Before vs After</h2>

    <div class="comparison">
      <div class="mini-box">
        <b>❌ Before</b>
        <p style="color:#aaa;">
          track_final_v3.mp3<br>
          no artwork<br>
          unknown artist<br>
          messy Rekordbox library
        </p>
      </div>

      <div class="mini-box">
        <b>✅ After</b>
        <p style="color:#aaa;">
          Drake - One Dance.mp3<br>
          cover art included<br>
          full metadata<br>
          ready for Rekordbox
        </p>
      </div>
    </div>
  </div>

  <div class="card full">
    <h2>Why DJs Join Pro</h2>
    <div class="pro-grid">
      <div class="pro-feature">Save time before sets</div>
      <div class="pro-feature">Fix messy files faster</div>
      <div class="pro-feature">Prepare tracks in bulk</div>
      <div class="pro-feature">Keep libraries clean</div>
    </div>
  </div>

</div>
</section>

<script>
function download(){
  const urls = document.getElementById("urls").value;
  if (!urls.trim()) return alert("Paste links first");

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
<title>WaveFetch Pro Waitlist</title>
<style>
  body {
    margin:0;
    min-height:100vh;
    font-family:Arial,sans-serif;
    background:linear-gradient(135deg,#080812,#1f1235,#ff5500);
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:30px;
  }
  .box {
    max-width:560px;
    background:rgba(0,0,0,.62);
    border:1px solid rgba(255,255,255,.14);
    border-radius:26px;
    padding:40px;
  }
  a {
    display:inline-block;
    margin-top:20px;
    padding:14px 22px;
    background:#ff5500;
    color:white;
    border-radius:14px;
    text-decoration:none;
    font-weight:bold;
  }
</style>
</head>
<body>
  <div class="box">
    <h1>You're on the WaveFetch Pro waitlist 🎧</h1>
    <p>Thanks for joining. You’ll be first to know when Pro launches.</p>
    <a href="/">Back to WaveFetch</a>
  </div>
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
    urls = [u.strip() for u in request.form.get("urls", "").splitlines() if u.strip()]
    temp_dir = tempfile.mkdtemp()

    for i, url in enumerate(urls, start=1):
        with yt_dlp.YoutubeDL({
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, f"{i:03d} - %(artist|uploader)s - %(title)s.%(ext)s"),
            "writethumbnail": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"}
            ],
        }) as ydl:
            ydl.download([url])

    files = glob.glob(os.path.join(temp_dir, "*.mp3"))

    if len(files) == 1:
        return send_file(files[0], as_attachment=True)

    zip_path = os.path.join(temp_dir, "WaveFetch_Tracks.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in files:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
