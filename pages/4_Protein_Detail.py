import streamlit as st
from pathlib import Path
import html
from urllib.request import urlopen

from utils import styling, data_loader


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Protein Detail — RiceCare AI",
    page_icon="🧬",
    layout="wide",
)

styling.inject_global_css()


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🧬 Protein Detail")
st.caption(
    "Detailed molecular information, FASTA sequence, BLAST, MSA and InterPro analysis"
)


# ============================================================
# GET SELECTED PROTEIN
# ============================================================

protein_id = st.session_state.get("rc_selected_protein_id")


if not protein_id:
    st.warning(
        "No protein has been selected yet. "
        "Please select a protein from the Molecular Information page."
    )
    st.stop()


# ============================================================
# LOAD PROTEIN INFORMATION
# ============================================================

try:
    protein = data_loader.get_protein_by_id(protein_id)
except Exception as e:
    st.error("Unable to load the selected protein.")
    st.exception(e)
    st.stop()


if not protein:
    st.error(
        f"No protein information was found for protein ID `{protein_id}`."
    )
    st.stop()


# ============================================================
# BASIC PROTEIN INFORMATION
# ============================================================

st.markdown("## 🧬 Protein Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Basic Details")

    st.write(
        f"**Protein ID:** `{protein.get('protein_id', protein_id)}`"
    )

    st.write(
        f"**Protein Name:** "
        f"{protein.get('protein_name', 'Not available')}"
    )

    st.write(
        f"**Gene Name:** "
        f"{protein.get('gene_name', 'Not available')}"
    )

    st.write(
        f"**Disease / Condition:** "
        f"{protein.get('disease_id', 'Not available')}"
    )


with col2:
    st.markdown("### Biological Details")

    st.write(
        f"**UniProt ID:** "
        f"{protein.get('uniprot_id', 'Not available')}"
    )

    st.write(
        f"**Organism:** "
        f"{protein.get('organism', 'Not available')}"
    )

    st.write(
        f"**Sequence Length:** "
        f"{protein.get('sequence_length', 'Not available')}"
    )

    st.write(
        f"**Verification Status:** "
        f"{protein.get('verification_status', 'Not available')}"
    )


# ============================================================
# PROTEIN FUNCTION
# ============================================================

st.markdown("### 🔬 Protein Function")

st.info(
    protein.get(
        "function",
        "Protein function information is not available."
    )
)


# ============================================================
# FASTA SEQUENCE
# ============================================================

st.markdown("---")

st.markdown("## 🧬 FASTA Sequence")

with st.expander("▶ View FASTA Sequence"):

    accession = str(
        protein.get("uniprot_id", "")
    ).strip()

    if (
        not accession
        or accession == "VERIFY_ON_UNIPROT"
    ):

        st.warning(
            "FASTA sequence is not available because a verified "
            "UniProt accession is required."
        )

    else:

        fasta_url = (
            f"https://rest.uniprot.org/uniprotkb/"
            f"{accession}.fasta"
        )

        try:

            with urlopen(
                fasta_url,
                timeout=10
            ) as response:

                fasta_sequence = response.read().decode(
                    "utf-8"
                )

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
                "Please verify that the UniProt accession is correct."
            )


# ============================================================
# ANALYSIS HELPER
# ============================================================

def get_analysis_rows(protein_id_value, analysis_type):
    """
    Safely retrieve analysis information.
    """

    try:

        rows = data_loader.get_analysis_for_protein(
            protein_id_value,
            analysis_type
        )

        if rows is None:
            return []

        return rows

    except Exception:

        return []


# ============================================================
# BLAST ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("## 🔎 BLAST Analysis")

st.write(
    "BLAST was used to identify proteins with similar sequences."
)

blast_rows = get_analysis_rows(
    protein_id,
    "BLAST"
)


if blast_rows:

    valid_blast_rows = [
        row
        for row in blast_rows
        if str(row.get("status", "")).strip()
        not in [
            "AWAITING_USER_BLAST_RESULTS",
            "PENDING",
            ""
        ]
    ]

    if valid_blast_rows:

        with st.expander("▶ View Detailed BLAST Results"):

            st.dataframe(
                valid_blast_rows,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "No completed BLAST results have been added yet for "
            "this protein."
        )

else:

    st.info(
        "No BLAST results have been added yet for this protein. "
        "Populate `data/protein_analysis.csv` with the actual "
        "BLAST result to activate this section."
    )


# ============================================================
# MSA FILE MAPPING
# ============================================================

msa_files = {

    "PROT_XA21":
        "data/msa/xa21_msa.txt",

    "PROT_PITA":
        "data/msa/pi-ta_msa.txt",

    "PROT_PBZ1":
        "data/msa/pbz1_msa.txt",

    "PROT_OSPR1":
        "data/msa/ospr1_msa.txt",

    "PROT_OSRAB16":
        "data/msa/rab16_msa.txt",
}


# ============================================================
# MSA ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("## 🧬 Multiple Sequence Alignment (MSA)")

st.write(
    "Multiple sequence alignment was used to compare the "
    "selected protein with homologous protein sequences."
)


msa_file = msa_files.get(protein_id)


if msa_file:

    msa_path = Path(msa_file)

    if msa_path.exists():

        try:

            with open(
                msa_path,
                "r",
                encoding="utf-8"
            ) as file:

                msa_text = file.read()

            if msa_text.strip():

                # Escape HTML characters first
                msa_html = html.escape(msa_text)

                # Highlight conservation symbols
                msa_html = msa_html.replace(
                    "*",
                    '<span class="msa-star">*</span>'
                )

                msa_html = msa_html.replace(
                    ":",
                    '<span class="msa-colon">:</span>'
                )

                msa_html = msa_html.replace(
                    ".",
                    '<span class="msa-dot">.</span>'
                )

                st.markdown(
                    f"""
                    <style>

                    .msa-container {{
                        background-color: #f8f9fa;
                        border: 1px solid #cccccc;
                        border-radius: 8px;
                        padding: 18px;
                        overflow-x: auto;
                        overflow-y: auto;
                        max-height: 700px;
                        white-space: pre;
                        font-family: "Courier New", monospace;
                        font-size: 13px;
                        line-height: 1.55;
                    }}

                    .msa-star {{
                        background-color: #90EE90;
                        color: #006400;
                        font-weight: bold;
                    }}

                    .msa-colon {{
                        background-color: #ADD8E6;
                        color: #00008B;
                        font-weight: bold;
                    }}

                    .msa-dot {{
                        background-color: #FFD580;
                        color: #8B4500;
                        font-weight: bold;
                    }}

                    </style>

                    <div class="msa-container">
                    {msa_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### 🎨 Conservation Legend")

                legend_col1, legend_col2, legend_col3, legend_col4 = (
                    st.columns(4)
                )

                with legend_col1:
                    st.markdown(
                        "🟩 **`*`** — Identical residue"
                    )

                with legend_col2:
                    st.markdown(
                        "🟦 **`:`** — Strongly conserved"
                    )

                with legend_col3:
                    st.markdown(
                        "🟧 **`.`** — Weakly conserved"
                    )

                with legend_col4:
                    st.markdown(
                        "⬜ **Blank** — Low/no conservation"
                    )

            else:

                st.warning(
                    f"The MSA file `{msa_file}` is empty."
                )

        except Exception as e:

            st.error(
                "Unable to read the MSA file."
            )

            st.exception(e)

    else:

        st.warning(
            f"MSA file not found: `{msa_file}`"
        )

        st.info(
            "Create the file inside the `data/msa/` folder "
            "and add the Clustal Omega alignment."
        )

else:

    st.info(
        "No MSA file is configured for this protein."
    )


# ============================================================
# MSA DATABASE ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("## 📊 MSA Analysis Information")

msa_rows = get_analysis_rows(
    protein_id,
    "MSA"
)


if msa_rows:

    valid_msa_rows = [
        row
        for row in msa_rows
        if str(row.get("status", "")).strip()
        not in [
            "AWAITING_USER_MSA_RESULTS",
            "PENDING",
            ""
        ]
    ]

    if valid_msa_rows:

        st.dataframe(
            valid_msa_rows,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "MSA information has not been added to the analysis database yet."
        )

else:

    st.info(
        "No MSA summary information is available."
    )


# ============================================================
# INTERPRO ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("## 🧩 InterPro Analysis")

st.write(
    "InterPro analysis was used to identify protein families, "
    "domains and functional characteristics."
)

interpro_rows = get_analysis_rows(
    protein_id,
    "INTERPRO"
)


if interpro_rows:

    valid_interpro_rows = [
        row
        for row in interpro_rows
        if str(row.get("status", "")).strip()
        not in [
            "PENDING",
            ""
        ]
    ]

    if valid_interpro_rows:

        with st.expander("▶ View InterPro Results"):

            st.dataframe(
                valid_interpro_rows,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "No completed InterPro results are available yet."
        )

else:

    st.info(
        "No InterPro results have been added yet for this protein."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

st.markdown("---")

st.markdown("## 🧪 Protein Analysis Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)


with summary_col1:

    st.markdown("### 🔎 BLAST")

    st.write(
        "Identifies proteins with similar sequences and "
        "provides sequence similarity information."
    )


with summary_col2:

    st.markdown("### 🧬 MSA")

    st.write(
        "Compares homologous sequences and highlights "
        "conserved and variable regions."
    )


with summary_col3:

    st.markdown("### 🧩 InterPro")

    st.write(
        "Identifies protein families, domains and "
        "functional characteristics."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "RiceCare AI • Protein molecular information and sequence analysis"
)
