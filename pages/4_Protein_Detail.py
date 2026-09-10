import streamlit as st
from utils import styling, data_loader
from urllib.request import urlopen

st.set_page_config(
    page_title="Protein Detail — RiceCare AI",
    page_icon="🧬",
    layout="wide"
)

styling.inject_global_css()

protein_id = st.session_state.get("rc_selected_protein_id")

if not protein_id:
    st.warning(
        "No protein selected. Go to the Molecular Information page and click "
        "**View Analysis** on a protein card."
    )
    st.stop()

protein = data_loader.get_protein_by_id(protein_id)

if not protein:
    st.error(
        f"Protein `{protein_id}` not found in `data/protein_information.csv`."
    )
    st.stop()

st.markdown("## 🧬 Protein Information")

verified = protein.get("verification_status") == "VERIFIED_SEARCH_RESULT"
badge = (
    "✅ Verified via source lookup"
    if verified
    else "⚠️ Needs verification on UniProt"
)

st.markdown(f"### {protein.get('protein_name', '')}")
st.caption(badge)

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"**Gene name:** {protein.get('gene_name', '—')}")
    st.markdown(
        f"**UniProt accession:** `{protein.get('uniprot_id', '—')}`"
    )
    st.markdown(f"**Organism:** {protein.get('organism', '—')}")

with c2:
    st.markdown(
        f"**Sequence length:** {protein.get('sequence_length', '—')}"
    )
    st.markdown(
        f"**Associated condition:** {protein.get('disease_id', '—')}"
    )

st.markdown("**Function**")
st.write(protein.get("function", "—"))


# ---------------- FASTA SEQUENCE ----------------

with st.expander("▶ View FASTA Sequence"):

    accession = str(
        protein.get("uniprot_id", "")
    ).strip()

    if accession == "VERIFY_ON_UNIPROT" or not accession:

        st.warning(
            "FASTA sequence is not available because a verified "
            "UniProt accession is required."
        )

    else:

        fasta_url = (
            f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
        )

        try:

            with urlopen(fasta_url, timeout=10) as response:
                fasta_sequence = response.read().decode("utf-8")

            st.success(
                "✅ FASTA sequence retrieved successfully from UniProt."
            )

            st.code(
                fasta_sequence,
                language="text"
            )

        except Exception:

            st.error(
                f"Unable to retrieve the FASTA sequence for "
                f"UniProt accession `{accession}`."
            )

            st.info(
                f"Please verify the UniProt accession `{accession}`."
            )


st.markdown("---")


# ---------------- BLAST ----------------

st.markdown("### 🔎 BLAST Analysis")

st.write(
    "BLAST was used to identify proteins with similar sequences."
)

blast_rows = data_loader.get_analysis_for_protein(
    protein_id,
    "BLAST"
)

if (
    blast_rows
    and blast_rows[0].get("status")
    != "AWAITING_USER_BLAST_RESULTS"
):

    with st.expander("▶ View Detailed BLAST Results"):
        st.dataframe(
            blast_rows,
            use_container_width=True
        )

else:

    st.info(
        "No BLAST results have been added yet for this protein. "
        "Populate `data/protein_analysis.csv` "
        "(analysis_type = BLAST) with your actual BLAST output "
        "to activate this section."
    )


st.markdown("---")


# ---------------- MSA ----------------

st.markdown("### 🧬 Multiple Sequence Alignment")

st.write(
    "Multiple Sequence Alignment compares related protein sequences "
    "and helps identify conserved regions."
)

msa_rows = data_loader.get_analysis_for_protein(
    protein_id,
    "MSA"
)

if (
    msa_rows
    and msa_rows[0].get("status")
    != "AWAITING_USER_MSA_RESULTS"
):

    with st.expander("▶ View Full Alignment"):
        st.dataframe(
            msa_rows,
            use_container_width=True
        )

else:

    st.info(
        "No MSA results have been added yet for this protein. "
        "Populate `data/protein_analysis.csv` "
        "(analysis_type = MSA) with your actual alignment output "
        "to activate this section."
    )


st.markdown("---")


