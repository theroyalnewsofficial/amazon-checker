import streamlit as st
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="PureFrame Studio — Pro Product Studio", page_icon="⬢", layout="wide", initial_sidebar_state="expanded")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'cached_cuts' not in st.session_state:
    st.session_state.cached_cuts = []
if 'last_files' not in st.session_state:
    st.session_state.last_files = None

REMBG_AVAILABLE = False
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    @st.cache_resource
    def get_session():
        return new_session("u2net")
except:
    REMBG_AVAILABLE = False

def remove_bg_safe(image):
    if not REMBG_AVAILABLE:
        return image
    try:
        sess = get_session()
        result = remove(image, session=sess)
        if not result.getbbox():
            return image
        return result
    except:
        return image

# --- FIXED CSS - SIDEBAR BACK BUTTON VISIBLE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hide only menu, not header toggle */
    #MainMenu, footer,.stDeployButton {display: none!important;}

    /* Keep header for sidebar toggle */
    [data-testid="stHeader"] { background: transparent!important; display:flex!important; }

    /* IMPORTANT: Keep collapsed control visible */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex!important;
        position: fixed!important;
        top: 16px!important;
        left: 16px!important;
        z-index: 999999!important;
        background: white!important;
        border: 1px solid #e5e5e5!important;
        border-radius: 10px!important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1)!important;
        width: 40px!important;
        height: 40px!important;
        align-items: center!important;
        justify-content: center!important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: white!important;
        border-radius: 10px!important;
    }

    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
  .stApp { background: #fafaf9; }
  .brand { display:flex; align-items:center; gap:10px; margin-bottom: 24px; }
  .brand-icon { width: 36px; height: 36px; background: #111; color: white; border-radius: 10px; display:flex; align-items:center; justify-content:center; font-weight:800; }
  .brand-text { font-weight:800; font-size: 16px; letter-spacing: -0.5px; }
  .brand-text span { font-weight:400; color:#888; }
  .hero { background: linear-gradient(135deg, #0e0e0e 0%, #2a2a2a 100%); padding: 42px 32px; border-radius: 20px; color: white; margin-bottom: 20px; position: relative; overflow:hidden; }
  .hero h1 { font-size: 38px; font-weight: 800; line-height: 1.1; margin:0; letter-spacing: -1px; }
  .hero p { color: #a3a3a3; font-size: 14px; margin-top: 8px; }
  .card { background: white; border-radius: 16px; border: 1px solid #eee; padding: 20px; }
  .swatch { width: 100%; height: 48px; border-radius: 12px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); cursor:pointer; }
  .swatch-active { border: 2px solid #111!important; box-shadow: 0 0 0 3px #111!important;}
    [data-testid="stDownloadButton"]>button { background: #111; color: white; border-radius: 12px; height: 56px; font-weight: 700; font-size: 15px; width:100%; border:none; }
    @media (max-width: 768px) {
     .hero h1 { font-size: 26px!important; }
      [data-testid="column"] { width: 100%!important; flex: 1 1 100%!important; min-width: 100%!important; }
      [data-testid="stHorizontalBlock"] { flex-direction: column!important; }
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">P</div><div class="brand-text">PureFrame <span>STUDIO</span></div></div>', unsafe_allow_html=True)
    st.caption("Professional E-commerce Photo Editor • v2.0")

    files = st.file_uploader("Upload product images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    if files:
        st.success(f"{len(files)} images loaded")

    st.divider()
    st.markdown("**Studio Background**")
    cols = st.columns(4)
    presets = ["#FFFFFF","#000000","#F5F5F3","#3B82F6","#EF4444","#22C55E","#F59E0B","#E9D5FF"]
    for i, clr in enumerate(presets):
        col = cols[i % 4]
        with col:
            active = "swatch-active" if st.session_state.bg_color == clr else ""
            if st.button(" ", key=f"sw_{clr}_{i}"):
                st.session_state.bg_color = clr
            st.markdown(f"<div class='swatch {active}' style='background:{clr}'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-size:9px; color:#999; margin-bottom:8px;'>{clr}</div>", unsafe_allow_html=True)

    custom = st.color_picker("Custom color", st.session_state.bg_color)
    if custom!= st.session_state.bg_color:
        st.session_state.bg_color = custom

    st.markdown(f"<div style='padding:12px; background:{st.session_state.bg_color}; border-radius:10px; border:1px solid #ddd; text-align:center; font-weight:700; font-size:13px; margin-top:8px;'>{st.session_state.bg_color}</div>")

    st.divider()
    size_opt = st.selectbox("Output Size", ["2000x2000 - Amazon", "1080x1080 - Instagram", "1500x1500 - Shopify"], index=0)
    quality = st.slider("Quality", 80, 100, 95)

    st.markdown("---")
    st.markdown('<div style="font-size:11px; color:#aaa;">Tip: Hide sidebar using arrow at top. Click the floating button to bring it back.</div>', unsafe_allow_html=True)

# --- MAIN ---
st.markdown(f'<div class="hero"><h1>Product photos,<br>ready for store.</h1><p>Main background: {st.session_state.bg_color} • Size: {size_opt.split(" - ")[0]}</p></div>', unsafe_allow_html=True)

if files:
    file_names = [f.name for f in files]
    if st.session_state.last_files!= file_names:
        st.session_state.last_files = file_names
        st.session_state.cached_cuts = []
        prog = st.progress(0, text="AI removing backgrounds...")
        for idx, f in enumerate(files):
            orig = Image.open(f).convert("RGBA")
            cut = remove_bg_safe(orig)
            st.session_state.cached_cuts.append((f.name, cut))
            prog.progress((idx+1)/len(files))
        prog.empty()

    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    processed = []
    for name, cut in st.session_state.cached_cuts:
        w,h = cut.size
        m = max(w,h) + int(max(w,h)*0.10)
        base = Image.new("RGBA", (m,m), (r,g,b,255))
        base.paste(cut, ((m-w)//2, (m-h)//2), cut)
        final_size = int(size_opt.split("x")[0])
        final = base.resize((final_size, final_size), Image.LANCZOS)
        processed.append((name, final.convert("RGB")))

    cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with cols[i % 4]:
            st.image(img, caption=name[:18], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=quality)
            z.writestr(f"studio_{name.rsplit('.',1)[0]}.jpg", b.getvalue())

    st.divider()
    st.download_button(f"Download {len(processed)} Images ZIP", data=zbuf.getvalue(), file_name=f"pureframe_{st.session_state.bg_color.replace('#','')}.zip", mime="application/zip", use_container_width=True)
else:
    st.markdown('<div style="text-align:center; padding:80px 20px; background:white; border-radius:16px; border:1.5px dashed #e5e5e5;"><h3>Drop your product images</h3><p style="color:#999; font-size:13px;">Sidebar hides? Click top-left floating button to bring it back.</p></div>', unsafe_allow_html=True)
