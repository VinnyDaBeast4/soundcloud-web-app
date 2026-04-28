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
  .tagline { font-size:18px; color:#d6d6d6; max-width:720px; margin:15px auto 0; line-height:1.6; }
  .cards { display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:35px; }
  .card {
    background:rgba(0,0,0,.58);
    border:1px solid rgba(255,255,255,.14);
    border-radius:26px;
    padding:30px;
    box-shadow:0 20px 60px rgba(0,0,0,.42);
    backdrop-filter:blur(12px);
  }
  .card h2 { margin-top:0; font-size:28px; }
  .free-label { color:#ff7a2f; font-weight:bold; font-size:13px; }
  .pro-label { color:#c7a7ff; font-weight:bold; font-size:13px; }
  textarea, input, select {
    width:100%; padding:15px; border-radius:14px; border:none; outline:none;
    font-size:14px; box-sizing:border-box; margin:10px 0;
  }
  textarea { height:150px; resize:vertical; }
  button {
    width:100%; padding:15px; border-radius:14px; border:none;
    background:#ff5500; color:white; font-size:16px; font-weight:bold; cursor:pointer;
  }
  button:hover { background:#ff6a1f; }
  .pro-button { background:linear-gradient(135deg,#7b45ff,#ff5500); }
  .features { display:grid; gap:10px; margin-top:15px; }
  .feature { background:rgba(255,255,255,.08); padding:10px; border-radius:12px; }
  .price { font-size:30px; font-weight:bold; }
  .full { margin-top:22px; }
  .small { color:#cfcfcf; font-size:13px; line-height:1.5; }
  @media (max-width:800px){ .cards{grid-template-columns:1fr;} h1{font-size:40px;} }
</style>
</head>

<body>
<section class="hero">
<div class="container">

  <div class="top">
    <div class="logo">🎧</div>
    <h1>WaveFetch</h1>
    <p class="tagline">Download clean MP3s with artwork, metadata, and DJ-ready formatting.</p>
  </div>

  <div class="cards">

    <div class="card">
      <div class="free-label">FREE</div>
      <h2>Download Tracks</h2>
      <textarea id="urls" placeholder="Paste one link per line..."></textarea>
      <button onclick="download()">Download Tracks</button>

      <div class="features">
        <div class="feature">MP3 + Metadata</div>
        <div class="feature">Cover Art Embedded</div>
        <div class="feature">Rekordbox Ready</div>
      </div>
    </div>

    <div class="card">
      <div class="pro-label">PRO</div>
      <h2>WaveFetch Pro</h2>
      <div class="price">$19</div>
      <p class="small">Join the early access waitlist. Only your email is required.</p>

      <form method="POST" action="https://formspree.io/f/mgorjynj" onsubmit="trackEvent('waitlist_signup_click')">
        <input type="hidden" name="_next" value="{{ site_url }}/success">

        <input type="email" name="email" placeholder="Your email" required>

        <select name="software">
          <option value="">What DJ software do you use? (optional)</option>
          <option>Rekordbox</option>
          <option>Serato</option>
          <option>Traktor</option>
          <option>VirtualDJ</option>
          <option>Other</option>
        </select>

        <select name="would_pay">
          <option value="">Would you pay $19 for Pro? (optional)</option>
          <option>Yes</option>
          <option>Maybe</option>
          <option>No</option>
        </select>

        <textarea name="problem" placeholder="Biggest problem with your DJ library? (optional)"></textarea>

        <button class="pro-button" type="submit">Join Waitlist</button>
      </form>

      <div class="features">
        <div class="feature">BPM Detection</div>
        <div class="feature">Key Detection</div>
        <div class="feature">Auto Rename</div>
        <div class="feature">Duplicate Cleaner</div>
      </div>
    </div>

  </div>

  <div class="card full">
    <div class="pro-label">PRO FEATURE TEST</div>
    <h2>Smart Rename Tool</h2>
    <p class="small">Upload MP3 files you already own. WaveFetch will rename them cleanly for DJ library prep.</p>

    <form method="POST" action="/smart-rename" enctype="multipart/form-data" onsubmit="trackEvent('smart_rename_click')">
      <input type="file" name="files" multiple accept=".mp3">
      <button class="pro-button" type="submit">Smart Rename Files</button>
    </form>

    <div class="features">
      <div class="feature">Example: messy_song_name.mp3 → Messy Song Name [DJ Ready].mp3</div>
      <div class="feature">Multiple files return as a ZIP</div>
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

<script async src="https://www.googletagmanager.com/gtag/js?id={{ ga_id }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{ ga_id }}');
  gtag('event', 'waitlist_signup_success');
</script>

<style>
  body {
    margin:0;
    min-height:100vh;
    font-family:Arial,sans-serif;
    background:
      radial-gradient(circle at top left, rgba(255,85,0,.45), transparent 35%),
      radial-gradient(circle at bottom right, rgba(111,66,255,.35), transparent 35%),
      linear-gradient(135deg,#080812,#151528,#1f1235);
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    text-align:center;
    padding:30px;
  }
  .box {
    max-width:560px;
    background:rgba(0,0,0,.62);
    border:1px solid rgba(255,255,255,.14);
    border-radius:26px;
    padding:40px;
    box-shadow:0 20px 60px rgba(0,0,0,.45);
  }
  h1 { font-size:38px; margin-bottom:10px; }
  p { color:#d6d6d6; line-height:1.6; }
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
    <p>Thanks for joining. You’ll be first to know when BPM detection, key detection, smart renaming, and DJ library tools are ready.</p>
    <a href="/">Back to WaveFetch</a>
  </div>
</body>
</html>
"""

def clean_filename(name):
    name = re.sub(r'[\\\\/*?:"<>|]', "", name)
    return name.strip()[:120]

@app.route("/")
def home():
    return render_template_string(HTML, ga_id=GA_ID, site_url=SITE_URL)

@app.route("/success")
def success():
    return render_template_string(SUCCESS_HTML, ga_id=GA_ID)

@app.route("/download", methods=["POST"])
def download():
    raw_urls = request.form.get("urls", "")
    urls = [u.strip() for u in raw_urls.splitlines() if u.strip()]

    temp_dir = tempfile.mkdtemp()

    for i, url in enumerate(urls, start=1):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, f"{i:03d} - %(artist|uploader)s - %(title)s.%(ext)s"),
            "writethumbnail": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    files = glob.glob(os.path.join(temp_dir, "*.mp3"))

    if len(files) == 1:
        return send_file(files[0], as_attachment=True)

    zip_path = os.path.join(temp_dir, "WaveFetch.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in files:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True)

@app.route("/smart-rename", methods=["POST"])
def smart_rename():
    uploaded_files = request.files.getlist("files")
    uploaded_files = [f for f in uploaded_files if f.filename]

    if not uploaded_files:
        return "No files uploaded.", 400

    temp_dir = tempfile.mkdtemp()
    renamed_files = []

    for file in uploaded_files:
        original_name = secure_filename(file.filename)
        save_path = os.path.join(temp_dir, original_name)
        file.save(save_path)

        base = os.path.splitext(original_name)[0]
        base = base.replace("_", " ").replace("-", " ")
        base = re.sub(r"\\s+", " ", base).strip().title()

        new_name = clean_filename(base) + " [DJ Ready].mp3"
        new_path = os.path.join(temp_dir, new_name)

        os.rename(save_path, new_path)
        renamed_files.append(new_path)

    if len(renamed_files) == 1:
        return send_file(renamed_files[0], as_attachment=True, download_name=os.path.basename(renamed_files[0]))

    zip_path = os.path.join(temp_dir, "WaveFetch_Smart_Rename.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in renamed_files:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="WaveFetch_Smart_Rename.zip")

if __name__ == "__main__":
    app.run()
