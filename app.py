import streamlit as st
import replicate
import requests
from PIL import Image
import io
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Caricature Studio", page_icon="🎨")

# Add your Replicate Token here or set it in your Environment Variables
REPLICATE_API_TOKEN = st.sidebar.text_input("Enter Replicate API Token", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# --- STYLE DICTIONARY (Prompt Engineering) ---
STYLES = {
    "Classic Funny": {
        "prompt": "Extreme caricature, exaggerated features, big head, small body, funny digital art, high quality",
        "denoising": 0.7,
        "id_strength": 0.8
    },
    "Disney/Pixar": {
        "prompt": "3D render, Pixar style character, big expressive eyes, smooth skin, cinematic lighting, masterpiece",
        "denoising": 0.5,
        "id_strength": 0.7
    },
    "Grand Theft Auto": {
        "prompt": "GTA V loading screen art style, thick brush strokes, high contrast, cel-shaded, vibrant colors",
        "denoising": 0.6,
        "id_strength": 0.75
    },
    "Pencil Sketch": {
        "prompt": "Hand-drawn charcoal caricature sketch, messy lines, artistic, high contrast, black and white",
        "denoising": 0.8,
        "id_strength": 0.85
    }
}

# --- UI DESIGN ---
st.title("🎨 AI Caricature Studio")
st.markdown("Upload a photo and transform it into a hilarious or artistic caricature.")

# Sidebar for controls
st.sidebar.header("Settings")
selected_style = st.sidebar.selectbox("Choose a Style", list(STYLES.keys()))
uploaded_file = st.file_uploader("Upload a clear headshot (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Show Preview
    img = Image.open(uploaded_file)
    st.image(img, caption="Your Upload", width=300)

    if st.button("Generate Caricature"):
        if not REPLICATE_API_TOKEN:
            st.error("Please enter your Replicate API Token in the sidebar!")
        else:
            with st.spinner("🧠 AI is drawing your caricature..."):
                try:
                    # 1. Setup Input
                    style_cfg = STYLES[selected_style]
                    
                    # 2. Call the Face-to-Many Model
                    # This model is specifically built to keep the face recognizable
                    output = replicate.run(
                        "fofr/face-to-many:e752834f501810794c0390163013867c744c80327f29f074d284e31e5138f3f8",
                        input={
                            "image": uploaded_file,
                            "prompt": style_cfg["prompt"],
                            "instant_id_strength": style_cfg["id_strength"],
                            "denoising_strength": style_cfg["denoising"],
                            "negative_prompt": "realistic, photo, ugly, blurry, deformed eyes"
                        }
                    )

                    # 3. Process Result
                    result_url = output[0]
                    res_img_data = requests.get(result_url).content
                    
                    # 4. Display Result
                    st.success("Done!")
                    st.image(res_img_data, caption=f"Style: {selected_style}")

                    # 5. Download Button
                    st.download_button(
                        label="Download Caricature",
                        data=res_img_data,
                        file_name=f"caricature_{selected_style.lower()}.png",
                        mime="image/png"
                    )

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by Replicate AI and Streamlit.")