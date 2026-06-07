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
# This looks for a Secret named REPLICATE_API_TOKEN in your Streamlit Dashboard
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("Missing Replicate API Token! Please add it to 'Secrets' in the Streamlit Cloud Dashboard.")
    st.info("Format: REPLICATE_API_TOKEN = 'r8_your_token_here'")
    st.stop()

# --- STYLE DEFINITIONS ---
STYLE_MAP = {
    "Classic Exaggerated": {
        "prompt": "extreme caricature, highly exaggerated facial features, big head, tiny body, funny digital art, professional illustration",
        "denoising": 0.7,
        "id_strength": 0.8
    },
    "Disney/Pixar 3D": {
        "prompt": "Disney Pixar character style, 3D render, expressive eyes, smooth textures, cinematic lighting, masterpiece",
        "denoising": 0.5,
        "id_strength": 0.7
    },
    "GTA Loading Screen": {
        "prompt": "GTA V loading screen art, thick brush strokes, high contrast, cel-shaded, vibrant urban colors",
        "denoising": 0.6,
        "id_strength": 0.75
    },
    "Pencil Sketch": {
        "prompt": "rough charcoal caricature sketch, messy artistic lines, black and white, hand-drawn on paper",
        "denoising": 0.8,
        "id_strength": 0.85
    }
}

# --- MAIN UI ---
st.title("🎨 AI Caricature Studio")
st.write("Turn your photo into a hilarious caricature using AI.")

# Sidebar for style selection only
selected_style = st.sidebar.selectbox("Choose Your Style", list(STYLE_MAP.keys()))
st.sidebar.markdown("---")
st.sidebar.write("### Instructions")
st.sidebar.write("1. Upload a clear face photo.")
st.sidebar.write("2. Pick a style.")
st.sidebar.write("3. Click Generate!")

uploaded_file = st.file_uploader("Upload a photo (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Magic Generate ✨"):
        with col2:
            with st.spinner("Drawing..."):
                try:
                    cfg = STYLE_MAP[selected_style]
                    
                    # Call the AI Model
                    output = replicate.run(
                        "fofr/face-to-many:e752834f501810794c0390163013867c744c80327f29f074d284e31e5138f3f8",
                        input={
                            "image": uploaded_file,
                            "prompt": cfg["prompt"],
                            "instant_id_strength": cfg["id_strength"],
                            "denoising_strength": cfg["denoising"],
                            "negative_prompt": "realistic, photo, photograph, ugly, blurry, low quality"
                        }
                    )

                    # Get Result
                    res_url = output[0]
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Your Caricature", use_container_width=True)

                    # Download link
                    st.download_button(
                        label="📥 Download Caricature",
                        data=res_bytes,
                        file_name=f"caricature_{selected_style.lower().replace(' ', '_')}.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

st.markdown("---")
st.caption("Powered by Replicate AI & Streamlit Cloud")
