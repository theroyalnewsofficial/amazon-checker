import streamlit as st
from PIL import Image
import io

# This is the real AI remover
from rembg import remove

st.set_page_config(page_title="PixelPerfect V4 - Real BG Remover", page_icon="✂️", layout="wide", initial_sidebar_state="collapsed")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def set_color(c):
    st.session_state.bg_color = c

dark_bg = "#0a0a0a" if st.session_state.dark_mode else "#fcfcfc"
card_bg = "rgba(30,30,30,0.85)" if st.session_state.dark_mode else "rgba(255,255,255,0.85)"
text_color = "#fff" if st.session_state.dark_mode else "#111"

st.markdown(f"""
<style>
    #MainMenu, footer, header, .stDeployButton {{visibility: hidden;}}
    .stApp {{ background: {dark_bg}; }}
    .hero {{ background: linear-gradient(135deg, #111 0%, #333 100%); padding: 50px; border-radius: 24px; text-align:center; margin-bottom:20px; }}
    .hero h1 {{ color: white; font-size: 46px; font-weight: 800; }}
    .hero p {{ color: #aaa; }}
    .glass-card {{ background: {card_bg}; backdrop-filter: blur(20px); border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }}
    .stButton>button {{ background:#111; color:white; border-radius:12px; height:56px; font-weight:700; border:none; }}
    .stButton>button:hover {{ background:#FF9900; }}
</style>
""", unsafe_allow_html=True)

# Header
c1,c2 = st.columns([5,1])
with c1:
    st.markdown(f"<h2 style='color:{text_color}'>✂️ PixelPerfect V4 <span style='font-weight:400; opacity:0.6'>REAL REMOVER</span></h2>", unsafe_allow_html=True)
with c2:
    if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("""<div class="hero"><h1>Real AI Background Remover</h1><p>Photoshop style - Subject thakbe, background remove hoye jabe. Then any color.</p></div>""", unsafe_allow_html=True)

left,right = st.columns([1.8,1.2], gap="large")
with left:
    uploaded = st.file_uploader("Upload", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
    if uploaded:
        st.markdown("**Quick Colors - 1 Click**")
        cols = st.columns(7)
        colors = ["#FFFFFF","#000000","#3B82F6","#FBBF24","#22C55E","#EF4444","#8B5CF6"]
        labels = ["Amazon","Black","Blue","Yellow","Green","Red","Purple"]
        for col, clr, lbl in zip(cols, colors, labels):
            with col:
                if st.button(" ", key=f"c_{clr}", use_container_width=True):
                    set_color(clr); st.rerun()
                st.markdown(f"<div style='text-align:center'><div style='width:42px; height:42px; border-radius:50%; background:{clr}; border:3px solid white; box-shadow:0 2px 8px rgba(0,0,0,0.2); margin:0 auto'></div><span style='font-size:10px'>{lbl}</span></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='glass-card'><b style='color:{text_color}'>Settings</b>", unsafe_allow_html=True)
    pick = st.color_picker("Choose ANY Background Color", st.session_state.bg_color)
    if pick != st.session_state.bg_color:
        st.session_state.bg_color = pick; st.rerun()
    st.markdown(f"<div style='padding:10px; background:{st.session_state.bg_color}; border-radius:10px; text-align:center; font-weight:700; color:{'#000' if st.session_state.bg_color=='#FFFFFF' else '#fff'}'>{st.session_state.bg_color}</div>", unsafe_allow_html=True)
    size = st.selectbox("Size", ["2000x2000 Amazon", "1080x1080", "Original"])
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    original = Image.open(uploaded).convert("RGBA")
    
    # REAL AI REMOVAL
    with st.spinner("✂️ AI subject kete ber korche... 5 sec wait koro"):
        no_bg = remove(original) # <-- Eikhane asol magic hocche

    # Apply custom color
    hex_c = st.session_state.bg_color.lstrip('#')
    r,g,b = tuple(int(hex_c[i:i+2], 16) for i in (0,2,4))
    colored_bg = Image.new("RGBA", no_bg.size, (r,g,b,255))
    final_rgba = Image.alpha_composite(colored_bg, no_bg)

    w,h = final_rgba.size; m = max(w,h)
    square = Image.new("RGBA", (m,m), (r,g,b,255))
    square.paste(final_rgba, ((m-w)//2, (m-h)//2), final_rgba)

    if "2000" in size:
        final = square.resize((2000,2000), Image.LANCZOS)
    elif "1080" in size:
        final = square.resize((1080,1080), Image.LANCZOS)
    else:
        final = final_rgba

    final_rgb = final.convert("RGB")

    st.divider()
    c1,c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='glass-card'><b>Original</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass-card'><b>Result - BG Removed + {st.session_state.bg_color}</b>", unsafe_allow_html=True)
        st.image(final_rgb, use_container_width=True)
        buf = io.BytesIO(); final_rgb.save(buf, format="JPEG", quality=98)
        if st.download_button("⬇ Download Real Removed JPG", data=buf.getvalue(), file_name=f"REMOVED_{uploaded.name}", mime="image/jpeg", use_container_width=True):
            st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Upload koro - ebar asol Photoshop er moto background remove hobe!")
