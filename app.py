import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="PixelPerfect V3 Ultra", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def set_color(color):
    st.session_state.bg_color = color

# --- ULTRA PRO CSS ---
dark_bg = "#0a0a0a" if st.session_state.dark_mode else "#fcfcfc"
card_bg = "rgba(30,30,30,0.85)" if st.session_state.dark_mode else "rgba(255,255,255,0.85)"
text_color = "#ffffff" if st.session_state.dark_mode else "#111111"
sub_text = "#999999" if st.session_state.dark_mode else "#666666"

st.markdown(f"""
<style>
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {{visibility: hidden;}}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {dark_bg}; }}
    .hero {{
        background: linear-gradient(135deg, #111111 0%, #2c2c2c 100%);
        padding: 60px 40px; border-radius: 24px; text-align: center; margin-bottom: 30px;
        border: 1px solid #222; position: relative; overflow: hidden;
    }}
    .hero h1 {{ font-size: 50px; font-weight: 800; color: white; line-height: 1.1; }}
    .hero p {{ color: #aaa; font-size: 18px; }}
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    }}
    .stButton>button {{ background: #111; color: white; border-radius: 12px; height: 56px; font-weight: 700; border: none; }}
    .stButton>button:hover {{ background: #FF9900; color: white; }}
</style>
""", unsafe_allow_html=True)

# Header
h1, h2 = st.columns([5,1])
with h1:
    st.markdown(f"<h2 style='color:{text_color}; margin:0;'>✨ PixelPerfect <span style='font-weight:400; color:{sub_text}'>V3 ULTRA</span></h2>", unsafe_allow_html=True)
with h2:
    if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("""
<div class="hero">
    <h1>Studio Backgrounds<br>in One Click.</h1>
    <p>Pick any color, auto resize to 2000x2000 Amazon ready. Fast & 100% Stable.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.8, 1.2], gap="large")
with left:
    uploaded = st.file_uploader("Drop image here", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
    if uploaded:
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Quick Presets - One Click</b></div>", unsafe_allow_html=True)
        b_cols = st.columns(7)
        colors = ["#FFFFFF", "#000000", "#3B82F6", "#FBBF24", "#22C55E", "#EF4444", "#8B5CF6"]
        labels = ["Amazon", "Premium", "Blue", "Yellow", "Green", "Red", "Purple"]
        for col, color, label in zip(b_cols, colors, labels):
            with col:
                if st.button(" ", key=f"b_{color}", use_container_width=True):
                    set_color(color)
                    st.rerun()
                st.markdown(f"<div style='text-align:center; margin-top:-10px;'><div style='width:44px; height:44px; border-radius:50%; background:{color}; border:3px solid white; box-shadow:0 2px 10px rgba(0,0,0,0.2); margin:0 auto;'></div><span style='font-size:11px; color:{sub_text}'>{label}</span></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Customize</b>", unsafe_allow_html=True)
    picked = st.color_picker("Pick Any Color", st.session_state.bg_color)
    if picked != st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()
    st.markdown(f"<div style='margin-top:10px; padding:12px; background:{st.session_state.bg_color}; border-radius:10px; border:1px solid #ddd; text-align:center; font-weight:700; color:{'#000' if st.session_state.bg_color=='#FFFFFF' else '#fff'}'>{st.session_state.bg_color}</div>", unsafe_allow_html=True)
    size = st.selectbox("Output Size", ["2000x2000 (Amazon)", "1080x1080 (Insta)", "Original"])
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    original = Image.open(uploaded).convert("RGBA")
    hex_c = st.session_state.bg_color.lstrip('#')
    r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
    
    # STABLE METHOD: Create colored square background and center product
    w,h = original.size
    m = max(w,h)
    # If image has transparency, composite it on chosen color
    bg_base = Image.new("RGBA", (m,m), (r,g,b,255))
    bg_base.paste(original, ((m-w)//2, (m-h)//2), original if original.mode=='RGBA' else None)
    
    if "2000" in size:
        final = bg_base.resize((2000,2000), Image.LANCZOS)
    elif "1080" in size:
        final = bg_base.resize((1080,1080), Image.LANCZOS)
    else:
        final = bg_base

    final_rgb = final.convert("RGB")

    st.divider()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Original</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Result • {st.session_state.bg_color}</b>", unsafe_allow_html=True)
        st.image(final_rgb, use_container_width=True)
        buf = io.BytesIO(); final_rgb.save(buf, format="JPEG", quality=98)
        if st.download_button(f"⬇ Download JPG", data=buf.getvalue(), file_name=f"PIXEL_{st.session_state.bg_color.replace('#','')}_{uploaded.name}", mime="image/jpeg", use_container_width=True):
            st.balloons()
            st.toast(f"Ready! Background: {st.session_state.bg_color} 🎉", icon="✅")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='glass-card' style='text-align:center; padding:60px;'><p style='font-size:50px;'>📸</p><p style='color:{text_color}; font-weight:600;'>Drop image to start</p></div>", unsafe_allow_html=True)

st.markdown("<br><center style='color:#666; font-size:12px;'>© 2026 PixelPerfect V3 Ultra • Stable Edition</center>", unsafe_allow_html=True)
