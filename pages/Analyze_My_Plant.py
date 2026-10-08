import time
import streamlit as st
from PIL import Image

from utils import styling, data_loader, model_utils


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Analyze My Plant — RiceCare AI",
    page_icon="📷",
    layout="wide"
)

styling.inject_global_css()


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("## 📷 Analyze Your Rice Plant")

st.caption(
    "Upload a clear photo of a rice leaf to get AI-based "
    "prediction scores across all four classes."
)


# ============================================================
# MODEL STATUS
# ============================================================

if model_utils.is_demo_mode():
    st.error(
        "⚠️ **Trained model not found.** "
        "Please make sure "
        "`rice_leaf_disease_efficientnetb0.keras` "
        "is inside the `models/` folder."
    )
else:
    st.success(
        "🤖 **AI Model Ready** — "
        "Rice leaf disease detection model loaded."
    )


# ============================================================
# IMAGE UPLOAD / CAMERA
# ============================================================

upload_col, preview_col = st.columns([1, 1])


with upload_col:

    uploaded_file = st.file_uploader(
        "Drag & drop or browse a rice leaf image",
        type=["jpg", "jpeg", "png"],
        help=(
            "Best results with a clear, well-lit, "
            "close-up photo of a single leaf."
        ),
    )

    camera_image = st.camera_input(
        "Or take a photo"
    )


# Uploaded image takes priority
image_source = uploaded_file or camera_image


# ============================================================
# IMAGE PREVIEW
# ============================================================

with preview_col:

    if image_source is not None:

        image = Image.open(image_source)

        st.image(
            image,
            caption="Image Preview",
            use_container_width=True
        )

        if st.button("✖️ Remove Image"):
            st.rerun()

    else:

        st.markdown(
            """
            <div class="rc-card"
                 style="text-align:center; padding:3rem 1rem;">

                <h4>📷 Upload Image</h4>

                <p>
                    Drag &amp; drop a rice leaf photo,
                    or use your camera above.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.markdown(
    "<br/>",
    unsafe_allow_html=True
)

analyze_clicked = st.button(
    "🔍 ANALYZE",
    type="primary",
    use_container_width=True,
    disabled=image_source is None
)


# ============================================================
# RUN AI PREDICTION
# ============================================================

if analyze_clicked and image_source is not None:

    image = Image.open(image_source)

    progress_box = st.empty()

    stages = [
        "🔎 Analyzing image...",
        "🧩 Checking visual patterns...",
        "🤖 Running AI model...",
        "📊 Generating prediction...",
    ]

    for stage in stages:

        progress_box.info(stage)

        time.sleep(0.35)

    progress_box.empty()


    # --------------------------------------------------------
    # REAL MODEL PREDICTION
    # --------------------------------------------------------

    scores = model_utils.predict(image)


    # --------------------------------------------------------
    # Convert model IDs to existing RiceCare IDs
    # --------------------------------------------------------
    #
    # Trained model:
    #
    # bacterial_leaf_blight
    # brown_spot
    # healthy
    # leaf_blast
    #
    # Existing RiceCare application:
    #
    # BACTERIAL_LEAF_BLIGHT
    # BROWN_SPOT
    # HEALTHY
    # RICE_BLAST
    #

    id_mapping = {
        "bacterial_leaf_blight": "BACTERIAL_LEAF_BLIGHT",
        "brown_spot": "BROWN_SPOT",
        "healthy": "HEALTHY",
        "leaf_blast": "RICE_BLAST",
    }


    converted_scores = {}

    for model_id, probability in scores.items():

        app_id = id_mapping.get(
            model_id,
            model_id
        )

        converted_scores[app_id] = float(
            probability
        )


    # --------------------------------------------------------
    # Get top prediction
    # --------------------------------------------------------

    top_id, top_score = model_utils.get_top_prediction(
        converted_scores
    )


    # --------------------------------------------------------
    # Save prediction in session
    # --------------------------------------------------------

    st.session_state["rc_last_scores"] = converted_scores

    st.session_state["rc_last_top"] = top_id

    st.session_state["rc_last_image_bytes"] = (
        image_source.getvalue()
    )


# ============================================================
# RESULTS
# ============================================================

if "rc_last_scores" in st.session_state:

    scores = st.session_state["rc_last_scores"]

    top_id = st.session_state["rc_last_top"]


    # --------------------------------------------------------
    # Disease information
    # --------------------------------------------------------

    disease_info = data_loader.get_disease_info(
        top_id
    )


    # --------------------------------------------------------
    # RESULTS HEADER
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 🤖 AI Prediction"
    )


    st.markdown(
        f"""
        <div class="rc-result-headline">

            <div class="rc-label">
                Most likely condition
            </div>

            <div class="rc-disease-name">
                {disease_info['emoji']}
                {disease_info['disease_name']}
            </div>

            <div>
                Model prediction score:
                <b>{scores[top_id] * 100:.1f}%</b>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.caption(
        "Model prediction scores "
        "(not a guaranteed diagnosis)"
    )


    # --------------------------------------------------------
    # ALL PREDICTION SCORES
    # --------------------------------------------------------

    for disease_id in sorted(
        scores,
        key=scores.get,
        reverse=True
    ):

        info = data_loader.get_disease_info(
            disease_id
        )

        pct = scores[disease_id] * 100

        st.markdown(
            f"**{info['emoji']} "
            f"{info['disease_name']}** — "
            f"{pct:.1f}%"
        )

        st.progress(
            min(
                max(
                    scores[disease_id],
                    0.0
                ),
                1.0
            )
        )


    # ========================================================
    # COMPARE WITH SAMPLE IMAGES
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### 👀 Compare Your Plant"
    )

    st.caption(
        "Compare the visible symptoms with these "
        "representative examples. Visual comparison "
        "alone does not confirm a diagnosis."
    )


    cmp1, cmp2 = st.columns([1, 2])


    # --------------------------------------------------------
    # User image
    # --------------------------------------------------------

    with cmp1:

        st.markdown(
            "**Your Image**"
        )

        st.image(
            st.session_state["rc_last_image_bytes"],
            use_container_width=True
        )


    # --------------------------------------------------------
    # Reference images
    # --------------------------------------------------------

    with cmp2:

        st.markdown(
            f"**Typical {disease_info['disease_name']}**"
        )

        sample_paths = data_loader.get_sample_images(
            top_id
        )

        if sample_paths:

            cols = st.columns(
                len(sample_paths)
            )

            for c, path in zip(
                cols,
                sample_paths
            ):

                c.image(
                    path,
                    use_container_width=True
                )

        else:

            st.warning(
                f"No sample images found yet for "
                f"**{disease_info['disease_name']}**. "
                f"Add reference photos to "
                f"`data/sample_images/"
                f"{data_loader.DISEASE_ID_TO_FOLDER.get(top_id, '')}/`."
            )


    # ========================================================
    # DISEASE INFORMATION
    # ========================================================

    st.markdown("---")

    st.markdown(
        f"### {disease_info['emoji']} "
        f"{disease_info['disease_name']}"
    )


    # --------------------------------------------------------
    # Causal organism
    # --------------------------------------------------------

    if top_id != "HEALTHY":

        st.markdown(
            f"**🧫 Caused by:** "
            f"{disease_info['causal_organism']} "
            f"({disease_info['causative_agent']})"
        )


    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    st.write(
        disease_info["description"]
    )


    # --------------------------------------------------------
    # Symptoms / Management
    # --------------------------------------------------------

    dcol1, dcol2 = st.columns(2)


    with dcol1:

        st.markdown(
            "**🔎 Common Symptoms**"
        )

        if disease_info["symptoms"]:

            for symptom in disease_info["symptoms"]:

                st.markdown(
                    f"- {symptom}"
                )

        else:

            st.caption(
                "No symptom data available."
            )


    with dcol2:

        header = (
            "🌾 General Management"
            if top_id != "HEALTHY"
            else "🌾 Recommended Practices"
        )

        st.markdown(
            f"**{header}**"
        )

        if disease_info["management"]:

            for management in disease_info["management"]:

                st.markdown(
                    f"- {management}"
                )

        else:

            st.caption(
                "No management data available."
            )


    # ========================================================
    # MOLECULAR INFORMATION
    # ========================================================

    st.markdown(
        "<br/>",
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="rc-card">

            <h4>
                🧬 Explore Molecular Information
            </h4>

            <p>
                The AI predicts the visual disease class.
                The molecular information below is separately
                researched and describes rice defense/stress-
                related proteins associated with the biological
                response to the selected condition — it is not
                detected from the photograph itself.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Molecular information button
    # --------------------------------------------------------

    if st.button(
        "🧬 Explore Molecular Information for This Result",
        type="primary"
    ):

        st.session_state[
            "rc_molecular_disease_id"
        ] = top_id

        st.switch_page(
            "pages/3_Molecular_Information.py"
        )


    # ========================================================
    # DISCLAIMER
    # ========================================================

    styling.disclaimer()


# ============================================================
# FOOTER
# ============================================================

styling.footer()
