import streamlit as st
from PIL import Image
import io
import zipfile
import os

# --- SAFE AI IMPORT ---
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    @st.cache_resource
    def get_session():
        # isnet-general-use = Product এর জন্য সবচেয়ে Smooth & Accurate
        return new_session("isnet-general-use")

    def remove_bg_smooth(image):
        try:
            session = get_session()
            # Alpha Matting = Edge Smooth
            result = remove(
                image,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )
            # Safety: যদি 90% কেটে যায়, মানে ভুল কেটেছে, Original ফেরত দাও
            if result.getbbox():
                bbox = result.getbbox()
                if bbox:
                    area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])
                    total = image.size[0] * image.size[1]
                    if area < (total * 0.05):
                        return image
            else:
                return image
            return result
        except:
            return image

except:
    REMBG_AVAILABLE = False
    def remove_bg_smooth(image):
        return image

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="PureFrame Studio",
    page_icon="logo.png" if os.path.exists("logo.png") else "⬢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

def set_color(c):
    st.session_state.bg_color = c

# --- WHITE LABEL CSS - HIDE ALL STREAMLIT BRANDING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    #MainMenu, footer,.stDeployButton, header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none!important; visibility: hidden!important; height: 0!important;}
 .stApp > header {display: none!important;}
    section[data-testid="stSidebar"] {display: none!important;}

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
 .stApp { background: #f8f8f7; }
 .navbar { display:flex; justify-content:space-between; align-items:center; padding: 12px 0 28px 0; border-bottom: 1px solid #eee; margin-bottom: 28px;}
 .hero { background: #0e0e0e; padding: 64px 40px; border-radius: 32px; text-align: center; margin-bottom: 32px; color: white;}
 .hero h1 { font-size: 50px; font-weight: 800; line-height: 1.05; margin:0; color: white; letter-spacing: -1.5px; }
 .hero h1 i { font-style: normal; color: #a3a3a3; font-weight: 300; }
 .hero p { color: #888; font-size: 15px; margin-top: 14px;}
 .swatch { width: 46px; height: 46px; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.12); margin: 0 auto; cursor: pointer; transition: 0.2s; }
 .swatch:hover { transform: scale(1.08); }
 .stButton>button { background:#111; color:white; border-radius:12px; height:48px; font-weight:600; border:none; width:100%;}
 .stDownloadButton>button { background: #111; color: white; border-radius: 12px; height: 54px; font-weight: 700; width:100%;}
</style>
""", unsafe_allow_html=True)

# --- NAVBAR WITH LOGO ---
try:
    logo_img = Image.open("logo.png")
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        st.image(logo_img, use_container_width=True)
    with c2:
        st.markdown('<div style="padding-top: 14px; display:flex; justify-content:space-between; align-items:center;"><div><span style="font-size:22px; font-weight:800; color:#111; letter-spacing:-0.8px;">PureFrame</span> <span style="font-size:22px; font-weight:300; color:#888;">STUDIO</span></div><div style="color:#888; font-size:11px; font-weight:700; letter-spacing:1.2px; border:1px solid #e5e5e5; padding:6px 12px; border-radius:20px; background:white;">AMAZON • SHOPIFY READY</div></div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="navbar"><div style="font-size:22px; font-weight:800; color:#111;">PureFrame <span style="font-weight:300; color:#888;">STUDIO</span></div><div style="color:#888; font-size:11px; font-weight:700; letter-spacing:1.2px; border:1px solid #e5e5e5; padding:6px 12px; border-radius:20px; background:white;">AMAZON • SHOPIFY READY</div></div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>Product Photos,<br><i>Studio Ready.</i></h1><p>AI background removal • Custom studio color • 2000x2000 Amazon compliant export</p></div>', unsafe_allow_html=True)

# --- CONTROLS ---
top1, top2, top3 = st.columns([1.3, 1, 1], gap="large")
with top1:
    files = st.file_uploader("Upload images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.caption(f"✓ {len(files)} images selected • Bulk enabled")

with top2:
    st.markdown("**Background**")
    cols = st.columns(5)
    colors = ["#FFFFFF","#000000","#F2F2F0","#3B82F6","#22C55E"]
    names = ["White","Black","Studio","Blue","Green"]
    for col, clr, nm in zip(cols, colors, names):
        with col:
            if st.button(" ", key=f"cl_{clr}"):
                set_color(clr); st.rerun()
            st.markdown(f"<div class='swatch' style='background:{clr}'></div><div style='text-align:center; font-size:10px; font-weight:600; color:#999; margin-top:6px'>{nm}</div>", unsafe_allow_html=True)
    picked = st.color_picker("Custom", st.session_state.bg_color, label_visibility="collapsed")
    if picked!= st.session_state.bg_color:
        st.session_state.bg_color = picked
        st.rerun()

with top3:
    st.markdown("**Export**")
    size = st.selectbox("Size", ["2000x2000 (Amazon)", "1080x1080 (Square)", "Original"], label_visibility="collapsed")
    do_remove = st.toggle("AI Smooth Removal", value=True, disabled=not REMBG_AVAILABLE)
    st.markdown(f"<div style='margin-top:10px; padding:10px; background:{st.session_state.bg_color}; border:1px solid #eee; border-radius:10px; text-align:center; font-weight:700; font-size:12px; color:{'#000' if st.session_state.bg_color.upper() in ['#FFFFFF','#F2F2F0'] else '#fff'}'>{st.session_state.bg_color.upper()} • {size.split(' ')[0]}</div>", unsafe_allow_html=True)

# --- PROCESSING WITH SMOOTH CUT ---
if files:
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    processed = []
    prog = st.progress(0, text="Processing with smooth edge...")

    for idx, f in enumerate(files):
        orig = Image.open(f).convert("RGBA")
        cut = remove_bg_smooth(orig) if do_remove else orig

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

        processed.append((f.name, final.convert("RGB")))
        prog.progress((idx+1)/len(files), text=f"Processing {idx+1}/{len(files)} - Smooth Edge")

    st.divider()
    st.markdown(f"#### Processed • {len(processed)} Images • Smooth Cut Applied")
    g_cols = st.columns(4)
    for i, (name, img) in enumerate(processed):
        with g_cols[i % 4]:
            st.image(img, caption=name[:22], use_container_width=True)

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        for name, img in processed:
            b = io.BytesIO()
            img.save(b, format="JPEG", quality=96, optimize=True)
            z.writestr(f"pureframe_{st.session_state.bg_color.replace('#','')}_{name.rsplit('.',1)[0]}.jpg", b.getvalue())

    st.download_button(f"Download {len(processed)} Images as ZIP", data=zbuf.getvalue(), file_name=f"pureframe_studio_{st.session_state.bg_color.replace('#','')}.zip", mime="application/zip", use_container_width=True)
    st.balloons()
else:
    st.markdown("""
    <div style="text-align:center; padding:90px 40px; background:white; border-radius:24px; border:1.5px dashed #e5e5e5;">
        <div style="width:64px; height:64px; background:#111; color:white; border-radius:16px; display:flex; align-items:center; justify-content:center; margin:0 auto; font-size:28px; font-weight:800;">P</div>
        <h3 style="margin:18px 0 8px 0; color:#111; font-weight:700;">Drop product images to start</h3>
        <p style="color:#999; font-size:13px;">PNG, JPG, WEBP • Bulk up to 50 images • Smooth edge technology</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><div style='text-align:center; color:#bbb; font-size:11px;'>© 2026 PureFrame Studio • Professional Product Studio</div>", unsafe_allow_html=True)
