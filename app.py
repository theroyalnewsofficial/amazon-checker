import streamlit as st
from PIL import Image
import io
import zipfile
import os

st.set_page_config(page_title="PureFrame Studio", page_icon="⬢", layout="wide", initial_sidebar_state="collapsed")

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
        # এখানে Alpha Matting দিয়ে Smooth Cut
        result = remove(image, session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        if not result.getbbox():
            return image
        return result
    except:
        return image

st.markdown("""
<style>
    #MainMenu, footer,.stDeployButton, header, [data-testid="stHeader"] {display: none!important;}
   .stApp { background: #f8f8f7; }
   .hero { background: #0e0e0e; padding: 54px 40px; border-radius: 28px; text-align: center; margin-bottom: 24px; color: white;}
   .swatch { width: 44px; height: 44px; border-radius: 10px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.12); margin: 0 auto;}
   .stButton>button { background:#111; color:white; border-radius:10px; height:44px; font-weight:600; width:100%;}
   .stDownloadButton>button { background: #111; color: white; border-radius: 12px; height: 54px; font-weight: 700; width:100%;}
</style>
""", unsafe_allow_html=True)

# NAVBAR
st.markdown('<div style="display:flex; justify-content:space-between; padding: 10px 0 20px 0; border-bottom:1px solid #eee; margin-bottom:20px;"><div style="font-size:20px; font-weight:800;">PureFrame <span style="font-weight:300; color:#888;">STUDIO</span></div><div style="font-size:10px; font-weight:700; color:#888; border:1px solid #eee; padding:5px 10px; border-radius:20px; background:white;">MAIN IMAGE BG CHANGE</div></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>Main Background<br>Changer</h1><p style="color:#888;">Select color -> Main image background will change</p></div>', unsafe_allow_html=True)

top1, top2, top3 = st.columns([1.3, 1, 1], gap="medium")
with top1:
    files = st.file_uploader("Upload", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
with top2:
    st.markdown("**Choose New Background Color**")
    cols = st.columns(5)
    colors = ["#FFFFFF","#000000","#F2F2F0","#3B82F6","#FF0000"]
    for col, clr in zip(cols, colors):
        with col:
            if st.button(" ", key=f"c_{clr}"):
                st.session_state.bg_color = clr
                st.rerun()
            st.markdown(f"<div class='swatch' style='background:{clr}'></div>", unsafe_allow_html=True)
    picked = st.color_picker("Custom Color", st.session_state.bg_color)
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()
    st.markdown(f"<div style='margin-top:10px; padding:12px; background:{st.session_state.bg_color}; border-radius:10px; text-align:center; font-weight:700; border:1px solid #ddd;'>{st.session_state.bg_color}</div>", unsafe_allow_html=True)

with top3:
    size = st.selectbox("Export Size", ["2000x2000", "1080x1080"], label_visibility="collapsed")
    do_remove = st.toggle("AI Remove Background", value=True)

# --- MAIN LOGIC - IMAGE ER BG CHANGE ---
if files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    processed = []
    prog = st.progress(0, text="Changing main background...")

    for idx, f in enumerate(files):
        orig = Image.open(f).convert("RGBA")

        # 1. BG REMOVE - Subject কে আলাদা করো
        cut = remove_bg_safe(orig) if do_remove else orig

        # 2. MAIN IMAGE ER BG CHANGE - এখানেই আসল কাজ
        w,h = cut.size
        m = max(w,h)
        m = m + int(m*0.10) # 10% padding
        # তুমি যে কালার Pick করেছো, সেই কালার দিয়ে নতুন Canvas বানাও
        new_bg = Image.new("RGBA", (m,m), (r,g,b,255))
        # তার উপর Subject টা বসাও
        new_bg.paste(cut, ((m-w)//2, (m-h)//2), cut)

        final = new_bg.resize((2000,2000), Image.LANCZOS) if "2000" in size else new_bg.resize((1080,1080), Image.LANCZOS)
        processed.append((f.name, final.convert("RGB")))
        prog.progress((idx+1)/len(files))

    st.divider()
    st.markdown(f"### Result - Main Background Changed to {st.session_state.bg_color}")
    cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with cols[i % 4]:
            st.image(img, caption=name[:18], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=95)
            z.writestr(f"pureframe_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b.getvalue())
    st.download_button(f"Download {len(processed)} Images", data=zbuf.getvalue(), file_name="pureframe_main_bg_changed.zip", mime="application/zip", use_container_width=True)
else:
    st.markdown('<div style="text-align:center; padding:70px; background:white; border-radius:20px; border:1.5px dashed #ddd;">Image upload koro - Main image er background change hobe</div>', unsafe_allow_html=True)
