"""
RiceCare AI — Analyze My Plant
AI-powered rice leaf disease prediction.
"""

import streamlit as st
from PIL import Image

from utils import styling, data_loader
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
        st.warning(
            "⚙️ Trained model not found."
        )
    else:
        st.success(
            "🤖 AI Model Ready"
        )


# ============================================================
# PAGE HEADER
# ============================================================

styling.hero(
    "🌾 Analyze My Plant",
    "AI-Powered Rice Leaf Disease Detection",
    "Upload a rice leaf image to analyze its visual disease class."
)


# ============================================================
# IMAGE INPUT
# ============================================================

col1, col2 = st.columns(2)

with col1:

    uploaded_file = st.file_uploader(
        "Choose a rice leaf image",
        type=["jpg", "jpeg", "png"],
        key="rice_leaf_upload"
    )

with col2:

    camera_image = st.camera_input(
        "Take a photo of the rice leaf",
        key="rice_leaf_camera"
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
# PREDICTION
# ============================================================

if image is not None:

    # --------------------------------------------------------
    # SHOW IMAGE
    # --------------------------------------------------------

    st.image(
        image,
        caption="Selected rice leaf image",
        use_container_width=True
    )

    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    if st.button(
        "🤖 Analyze Image",
        use_container_width=True,
        type="primary"
    ):

        with st.spinner("Analyzing rice leaf..."):

            try:

                scores = model_utils.predict(image)

            except Exception as e:

                st.error(
                    "❌ AI model prediction failed."
                )

                st.code(
                    str(e),
                    language="text"
                )

                st.stop()

            # ------------------------------------------------
            # CHECK RESULTS
            # ------------------------------------------------

            if not scores:

                st.error(
                    "No prediction scores were returned."
                )

                st.stop()

            top_id, confidence = (
                model_utils.get_top_prediction(scores)
            )

            if top_id is None:

                st.error(
                    "Unable to determine the predicted class."
                )

                st.stop()

            # ------------------------------------------------
            # SAVE RESULTS
            # ------------------------------------------------

            st.session_state["prediction_scores"] = scores
            st.session_state["top_prediction"] = top_id
            st.session_state["prediction_confidence"] = confidence
            st.session_state["uploaded_image"] = image

            # ------------------------------------------------
            # DISEASE NAME
            # ------------------------------------------------

            disease_names = {
                "bacterial_leaf_blight":
                    "Bacterial Leaf Blight",

                "brown_spot":
                    "Brown Spot",

                "healthy":
                    "Healthy",

                "leaf_blast":
                    "Rice Blast"
            }

            disease_name = disease_names.get(
                top_id,
                top_id.replace("_", " ").title()
            )

            # ------------------------------------------------
            # SIMPLE RESULT
            # ------------------------------------------------

            st.success(
                f"Prediction completed: {disease_name}"
            )

            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            st.metric(
                "Prediction Confidence",
                f"{confidence * 100:.1f}%"
            )

            # ------------------------------------------------
            # ALL CLASS SCORES
            # ------------------------------------------------

            st.markdown("### Prediction Scores")

            display_names = {
                "bacterial_leaf_blight":
                    "Bacterial Leaf Blight",

                "brown_spot":
                    "Brown Spot",

                "healthy":
                    "Healthy",

                "leaf_blast":
                    "Rice Blast"
            }

            for class_id, score in scores.items():

                label = display_names.get(
                    class_id,
                    class_id.replace("_", " ").title()
                )

                st.write(
                    f"**{label}** — "
                    f"{score * 100:.1f}%"
                )

                st.progress(
                    float(score)
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("<br/>", unsafe_allow_html=True)

styling.disclaimer()
styling.footer()
