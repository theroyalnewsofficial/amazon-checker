import streamlit as st
from PIL import Image
import io
import zipfile

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    @st.cache_resource
    def get_session():
        return new_session("u2net")
except:
    REMBG_AVAILABLE = False

st.set_page_config(page_title="PureFrame Studio", page_icon="◐", layout="wide", initial_sidebar_state="collapsed")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

def set_color(c):
    st.session_state.bg_color = c

# --- FINAL WHITE LABEL CSS - HIDE ALL GIT / HOST BRANDING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* HIDE STREAMLIT & GITHUB COMPLETELY */
    #MainMenu, footer,.stDeployButton {display: none!important;}
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none!important; visibility: hidden!important; height: 0!important;}
   .stApp > header {display: none!important;}
    section[data-testid="stSidebar"] {display: none!important;}
    iframe {display: none!important;}

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
   .stApp { background: #fafafa; }

   .navbar { display:flex; justify-content:space-between; align-items:center; padding: 15px 0 25px 0; }
   .logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; color: #111; }
   .logo span { font-weight: 400; color: #888; }

   .hero { background: #111; padding: 60px 40px; border-radius: 28px; text-align: center; margin-bottom: 30px; color: white; }
   .hero h1 { font-size: 48px; font-weight: 800; line-height: 1.1; margin:0; color: white; }
   .hero p { color: #999; font-size: 16px; margin-top: 12px; }

   .card { background: white; border-radius: 20px; padding: 22px; border: 1px solid #eee; box-shadow: 0 10px 30px rgba(0,0,0,0.04); }
   .swatch { width: 48px; height: 48px; border-radius: 14px; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 0 auto; transition: 0.2s; }
   .swatch:hover { transform: scale(1.1); }

   .stButton>button { background:#111; color:white; border-radius:12px; height:52px; font-weight:700; border:none; width:100%; }
   .stButton>button:hover { background:#FF9900; color:white; }
   .stDownloadButton>button { background: #111; color: white; border-radius: 14px; height: 56px; font-weight: 800; width:100%; }
   .stDownloadButton>button:hover { background: #FF9900; color: white; }
</style>
""", unsafe_allow_html=True)

# Navbar
st.markdown('<div class="navbar"><div class="logo">◐ PureFrame <span>STUDIO</span></div><div style="color:#888; font-size:12px; font-weight:700; letter-spacing:1px;">AMAZON • SHOPIFY • READY</div></div>', unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>Studio-Grade Backgrounds,<br>In One Click.</h1>
    <p>AI removes background • Apply any studio color • Export 2000×2000 Amazon Compliant</p>
</div>
""", unsafe_allow_html=True)

# Controls
top1, top2, top3 = st.columns([1.3, 1, 1], gap="large")
with top1:
    files = st.file_uploader("Upload Images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.success(f"✅ {len(files)} images selected - Bulk ready")

with top2:
    st.markdown("**Background Color**")
    c_cols = st.columns(5)
    colors = ["#FFFFFF","#000000","#F5F5F0","#3B82F6","#22C55E"]
    labels = ["White","Black","Gray","Blue","Green"]
    for col, clr, lbl in zip(c_cols, colors, labels):
        with col:
            if st.button(" ", key=f"clr_{clr}"):
                set_color(clr); st.rerun()
            st.markdown(f"<div class='swatch' style='background:{clr}'></div><div style='text-align:center; font-size:10px; font-weight:600; color:#888; margin-top:6px'>{lbl}</div>", unsafe_allow_html=True)
    picked = st.color_picker("Custom", st.session_state.bg_color, label_visibility="collapsed")
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()

with top3:
    st.markdown("**Export Settings**")
    size = st.selectbox("Size", ["2000x2000 (Amazon)", "1080x1080 (Square)", "Original"], label_visibility="collapsed")
    do_remove = st.toggle("AI Background Removal", value=True, disabled=not REMBG_AVAILABLE)
    st.markdown(f"<div style='margin-top:10px; padding:12px; background:{st.session_state.bg_color}; border:1px solid #eee; border-radius:10px; text-align:center; font-weight:700; font-size:13px; color:{'#000' if st.session_state.bg_color.upper()=='#FFFFFF' else '#fff'}'>{st.session_state.bg_color.upper()}</div>", unsafe_allow_html=True)

if files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    processed = []
    prog = st.progress(0, text="Processing...")
    for idx, f in enumerate(files):
        orig = Image.open(f).convert("RGBA")
        if do_remove and REMBG_AVAILABLE:
            try:
                sess = get_session()
                cut = remove(orig, session=sess)
            except:
                cut = orig
        else:
            cut = orig
        w,h = cut.size
        m = max(w,h)
        m = m + int(m*0.08)
        base = Image.new("RGBA", (m,m), (r,g,b,255))
        base.paste(cut, ((m-w)//2, (m-h)//2), cut)
        if "2000" in size:
            final = base.resize((2000,2000), Image.LANCZOS)
        elif "1080" in size:
            final = base.resize((1080,1080), Image.LANCZOS)
        else:
            final = base
        final_rgb = final.convert("RGB")
        processed.append((f.name, final_rgb))
        prog.progress((idx+1)/len(files), text=f"Processed {idx+1}/{len(files)}")

    st.divider()
    st.markdown(f"#### Results • {len(processed)} Images • {st.session_state.bg_color.upper()}")
    g_cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with g_cols[i % 4]:
            st.image(img, caption=name[:18], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=96)
            z.writestr(f"pureframe_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b.getvalue())

    st.download_button(f"⬇ Download {len(processed)} Images as ZIP", data=zbuf.getvalue(), file_name=f"pureframe_studio_{st.session_state.bg_color.replace('#','')}.zip", mime="application/zip", use_container_width=True)
    st.balloons()
else:
    st.markdown("""
    <div style="text-align:center; padding:80px; background:white; border-radius:24px; border:2px dashed #eee;">
        <div style="font-size:64px">◐</div>
        <h3 style="margin:10px 0; color:#111;">Drop your product images to start</h3>
        <p style="color:#888">Bulk upload supported • Select up to 50 images at once</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><div style='text-align:center; color:#aaa; font-size:12px;'>© 2026 PureFrame Studio • Professional Product Studio</div>", unsafe_allow_html=True)
