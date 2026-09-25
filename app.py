import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="PixelPerfect V4", page_icon="✂️", layout="wide", initial_sidebar_state="collapsed")

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

def set_color(c):
    st.session_state.bg_color = c

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    .hero { background: linear-gradient(135deg, #111 0%, #333 100%); padding: 50px; border-radius: 24px; text-align:center; margin-bottom:20px; }
    .hero h1 { color: white; font-size: 44px; font-weight: 800; }
    .hero p { color: #aaa; }
    .glass-card { background: rgba(255,255,255,0.9); border-radius: 20px; padding: 20px; border: 1px solid #eee; box-shadow: 0 8px 32px rgba(0,0,0,0.08); }
    .stButton>button { background:#111; color:white; border-radius:12px; height:56px; font-weight:700; border:none; }
    .stButton>button:hover { background:#FF9900; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><h1>Real AI Background Remover</h1><p>Photoshop style - Subject thakbe, background remove hobe, then any color</p></div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("Image Upload Koro", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")

if uploaded:
    st.markdown("**Quick Colors:**")
    cols = st.columns(7)
    colors = ["#FFFFFF","#000000","#3B82F6","#FBBF24","#22C55E","#EF4444","#8B5CF6"]
    labels = ["Amazon","Black","Blue","Yellow","Green","Red","Purple"]
    for col, clr, lbl in zip(cols, colors, labels):
        with col:
            if st.button(" ", key=f"c_{clr}", use_container_width=True):
                set_color(clr); st.rerun()
            st.markdown(f"<div style='text-align:center'><div style='width:42px; height:42px; border-radius:50%; background:{clr}; border:3px solid white; box-shadow:0 2px 8px rgba(0,0,0,0.2); margin:0 auto'></div><span style='font-size:10px'>{lbl}</span></div>", unsafe_allow_html=True)

    col_pick1, col_pick2 = st.columns(2)
    with col_pick1:
        pick = st.color_picker("Custom Color", st.session_state.bg_color)
        if pick != st.session_state.bg_color:
            st.session_state.bg_color = pick
            st.rerun()
    with col_pick2:
        size = st.selectbox("Size", ["2000x2000 Amazon", "1080x1080 Insta", "Original"])
        st.markdown(f"<div style='padding:10px; background:{st.session_state.bg_color}; border-radius:10px; text-align:center; font-weight:700; border:1px solid #ddd;'>{st.session_state.bg_color}</div>", unsafe_allow_html=True)

    original = Image.open(uploaded).convert("RGBA")
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='glass-card'><b>Original</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='glass-card'><b>Result - {st.session_state.bg_color}</b>", unsafe_allow_html=True)
        # --- REAL AI PROCESSING INSIDE TRY ---
        try:
            from rembg import remove
            with st.spinner("✂️ AI subject katche... 10 sec lagbe first time"):
                no_bg = remove(original)
            
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
            st.image(final_rgb, use_container_width=True)
            buf = io.BytesIO(); final_rgb.save(buf, format="JPEG", quality=98)
            
            if st.download_button("⬇ Download JPG", data=buf.getvalue(), file_name=f"REMOVED_{uploaded.name}", mime="image/jpeg", use_container_width=True):
                st.balloons()
                st.success(f"Background Removed + {st.session_state.bg_color} Applied!")

        except Exception as e:
            st.error(f"AI Model Download Hocche... 1-2 min por refresh koro. Error: {e}")
            st.info("First time ektu time lage, model download hocche. Page ta 2 min por refresh koro.")

        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("👆 Upor e image upload koro - ebar asol Photoshop er moto background remove hobe!")

st.markdown("<br><center style='color:#888; font-size:12px;'>V4 Real Remover • Stable Build</center>", unsafe_allow_html=True)
