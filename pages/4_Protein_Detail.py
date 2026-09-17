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
    "Detailed molecular information, FASTA sequence, BLAST, "
    "MSA and InterPro analysis"
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


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fasta(accession):
    fasta_url = (
        f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
    )

    with urlopen(fasta_url, timeout=10) as response:
        return response.read().decode("utf-8")


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

        try:

            fasta_sequence = fetch_fasta(accession)

            st.success(
                "✅ FASTA sequence retrieved successfully from UniProt."
            )

            st.code(
                fasta_sequence,
                language="text"
            )

        except Exception as e:

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
        "No completed BLAST results have been added yet for this protein."
    )


# ============================================================
# MSA FILE MAPPING
# ============================================================

msa_files = {
    "PROT_XA21": "data/msa/xa21_msa.txt",
    "PROT_PITA": "data/msa/pi-ta_msa.txt",
    "PROT_PBZ1": "data/msa/pbz1_msa.txt",
    "PROT_OSPR1": "data/msa/ospr1_msa.txt",
    "PROT_OSRAB16": "data/msa/rab16_msa.txt",
}


# ============================================================
# MSA INFORMATION
# ============================================================

msa_info = {

    "PROT_XA21": {
        "region": "1–1025 aa",
        "description":
            "XA21 homologs show complete sequence conservation "
            "across the aligned 1025 amino acids.",
        "limit": 1025,
    },

    "PROT_PITA": {
        "region": "1–840 aa",
        "description":
            "Pi-ta homologs show substantial sequence conservation "
            "through approximately 840 amino acids.",
        "limit": 840,
    },

    "PROT_PBZ1": {
        "region": "1–158 aa",
        "description":
            "PBZ1 homologs show complete sequence conservation "
            "across the aligned 158 amino acids.",
        "limit": 158,
    },

    "PROT_OSPR1": {
        "region": "Aligned residues",
        "description":
            "OsPR1 homologs show complete conservation across "
            "the corresponding aligned residues.",
        "limit": None,
    },

    "PROT_OSRAB16": {
        "region": "Full alignment",
        "description":
            "RAB16 homologs contain conserved regions together "
            "with variable and gapped regions.",
        "limit": None,
    },
}


# ============================================================
# PARSE CLUSTAL ALIGNMENT
# ============================================================

def parse_clustal(msa_text):

    blocks = []

    current_sequences = []
    current_consensus = ""

    for line in msa_text.splitlines():

        if not line.strip():

            if current_sequences:

                blocks.append(
                    {
                        "sequences": current_sequences,
                        "consensus": current_consensus,
                    }
                )

                current_sequences = []
                current_consensus = ""

            continue

        if line.upper().startswith("CLUSTAL"):

            continue

        stripped = line.strip()

        # Consensus lines contain only alignment symbols/spaces.
        if (
            line[:1].isspace()
            and stripped
            and all(char in "*:. " for char in stripped)
        ):

            current_consensus = stripped
            continue

        parts = line.split()

        if len(parts) >= 2:

            sequence_id = parts[0]
            sequence = parts[1]

            current_sequences.append(
                (
                    sequence_id,
                    sequence
                )
            )

    if current_sequences:

        blocks.append(
            {
                "sequences": current_sequences,
                "consensus": current_consensus,
            }
        )

    return blocks


# ============================================================
# COLOR ACTUAL AMINO ACIDS
# ============================================================

def color_sequence(sequence, consensus):

    result = []

    for index, residue in enumerate(sequence):

        symbol = ""

        if index < len(consensus):
            symbol = consensus[index]

        safe_residue = html.escape(residue)

        if symbol == "*":

            result.append(
                '<span class="aa aa-identical">'
                + safe_residue
                + "</span>"
            )

        elif symbol == ":":

            result.append(
                '<span class="aa aa-strong">'
                + safe_residue
                + "</span>"
            )

        elif symbol == ".":

            result.append(
                '<span class="aa aa-weak">'
                + safe_residue
                + "</span>"
            )

        else:

            result.append(
                '<span class="aa">'
                + safe_residue
                + "</span>"
            )

    return "".join(result)


# ============================================================
# RENDER MSA BLOCK
# ============================================================

def render_msa_block(block):

    sequences = block["sequences"]
    consensus = block["consensus"]

    if not sequences:
        return ""

    id_width = max(
        len(sequence_id)
        for sequence_id, sequence in sequences
    )

    rows = []

    # --------------------------------------------------------
    # Sequence rows
    # --------------------------------------------------------

    for sequence_id, sequence in sequences:

        colored_sequence = color_sequence(
            sequence,
            consensus
        )

        safe_id = html.escape(sequence_id)

        rows.append(
            '<div class="msa-row">'
            '<span class="msa-name">'
            + safe_id.ljust(id_width)
            + "</span>"
            '<span class="msa-sequence">'
            + colored_sequence
            + "</span>"
            "</div>"
        )

    # --------------------------------------------------------
    # Conservation row
    # --------------------------------------------------------

    if consensus:

        consensus_html = []

        for symbol in consensus:

            if symbol == "*":

                consensus_html.append(
                    '<span class="cons-identical">*</span>'
                )

            elif symbol == ":":

                consensus_html.append(
                    '<span class="cons-strong">:</span>'
                )

            elif symbol == ".":

                consensus_html.append(
                    '<span class="cons-weak">.</span>'
                )

            else:

                consensus_html.append(" ")

        rows.append(
            '<div class="msa-row consensus-row">'
            '<span class="msa-name">'
            + (" " * id_width)
            + "</span>"
            '<span class="msa-consensus">'
            + "".join(consensus_html)
            + "</span>"
            "</div>"
        )

    return "".join(rows)


# ============================================================
# LIMIT ALIGNMENT TO SPECIFIC REGION
# ============================================================

def limit_blocks(blocks, limit):

    if limit is None:
        return blocks

    result = []

    current_position = 0

    for block in blocks:

        sequences = block["sequences"]

        if not sequences:
            continue

        block_length = len(
            sequences[0][1]
        )

        if current_position >= limit:
            break

        remaining = limit - current_position

        keep_length = min(
            block_length,
            remaining
        )

        new_sequences = []

        for sequence_id, sequence in sequences:

            new_sequences.append(
                (
                    sequence_id,
                    sequence[:keep_length]
                )
            )

        new_consensus = block["consensus"][:keep_length]

        result.append(
            {
                "sequences": new_sequences,
                "consensus": new_consensus,
            }
        )

        current_position += block_length

    return result


# ============================================================
# MSA
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

            msa_text = msa_path.read_text(
                encoding="utf-8"
            )

            if not msa_text.strip():

                st.warning(
                    f"The MSA file `{msa_file}` is empty."
                )

            else:

                blocks = parse_clustal(
                    msa_text
                )

                information = msa_info.get(
                    protein_id,
                    {
                        "region": "Full alignment",
                        "description":
                            "Conservation is shown directly "
                            "on the aligned amino-acid residues.",
                        "limit": None,
                    }
                )

                # ------------------------------------------------
                # Conserved region
                # ------------------------------------------------

                st.markdown(
                    "### 🎯 Conserved Region"
                )

                region_col1, region_col2 = st.columns(
                    [1, 3]
                )

                with region_col1:

                    st.metric(
                        "Region",
                        information["region"]
                    )

                with region_col2:

                    st.info(
                        information["description"]
                    )

                # ------------------------------------------------
                # Legend
                # ------------------------------------------------

                st.markdown(
                    "### 🎨 Conservation Key"
                )

                legend1, legend2, legend3, legend4 = st.columns(4)

                with legend1:

                    st.markdown(
                        '<span class="legend '
                        'legend-identical">A</span> '
                        '**Identical (`*`)**',
                        unsafe_allow_html=True
                    )

                with legend2:

                    st.markdown(
                        '<span class="legend '
                        'legend-strong">A</span> '
                        '**Strongly conserved (`:`)**',
                        unsafe_allow_html=True
                    )

                with legend3:

                    st.markdown(
                        '<span class="legend '
                        'legend-weak">A</span> '
                        '**Weakly conserved (`.`)**',
                        unsafe_allow_html=True
                    )

                with legend4:

                    st.markdown(
                        "⬜ Variable / non-conserved"
                    )

                # ------------------------------------------------
                # Main region
                # ------------------------------------------------

                main_blocks = limit_blocks(
                    blocks,
                    information["limit"]
                )

                msa_html = []

                for block in main_blocks:

                    msa_html.append(
                        render_msa_block(block)
                    )

                complete_html = "".join(
                    msa_html
                )

                # ------------------------------------------------
                # Display CSS
                # ------------------------------------------------

                st.markdown(
                    """
                    <style>

                    .msa-box {
                        width: 100%;
                        max-height: 720px;
                        overflow-x: auto;
                        overflow-y: auto;
                        border: 1px solid #d6d6d6;
                        border-radius: 10px;
                        background-color: #fafafa;
                        padding: 18px;
                        box-sizing: border-box;
                    }

                    .msa-content {
                        width: max-content;
                        min-width: 100%;
                        font-family:
                            "Courier New",
                            Courier,
                            monospace;
                        font-size: 13px;
                        line-height: 1.7;
                        white-space: nowrap;
                    }

                    .msa-row {
                        display: flex;
                        white-space: pre;
                        min-height: 22px;
                    }

                    .msa-name {
                        display: inline-block;
                        flex-shrink: 0;
                        margin-right: 18px;
                        color: #333333;
                        font-weight: 600;
                    }

                    .msa-sequence {
                        display: inline-block;
                    }

                    .aa {
                        display: inline-block;
                        width: 1ch;
                        text-align: center;
                        border-radius: 2px;
                    }

                    .aa-identical {
                        background-color: #b7f7b7;
                        color: #075b07;
                        font-weight: 700;
                    }

                    .aa-strong {
                        background-color: #b9dcff;
                        color: #063f78;
                        font-weight: 700;
                    }

                    .aa-weak {
                        background-color: #ffdca8;
                        color: #7a4100;
                        font-weight: 700;
                    }

                    .consensus-row {
                        color: #555555;
                        font-weight: 700;
                    }

                    .msa-consensus {
                        display: inline-block;
                    }

                    .cons-identical {
                        color: #087408;
                        font-weight: 900;
                    }

                    .cons-strong {
                        color: #075b9e;
                        font-weight: 900;
                    }

                    .cons-weak {
                        color: #b15d00;
                        font-weight: 900;
                    }

                    .legend {
                        display: inline-block;
                        width: 22px;
                        height: 22px;
                        line-height: 22px;
                        text-align: center;
                        border-radius: 3px;
                        font-family:
                            "Courier New",
                            monospace;
                        font-weight: 700;
                    }

                    .legend-identical {
                        background-color: #b7f7b7;
                        color: #075b07;
                    }

                    .legend-strong {
                        background-color: #b9dcff;
                        color: #063f78;
                    }

                    .legend-weak {
                        background-color: #ffdca8;
                        color: #7a4100;
                    }

                    </style>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="msa-box">'
                    '<div class="msa-content">'
                    + complete_html
                    + "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )

                # ------------------------------------------------
                # Pi-ta divergent C-terminal region
                # ------------------------------------------------

                if (
                    protein_id == "PROT_PITA"
                    and information["limit"] is not None
                ):

                    limit = information["limit"]

                    divergent_blocks = []

                    current_position = 0

                    for block in blocks:

                        sequences = block["sequences"]

                        if not sequences:
                            continue

                        block_length = len(
                            sequences[0][1]
                        )

                        block_start = current_position

                        block_end = (
                            current_position
                            + block_length
                        )

                        if block_end > limit:

                            start_index = max(
                                0,
                                limit - block_start
                            )

                            new_sequences = []

                            for sequence_id, sequence in sequences:

                                new_sequences.append(
                                    (
                                        sequence_id,
                                        sequence[start_index:]
                                    )
                                )

                            divergent_blocks.append(
                                {
                                    "sequences":
                                        new_sequences,
                                    "consensus":
                                        block["consensus"]
                                        [start_index:],
                                }
                            )

                        current_position = block_end

                    if divergent_blocks:

                        st.markdown("---")

                        st.markdown(
                            "### ⚠️ Pi-ta C-terminal "
                            "Divergent Region"
                        )

                        st.warning(
                            "After approximately 840 aa, "
                            "the Pi-ta homologs show greater "
                            "sequence divergence and gaps."
                        )

                        divergent_html = []

                        for block in divergent_blocks:

                            divergent_html.append(
                                render_msa_block(block)
                            )

                        with st.expander(
                            "▶ View C-terminal Divergent Region"
                        ):

                            st.markdown(
                                '<div class="msa-box">'
                                '<div class="msa-content">'
                                + "".join(divergent_html)
                                + "</div>"
                                "</div>",
                                unsafe_allow_html=True
                            )

        except Exception as e:

            st.error(
                "Unable to read or display the MSA file."
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
# MSA DATABASE INFORMATION
# ============================================================

st.markdown("---")
st.markdown("## 📊 MSA Analysis Information")

msa_rows = get_analysis_rows(
    protein_id,
    "MSA"
)

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
