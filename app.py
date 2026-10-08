```python
"""
RiceCare AI — Home
Entry point for the multipage Streamlit application.
Run with: streamlit run app.py
"""

import streamlit as st

from utils import styling
from utils.model_utils import is_demo_mode


st.set_page_config(
    page_title="RiceCare AI — Home",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
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

    if is_demo_mode():

        st.warning(
            "⚙️ Demo Mode\n\n"
            "No trained model found."
        )

    else:

        st.success(
            "✅ Trained model loaded"
        )


# ============================================================
# HERO SECTION
# ============================================================

styling.hero(
    "🌾 RiceCare AI",
    "AI-Powered Rice Disease Detection & Molecular Insights",
    "Upload a rice-leaf image to explore possible disease "
    "conditions, symptoms, general management information "
    "and relevant rice defense/stress protein research.",
)


# ============================================================
# FLOW DIAGRAM
# ============================================================

styling.flow_diagram(
    [
        "🌾 Rice field",
        "🍃 Leaf structure",
        "🧬 Molecular view",
        "🤖 AI",
    ]
)


# ============================================================
# MAIN BUTTONS
# ============================================================

col1, col2, col3 = st.columns([1, 1, 1])

with col2:

    a, b = st.columns(2)

    with a:

        if st.button(
            "📷 Analyze My Plant",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/Analyze_My_Plant.py"
            )

    with b:

        if st.button(
            "🔬 Explore Rice Research",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/2_Explore_Rice_Diseases.py"
            )


st.markdown(
    "<br/>",
    unsafe_allow_html=True,
)


# ============================================================
# PROJECT HIGHLIGHTS
# ============================================================

st.markdown(
    "### Project Highlights"
)

h1, h2, h3, h4 = st.columns(4)


# ------------------------------------------------------------
# 1. RICE CLASSES
# ------------------------------------------------------------

with h1:

    st.markdown(
        """
        <div class="rc-card">
            <h4>🌱 4 Rice Classes</h4>
            <p>
                Healthy · Rice Blast · Brown Spot ·
                Bacterial Leaf Blight
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 2. AI DETECTION
# ------------------------------------------------------------

with h2:

    st.markdown(
        """
        <div class="rc-card">
            <h4>🤖 AI Detection</h4>
            <p>
                Image-based classification of rice
                leaf conditions
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 3. PROTEIN RESEARCH
# ------------------------------------------------------------

with h3:

    st.markdown(
        """
        <div class="rc-card">
            <h4>🧬 Protein Research</h4>
            <p>
                Rice defense &amp; stress-response
                proteins
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 4. BIOINFORMATICS
# ------------------------------------------------------------

with h4:

    st.markdown(
        """
        <div class="rc-card">
            <h4>🔬 Bioinformatics</h4>
            <p>
                BLAST · MSA · InterPro domain analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    "<br/>",
    unsafe_allow_html=True,
)

styling.disclaimer()

styling.footer()
```
