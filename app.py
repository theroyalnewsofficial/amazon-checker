import streamlit as st
from PIL import Image
import io
import zipfile
import os

st.set_page_config(page_title="PureFrame Studio", page_icon="⬢", layout="wide", initial_sidebar_state="collapsed")

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
    #MainMenu, footer,.stDeployButton, header, [data-testid="stHeader"] {display: none!important;}
   .stApp { background: #f8f8f7; }
   .hero { background: #0e0e0e; padding: 40px; border-radius: 24px; text-align: center; color: white; margin-bottom: 20px;}
   .swatch { width: 44px; height: 44px; border-radius: 10px; border: 2px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.12); margin: 0 auto;}
    @media (max-width: 768px) {
       .block-container { padding: 1rem!important; }
       .hero h1 { font-size: 28px!important;}
        [data-testid="column"] { width: 100%!important; flex: 1 1 100%!important; min-width: 100%!important; }
        [data-testid="stHorizontalBlock"] { flex-direction: column!important; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>PureFrame Studio</h1><p>Fixed Color Change Issue</p></div>', unsafe_allow_html=True)

# --- CONTROLS ---
top1, top2 = st.columns([1, 1])
with top1:
    files = st.file_uploader("Upload Images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)

with top2:
    st.markdown("**Pick Background Color**")
    c1, c2, c3, c4, c5 = st.columns(5)
    colors = ["#FFFFFF","#000000","#F2F2F0","#3B82F6","#22C55E"]
    for col, clr in zip([c1,c2,c3,c4,c5], colors):
        with col:
            if st.button(" ", key=f"btn_{clr}"):
                st.session_state.bg_color = clr
            st.markdown(f"<div class='swatch' style='background:{clr}'></div>", unsafe_allow_html=True)

    # Color picker without auto rerun loop
    new_color = st.color_picker("Custom Color", st.session_state.bg_color)
    if new_color!= st.session_state.bg_color:
        st.session_state.bg_color = new_color

    st.markdown(f"<div style='padding:10px; background:{st.session_state.bg_color}; border-radius:8px; text-align:center; border:1px solid #ddd; margin-top:10px;'>{st.session_state.bg_color}</div>")

if files:
    # Check if files are new, then only run AI once
    file_names = [f.name for f in files]
    if st.session_state.last_files!= file_names:
        st.session_state.last_files = file_names
        st.session_state.cached_cuts = []
        progress = st.progress(0, text="Removing background once...")
        for idx, f in enumerate(files):
            orig = Image.open(f).convert("RGBA")
            cut = remove_bg_safe(orig)
            st.session_state.cached_cuts.append((f.name, cut))
            progress.progress((idx+1)/len(files))
        progress.empty()

    # NOW - Only change BG color, no AI re-run
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))

    processed = []
    for name, cut in st.session_state.cached_cuts:
        w,h = cut.size
        m = max(w,h) + int(max(w,h)*0.08)
        base = Image.new("RGBA", (m,m), (r,g,b,255))
        base.paste(cut, ((m-w)//2, (m-h)//2), cut)
        final = base.resize((2000,2000), Image.LANCZOS)
        processed.append((name, final.convert("RGB")))

    st.divider()
    cols = st.columns(2)
    for i, (name, img) in enumerate(processed):
        with cols[i % 2]:
            st.image(img, caption=f"{name} - BG: {st.session_state.bg_color}", use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=95)
            z.writestr(f"pureframe_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b.getvalue())
    st.download_button(f"Download {len(processed)} Images ZIP", zbuf.getvalue(), "pureframe.zip", "application/zip", use_container_width=True)
else:
    st.info("Upload images - then change color as much as you want, no error!")
