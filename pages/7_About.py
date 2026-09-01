import streamlit as st
from utils import styling

st.set_page_config(page_title="About — RiceCare AI", page_icon="ℹ️", layout="wide")
styling.inject_global_css()

st.markdown("## ℹ️ About RiceCare AI")

st.markdown("### Problem")
st.write(
    "Rice diseases can significantly affect crop productivity, and farmers often lack quick, "
    "accessible access to disease identification and management information."
)

st.markdown("### Our Solution")
st.write(
    "An AI-assisted rice disease classification system combined with a molecular-information "
    "layer, designed to support — not replace — expert agricultural diagnosis."
)

st.markdown("### Technology")
tech = ["Python", "Streamlit", "TensorFlow / Keras", "Pandas", "Google Colab",
        "Google Drive", "UniProt", "BLAST", "MSA", "InterPro"]
cols = st.columns(5)
for i, t in enumerate(tech):
    cols[i % 5].markdown(f'<span class="rc-badge">{t}</span>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("### Current Scope")
st.write("Rice only — 4 classes: Healthy, Rice Blast, Brown Spot, Bacterial Leaf Blight.")

st.markdown("### Future Scope")
st.write("Architecture designed to extend to additional crops:")
st.markdown("🌾 Wheat &nbsp;&nbsp; 🌽 Maize &nbsp;&nbsp; 🍅 Tomato &nbsp;&nbsp; and other crops.")

styling.disclaimer()
styling.footer()
