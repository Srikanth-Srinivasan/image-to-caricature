import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Caricature Studio", page_icon="🎨", layout="centered")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #28a745; color: white; }
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
    "Classic Exaggerated": {
        "prompt": "extreme caricature, highly exaggerated facial features, big head, tiny body, funny digital art",
        "denoising": 0.7,
        "id_strength": 0.8
    },
    "Disney/Pixar 3D": {
        "prompt": "Disney Pixar character style, 3D render, expressive eyes, smooth textures, cinematic lighting",
        "denoising": 0.5,
        "id_strength": 0.7
    },
    "GTA Loading Screen": {
        "prompt": "GTA V loading screen art, thick brush strokes, high contrast, cel-shaded",
        "denoising": 0.6,
        "id_strength": 0.75
    },
    "Pencil Sketch": {
        "prompt": "charcoal caricature sketch, artistic lines, black and white, hand-drawn",
        "denoising": 0.8,
        "id_strength": 0.85
    }
}

# --- MAIN UI ---
st.title("🎨 AI Caricature Studio")
st.write("Turn your photo into a hilarious caricature using AI.")

selected_style = st.sidebar.selectbox("Choose Your Style", list(STYLE_MAP.keys()))

uploaded_file = st.file_uploader("Upload a photo (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Magic Generate ✨"):
        with col2:
            with st.spinner("Processing..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # UPDATED: Using the model name directly instead of the old version hash
                    # This ensures we use the latest working version.
                    output = replicate.run(
                        "fofr/face-to-many",
                        input={
                            "image": uploaded_file,
                            "style": "Cartoon", # Added a base style hint
                            "prompt": cfg["prompt"],
                            "instant_id_strength": cfg["id_strength"],
                            "denoising_strength": cfg["denoising"],
                            "negative_prompt": "realistic, photo, ugly, blurry"
                        }
                    )

                    # Get Result
                    res_url = output[0]
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Your Caricature", use_container_width=True)

                    st.download_button(
                        label="📥 Download Caricature",
                        data=res_bytes,
                        file_name=f"caricature.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Check if your Replicate account has credits or if the API token is correct.")

st.markdown("---")
st.caption("Powered by Replicate AI & Streamlit Cloud")
