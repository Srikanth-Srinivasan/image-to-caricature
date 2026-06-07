import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Multi-Model Caricature AI", page_icon="🎨", layout="centered")

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
    st.error("Missing Replicate API Token in Secrets!")
    st.stop()

# --- PROVIDER & MODEL CONFIGURATION ---
# We use slugs (names) instead of hashes to ensure we always use the latest stable version
PROVIDERS = {
    "Stability AI (SDXL)": {
        "model": "stability-ai/sdxl",
        "strength_param": "prompt_strength",
        "extra_params": {"guidance_scale": 7.5, "output_format": "jpg"}
    },
    "Black Forest Labs (FLUX Dev)": {
        "model": "black-forest-labs/flux-dev",
        "strength_param": "prompt_strength",
        "extra_params": {"guidance": 3.5, "output_format": "jpg"}
    },
    "Face-to-Many (Specialized)": {
        "model": "fofr/face-to-many",
        "strength_param": "denoising_strength",
        "extra_params": {"instant_id_strength": 0.8, "style": "Cartoon"}
    }
}

STYLES = {
    "Funny Caricature": "A professional digital caricature, exaggerated funny facial features, big head, small body, colorful hand-drawn style",
    "Disney Pixar": "3D character render, Disney Pixar style, big expressive eyes, smooth stylized skin, cinematic 3D lighting",
    "Comic Book": "Modern comic book illustration, bold ink lines, vibrant colors, cel-shaded superhero aesthetic",
    "Artistic Sketch": "Hand-drawn charcoal sketch, artistic caricature lines, high contrast, black and white"
}

# --- SIDEBAR UI ---
st.sidebar.title("Configuration")
selected_provider = st.sidebar.selectbox("Select AI Provider", list(PROVIDERS.keys()))
selected_style = st.sidebar.selectbox("Select Art Style", list(STYLES.keys()))
exaggeration = st.sidebar.slider("Exaggeration Level", 0.4, 0.9, 0.65, help="Higher = More AI change, Lower = More like original photo")

# --- MAIN UI ---
st.title("🎨 Multi-Model Caricature AI")
st.write(f"Currently using: **{selected_provider}**")

uploaded_file = st.file_uploader("Upload a face photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Generate My Caricature ✨"):
        with col2:
            with st.spinner(f"Requesting from {selected_provider}..."):
                try:
                    # 1. Get configuration for chosen provider
                    config = PROVIDERS[selected_provider]
                    prompt = STYLES[selected_style]
                    
                    # 2. Build input dictionary dynamically
                    input_data = {
                        "image": uploaded_file,
                        "prompt": prompt,
                        config["strength_param"]: exaggeration,
                    }
                    # Add any provider-specific extra parameters
                    input_data.update(config["extra_params"])

                    # 3. Run Replicate
                    output = replicate.run(config["model"], input=input_data)

                    # 4. Handle Result
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption=f"Result ({selected_provider})", use_container_width=True)

                    st.download_button(
                        label="📥 Download JPG",
                        data=res_bytes,
                        file_name=f"caricature_{selected_provider.split()[0].lower()}.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Tip: If you get a permission error, visit Replicate.com, find this model, and run it once on the website to accept their terms.")

st.markdown("---")
st.caption("This app automatically connects to the latest stable versions of Stability AI, FLUX, and Face-to-Many.")
