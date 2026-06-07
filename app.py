import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FLUX Caricature Pro", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #4F46E5; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10B981; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- REPLICATE AUTHENTICATION ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("Missing Replicate API Token! Please add it to 'Secrets' in the Streamlit Cloud Dashboard.")
    st.stop()

# --- STYLE DEFINITIONS ---
STYLE_MAP = {
    "Professional Caricature": {
        "prompt": "A professional digital caricature of the person in the image, exaggerated features, big head, expressive smile, hand-drawn digital art style, high quality",
        "strength": 0.65  # Reverted to 0.65 for better likeness preservation
    },
    "Disney/Pixar Style": {
        "prompt": "A high-quality 3D character render, Disney Pixar style, big expressive eyes, smooth skin, cinematic lighting, stylized animation look",
        "strength": 0.60
    },
    "Comic Book Hero": {
        "prompt": "A vibrant comic book illustration, Marvel/DC style, bold ink lines, cel-shaded, superhero aesthetic",
        "strength": 0.55
    }
}

# --- MAIN UI ---
st.title("🎨 FLUX Caricature Pro")
st.write("Exaggeration level reverted to **0.65** for a balanced likeness.")

selected_style = st.sidebar.selectbox("Choose Your Style", list(STYLE_MAP.keys()))

uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Generate My Caricature ✨"):
        with col2:
            with st.spinner("FLUX Pro is stylizing your photo..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # Run FLUX Kontext Pro
                    output = replicate.run(
                        "black-forest-labs/flux-kontext-pro",
                        input={
                            "image": uploaded_file,
                            "prompt": cfg["prompt"],
                            "prompt_strength": cfg["strength"],
                            "guidance": 3.5,
                            "num_outputs": 1,
                            "aspect_ratio": "1:1",
                            "output_format": "jpg",
                            "output_quality": 95
                        }
                    )

                    # Get Result
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Generated Result", use_container_width=True)

                    st.download_button(
                        label="📥 Download JPG",
                        data=res_bytes,
                        file_name=f"caricature_065.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Powered by Black Forest Labs & Replicate")
