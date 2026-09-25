import streamlit as st
from PIL import Image
import io

# Try to import rembg, if fails app will still work
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except:
    REMBG_AVAILABLE = False

st.set_page_config(page_title="PixelPerfect Pro - Color Background", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# --- PRO DESIGN - NO LOGO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
 .stDeployButton {display:none;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
 .hero { background: linear-gradient(135deg, #0f0f0f 0%, #2a2a2a 100%); color: white; padding: 50px 40px; border-radius: 20px; text-align: center; margin-bottom: 25px; }
 .hero h1 { font-size: 44px; font-weight: 800; }
 .hero p { color: #a1a1a1; }
 .stButton>button { background: #111; color: white; border-radius: 12px; height: 54px; font-weight: 600; border:none; }
 .stButton>button:hover { background: #FF9900; color: white; }
 .card { background: white; border: 1px solid #eee; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Background Remover + Custom Color</h1>
    <p>Remove background and apply any color you want. Perfect for Amazon, Shopify, eBay & Social Media.</p>
</div>
""", unsafe_allow_html=True)

# --- CONTROLS ---
c1, c2, c3 = st.columns([1.5, 1, 1])
with c1:
    uploaded_file = st.file_uploader("Upload Product Image", type=["png","jpg","jpeg","webp"])
with c2:
    # COLOR PICKER - MAIN FEATURE
    bg_color = st.color_picker("Choose Background Color", "#FFFFFF")
    st.caption(f"Selected: {bg_color}")
with c3:
    size_option = st.selectbox("Output Size", ["2000x2000 (Amazon)", "1000x1000", "Original Size"])
    remove_bg_toggle = st.toggle("✦ Remove Background (AI)", value=True, disabled=not REMBG_AVAILABLE)

if not REMBG_AVAILABLE:
    st.warning("AI Background Remover is installing... It will be ready in 2-3 minutes after deploy. Please wait and refresh.")

if uploaded_file:
    col1, col2 = st.columns(2, gap="large")
    original = Image.open(uploaded_file).convert("RGBA")

    with col1:
        st.markdown("<div class='card'><b>Original Image</b>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PROCESSING ---
    if remove_bg_toggle and REMBG_AVAILABLE:
        with st.spinner("AI is removing background..."):
            no_bg = remove(original)
    else:
        no_bg = original

    # Convert hex color to RGB
    hex_color = bg_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Create new background with selected color
    background = Image.new("RGBA", no_bg.size, (r, g, b, 255))
    final_rgba = Image.alpha_composite(background, no_bg)

    # Resize logic
    if size_option == "2000x2000 (Amazon)":
        w, h = final_rgba.size
        max_side = max(w, h)
        square = Image.new("RGBA", (max_side, max_side), (r, g, b, 255))
        square.paste(final_rgba, ((max_side - w)//2, (max_side - h)//2), final_rgba)
        final = square.resize((2000, 2000), Image.LANCZOS)
    elif size_option == "1000x1000":
        w, h = final_rgba.size
        max_side = max(w, h)
        square = Image.new("RGBA", (max_side, max_side), (r, g, b, 255))
        square.paste(final_rgba, ((max_side - w)//2, (max_side - h)//2), final_rgba)
        final = square.resize((1000, 1000), Image.LANCZOS)
    else:
        final = final_rgba

    final_rgb = final.convert("RGB")

    with col2:
        st.markdown(f"<div class='card'><b>Result with {bg_color} Background</b>", unsafe_allow_html=True)
        st.image(final_rgb, use_container_width=True)

        buf = io.BytesIO()
        final_rgb.save(buf, format="JPEG", quality=95)

        st.download_button(
            label=f"Download JPG ({bg_color})",
            data=buf.getvalue(),
            file_name=f"custom_bg_{bg_color.replace('#','')}_{uploaded_file.name.split('.')[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- COLOR PRESETS FOR AMAZON / ECOM ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🔥 Quick Presets:")
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1: st.markdown("⬜ **#FFFFFF** - Amazon Main")
    with p2: st.markdown("⬛ **#000000** - Premium")
    with p3: st.markdown("🟦 **#3B82F6** - Shopify")
    with p4: st.markdown("🟨 **#FBBF24** - Lifestyle")
    with p5: st.markdown(f"🎨 **{bg_color}** - Custom")

else:
    st.info("👆 Upload an image and pick any background color you want!")

st.markdown("<br><center style='color:#aaa; font-size:12px;'>© 2026 PixelPerfect Pro • Background Remover + Custom Color Tool</center>", unsafe_allow_html=True)
