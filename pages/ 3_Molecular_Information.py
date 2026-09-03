import streamlit as st
from utils import styling, data_loader

st.set_page_config(page_title="Molecular Information — RiceCare AI", page_icon="🧬", layout="wide")
styling.inject_global_css()

st.markdown("## 🧬 Molecular Information")

st.markdown(
    """<div class="rc-card">
    <p><b>Important:</b> The AI predicts the visual disease class from the uploaded photo.
    The molecular information on this page is <b>separately researched</b> and describes rice
    defense/stress-related proteins associated with the biological response to the selected
    condition. It is <b>not</b> directly detected from the photograph.</p>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown("<br/>", unsafe_allow_html=True)

default_id = st.session_state.get("rc_molecular_disease_id", "BACTERIAL_LEAF_BLIGHT")
disease_names = {d: data_loader.get_disease_info(d)["disease_name"] for d in data_loader.DISEASE_CLASSES}
selected_id = st.selectbox(
    "Select a condition to explore its molecular information",
    options=list(disease_names.keys()),
    format_func=lambda x: disease_names[x],
    index=list(disease_names.keys()).index(default_id) if default_id in disease_names else 0,
)
st.session_state["rc_molecular_disease_id"] = selected_id

disease_info = data_loader.get_disease_info(selected_id)
st.markdown(f"### {disease_info['emoji']} {disease_info['disease_name']}")
st.write(
    "When rice is exposed to pathogen attack or environmental stress, it activates a complex "
    "defense and stress-response system involving multiple proteins and signaling pathways."
)

proteins = data_loader.get_proteins_for_disease(selected_id)

st.markdown("### 🌾 Relevant Rice Defense/Stress Proteins")

if not proteins:
    st.warning(
        f"No verified protein records exist yet for **{disease_info['disease_name']}** in "
        f"`data/protein_information.csv`. Add rows with `disease_id = {selected_id}` to populate this section."
    )
else:
    cols = st.columns(min(3, len(proteins)))
    for i, protein in enumerate(proteins):
        with cols[i % len(cols)]:
            verified = protein.get("verification_status") == "VERIFIED_SEARCH_RESULT"
            badge = '<span class="rc-badge rc-badge-teal">✅ Verified</span>' if verified else \
                    '<span class="rc-badge rc-badge-gold">⚠️ Needs verification</span>'
            st.markdown(
                f"""<div class="rc-card">
                <h4>🧬 {protein.get('protein_name','')}</h4>
                {badge}
                <p style="margin-top:0.6rem;">
                <b>Gene:</b> {protein.get('gene_name','—')}<br/>
                <b>UniProt ID:</b> {protein.get('uniprot_id','—')}<br/>
                <b>Organism:</b> {protein.get('organism','—')}<br/>
                <b>Function:</b> {protein.get('function','—')}
                </p>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("View Analysis", key=f"view_{protein.get('protein_id')}"):
                st.session_state["rc_selected_protein_id"] = protein.get("protein_id")
                st.switch_page("pages/3_Protein_Detail.py")

styling.disclaimer()
styling.footer()
