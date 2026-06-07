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

# --- STYLE DEFINITIONS FOR FLUX ---
# prompt_strength: 0.1 is almost no change, 0.9 is a total change. 0.6 is the sweet spot for caricatures.
STYLE_MAP = {
    "Professional Caricature": {
        "prompt": "A professional digital caricature of the person in the image, exaggerated funny features, big head, expressive smile, hand-drawn style, high resolution, detailed art",
        "strength": 0.65
    },
    "Pixar 3D Style": {
        "prompt": "A high-quality 3D character render of the person, Disney Pixar style, big eyes, smooth skin, cinematic lighting, stylized animation look",
        "strength": 0.60
    },
    "Comic Book Hero": {
        "prompt": "A vibrant comic book illustration of the person, Marvel/DC style, bold lines, cel-shaded, superhero aesthetic",
        "strength": 0.55
    }
}

# --- MAIN UI ---
st.title("🎨 FLUX Caricature Pro")
st.write("Using `flux-kontext-pro` to transform your photos.")

selected_style = st.sidebar.selectbox("Choose Your Style", list(STYLE_MAP.keys()))
st.sidebar.info("FLUX Kontext Pro is a high-fidelity model. Generation may take 20-30 seconds.")

uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original", use_container_width=True)

    if st.button("Generate with FLUX Pro ✨"):
        with col2:
            with st.spinner("FLUX is reimagining your image..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # Call FLUX Kontext Pro
                    # Note: FLUX models use 'image' and 'prompt_strength' for image-to-image
                    output = replicate.run(
                        "black-forest-labs/flux-kontext-pro",
                        input={
                            "image": uploaded_file,
                            "prompt": cfg["prompt"],
                            "prompt_strength": cfg["strength"],
                            "guidance": 3.5,
                            "num_outputs": 1,
                            "aspect_ratio": "1:1",
                            "output_format": "webp",
                            "output_quality": 90
                        }
                    )

                    # FLUX output is typically a list or a single URL string
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="FLUX Caricature", use_container_width=True)

                    st.download_button(
                        label="📥 Download WebP",
                        data=res_bytes,
                        file_name=f"flux_caricature.webp",
                        mime="image/webp"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Ensure you have permission to use black-forest-labs/flux-kontext-pro on Replicate.")

st.markdown("---")
st.caption("Powered by Black Forest Labs & Replicate")
