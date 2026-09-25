import streamlit as st
from PIL import Image, ImageOps
import io

# --- SAFE IMPORT - APP CRASH KORBE NA ---
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    # Cache the model so it downloads only once
    @st.cache_resource
    def get_session():
        return new_session("u2net") # most stable model
except Exception as e:
    REMBG_AVAILABLE = False

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="PixelPerfect Ultra",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# SESSION STATE
# ============================================================
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def set_color(color):
    st.session_state.bg_color = color

# ============================================================
# THEME
# ============================================================
dark_bg = "#0a0a0a" if st.session_state.dark_mode else "#fafafa"
card_bg = "rgba(30,30,30,0.75)" if st.session_state.dark_mode else "rgba(255,255,255,0.85)"
text_color = "#ffffff" if st.session_state.dark_mode else "#111111"
sub_text = "#999999" if st.session_state.dark_mode else "#666666"
border_col = "rgba(255,255,255,0.1)" if st.session_state.dark_mode else "rgba(0,0,0,0.06)"
shadow = "0 10px 40px rgba(0,0,0,0.3)" if st.session_state.dark_mode else "0 10px 40px rgba(0,0,0,0.06)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    #MainMenu, footer, header,.stDeployButton, [data-testid="stToolbar"] {{visibility: hidden;}}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
   .stApp {{ background: {dark_bg}; }}
   .hero {{
        background: linear-gradient(135deg, #111111 0%, #1e1e1e 50%, #2c2c2c 100%);
        padding: 70px 40px; border-radius: 28px; text-align: center; margin-bottom: 32px;
        border: 1px solid #222;
    }}
   .hero h1 {{ font-size: 54px; font-weight: 900; color: white; line-height: 1.05; }}
   .hero h1 span {{ background: linear-gradient(135deg, #FF9900 0%, #FFCC66 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
   .hero p {{ color: #aaa; font-size: 17px; margin-top: 16px; }}
   .hero.badge {{ display: inline-block; background: rgba(255,153,0,0.15); color: #FF9900; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; }}
   .glass-card {{ background: {card_bg}; backdrop-filter: blur(20px); border: 1px solid {border_col}; border-radius: 20px; padding: 24px; box-shadow: {shadow}; }}
   .stButton>button {{ background: {text_color}; color: {dark_bg}; border-radius: 14px; height: 52px; font-weight: 700; border: none; }}
   .stButton>button:hover {{ background: #FF9900; color: white; }}
   .stDownloadButton>button {{ background: linear-gradient(135deg, #FF9900 0%, #FF6600 100%); color: white; border-radius: 14px; height: 56px; font-weight: 800; border: none; box-shadow: 0 8px 25px rgba(255,153,0,0.3); }}
    [data-testid="stFileUploader"] {{ border: 2px dashed {border_col}; border-radius: 20px; padding: 20px; background: {card_bg}; }}
</style>
""", unsafe_allow_html=True)

# HEADER
h1, h2 = st.columns([5,1])
with h1:
    st.markdown(f"<h2 style='color:{text_color}; font-weight:800'>✨ PixelPerfect <span style='font-weight:400; color:{sub_text}'>ULTRA</span></h2>", unsafe_allow_html=True)
with h2:
    if st.button("🌙" if not st.session_state.dark_mode else "☀", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("""
<div class="hero">
    <div class="badge">⚡ Real BG Remover</div>
    <h1>Studio Backgrounds<br><span>in One Click.</span></h1>
    <p>AI will cut subject • Pick any color • Auto-resize to 2000×2000 Amazon-ready</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.8, 1.2], gap="large")
with left:
    uploaded = st.file_uploader("Drop image here", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
    if uploaded:
        st.markdown(f"<b style='color:{text_color}'>🎨 Quick Presets</b>", unsafe_allow_html=True)
        b_cols = st.columns(7)
        colors = ["#FFFFFF", "#000000", "#3B82F6", "#FBBF24", "#22C55E", "#EF4444", "#8B5CF6"]
        labels = ["Amazon", "Premium", "Blue", "Yellow", "Green", "Red", "Purple"]
        for col, color, label in zip(b_cols, colors, labels):
            with col:
                if st.button(" ", key=f"preset_{color}", use_container_width=True):
                    set_color(color); st.rerun()
                st.markdown(f"<div style='width:56px; height:56px; border-radius:16px; background:{color}; border:3px solid white; box-shadow:0 4px 15px rgba(0,0,0,0.15); margin:0 auto'></div><div style='text-align:center; font-size:11px; color:{sub_text}; font-weight:600; margin-top:8px;'>{label}</div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<b style='color:{text_color}'>🎯 Customize</b>", unsafe_allow_html=True)
    picked = st.color_picker("Pick Any Color", st.session_state.bg_color)
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked; st.rerun()
    st.markdown(f"<div style='margin-top:12px; padding:14px; background:{st.session_state.bg_color}; border-radius:12px; text-align:center; font-weight:800; color:{'#000' if st.session_state.bg_color.upper()=='#FFFFFF' else '#fff'}'>{st.session_state.bg_color.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    size = st.selectbox("📐 Output Size", ["2000×2000 (Amazon)", "1080×1080 (Instagram)", "Original"])
    # --- NEW TOGGLE FOR REAL REMOVAL ---
    do_remove = st.toggle("✂️ Real Background Remove (AI)", value=True, disabled=not REMBG_AVAILABLE)
    if not REMBG_AVAILABLE:
        st.warning("AI is installing... 1 min por refresh koro. Then auto on hobe.")

# PROCESSING
if uploaded:
    original = Image.open(uploaded).convert("RGBA")

    with st.spinner("⚡ Processing..."):
        # --- REAL REMOVAL LOGIC ---
        if do_remove and REMBG_AVAILABLE:
            try:
                session = get_session()
                no_bg = remove(original, session=session)
            except Exception as e:
                st.error(f"AI Model download hocche, 1 min por refresh koro. {e}")
                no_bg = original
        else:
            no_bg = original

        hex_c = st.session_state.bg_color.lstrip('#')
        r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))

        w, h = no_bg.size
        m = max(w, h)
        padding = int(m * 0.05)
        m = m + padding * 2

        bg_base = Image.new("RGBA", (m, m), (r, g, b, 255))
        bg_base.paste(no_bg, ((m - w) // 2, (m - h) // 2), no_bg)

        if "2000" in size:
            final = bg_base.resize((2000, 2000), Image.LANCZOS)
        elif "1080×1080" in size:
            final = bg_base.resize((1080, 1080), Image.LANCZOS)
        else:
            final = bg_base

        final_rgb = final.convert("RGB")

    st.divider()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"<b style='color:{text_color}'>📷 Original</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
    with c2:
        st.markdown(f"<b style='color:{text_color}'>✨ Result • {st.session_state.bg_color.upper()} {'• BG Removed' if do_remove else ''}</b>", unsafe_allow_html=True)
        st.image(final_rgb, use_container_width=True)
        buf = io.BytesIO()
        final_rgb.save(buf, format="JPEG", quality=98, optimize=True)
        if st.download_button("⬇ Download JPG", data=buf.getvalue(), file_name=f"pixelperfect_{st.session_state.bg_color.replace('#','')}_{uploaded.name.rsplit('.',1)[0]}.jpg", mime="image/jpeg", use_container_width=True):
            st.balloons()
            st.toast(f"✅ Ready! {st.session_state.bg_color.upper()}", icon="🎉")
else:
    st.markdown(f"""
    <div style="text-align:center; padding:80px 40px; background:{card_bg}; border-radius:24px; border:2px dashed {border_col};">
        <div style="font-size:72px;">📸</div>
        <h3 style="color:{text_color}">Drop an image to get started</h3>
        <p style="color:{sub_text}">Real AI will cut subject & apply any color</p>
    </div>
    """, unsafe_allow_html=True)
