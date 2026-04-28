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
  }

  .pro-label {
    color: #c7a7ff;
    font-weight: bold;
    font-size: 13px;
  }

  textarea, input, select {
    width: 100%;
    padding: 15px;
    border-radius: 14px;
    border: none;
    outline: none;
    font-size: 14px;
    box-sizing: border-box;
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
  }

  .features {
    display: grid;
    gap: 10px;
    margin-top: 15px;
  }

  .feature {
    background: rgba(255,255,255,0.08);
    padding: 10px;
    border-radius: 12px;
  }

  .price {
    font-size: 30px;
    font-weight: bold;
  }

  @media (max-width: 800px) {
    .cards {
      grid-template-columns: 1fr;
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
          Download clean MP3s with artwork, metadata, and DJ-ready formatting.
        </p>
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

          <form method="POST" action="https://formspree.io/f/mgorjynj">
            <input type="email" name="email" placeholder="Your email" required>

            <select name="software" required>
              <option value="">DJ software</option>
              <option>Rekordbox</option>
              <option>Serato</option>
              <option>Other</option>
            </select>

            <select name="would_pay" required>
              <option value="">Would you pay $19?</option>
              <option>Yes</option>
              <option>Maybe</option>
              <option>No</option>
            </select>

            <textarea name="problem" placeholder="Biggest problem with your DJ library?"></textarea>

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

    </div>
  </section>

<script>
function download(){
  const urls = document.getElementById("urls").value;
  if (!urls.trim()) return alert("Paste links first");

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

@app.route("/")
def home():
    return render_template_string(HTML)

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

if __name__ == "__main__":
    app.run()
