"""
RiceCare AI — Home
Entry point for the multipage Streamlit application.
Run with:  streamlit run app.py
"""

import styling
from model_performance import is_demo_mode

st.set_page_config(
    page_title="RiceCare AI — Home",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

styling.inject_global_css()

with st.sidebar:
    st.markdown("### 🌾 RiceCare AI")
    st.caption("AI-Powered Rice Disease & Molecular Information Analyzer")
    if is_demo_mode():
        st.warning("⚙️ Demo Mode\n\nNo trained model found in `/model`. Predictions use a placeholder "
                    "heuristic until a real `.h5`/`.keras` model is added.")
    else:
        st.success("✅ Trained model loaded")

# ---------------- HERO ----------------
styling.hero(
    "🌾 RiceCare AI",
    "AI-Powered Rice Disease Detection & Molecular Insights",
    "Upload a rice-leaf image to explore possible disease conditions, symptoms, "
    "general management information and relevant rice defense/stress protein research.",
)

styling.flow_diagram(["🌾 Rice field", "🍃 Leaf structure", "🧬 Molecular view", "🤖 AI"])

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    a, b = st.columns(2)
    with a:
        if st.button("📷 Analyze My Plant", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Analyze_My_Plant.py")
    with b:
        if st.button("🔬 Explore Rice Research", use_container_width=True):
            st.switch_page("pages/2_Explore_Rice_Diseases.py")

st.markdown("<br/>", unsafe_allow_html=True)

# ---------------- HIGHLIGHTS ----------------
st.markdown("### Project Highlights")
h1, h2, h3, h4 = st.columns(4)

with h1:
    st.markdown(
        """<div class="rc-card">
        <h4>🌱 4 Rice Classes</h4>
        <p>Healthy · Rice Blast · Brown Spot · Bacterial Leaf Blight</p>
        </div>""",
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        """<div class="rc-card">
        <h4>🤖 AI Detection</h4>
        <p>Image-based classification of rice leaf conditions</p>
        </div>""",
        unsafe_allow_html=True,
    )
with h3:
    st.markdown(
        """<div class="rc-card">
        <h4>🧬 Protein Research</h4>
        <p>Rice defense &amp; stress-response proteins</p>
        </div>""",
        unsafe_allow_html=True,
    )
with h4:
    st.markdown(
        """<div class="rc-card">
        <h4>🔬 Bioinformatics</h4>
        <p>BLAST · MSA · InterPro domain analysis</p>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)
styling.disclaimer()
styling.footer()
