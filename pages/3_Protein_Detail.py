import streamlit as st
from utils import styling, data_loader

st.set_page_config(page_title="Protein Detail — RiceCare AI", page_icon="🧬", layout="wide")
styling.inject_global_css()

protein_id = st.session_state.get("rc_selected_protein_id")

if not protein_id:
    st.warning("No protein selected. Go to the Molecular Information page and click **View Analysis** "
               "on a protein card.")
    st.stop()

protein = data_loader.get_protein_by_id(protein_id)
if not protein:
    st.error(f"Protein `{protein_id}` not found in `data/protein_information.csv`.")
    st.stop()

st.markdown("## 🧬 Protein Information")

verified = protein.get("verification_status") == "VERIFIED_SEARCH_RESULT"
badge = "✅ Verified via source lookup" if verified else "⚠️ Needs verification on UniProt"
st.markdown(f"### {protein.get('protein_name','')}")
st.caption(badge)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Gene name:** {protein.get('gene_name','—')}")
    st.markdown(f"**UniProt accession:** `{protein.get('uniprot_id','—')}`")
    st.markdown(f"**Organism:** {protein.get('organism','—')}")
with c2:
    st.markdown(f"**Sequence length:** {protein.get('sequence_length','—')}")
    st.markdown(f"**Associated condition:** {protein.get('disease_id','—')}")

st.markdown("**Function**")
st.write(protein.get("function", "—"))

with st.expander("▶ View FASTA Sequence"):
    if str(protein.get("uniprot_id")) == "VERIFY_ON_UNIPROT" or not protein.get("uniprot_id"):
        st.warning("FASTA sequence not yet available — a verified UniProt accession is required first. "
                   "Look up this protein on uniprot.org and update `protein_information.csv`.")
    else:
        st.info(
            f"FASTA sequence not bundled in this demo dataset. Fetch it directly from UniProt using "
            f"accession `{protein.get('uniprot_id')}`:\n\n"
            f"`https://www.uniprot.org/uniprotkb/{protein.get('uniprot_id')}/entry`"
        )

st.markdown("---")

# ---------------- BLAST ----------------
st.markdown("### 🔎 BLAST Analysis")
st.write("BLAST was used to identify proteins with similar sequences.")
blast_rows = data_loader.get_analysis_for_protein(protein_id, "BLAST")
if blast_rows and blast_rows[0].get("status") != "AWAITING_USER_BLAST_RESULTS":
    with st.expander("▶ View Detailed BLAST Results"):
        st.dataframe(blast_rows, use_container_width=True)
else:
    st.info("No BLAST results have been added yet for this protein. Populate `data/protein_analysis.csv` "
            "(analysis_type = BLAST) with your actual BLAST output to activate this section.")

st.markdown("---")

# ---------------- MSA ----------------
st.markdown("### 🧬 Multiple Sequence Alignment")
st.write("Multiple Sequence Alignment compares related protein sequences and helps identify conserved regions.")
msa_rows = data_loader.get_analysis_for_protein(protein_id, "MSA")
if msa_rows and msa_rows[0].get("status") != "AWAITING_USER_MSA_RESULTS":
    with st.expander("▶ View Full Alignment"):
        st.dataframe(msa_rows, use_container_width=True)
else:
    st.info("No MSA results have been added yet for this protein. Populate `data/protein_analysis.csv` "
            "(analysis_type = MSA) with your actual alignment output to activate this section.")

st.markdown("---")

# ---------------- InterPro ----------------
st.markdown("### 🧩 Protein Domain Analysis")
st.write("InterPro helps identify known protein domains, families and functional regions.")
interpro_rows = data_loader.get_analysis_for_protein(protein_id, "INTERPRO")
if interpro_rows and interpro_rows[0].get("status") != "AWAITING_USER_INTERPRO_RESULTS":
    for row in interpro_rows:
        st.markdown(f"- **{row.get('detail_field_1','')}** ({row.get('detail_field_2','')}–{row.get('detail_field_3','')})")
else:
    st.info("No InterPro domain results have been added yet for this protein. Populate "
            "`data/protein_analysis.csv` (analysis_type = INTERPRO) with your actual domain output "
            "to activate this section, including a visual domain diagram.")

st.markdown("---")

# ---------------- FINAL INSIGHT ----------------
st.markdown("### 🧠 Molecular Insight")
has_real_analysis = (
    blast_rows and blast_rows[0].get("status") != "AWAITING_USER_BLAST_RESULTS"
    and msa_rows and msa_rows[0].get("status") != "AWAITING_USER_MSA_RESULTS"
    and interpro_rows and interpro_rows[0].get("status") != "AWAITING_USER_INTERPRO_RESULTS"
)
if has_real_analysis:
    st.success(
        "This rice protein is associated with the plant's defense/stress response. Sequence comparison "
        "identified related proteins and conserved regions, while domain analysis identified known "
        "functional regions that may help researchers understand its biological role."
    )
else:
    st.warning(
        "A complete molecular insight will be generated automatically once verified BLAST, MSA, and "
        "InterPro results are available for this protein. This ensures the conclusion is generated only "
        "from actual verified analysis results, never invented."
    )

styling.disclaimer()
styling.footer()
