import streamlit as st
from PIL import Image
import io
import zipfile
import os
import time

# --- SAFE AI IMPORT ---
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    @st.cache_resource
    def get_session():
        return new_session("u2net")
except Exception:
    REMBG_AVAILABLE = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="PureFrame Studio • Enterprise AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

# --- GLOBAL COREX DARK ENTERPRISE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Hide standard Streamlit header elements */
    #MainMenu, footer, .stDeployButton, header, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none!important;
        visibility: hidden!important;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: #090A0F;
        color: #F3F4F6;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0D0E15 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Corex Glass Card Component */
    .glass-card {
        background: rgba(18, 20, 29, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    /* Metric Badge & Chips */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        color: #10B981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    /* Hero Banner Styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(180deg, #FFFFFF 0%, #A1A1AA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .hero-sub {
        color: #9CA3AF;
        font-size: 14px;
        font-weight: 400;
    }

    /* Streamlit Input Customization */
    div[data-baseweb="select"] > div {
        background-color: #161822 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 48px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 52px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; padding: 10px 0 20px 0;">
            <div style="background:#6366F1; width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; color:white;">P</div>
            <div>
                <div style="font-weight:800; font-size:16px; color:#FFF; letter-spacing:-0.5px;">PureFrame</div>
                <div style="font-size:10px; color:#6B7280; font-weight:600;">ECOSYSTEM v2.4</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<span class="status-badge">● AI Core Engine Active</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🎛 Control Suite")
    export_size = st.selectbox("Resolution Target", ["2000x2000 (Amazon Main)", "1080x1080 (Shopify Square)", "Original Size"])
    ai_bg_remove = st.toggle("AI Smart Background Cutout", value=True, disabled=not REMBG_AVAILABLE)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎨 Background Canvas")
    
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    if preset_col1.button("Pure White"): st.session_state.bg_color = "#FFFFFF"
    if preset_col2.button("Dark Void"): st.session_state.bg_color = "#000000"
    if preset_col3.button("Studio Grey"): st.session_state.bg_color = "#F2F2F0"

    custom_color = st.color_picker("Custom Palette Color", st.session_state.bg_color)
    st.session_state.bg_color = custom_color

# --- MAIN DASHBOARD TOPBAR ---
c1, c2 = st.columns([0.7, 0.3])
with c1:
    st.markdown("""
    <div class="hero-container">
        <div class="status-badge" style="margin-bottom:12px;">Next-Gen E-Commerce Processor</div>
        <div class="hero-title">Studio Quality Photos in Seconds.</div>
        <div class="hero-sub">Automated background extraction, studio lighting match, and Amazon/Shopify compliance engine.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:11px; color:#6B7280; font-weight:700; letter-spacing:1px; text-transform:uppercase;">Selected Canvas</div>
        <div style="width:100%; height:42px; background:{st.session_state.bg_color}; border-radius:10px; margin:12px 0; border:1px solid rgba(255,255,255,0.2);"></div>
        <div style="font-family:monospace; font-size:14px; font-weight:700; color:#FFF;">{st.session_state.bg_color.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# --- DRAG & DROP WORKSPACE ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 📁 Batch Media Processing Workspace")
files = st.file_uploader("Drop product images here", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESS & GALLERY ---
if files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
    processed = []

    progress_bar = st.progress(0, text="Initializing Enterprise Engine...")

    for idx, f in enumerate(files):
        orig = Image.open(f).convert("RGBA")
        if ai_bg_remove and REMBG_AVAILABLE:
            try:
                sess = get_session()
                cut = remove(orig, session=sess)
            except Exception:
                cut = orig
        else:
            cut = orig

        w, h = cut.size
        m = max(w, h)
        m = m + int(m * 0.08)
        base = Image.new("RGBA", (m, m), (r, g, b, 255))
        base.paste(cut, ((m - w) // 2, (m - h) // 2), cut)

        if "2000" in export_size:
            final = base.resize((2000, 2000), Image.LANCZOS)
        elif "1080" in export_size:
            final = base.resize((1080, 1080), Image.LANCZOS)
        else:
            final = base

        processed.append((f.name, final.convert("RGB")))
        progress_bar.progress((idx + 1) / len(files), text=f"Rendering {idx + 1}/{len(files)}: {f.name}")

    time.sleep(0.3)
    progress_bar.empty()

    st.markdown(f"### 🖼 Output Gallery ({len(processed)} Items Ready)")
    
    g_cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with g_cols[i % 4]:
            st.image(img, caption=f"{name[:18]}...", use_container_width=True)

    # ZIP Building
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b_io = io.BytesIO()
            img.save(b_io, format="JPEG", quality=96, optimize=True)
            z.writestr(f"pureframe_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b_io.getvalue())

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        f"⚡ Download Complete Studio Package ({len(processed)} Assets)", 
        data=zbuf.getvalue(), 
        file_name=f"pureframe_export_{st.session_state.bg_color.replace('#','')}.zip", 
        mime="application/zip", 
        use_container_width=True
    )
else:
    st.info("👋 Upload images in the section above to trigger the Corex processing pipeline.")

st.markdown("<br><hr style='border-color:rgba(255,255,255,0.05);'><div style='text-align:center; color:#4B5563; font-size:12px;'>Corex Ecosystem Engine • PureFrame Studio International Suite</div>", unsafe_allow_html=True)
