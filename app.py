import streamlit as st
from PIL import Image
import io

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except:
    REMBG_AVAILABLE = False

st.set_page_config(page_title="PixelPerfect V3 Ultra", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# --- SESSION STATE FOR COLOR & DARK MODE ---
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def set_color(color):
    st.session_state.bg_color = color

# --- ULTRA PRO CSS - GLASSMORPHISM ---
dark_bg = "#0a0a0a" if st.session_state.dark_mode else "#fcfcfc"
card_bg = "rgba(30,30,30,0.8)" if st.session_state.dark_mode else "rgba(255,255,255,0.85)"
text_color = "#ffffff" if st.session_state.dark_mode else "#111111"
sub_text = "#888888" if st.session_state.dark_mode else "#666666"

st.markdown(f"""
<style>
    #MainMenu, footer, header,.stDeployButton, [data-testid="stToolbar"] {{visibility: hidden;}}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: {dark_bg}; }}
   .stApp {{ background: {dark_bg}; }}

   .hero {{
        background: linear-gradient(135deg, #111111 0%, #333333 100%);
        border: 1px solid #222;
        padding: 60px 40px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }}
   .hero::before {{
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,153,0,0.15) 0%, transparent 70%);
    }}
   .hero h1 {{ font-size: 52px; font-weight: 800; color: white; position: relative; line-height: 1.1; }}
   .hero p {{ color: #aaa; font-size: 18px; position: relative; }}

   .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    }}
   .color-bubble {{
        width: 44px; height: 44px; border-radius: 50%; border: 3px solid white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15); cursor: pointer; display: inline-block; margin: 4px;
        transition: transform 0.2s;
    }}
   .color-bubble:hover {{ transform: scale(1.15); }}
   .stButton>button {{
        background: #111; color: white; border-radius: 12px; height: 56px; font-weight: 700; border: none; font-size: 16px;
    }}
   .stButton>button:hover {{ background: #FF9900; color: white; transform: translateY(-1px); }}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
h1, h2 = st.columns([5,1])
with h1:
    st.markdown(f"<h2 style='color:{text_color}; margin:0;'>✨ PixelPerfect <span style='font-weight:400; color:{sub_text}'>V3 ULTRA</span></h2>", unsafe_allow_html=True)
with h2:
    if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown(f"""
<div class="hero">
    <h1>Studio Quality Backgrounds<br>in One Click.</h1>
    <p>AI removes background, you pick any color. Amazon, Shopify & Instagram ready.</p>
</div>
""", unsafe_allow_html=True)

# --- CONTROLS ---
left, right = st.columns([1.8, 1.2], gap="large")

with left:
    uploaded = st.file_uploader("Drop image here", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
    if uploaded:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Quick Color Presets</b><p style='color:{sub_text}; font-size:13px; margin:0;'>One click to apply</p></div>", unsafe_allow_html=True)

        # COLOR BUBBLES
        b_cols = st.columns(7)
        colors = ["#FFFFFF", "#000000", "#3B82F6", "#FBBF24", "#22C55E", "#EF4444", "#8B5CF6"]
        labels = ["Amazon", "Premium", "Shopify", "Lifestyle", "Nature", "Sale", "Brand"]
        for i, (col, color) in enumerate(zip(b_cols, colors)):
            with col:
                if st.button(f"", key=f"bubble_{color}", help=f"{labels[i]} {color}", use_container_width=True):
                    set_color(color)
                    st.rerun()
                st.markdown(f"<div style='text-align:center'><div class='color-bubble' style='background:{color}; border-color:{'#333' if color=='#FFFFFF' else 'white'}'></div><br><span style='font-size:11px; color:{sub_text}'>{labels[i]}</span></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Customize</b>", unsafe_allow_html=True)
    picked = st.color_picker("Custom Color", st.session_state.bg_color)
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked

    st.markdown(f"<div style='margin-top:15px; padding:12px; background:{st.session_state.bg_color}; border-radius:10px; border:1px solid #ddd; text-align:center; color:{'#000' if st.session_state.bg_color=='#FFFFFF' else '#fff'}; font-weight:600;'>{st.session_state.bg_color}</div>", unsafe_allow_html=True)

    size = st.selectbox("Size", ["2000x2000 (Amazon Pro)", "1080x1080 (Instagram)", "Original"])
    do_remove = st.toggle("✦ AI Background Remove", value=True, disabled=not REMBG_AVAILABLE)
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    original = Image.open(uploaded).convert("RGBA")

    # PROCESS
    if do_remove and REMBG_AVAILABLE:
        with st.spinner("✨ AI is creating magic..."):
            no_bg = remove(original)
    else:
        no_bg = original

    hex_c = st.session_state.bg_color.lstrip('#')
    r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
    bg = Image.new("RGBA", no_bg.size, (r, g, b, 255))
    final_rgba = Image.alpha_composite(bg, no_bg)

    if "2000x2000" in size:
        w,h = final_rgba.size; m=max(w,h)
        sq = Image.new("RGBA", (m,m), (r,g,b,255)); sq.paste(final_rgba, ((m-w)//2,(m-h)//2), final_rgba)
        final = sq.resize((2000,2000), Image.LANCZOS)
    elif "1080" in size:
        w,h = final_rgba.size; m=max(w,h)
        sq = Image.new("RGBA", (m,m), (r,g,b,255)); sq.paste(final_rgba, ((m-w)//2,(m-h)//2), final_rgba)
        final = sq.resize((1080,1080), Image.LANCZOS)
    else:
        final = final_rgba

    final_rgb = final.convert("RGB")

    st.divider()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Before</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>After • {st.session_state.bg_color}</b>", unsafe_allow_html=True)
        st.image(final_rgb, use_container_width=True)
        buf = io.BytesIO(); final_rgb.save(buf, format="JPEG", quality=98)

        if st.download_button(f"⬇ Download {size.split(' ')[0]} JPG", data=buf.getvalue(), file_name=f"PIXEL_{st.session_state.bg_color.replace('#','')}_{uploaded.name.split('.')[0]}.jpg", mime="image/jpeg", use_container_width=True, key="dl_final"):
            st.balloons()
            st.toast(f"Downloaded with {st.session_state.bg_color} background! 🎉", icon="✅")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='glass-card' style='text-align:center; padding:60px;'><p style='font-size:50px; margin:0;'>📸</p><p style='color:{text_color}; font-weight:600; font-size:18px;'>Drop your product image to start</p><p style='color:{sub_text}'>PNG, JPG, WEBP supported</p></div>", unsafe_allow_html=True)

st.markdown("<br><br><center style='color:#666; font-size:12px;'>© 2026 PixelPerfect V3 Ultra • Built with Glassmorphism • No affiliation with Amazon</center>", unsafe_allow_html=True)
