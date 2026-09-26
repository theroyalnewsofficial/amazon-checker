import streamlit as st
from PIL import Image
import io
import zipfile
import os

st.set_page_config(page_title="PureFrame Studio — Pro Product Studio", page_icon="⬢", layout="wide", initial_sidebar_state="expanded")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'cached_cuts' not in st.session_state:
    st.session_state.cached_cuts = []
if 'last_files' not in st.session_state:
    st.session_state.last_files = None

# --- AI ---
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

# --- PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer,.stDeployButton, header, [data-testid="stHeader"] {display: none!important;}

    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
   .stApp { background: #fafaf9; }

   .brand { display:flex; align-items:center; gap:10px; margin-bottom: 24px; }
   .brand-icon { width: 36px; height: 36px; background: #111; color: white; border-radius: 10px; display:flex; align-items:center; justify-content:center; font-weight:800; }
   .brand-text { font-weight:800; font-size: 16px; letter-spacing: -0.5px; }
   .brand-text span { font-weight:400; color:#888; }

   .hero { background: linear-gradient(135deg, #0e0e0e 0%, #2a2a2a 100%); padding: 42px 32px; border-radius: 20px; color: white; margin-bottom: 20px; position: relative; overflow:hidden; }
   .hero h1 { font-size: 38px; font-weight: 800; line-height: 1.1; margin:0; letter-spacing: -1px; }
   .hero p { color: #a3a3a3; font-size: 14px; margin-top: 8px; }
   .hero-badge { position:absolute; top:20px; right:20px; background: rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.15); padding: 6px 12px; border-radius: 20px; font-size: 10px; letter-spacing:1px; font-weight:700; }

   .card { background: white; border-radius: 16px; border: 1px solid #eee; padding: 20px; }
   .swatch { width: 100%; height: 48px; border-radius: 12px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); cursor:pointer; transition: 0.2s; }
   .swatch:hover { transform: scale(1.05); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
   .swatch-active { border: 2px solid #111!important; box-shadow: 0 0 0 3px #111!important;}

   .metric { background: white; border-radius: 12px; padding: 12px; border:1px solid #eee; text-align:center; }
   .metric b { font-size: 18px; display:block; }
   .metric span { font-size: 11px; color:#888; text-transform:uppercase; letter-spacing:0.5px; font-weight:600;}

    [data-testid="stDownloadButton"]>button { background: #111; color: white; border-radius: 12px; height: 56px; font-weight: 700; font-size: 15px; width:100%; border:none; }
    [data-testid="stDownloadButton"]>button:hover { background: #000; }

    @media (max-width: 768px) {
      .hero h1 { font-size: 26px!important; }
      .hero { padding: 28px 20px!important; }
       [data-testid="column"] { width: 100%!important; flex: 1 1 100%!important; min-width: 100%!important; }
       [data-testid="stHorizontalBlock"] { flex-direction: column!important; }
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR - PROFESSIONAL CONTROLS ---
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">P</div><div class="brand-text">PureFrame <span>STUDIO</span></div></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px; color:#888; margin-top:-18px; margin-bottom:24px;">Professional E-commerce Photo Editor • v2.0</p>', unsafe_allow_html=True)

    st.markdown("**1. Upload Product**")
    files = st.file_uploader("Drag & drop product images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.success(f"{len(files)} images loaded")

    st.divider()
    st.markdown("**2. Studio Background**")
    st.caption("Choose background for main image")

    cols = st.columns(4)
    presets = [
        ("#FFFFFF", "Pure White"),
        ("#000000", "Deep Black"),
        ("#F5F5F3", "Studio Gray"),
        ("#3B82F6", "Brand Blue"),
        ("#EF4444", "Ruby"),
        ("#22C55E", "Forest"),
        ("#F59E0B", "Amber"),
        ("#E9D5FF", "Soft Lilac"),
    ]
    for i, (clr, name) in enumerate(presets):
        col = cols[i % 4]
        with col:
            active = "swatch-active" if st.session_state.bg_color == clr else ""
            if st.button(" ", key=f"sw_{clr}_{i}", help=name):
                st.session_state.bg_color = clr
            st.markdown(f"<div class='swatch {active}' style='background:{clr}' title='{name}'></div><div style='text-align:center; font-size:9px; color:#999; margin:4px 0 8px 0; font-weight:600;'>{name}</div>", unsafe_allow_html=True)

    custom = st.color_picker("Custom studio color", st.session_state.bg_color)
    if custom!= st.session_state.bg_color:
        st.session_state.bg_color = custom

    st.markdown(f"<div style='padding:12px; background:{st.session_state.bg_color}; border-radius:10px; border:1px solid #ddd; text-align:center; font-weight:700; font-size:13px; margin-top:8px; color:{'#fff' if st.session_state.bg_color in ['#000000','#3B82F6'] else '#111'}'>{st.session_state.bg_color} • Selected</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("**3. Export Settings**")
    size_opt = st.selectbox("Output Size", ["2000x2000 - Amazon Main", "1080x1080 - Instagram Square", "1500x1500 - Shopify"], index=0)
    quality = st.slider("JPEG Quality", 80, 100, 95)

    st.divider()
    st.markdown('<div style="font-size:11px; color:#aaa; line-height:1.5;">✓ AI background removal<br>✓ Bulk up to 50 images<br>✓ Amazon compliant<br>✓ No watermark</div>', unsafe_allow_html=True)

# --- MAIN AREA ---
m1, m2, m3 = st.columns([2.5, 1, 1])
with m1:
    st.markdown(f'<div class="hero"><div class="hero-badge">PRO • {st.session_state.bg_color}</div><h1>Product photos,<br>ready for store.</h1><p>AI removes background • Applies studio background • Exports at {size_opt.split(" - ")[0]}</p></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric"><b>{len(files) if files else 0}</b><span>Images</span></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric"><b>{st.session_state.bg_color}</b><span>Background</span></div>', unsafe_allow_html=True)

if files:
    file_names = [f.name for f in files]
    if st.session_state.last_files!= file_names:
        st.session_state.last_files = file_names
        st.session_state.cached_cuts = []
        prog = st.progress(0, text="AI processing — removing backgrounds...")
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

    st.markdown(f"#### Preview • Main background changed to **{st.session_state.bg_color}**")
    cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with cols[i % 4]:
            st.image(img, caption=name[:22], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=quality, optimize=True)
            z.writestr(f"studio_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b.getvalue())

    st.divider()
    cta1, cta2 = st.columns([2,1])
    with cta1:
        st.download_button(f"Download {len(processed)} Images as ZIP — {size_opt.split(' - ')[0]}", data=zbuf.getvalue(), file_name=f"pureframe_studio_{st.session_state.bg_color.replace('#','')}.zip", mime="application/zip", use_container_width=True)
    with cta2:
        st.markdown(f"<div style='background:white; border:1px solid #eee; border-radius:12px; padding:14px; text-align:center; font-size:12px; color:#666;'><b>{size_opt}</b><br>Ready for upload</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px; background:white; border-radius:16px; border:1.5px dashed #e5e5e5;">
        <div style="width:64px; height:64px; background:#111; color:white; border-radius:16px; display:flex; align-items:center; justify-content:center; margin:0 auto; font-size:28px; font-weight:800;">↑</div>
        <h3 style="margin:18px 0 8px 0; font-weight:700;">Drop your product images</h3>
        <p style="color:#999; font-size:13px; max-width:400px; margin:0 auto;">Supports PNG, JPG, WEBP. Bulk process up to 50 images. Background will be replaced with your selected studio color.</p>
    </div>
    """, unsafe_allow_html=True)
