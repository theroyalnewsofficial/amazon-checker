import streamlit as st
from PIL import Image
import io
import zipfile
import os

st.set_page_config(
    page_title="PureFrame Studio",
    page_icon="⬢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

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
        result = remove(image, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        if not result.getbbox():
            return image
        return result
    except:
        return image

# --- MOBILE RESPONSIVE CSS ---
st.markdown("""
<style>
    #MainMenu, footer,.stDeployButton, header, [data-testid="stHeader"], [data-testid="stToolbar"] {display: none!important;}
.stApp > header {display: none!important;}
    section[data-testid="stSidebar"] {display: none!important;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8f8f7; }
.hero { background: #0e0e0e; padding: 54px 40px; border-radius: 28px; text-align: center; margin-bottom: 24px; color: white;}
.hero h1 { font-size: 46px; font-weight: 800; line-height: 1.05; margin:0; color: white;}
.swatch { width: 44px; height: 44px; border-radius: 10px; border: 2px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.12); margin: 0 auto;}
.stButton>button { background:#111; color:white; border-radius:10px; height:44px; font-weight:600; width:100%;}
.stDownloadButton>button { background: #111; color: white; border-radius: 12px; height: 54px; font-weight: 700; width:100%;}

    /* --- MOBILE RESPONSIVE FIX --- */
    @media (max-width: 768px) {
       .block-container { padding: 1rem 1rem 2rem 1rem!important; }
       .hero { padding: 32px 20px!important; border-radius: 20px!important; margin-bottom: 16px!important;}
       .hero h1 { font-size: 30px!important; line-height: 1.1!important;}
       .hero p { font-size: 13px!important;}

        /* Columns stack on mobile */
        [data-testid="column"] {
            width: 100%!important;
            flex: 1 1 100%!important;
            min-width: 100%!important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column!important;
            gap: 1.5rem!important;
        }
        /* Make swatches bigger for touch */
       .swatch { width: 54px!important; height: 54px!important;}
       .stButton>button { height: 52px!important; font-size: 16px!important;}
       .stDownloadButton>button { height: 60px!important; font-size: 17px!important;}
    }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR ---
try:
    if os.path.exists("logo.png"):
        logo_img = Image.open("logo.png")
        c1, c2 = st.columns([0.12, 0.88])
        with c1: st.image(logo_img, use_container_width=True)
        with c2: st.markdown('<div style="padding-top:10px;"><span style="font-size:20px; font-weight:800;">PureFrame</span> <span style="font-weight:300; color:#888;">STUDIO</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="display:flex; justify-content:space-between; padding: 10px 0 20px 0; border-bottom:1px solid #eee; margin-bottom:20px;"><div style="font-size:20px; font-weight:800;">PureFrame <span style="font-weight:300; color:#888;">STUDIO</span></div><div style="font-size:10px; font-weight:700; color:#888; border:1px solid #eee; padding:5px 10px; border-radius:20px; background:white;">AMAZON READY</div></div>', unsafe_allow_html=True)
except:
    st.markdown('<div style="font-size:20px; font-weight:800; padding-bottom:20px;">PureFrame <span style="font-weight:300;">STUDIO</span></div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>Product Photos,<br>Studio Ready.</h1><p style="color:#888; font-size:14px; margin-top:10px;">AI removal • Custom color • 2000x2000 Amazon compliant</p></div>', unsafe_allow_html=True)

# --- CONTROLS ---
top1, top2, top3 = st.columns([1.3, 1, 1], gap="medium")
with top1:
    files = st.file_uploader("Upload Images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
with top2:
    st.markdown("**Background Color**")
    cols = st.columns(5)
    colors = ["#FFFFFF","#000000","#F2F2F0","#3B82F6","#22C55E"]
    for col, clr in zip(cols, colors):
        with col:
            if st.button(" ", key=f"c_{clr}"):
                st.session_state.bg_color = clr
                st.rerun()
            st.markdown(f"<div class='swatch' style='background:{clr}'></div>", unsafe_allow_html=True)
    picked = st.color_picker("Custom", st.session_state.bg_color, label_visibility="collapsed")
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()
with top3:
    size = st.selectbox("Export Size", ["2000x2000", "1080x1080", "Original"], label_visibility="collapsed")
    do_remove = st.toggle("AI Removal", value=True)

# --- PROCESS ---
if files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    processed = []
    prog = st.progress(0)

    for idx, f in enumerate(files):
        orig = Image.open(f).convert("RGBA")
        cut = remove_bg_safe(orig) if do_remove else orig
        w,h = cut.size
        m = max(w,h) + int(max(w,h)*0.08)
        base = Image.new("RGBA", (m,m), (r,g,b,255))
        base.paste(cut, ((m-w)//2, (m-h)//2), cut)
        if "2000" in size:
            final = base.resize((2000,2000), Image.LANCZOS)
        elif "1080" in size:
            final = base.resize((1080,1080), Image.LANCZOS)
        else:
            final = base
        processed.append((f.name, final.convert("RGB")))
        prog.progress((idx+1)/len(files))

    st.divider()
    st.markdown(f"#### Result - {len(processed)} Images")
    # On mobile, show 2 columns only for better view
    cols = st.columns(2)
    for i, (name, img) in enumerate(processed):
        with cols[i % 2]:
            st.image(img, caption=name[:18], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=95)
            z.writestr(f"pureframe_{name.rsplit('.',1)[0]}.jpg", b.getvalue())

    st.download_button(f"Download {len(processed)} Images ZIP", data=zbuf.getvalue(), file_name="pureframe.zip", mime="application/zip", use_container_width=True)
else:
    st.markdown('<div style="text-align:center; padding:70px 20px; background:white; border-radius:20px; border:1.5px dashed #ddd;">Drop images to start<br><span style="color:#999; font-size:12px;">Mobile & Desktop Ready • Bulk up to 50 images</span></div>', unsafe_allow_html=True)
