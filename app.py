import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Stability Caricature Studio", page_icon="🖌️", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007BFF; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #28A745; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- REPLICATE AUTHENTICATION ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("Missing Replicate API Token! Please add it to 'Secrets' in the Streamlit Cloud Dashboard.")
    st.stop()

# --- STYLE DEFINITIONS ---
# Stability AI SDXL uses 'prompt_strength' to control the transformation.
STYLE_MAP = {
    "Classic Caricature": {
        "prompt": "Professional digital caricature, exaggerated funny facial features, big head, tiny body, colorful hand-drawn style, high detail, masterpiece",
        "strength": 0.65
    },
    "Pixar Animation": {
        "prompt": "Disney Pixar 3D character style, big expressive eyes, smooth textures, cinematic 3D render, cute stylized look",
        "strength": 0.60
    },
    "Superhero Comic": {
        "prompt": "Modern comic book art style, bold ink lines, vibrant colors, superhero character design, cel-shaded illustration",
        "strength": 0.55
    }
}

# --- MAIN UI ---
st.title("🖌️ Stability Caricature Studio")
st.write("Using **Stability AI (SDXL)** to transform your photo.")

selected_style = st.sidebar.selectbox("Choose Your Style", list(STYLE_MAP.keys()))

uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Generate My Caricature ✨"):
        with col2:
            with st.spinner("Stability AI is processing..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # Run Stability AI SDXL (Image-to-Image)
                    output = replicate.run(
                        "stability-ai/sdxl:7762d339291264c5029e24b4249a4f4d2f09923835f1f9435b540f2e08816c7f",
                        input={
                            "image": uploaded_file,
                            "prompt": cfg["prompt"],
                            "prompt_strength": cfg["strength"],
                            "negative_prompt": "photorealistic, ugly, blurry, low quality, distorted",
                            "num_outputs": 1,
                            "guidance_scale": 7.5,
                            "refine": "expert_ensemble_refiner",
                            "apply_watermark": False
                        }
                    )

                    # Get Result
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Stability Result", use_container_width=True)

                    st.download_button(
                        label="📥 Download JPG",
                        data=res_bytes,
                        file_name=f"stability_caricature.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Powered by Stability AI & Replicate")
