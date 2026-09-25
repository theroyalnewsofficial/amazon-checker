import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PixelPerfect V5 - Real Remover", page_icon="✂️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu, footer, header,.stDeployButton {visibility: hidden;}
   .hero { background: linear-gradient(135deg, #111 0%, #333 100%); padding: 50px; border-radius: 24px; text-align:center; margin-bottom:20px; }
   .hero h1 { color: white; font-size: 44px; font-weight: 800; }
   .hero p { color: #aaa; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>✂️ Real AI Background Remover V5</h1>
    <p>No Server Crash • 100% Working • Subject kete ber korbe, background e jekono color dite parbe</p>
</div>
""", unsafe_allow_html=True)

# This is the MAGIC - Client-side AI, no Python library needed
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
    body { font-family: Inter, sans-serif; background: #fcfcfc; margin: 0; padding: 20px; }
   .container { max-width: 1100px; margin: 0 auto; }
   .upload-box { border: 3px dashed #ddd; border-radius: 20px; padding: 40px; text-align: center; background: white; cursor: pointer; transition: 0.3s; }
   .upload-box:hover { border-color: #FF9900; background: #fff8ec; }
   .controls { background: white; border-radius: 20px; padding: 20px; margin-top: 20px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
   .color-bubble { width: 44px; height: 44px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.2); cursor: pointer; display: inline-block; margin: 4px; }
   .color-bubble:hover { transform: scale(1.1); }
    #canvas { max-width: 100%; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
   .result-card { background: white; border-radius: 20px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    button { background: #111; color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 16px; }
    button:hover { background: #FF9900; }
</style>
</head>
<body>
<div class="container">
    <div class="upload-box" id="uploadBox" onclick="document.getElementById('fileInput').click()">
        <div style="font-size: 48px;">📸</div>
        <h3>Click to Upload Product Image</h3>
        <p style="color:#888">PNG, JPG, WEBP - AI will remove background in your browser</p>
        <input type="file" id="fileInput" accept="image/*" style="display:none">
    </div>

    <div class="controls" id="controls" style="display:none">
        <div><b>Pick Background:</b></div>
        <div class="color-bubble" style="background:#FFFFFF" onclick="setBg('#FFFFFF')"></div>
        <div class="color-bubble" style="background:#000000" onclick="setBg('#000000')"></div>
        <div class="color-bubble" style="background:#3B82F6" onclick="setBg('#3B82F6')"></div>
        <div class="color-bubble" style="background:#FBBF24" onclick="setBg('#FBBF24')"></div>
        <div class="color-bubble" style="background:#22C55E" onclick="setBg('#22C55E')"></div>
        <div class="color-bubble" style="background:#EF4444" onclick="setBg('#EF4444')"></div>
        <input type="color" id="colorPicker" value="#FFFFFF" style="width:44px; height:44px; border-radius:50%; border:none; cursor:pointer;" oninput="setBg(this.value)">
        <select id="sizeSelect" style="padding:10px; border-radius:10px; border:1px solid #ddd;">
            <option value="2000">2000x2000 Amazon</option>
            <option value="1080">1080x1080 Insta</option>
            <option value="original">Original</option>
        </select>
        <button onclick="downloadImage()">⬇ Download JPG</button>
        <span id="status" style="color:#22c55e; font-weight:600;"></span>
    </div>

    <div style="display:flex; gap:20px; margin-top:20px; flex-wrap: wrap;">
        <div class="result-card" style="flex:1; min-width:300px;">
            <b>Original</b><br><br>
            <img id="originalPreview" style="max-width:100%; border-radius:12px; display:none;">
        </div>
        <div class="result-card" style="flex:1; min-width:300px;">
            <b id="resultTitle">Result - #FFFFFF</b><br><br>
            <canvas id="canvas" style="display:none;"></canvas>
            <div id="placeholder" style="padding:40px; text-align:center; color:#aaa;">Result will appear here</div>
        </div>
    </div>
</div>

<script type="module">
    import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.4.5/+esm';

    let originalImage = null;
    let cutoutImage = null;
    let currentBg = '#FFFFFF';

    document.getElementById('fileInput').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            document.getElementById('originalPreview').src = ev.target.result;
            document.getElementById('originalPreview').style.display = 'block';
            document.getElementById('uploadBox').innerHTML = '<h3>✅ Image Loaded - Processing...</h3>';
        };
        reader.readAsDataURL(file);

        document.getElementById('status').innerText = '✂️ AI is cutting subject... 5-10 sec';
        document.getElementById('controls').style.display = 'flex';

        try {
            // REAL AI REMOVAL IN BROWSER
            const blob = await removeBackground(file);
            const url = URL.createObjectURL(blob);
            const img = new Image();
            img.onload = () => {
                cutoutImage = img;
                drawResult();
                document.getElementById('status').innerText = '✅ Background Removed! Pick any color.';
                document.getElementById('uploadBox').innerHTML = '<h3>✅ Done! Upload another?</h3><p style="color:#888">Click to upload new image</p>';
            };
            img.src = url;
        } catch (err) {
            document.getElementById('status').innerText = 'Error: ' + err.message;
            console.error(err);
        }
    });

    window.setBg = function(color) {
        currentBg = color;
        document.getElementById('colorPicker').value = color;
        document.getElementById('resultTitle').innerText = 'Result - ' + color;
        drawResult();
    }

    function drawResult() {
        if (!cutoutImage) return;
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        let size = document.getElementById('sizeSelect').value;
        let outSize = 2000;
        if (size === '1080') outSize = 1080;
        if (size === 'original') outSize = Math.max(cutoutImage.width, cutoutImage.height);

        canvas.width = outSize;
        canvas.height = outSize;
        canvas.style.display = 'block';
        document.getElementById('placeholder').style.display = 'none';

        // Fill background color
        ctx.fillStyle = currentBg;
        ctx.fillRect(0, 0, outSize, outSize);

        // Center the cutout
        const scale = Math.min(outSize / cutoutImage.width, outSize / cutoutImage.height) * 0.9;
        const w = cutoutImage.width * scale;
        const h = cutoutImage.height * scale;
        const x = (outSize - w) / 2;
        const y = (outSize - h) / 2;

        ctx.drawImage(cutoutImage, x, y, w, h);
    }

    document.getElementById('sizeSelect').addEventListener('change', drawResult);

    window.downloadImage = function() {
        const canvas = document.getElementById('canvas');
        const link = document.createElement('a');
        link.download = 'pixelperfect_' + currentBg.replace('#','') + '_' + Date.now() + '.jpg';
        link.href = canvas.toDataURL('image/jpeg', 0.95);
        link.click();
    }
</script>
</body>
</html>
""", height=900, scrolling=True)

st.markdown("<br><center style='color:#888; font-size:12px;'>© 2026 PixelPerfect V5 • Real AI in Browser • 100% Stable • No Server Error</center>", unsafe_allow_html=True)
