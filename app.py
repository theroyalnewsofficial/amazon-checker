import streamlit as st
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="PureFrame Studio", page_icon="⬢", layout="wide", initial_sidebar_state="expanded")

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

st.markdown("""
<style>
    #MainMenu, footer,.stDeployButton {display: none!important;}
    [data-testid="stHeader"] { background: transparent!important; }
    [data-testid="stSidebarCollapsedControl"] {
        display: flex!important; position: fixed!important; top: 16px!important; left: 16px!important;
        z-index: 999999!important; background: white!important; border: 1px solid #e5e5e5!important;
        border-radius: 10px!important; box-shadow: 0 4px 12px rgba(0,0,0,0.1)!important;
    }
    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
 .stApp { background: #fafaf9; }
 .swatch { width: 100%; height: 44px; border-radius: 12px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
 .swatch-active { border: 2px solid #111!important; box-shadow: 0 0 0 2px #111!important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### PureFrame STUDIO")
    st.caption("Professional E-commerce Photo Editor • v2.0")

    files = st.file_uploader("Upload product images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    st.caption("200MB per file • PNG, JPG, WEBP")

    st.divider()
    st.markdown("**Studio Background**")

    presets = ["#FFFFFF","#EF4444","#000000","#22C55E","#F5F5F3","#F59E0B","#3B82F6","#E9D5FF"]
    cols = st.columns(4)
    for i, clr in enumerate(presets):
        col = cols[i % 4]
        with col:
            if st.button(" ", key=f"sw_{clr}_{i}"):
                st.session_state.bg_color = clr
            border = "2px solid #111" if st.session_state.bg_color == clr else "2px solid white"
            st.markdown(f"<div style='width:100%; height:44px; background:{clr}; border-radius:10px; border:{border}; box-shadow: 0 2px 6px rgba(0,0,0,0.08);'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-size:10px; color:#999; margin-bottom:10px;'>{clr}</div>", unsafe_allow_html=True)

    st.markdown("**Custom color**")
    custom = st.color_picker("Pick custom", st.session_state.bg_color, label_visibility="collapsed")
    if custom!= st.session_state.bg_color:
        st.session_state.bg_color = custom

    # FIXED: No raw div text, clean preview
    st.info(f"Selected: {st.session_state.bg_color}")

    st.divider()
    size_opt = st.selectbox("Output Size", ["2000x2000 - Amazon", "1080x1080 - Instagram", "1500x1500 - Shopify"], index=0)
    quality = st.slider("Quality", 80, 100, 89)

# --- MAIN ---
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0e0e0e 0%, #2a2a2a 100%); padding: 32px; border-radius: 20px; color: white; margin-bottom: 20px;">
    <h2 style="margin:0; font-weight:800;">Product photos,<br>ready for store.</h2>
    <p style="color:#aaa; margin-top:8px; font-size:13px;">Main background: {st.session_state.bg_color} • Size: {size_opt.split(' - ')[0]}</p>
</div>
""", unsafe_allow_html=True)

if files:
    file_names = [f.name for f in files]
    if st.session_state.last_files!= file_names:
        st.session_state.last_files = file_names
        st.session_state.cached_cuts = []
        prog = st.progress(0, text="Removing background...")
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
    st.download_button(f"Download {len(processed)} Images ZIP", data=zbuf.getvalue(), file_name="pureframe.zip", mime="application/zip", use_container_width=True)
else:
    st.markdown('<div style="text-align:center; padding:60px; background:white; border-radius:16px; border:1.5px dashed #ddd;">Drop images to start</div>', unsafe_allow_html=True)
