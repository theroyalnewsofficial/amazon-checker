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

st.set_page_config(page_title="PixelPerfect Bulk", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

def set_color(c):
    st.session_state.bg_color = c

st.markdown("""
<style>
    #MainMenu, footer, header,.stDeployButton {visibility: hidden;}
   .hero { background: linear-gradient(135deg, #111 0%, #333 100%); padding: 40px; border-radius: 24px; text-align:center; margin-bottom:20px; }
   .hero h1 { color: white; font-size: 42px; font-weight: 800; }
   .hero p { color: #aaa; }
   .glass-card { background: rgba(255,255,255,0.9); border-radius: 20px; padding: 20px; border: 1px solid #eee; }
   .stButton>button { background:#111; color:white; border-radius:12px; height:52px; font-weight:700; border:none; }
   .stButton>button:hover { background:#FF9900; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><h1>✨ Bulk Background Remover</h1><p>Select 10-20 Images at once • AI will remove & apply color • Download ZIP</p></div>""", unsafe_allow_html=True)

# CONTROLS
c1, c2, c3 = st.columns([1.2, 1, 1])
with c1:
    # --- MAIN CHANGE: accept_multiple_files=True ---
    uploaded_files = st.file_uploader("Select Multiple Images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} images selected")
with c2:
    picked = st.color_picker("Pick Background Color", st.session_state.bg_color)
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()
    # Color bubbles
    cols = st.columns(5)
    colors = ["#FFFFFF","#000000","#3B82F6","#FBBF24","#22C55E"]
    for col, clr in zip(cols, colors):
        with col:
            if st.button(" ", key=f"c_{clr}", use_container_width=True):
                set_color(clr); st.rerun()
            st.markdown(f"<div style='width:32px; height:32px; border-radius:50%; background:{clr}; border:2px solid white; box-shadow:0 2px 6px rgba(0,0,0,0.2); margin:0 auto'></div>", unsafe_allow_html=True)

with c3:
    size = st.selectbox("Size", ["2000x2000 Amazon", "1080x1080", "Original"])
    do_remove = st.toggle("✂️ Real BG Remove (AI)", value=True, disabled=not REMBG_AVAILABLE)

if uploaded_files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))

    # Process all images
    processed_images = []

    progress = st.progress(0, text="Processing...")
    for i, file in enumerate(uploaded_files):
        original = Image.open(file).convert("RGBA")

        if do_remove and REMBG_AVAILABLE:
            try:
                session = get_session()
                no_bg = remove(original, session=session)
            except:
                no_bg = original
        else:
            no_bg = original

        # Apply color background
        w,h = no_bg.size
        m = max(w,h)
        m = m + int(m*0.05*2)
        bg_base = Image.new("RGBA", (m,m), (r,g,b,255))
        bg_base.paste(no_bg, ((m-w)//2, (m-h)//2), no_bg)

        if "2000" in size:
            final = bg_base.resize((2000,2000), Image.LANCZOS)
        else:
            final = bg_base

        final_rgb = final.convert("RGB")
        processed_images.append((file.name, final_rgb))
        progress.progress((i+1)/len(uploaded_files), text=f"Processing {i+1}/{len(uploaded_files)}")

    st.divider()
    st.markdown(f"### ✨ Results - {len(processed_images)} Images • BG: {st.session_state.bg_color}")

    # Show in grid
    grid_cols = st.columns(4)
    for idx, (name, img) in enumerate(processed_images):
        with grid_cols[idx % 4]:
            st.image(img, caption=name, use_container_width=True)

    # ZIP Download
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zip_file:
        for name, img in processed_images:
            img_buf = io.BytesIO()
            img.save(img_buf, format="JPEG", quality=95)
            zip_file.writestr(f"pixelperfect_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", img_buf.getvalue())

    st.download_button(
        label=f"⬇ Download All {len(processed_images)} Images as ZIP",
        data=zip_buf.getvalue(),
        file_name=f"pixelperfect_bulk_{st.session_state.bg_color.replace('#','')}.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary"
    )
    st.balloons()

else:
    st.info("👆 Upor theke ekbare 10-20 ta image select koro - Ctrl diye multiple select kora jabe!")
