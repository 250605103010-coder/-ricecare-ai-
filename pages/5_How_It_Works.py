import streamlit as st
from utils import styling

st.set_page_config(page_title="How It Works — RiceCare AI", page_icon="❓", layout="wide")
styling.inject_global_css()

st.markdown("## ❓ How It Works")
st.caption("From leaf photo to molecular insight — the full RiceCare AI pipeline.")

steps = [
    ("📷", "Upload Rice Leaf", "You upload or capture a photo of a rice leaf."),
    ("⚙️", "Image Preprocessing", "The image is resized and normalized for the model."),
    ("🤖", "AI Classification", "The trained CNN (or demo-mode heuristic) scores the image."),
    ("📊", "Prediction Scores", "All four classes receive an independent probability score."),
    ("📚", "Disease Information", "The highest-scoring class pulls its verified info record."),
    ("🌾", "General Management", "Practical, non-prescriptive management guidance is shown."),
    ("🧬", "Molecular Information", "Related, separately-researched defense/stress proteins are shown."),
    ("🔎", "BLAST", "Sequence similarity search results, where available."),
    ("🧬", "MSA", "Multiple sequence alignment highlighting conserved regions."),
    ("🧩", "InterPro", "Known protein domains and functional regions."),
    ("🧠", "Final Molecular Insight", "A short, evidence-grounded summary — never invented."),
]

for i, (emoji, title, desc) in enumerate(steps):
    st.markdown(
        f"""<div class="rc-card" style="margin-bottom:0.7rem;
            animation: rc-fade-in 500ms ease-out {i*80}ms both;">
        <h4>{emoji} {title}</h4>
        <p>{desc}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if i < len(steps) - 1:
        st.markdown('<div style="text-align:center; color:#C69B3D; font-size:1.1rem;">↓</div>',
                    unsafe_allow_html=True)

styling.disclaimer()
styling.footer()
