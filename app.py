```python
"""
RiceCare AI — Analyze My Plant
AI-powered rice leaf disease detection.
"""

import streamlit as st
from PIL import Image

from utils import styling
from utils import model_utils


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Analyze My Plant — RiceCare AI",
    page_icon="🌾",
    layout="wide",
)

styling.inject_global_css()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🌾 RiceCare AI")
    st.caption(
        "AI-Powered Rice Disease & Molecular Information Analyzer"
    )

    if model_utils.is_demo_mode():
        st.warning("⚙️ Model not found")
    else:
        st.success("🤖 AI Model Ready")


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div style="text-align: center; padding: 20px 0 25px 0;">
        <h1>🌾 Analyze My Plant</h1>
        <p style="font-size: 18px;">
            Upload or capture a rice leaf image for AI analysis
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# IMAGE INPUT
# ============================================================

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📁 Upload Rice Leaf",
        type=["jpg", "jpeg", "png"],
        key="rice_leaf_upload",
    )

with col2:
    camera_image = st.camera_input(
        "📷 Take Photo",
        key="rice_leaf_camera",
    )


# ============================================================
# SELECT IMAGE
# ============================================================

image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

elif camera_image is not None:
    image = Image.open(camera_image).convert("RGB")


# ============================================================
# SHOW IMAGE + ANALYZE BUTTON
# ============================================================

if image is not None:

    st.markdown("### 📷 Selected Rice Leaf")

    st.image(
        image,
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_button = st.button(
        "🤖 Analyze My Plant",
        use_container_width=True,
        type="primary",
    )

    if analyze_button:

        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        with st.spinner("🔬 Analyzing rice leaf..."):

            try:
                scores = model_utils.predict(image)

            except Exception as e:

                st.error(
                    "❌ AI model prediction failed."
                )

                st.code(
                    str(e),
                    language="text",
                )

                st.stop()

        # ----------------------------------------------------
        # CHECK RESULT
        # ----------------------------------------------------

        if not scores:
            st.error(
                "❌ No prediction was returned."
            )
            st.stop()

        top_id, confidence = (
            model_utils.get_top_prediction(scores)
        )

        if top_id is None:
            st.error(
                "❌ Unable to determine the prediction."
            )
            st.stop()

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        st.session_state["prediction_scores"] = scores
        st.session_state["top_prediction"] = top_id
        st.session_state["prediction_confidence"] = confidence
        st.session_state["uploaded_image"] = image

        # ----------------------------------------------------
        # DISEASE NAMES
        # ----------------------------------------------------

        disease_names = {
            "bacterial_leaf_blight":
                "Bacterial Leaf Blight",

            "brown_spot":
                "Brown Spot",

            "healthy":
                "Healthy",

            "leaf_blast":
                "Rice Blast",
        }

        disease_name = disease_names.get(
            top_id,
            top_id.replace("_", " ").title(),
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        st.markdown("---")
        st.markdown("### 🤖 AI Analysis Result")

        st.success(
            f"Predicted condition: **{disease_name}**"
        )

        st.metric(
            "Model Confidence",
            f"{confidence * 100:.1f}%",
        )

        # ----------------------------------------------------
        # ALL PREDICTION SCORES
        # ----------------------------------------------------

        st.markdown("### 📊 Prediction Scores")

        display_names = {
            "bacterial_leaf_blight":
                "Bacterial Leaf Blight",

            "brown_spot":
                "Brown Spot",

            "healthy":
                "Healthy",

            "leaf_blast":
                "Rice Blast",
        }

        for class_id, score in scores.items():

            label = display_names.get(
                class_id,
                class_id.replace("_", " ").title(),
            )

            st.write(
                f"**{label}** — {score * 100:.1f}%"
            )

            st.progress(
                float(score)
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

styling.disclaimer()
styling.footer()
```
