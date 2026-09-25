import streamlit as st
from PIL import Image, ImageOps
import io

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
if 'processing' not in st.session_state:
    st.session_state.processing = False

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

# ============================================================
# ULTRA PRO CSS
# ============================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {{visibility: hidden;}}
    
    html, body, [class*="css"] {{ 
        font-family: 'Inter', sans-serif; 
        -webkit-font-smoothing: antialiased;
    }}
    
    .stApp {{ 
        background: {dark_bg};
        transition: background 0.4s ease;
    }}
    
    /* ===== HERO ===== */
    .hero {{
        background: linear-gradient(135deg, #111111 0%, #1e1e1e 50%, #2c2c2c 100%);
        padding: 70px 40px;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 32px;
        border: 1px solid #222;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }}
    .hero::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,153,0,0.12) 0%, transparent 60%);
        animation: rotate 20s linear infinite;
    }}
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    .hero h1 {{
        font-size: 54px;
        font-weight: 900;
        color: white;
        line-height: 1.05;
        margin: 0;
        letter-spacing: -2px;
        position: relative;
        z-index: 1;
    }}
    .hero h1 span {{
        background: linear-gradient(135deg, #FF9900 0%, #FFCC66 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero p {{
        color: #aaa;
        font-size: 17px;
        margin-top: 16px;
        position: relative;
        z-index: 1;
        font-weight: 400;
    }}
    .hero .badge {{
        display: inline-block;
        background: rgba(255,153,0,0.15);
        color: #FF9900;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }}
    
    /* ===== GLASS CARD ===== */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {border_col};
        border-radius: 20px;
        padding: 24px;
        box-shadow: {shadow};
        transition: all 0.3s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.12);
    }}
    
    /* ===== COLOR SWATCHES ===== */
    .color-swatch {{
        width: 56px;
        height: 56px;
        border-radius: 16px;
        border: 3px solid white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        margin: 0 auto;
    }}
    .color-swatch:hover {{
        transform: scale(1.15) rotate(-5deg);
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    }}
    .swatch-label {{
        text-align: center;
        font-size: 11px;
        color: {sub_text};
        font-weight: 600;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* ===== BUTTONS ===== */
    .stButton>button {{
        background: {text_color};
        color: {dark_bg};
        border-radius: 14px;
        height: 52px;
        font-weight: 700;
        border: none;
        font-size: 15px;
        transition: all 0.25s ease;
        width: 100%;
    }}
    .stButton>button:hover {{
        background: #FF9900;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,153,0,0.35);
    }}
    
    /* Download button */
    .stDownloadButton>button {{
        background: linear-gradient(135deg, #FF9900 0%, #FF6600 100%);
        color: white;
        border-radius: 14px;
        height: 56px;
        font-weight: 800;
        border: none;
        font-size: 16px;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(255,153,0,0.3);
    }}
    .stDownloadButton>button:hover {{
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 15px 35px rgba(255,153,0,0.5);
    }}
    
    /* ===== UPLOAD ZONE ===== */
    [data-testid="stFileUploader"] {{
        border: 2px dashed {border_col};
        border-radius: 20px;
        padding: 20px;
        background: {card_bg};
        transition: all 0.3s ease;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: #FF9900;
        background: rgba(255,153,0,0.05);
    }}
    
    /* ===== IMAGES ===== */
    .stImage img {{
        border-radius: 16px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }}
    .stImage img:hover {{
        transform: scale(1.02);
    }}
    
    /* ===== LABELS ===== */
    label {{
        color: {text_color} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    
    /* ===== SELECT ===== */
    .stSelectbox > div > div {{
        border-radius: 12px;
        background: {card_bg};
        border: 1px solid {border_col};
    }}
    
    /* ===== DIVIDER ===== */
    hr {{
        border-color: {border_col};
        margin: 40px 0;
    }}
    
    /* ===== HEADER TEXT ===== */
    .main-title {{
        color: {text_color};
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    .main-title span {{
        font-weight: 400;
        color: {sub_text};
    }}
    
    /* ===== SECTION HEADING ===== */
    .section-head {{
        color: {text_color};
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .section-head::before {{
        content: '';
        width: 4px;
        height: 18px;
        background: linear-gradient(180deg, #FF9900 0%, #FF6600 100%);
        border-radius: 2px;
    }}
    
    /* ===== COLOR PREVIEW ===== */
    .color-preview {{
        margin-top: 12px;
        padding: 14px;
        background: {st.session_state.bg_color};
        border-radius: 12px;
        border: 1px solid {border_col};
        text-align: center;
        font-weight: 800;
        font-size: 14px;
        letter-spacing: 1px;
        color: {'#000' if st.session_state.bg_color.upper() in ['#FFFFFF', '#FFF'] else '#fff'};
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* ===== EMPTY STATE ===== */
    .empty-state {{
        text-align: center;
        padding: 80px 40px;
        background: {card_bg};
        border-radius: 24px;
        border: 2px dashed {border_col};
    }}
    .empty-state .icon {{
        font-size: 72px;
        margin-bottom: 16px;
        display: block;
        animation: float 3s ease-in-out infinite;
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-10px); }}
    }}
    .empty-state h3 {{
        color: {text_color};
        font-weight: 700;
        margin: 0;
        font-size: 20px;
    }}
    .empty-state p {{
        color: {sub_text};
        margin-top: 8px;
        font-size: 14px;
    }}
    
    /* ===== FOOTER ===== */
    .footer {{
        text-align: center;
        color: {sub_text};
        font-size: 12px;
        margin-top: 40px;
        padding: 20px;
        font-weight: 500;
    }}
    .footer span {{
        color: #FF9900;
        font-weight: 700;
    }}
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {sub_text};
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #FF9900;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
h1, h2 = st.columns([5,1])
with h1:
    st.markdown(f"<h2 class='main-title'>✨ PixelPerfect <span>ULTRA</span></h2>", unsafe_allow_html=True)
with h2:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", use_container_width=True, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <div class="badge">⚡ One-Click Studio</div>
    <h1>Studio Backgrounds<br><span>in One Click.</span></h1>
    <p>Pick any color • Auto-resize to 2000×2000 • Amazon-ready in seconds</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN LAYOUT
# ============================================================
left, right = st.columns([1.8, 1.2], gap="large")

with left:
    uploaded = st.file_uploader(
        "Drop image here", 
        type=["png","jpg","jpeg","webp"], 
        label_visibility="collapsed"
    )
    
    if uploaded:
        st.markdown("<div class='section-head'>🎨 Quick Presets</div>", unsafe_allow_html=True)
        
        b_cols = st.columns(7)
        colors = ["#FFFFFF", "#000000", "#3B82F6", "#FBBF24", "#22C55E", "#EF4444", "#8B5CF6"]
        labels = ["Amazon", "Premium", "Blue", "Yellow", "Green", "Red", "Purple"]
        
        for col, color, label in zip(b_cols, colors, labels):
            with col:
                if st.button(" ", key=f"preset_{color}", use_container_width=True):
                    set_color(color)
                    st.rerun()
                st.markdown(
                    f"<div class='color-swatch' style='background:{color};'></div>"
                    f"<div class='swatch-label'>{label}</div>",
                    unsafe_allow_html=True
                )

with right:
    st.markdown("<div class='section-head'>🎯 Customize</div>", unsafe_allow_html=True)
    
    picked = st.color_picker("Pick Any Color", st.session_state.bg_color)
    if picked != st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()
    
    st.markdown(
        f"<div class='color-preview'>{st.session_state.bg_color.upper()}</div>",
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    size = st.selectbox(
        "📐 Output Size",
        ["2000×2000 (Amazon)", "1080×1080 (Instagram)", "1080×1350 (Portrait)", "Original"]
    )

# ============================================================
# PROCESSING
# ============================================================
if uploaded:
    with st.spinner("⚡ Processing your image..."):
        original = Image.open(uploaded).convert("RGBA")
        hex_c = st.session_state.bg_color.lstrip('#')
        r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
        
        # Smart square background
        w, h = original.size
        m = max(w, h)
        padding = int(m * 0.05)  # 5% padding
        m = m + padding * 2
        
        bg_base = Image.new("RGBA", (m, m), (r, g, b, 255))
        bg_base.paste(
            original,
            ((m - w) // 2, (m - h) // 2),
            original if original.mode == 'RGBA' else None
        )
        
        # Resize based on selection
        if "2000" in size:
            final = bg_base.resize((2000, 2000), Image.LANCZOS)
        elif "1080×1080" in size:
            final = bg_base.resize((1080, 1080), Image.LANCZOS)
        elif "1080×1350" in size:
            target_h = 1350
            ratio = target_h / m
            final = bg_base.resize((int(m * ratio), target_h), Image.LANCZOS)
        else:
            final = bg_base
        
        final_rgb = final.convert("RGB")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    
    with c1:
        st.markdown("<div class='section-head'>📷 Original</div>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown(
            f"<p style='color:{sub_text}; font-size:12px; text-align:center; margin-top:8px;'>"
            f"Size: {original.size[0]} × {original.size[1]} px</p>",
            unsafe_allow_html=True
        )
    
    with c2:
        st.markdown(
            f"<div class='section-head'>✨ Result • {st.session_state.bg_color.upper()}</div>",
            unsafe_allow_html=True
        )
        st.image(final_rgb, use_container_width=True)
        
        buf = io.BytesIO()
        final_rgb.save(buf, format="JPEG", quality=98, optimize=True)
        
        file_size_kb = len(buf.getvalue()) / 1024
        
        st.markdown(
            f"<p style='color:{sub_text}; font-size:12px; text-align:center; margin-top:8px;'>"
            f"Size: {final_rgb.size[0]} × {final_rgb.size[1]} px • {file_size_kb:.0f} KB</p>",
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.download_button(
            "⬇️  Download JPG",
            data=buf.getvalue(),
            file_name=f"pixelperfect_{st.session_state.bg_color.replace('#','')}_{uploaded.name.rsplit('.',1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        ):
            st.balloons()
            st.toast(f"✅ Ready! {st.session_state.bg_color.upper()}", icon="🎉")

else:
    st.markdown(f"""
    <div class="empty-state">
        <span class="icon">📸</span>
        <h3>Drop an image to get started</h3>
        <p>PNG • JPG • JPEG • WEBP — up to 10MB</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"<div class='footer'>Crafted with <span>♥</span> • PixelPerfect ULTRA 2026</div>",
    unsafe_allow_html=True
)
