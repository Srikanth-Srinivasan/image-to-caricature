import streamlit as st
import replicate
import requests
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Line Art & Caricature AI", page_icon="✏️", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1F2937; color: white; font-weight: bold; }
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
PROVIDERS = {
    "Stability AI (SDXL)": {
        "model": "stability-ai/sdxl",
        "strength_param": "prompt_strength",
        "extra_params": {"guidance_scale": 8.0, "output_format": "jpg"}
    },
    "Black Forest Labs (FLUX Dev)": {
        "model": "black-forest-labs/flux-dev",
        "strength_param": "prompt_strength",
        "extra_params": {"guidance": 3.5, "output_format": "jpg"}
    },
    "Face-to-Many (Identity focus)": {
        "model": "fofr/face-to-many",
        "strength_param": "denoising_strength",
        "extra_params": {"instant_id_strength": 0.8, "style": "Line Art"}
    }
}

# --- STYLES (NEW LINE DRAWING OPTIONS) ---
STYLES = {
    "Minimalist Line Art": "Clean black and white line drawing, minimalist ink strokes, white background, no shading, professional vector art style, simple outlines",
    "Detailed Pencil Sketch": "Hand-drawn pencil sketch on textured paper, detailed graphite shading, artistic caricature style, black and white",
    "Coloring Book Page": "Thick black outlines, coloring book style, pure white background, no colors, clean line art for kids",
    "Classic Caricature (Color)": "Professional digital caricature, exaggerated features, big head, small body, colorful hand-drawn style",
    "Disney Pixar": "3D character render, Disney Pixar style, big expressive eyes, smooth stylized skin, cinematic lighting"
}

# --- SIDEBAR UI ---
st.sidebar.title("Line Art Settings")
selected_provider = st.sidebar.selectbox("AI Provider", list(PROVIDERS.keys()))
selected_style = st.sidebar.selectbox("Art Style", list(STYLES.keys()))

# Suggestion for Line Drawing: Use a higher exaggeration for Line Art (around 0.75)
default_strength = 0.75 if "Line" in selected_style or "Book" in selected_style else 0.65
exaggeration = st.sidebar.slider("Exaggeration Level", 0.4, 0.9, default_strength, 
                               help="For Line Art, a higher level (0.75+) helps strip away the original photo's colors.")

# --- MAIN UI ---
st.title("✏️ Line Art & Caricature Studio")
st.write(f"Style: **{selected_style}** | Provider: **{selected_provider}**")

uploaded_file = st.file_uploader("Upload a face photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)

    if st.button("Generate Art ✨"):
        with col2:
            with st.spinner(f"Creating your {selected_style.lower()}..."):
                try:
                    config = PROVIDERS[selected_provider]
                    prompt = STYLES[selected_style]
                    
                    # Extra negative prompt to ensure B&W for line art
                    neg_prompt = "color, colorful, painting, photo, photorealistic, blurry, gray background" if "Line" in selected_style else "ugly, blurry, distorted"

                    input_data = {
                        "image": uploaded_file,
                        "prompt": prompt,
                        config["strength_param"]: exaggeration,
                        "negative_prompt": neg_prompt
                    }
                    input_data.update(config["extra_params"])

                    # Run Replicate
                    output = replicate.run(config["model"], input=input_data)

                    # Handle Result
                    res_url = output[0] if isinstance(output, list) else output
                    res_bytes = requests.get(res_url).content
                    
                    st.image(res_bytes, caption="Final Result", use_container_width=True)

                    st.download_button(
                        label="📥 Download Image",
                        data=res_bytes,
                        file_name=f"line_art_{selected_provider.split()[0].lower()}.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")
st.info("💡 **Pro Tip for Line Art:** If the result has too much color, move the **Exaggeration Level** up to 0.80 or 0.85.")
