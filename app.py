import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Caricature Studio", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #6366f1; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- REPLICATE AUTHENTICATION ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("Missing Replicate API Token! Please add it to 'Secrets' in the Streamlit Cloud Dashboard.")
    st.stop()

# --- STYLE DEFINITIONS ---
# strength: 0.1 (stays very close to photo) to 0.9 (complete change)
STYLE_MAP = {
    "Funny Caricature": {
        "prompt": "A professional digital caricature of the person, highly exaggerated funny facial features, big head, tiny body, colorful hand-drawn illustration style, high detail",
        "strength": 0.65
    },
    "Pixar Style": {
        "prompt": "Disney Pixar character 3D render, big expressive eyes, smooth stylized skin, cinematic 3D lighting, cute animation look",
        "strength": 0.55
    },
    "Ink Sketch": {
        "prompt": "Hand-drawn artistic charcoal sketch, caricature style, bold lines, high contrast, black and white, messy pencil strokes",
        "strength": 0.70
    }
}

# --- MAIN UI ---
st.title("🎨 AI Caricature Studio")
st.write("Using **Stability AI** (Latest Version)")

selected_style = st.sidebar.selectbox("Choose Style", list(STYLE_MAP.keys()))

uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Generate My Caricature ✨"):
        with col2:
            with st.spinner("Stability AI is drawing..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # We use the slug "stability-ai/sdxl" WITHOUT the hash. 
                    # This ensures the app never breaks when they update the model.
                    output = replicate.run(
                        "stability-ai/sdxl",
                        input={
                            "image": uploaded_file,
                            "prompt": cfg["prompt"],
                            "prompt_strength": cfg["strength"],
                            "negative_prompt": "photorealistic, ugly, blurry, low quality, distorted face",
                            "guidance_scale": 8.0,
                            "num_inference_steps": 50,
                            "output_format": "jpg"
                        }
                    )

                    # Get Result
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Generated Result", use_container_width=True)

                    st.download_button(
                        label="📥 Download JPG",
                        data=res_bytes,
                        file_name=f"caricature.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("If this is a permission error, visit https://replicate.com/stability-ai/sdxl and run it once on the website to accept terms.")

st.markdown("---")
st.caption("Powered by Stability AI & Replicate")
