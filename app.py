import streamlit as st
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="PureFrame Studio", page_icon="⬢", layout="wide", initial_sidebar_state="expanded")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'cached_cuts' not in st.session_state:
    st.session_state.cached_cuts = []
if 'cached_originals' not in st.session_state:
    st.session_state.cached_originals = []
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
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### PureFrame STUDIO")
    st.caption("v2.0 • Professional Editor")

    files = st.file_uploader("Upload product images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)

    st.divider()
    st.markdown("**Background Control**")
    ai_remove = st.toggle("✨ AI Remove Background", value=True)

    if ai_remove:
        st.markdown("**Studio Background**")
        presets = ["#FFFFFF","#000000","#F5F5F3","#3B82F6","#EF4444","#22C55E","#F59E0B","#E9D5FF"]
        cols = st.columns(4)
        for i, clr in enumerate(presets):
            with cols[i % 4]:
                if st.button(" ", key=f"sw_{clr}_{i}"):
                    st.session_state.bg_color = clr
                b = "2px solid #111" if st.session_state.bg_color==clr else "1px solid #eee"
                st.markdown(f"<div style='width:100%; height:38px; background:{clr}; border-radius:8px; border:{b};'></div>", unsafe_allow_html=True)

        custom = st.color_picker("Custom", st.session_state.bg_color, label_visibility="collapsed")
        if custom!= st.session_state.bg_color:
            st.session_state.bg_color = custom
        st.success(f"BG: {st.session_state.bg_color}")
    else:
        st.info("Original Mode - Original background will show")

    size_opt = st.selectbox("Output Size", ["2000x2000 - Amazon", "1080x1080 - Instagram"], index=0)

mode_text = "AI Removed" if ai_remove else "Original"
st.markdown(f"""
<div style="background:#111; padding:28px; border-radius:16px; color:white; margin-bottom:16px;">
    <h2 style="margin:0;">Product photos, ready for store.</h2>
    <p style="color:#888; font-size:13px; margin-top:6px;">Mode: {mode_text} • BG: {st.session_state.bg_color if ai_remove else 'Original'}</p>
</div>
""", unsafe_allow_html=True)

if files:
    file_names = [f.name for f in files]
    if st.session_state.last_files!= file_names:
        st.session_state.last_files = file_names
        st.session_state.cached_cuts = []
        st.session_state.cached_originals = []
        prog = st.progress(0, text="Processing...")
        for idx, f in enumerate(files):
            orig_rgba = Image.open(f).convert("RGBA")
            orig_rgb = Image.open(f).convert("RGB")
            st.session_state.cached_originals.append((f.name, orig_rgb))
            cut = remove_bg_safe(orig_rgba)
            st.session_state.cached_cuts.append((f.name, cut))
            prog.progress((idx+1)/len(files))
        prog.empty()

    processed = []
    if ai_remove:
        hex_c = st.session_state.bg_color.lstrip('#')
        r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
        for name, cut in st.session_state.cached_cuts:
            w,h = cut.size
            m = max(w,h) + int(max(w,h)*0.1)
            base = Image.new("RGBA", (m,m), (r,g,b,255))
            base.paste(cut, ((m-w)//2, (m-h)//2), cut)
            final = base.resize((2000,2000), Image.LANCZOS)
            processed.append((name, final.convert("RGB")))
    else:
        # FIXED: Original image will NOT disappear now
        for name, orig_rgb in st.session_state.cached_originals:
            w,h = orig_rgb.size
            m = max(w,h) + int(max(w,h)*0.1)
            base = Image.new("RGB", (m,m), (255,255,255))
            base.paste(orig_rgb, ((m-w)//2, (m-h)//2))
            final = base.resize((2000,2000), Image.LANCZOS)
            processed.append((name, final))

    cols = st.columns(3)
    for i, (name, img) in enumerate(processed):
        with cols[i % 3]:
            st.image(img, caption=f"{name[:18]} - {mode_text}", use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=95)
            z.writestr(f"{name.rsplit('.',1)[0]}.jpg", b.getvalue())
    st.download_button(f"Download {len(processed)} Images", zbuf.getvalue(), "pureframe.zip", "application/zip", use_container_width=True)
else:
    st.info("Upload images to start")
