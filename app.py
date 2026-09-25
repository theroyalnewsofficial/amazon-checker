import streamlit as st
from PIL import Image
import io
import zipfile
import pandas as pd

st.set_page_config(page_title="Amazon Image Checker", page_icon="📦", layout="wide")
st.title("📦 Amazon Image Checker Bot - Pro")
st.write("Amazon এর নিয়ম: 2000x2000, ব্যাকগ্রাউন্ড ১০০% সাদা")

uploaded_files = st.file_uploader("ছবি আপলোড করো (৫০০টা পর্যন্ত)", type=["jpg","jpeg","png"], accept_multiple_files=True)

if uploaded_files:
    report_data = []
    fixed_images = []

    for file in uploaded_files:
        img = Image.open(file).convert("RGB")
        w, h = img.size

        size_ok = w >= 2000 and h >= 2000
        # আরেকটু স্মার্ট চেক
        corners = [img.getpixel((5,5)), img.getpixel((w-6,5)), img.getpixel((5,h-6)), img.getpixel((w-6,h-6))]
        white_bg = all(r > 230 and g > 230 and b > 230 for r,g,b in corners)

        status = "✅ OK" if (size_ok and white_bg) else "❌ Fix লাগবে"
        
        report_data.append({
            "ফাইলের নাম": file.name,
            "সাইজ": f"{w}x{h}",
            "সাইজ OK?": "হ্যাঁ" if size_ok else "না",
            "BG সাদা?": "হ্যাঁ" if white_bg else "না",
            "স্ট্যাটাস": status
        })

        # ফিক্স
        fixed = Image.new("RGB", (2000,2000), (255,255,255))
        img_copy = img.copy()
        img_copy.thumbnail((1700,1700))
        fixed.paste(img_copy, ((2000-img_copy.width)//2, (2000-img_copy.height)//2))
        fixed_images.append((file.name, fixed))

    # সুন্দর টেবিল
    st.subheader("📊 রিপোর্ট")
    df = pd.DataFrame(report_data)
    st.dataframe(df, use_container_width=True)

    ok_count = sum(1 for r in report_data if "OK" in r["স্ট্যাটাস"])
    st.metric("মোট OK ছবি", f"{ok_count} / {len(report_data)}")

    # Zip Download
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for name, fimg in fixed_images:
            img_buffer = io.BytesIO()
            fimg.save(img_buffer, format="JPEG", quality=95)
            zip_file.writestr(f"fixed_{name}.jpg", img_buffer.getvalue())
    
    st.download_button("📥 সব ঠিক করা ছবি ZIP ডাউনলোড করো", zip_buffer.getvalue(), "fixed_amazon_images.zip", "application/zip", type="primary")