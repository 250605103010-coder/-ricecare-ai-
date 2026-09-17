```python
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
        f"https://rest.uniprot.org/uniprotkb/"
        f"{accession}.fasta"
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
# MSA DISPLAY CONFIGURATION
# ============================================================

msa_region_info = {

    "PROT_XA21": {
        "title": "Complete conserved region",
        "range": "1–1025 aa",
        "description":
            "XA21 homologs show complete sequence conservation "
            "across the aligned 1025 amino acids.",
        "main_limit": 1025,
    },

    "PROT_PITA": {
        "title": "Main conserved region",
        "range": "1–840 aa",
        "description":
            "Pi-ta homologs show substantial conservation through "
            "approximately 840 amino acids. The later C-terminal "
            "region contains greater sequence divergence and gaps.",
        "main_limit": 840,
    },

    "PROT_PBZ1": {
        "title": "Complete conserved region",
        "range": "1–158 aa",
        "description":
            "PBZ1 homologs show complete sequence conservation "
            "across the aligned 158 amino acids.",
        "main_limit": 158,
    },

    "PROT_OSPR1": {
        "title": "Aligned conserved region",
        "range": "Aligned residues",
        "description":
            "OsPR1 homologs show complete conservation across "
            "the corresponding aligned residues, with an "
            "N-terminal gap in one sequence.",
        "main_limit": None,
    },

    "PROT_OSRAB16": {
        "title": "Conserved and variable regions",
        "range": "Full alignment",
        "description":
            "RAB16 homologs contain several conserved regions "
            "together with variable and gapped regions.",
        "main_limit": None,
    },
}


# ============================================================
# CLUSTAL MSA PARSER
# ============================================================

def parse_clustal_blocks(msa_text):
    """
    Parse a Clustal Omega alignment into blocks.

    Each block contains:
        sequence rows
        conservation row

    The function preserves the original sequence order.
    """

    lines = msa_text.splitlines()

    blocks = []
    current_sequences = []
    current_consensus = None

    for line in lines:

        if not line.strip():
            if current_sequences:

                blocks.append(
                    {
                        "sequences": current_sequences,
                        "consensus": current_consensus or ""
                    }
                )

                current_sequences = []
                current_consensus = None

            continue

        stripped = line.strip()

        # Skip CLUSTAL heading
        if stripped.upper().startswith("CLUSTAL"):
            continue

        # Consensus line:
        # starts with spaces and contains *, :, .
        if (
            line[:1].isspace()
            and any(symbol in line for symbol in "*:.")
        ):
            current_consensus = line.strip()

            if current_sequences:

                blocks.append(
                    {
                        "sequences": current_sequences,
                        "consensus": current_consensus
                    }
                )

                current_sequences = []
                current_consensus = None

            continue

        parts = line.split()

        if len(parts) >= 2:

            sequence_id = parts[0]
            sequence_part = parts[1]

            # Ignore lines that are not sequence lines
            if (
                sequence_id.lower()
                not in ["clustal", "omega"]
                and sequence_part
            ):

                current_sequences.append(
                    (
                        sequence_id,
                        sequence_part
                    )
                )

    if current_sequences:

        blocks.append(
            {
                "sequences": current_sequences,
                "consensus": current_consensus or ""
            }
        )

    return blocks


# ============================================================
# COLOR ACTUAL AMINO ACIDS USING CONSERVATION LINE
# ============================================================

def color_sequence(sequence, consensus):

    """
    Color the actual amino-acid characters according to
    the Clustal conservation symbols.

    * = identical
    : = strongly conserved
    . = weakly conserved
    """

    output = []

    for index, residue in enumerate(sequence):

        symbol = ""

        if index < len(consensus):
            symbol = consensus[index]

        safe_residue = html.escape(residue)

        if symbol == "*":

            output.append(
                '<span class="msa-residue msa-identical">'
                f"{safe_residue}"
                "</span>"
            )

        elif symbol == ":":

            output.append(
                '<span class="msa-residue msa-strong">'
                f"{safe_residue}"
                "</span>"
            )

        elif symbol == ".":

            output.append(
                '<span class="msa-residue msa-weak">'
                f"{safe_residue}"
                "</span>"
            )

        else:

            output.append(
                f'<span class="msa-residue">'
                f"{safe_residue}"
                "</span>"
            )

    return "".join(output)


# ============================================================
# BUILD HTML MSA BLOCK
# ============================================================

def build_msa_html(blocks):

    html_blocks = []

    for block in blocks:

        sequences = block["sequences"]
        consensus = block["consensus"]

        if not sequences:
            continue

        # Determine longest sequence identifier
        id_width = max(
            len(sequence_id)
            for sequence_id, _ in sequences
        )

        block_html = []

        for sequence_id, sequence in sequences:

            colored_sequence = color_sequence(
                sequence,
                consensus
            )

            block_html.append(
                '<div class="msa-row">'
                f'<span class="msa-id" '
                f'style="width:{id_width + 2}ch;">'
                f'{html.escape(sequence_id)}'
                "</span>"
                f'<span class="msa-sequence">'
                f'{colored_sequence}'
                "</span>"
                "</div>"
            )

        # Conservation line
        if consensus:

            safe_consensus = html.escape(
                consensus
            )

            colored_consensus = (
                safe_consensus
                .replace(
                    "*",
                    '<span class="cons-star">*</span>'
                )
                .replace(
                    ":",
                    '<span class="cons-colon">:</span>'
                )
                .replace(
                    ".",
                    '<span class="cons-dot">.</span>'
                )
            )

            block_html.append(
                '<div class="msa-consensus-row">'
                f'<span class="msa-id" '
                f'style="width:{id_width + 2}ch;">'
                " "
                "</span>"
                f'<span class="msa-consensus">'
                f'{colored_consensus}'
                "</span>"
                "</div>"
            )

        html_blocks.append(
            '<div class="msa-block">'
            + "".join(block_html)
            + "</div>"
        )

    return "".join(html_blocks)


# ============================================================
# LIMIT MSA BY ALIGNMENT POSITION
# ============================================================

def limit_msa_blocks(blocks, max_position):

    """
    Keep only the alignment blocks whose cumulative sequence
    position is within max_position.

    This is mainly used for the Pi-ta 1–840 aa conserved region.
    """

    if max_position is None:
        return blocks

    limited_blocks = []
    current_position = 0

    for block in blocks:

        sequences = block["sequences"]

        if not sequences:
            continue

        block_length = len(
            sequences[0][1]
        )

        if current_position >= max_position:
            break

        remaining = (
            max_position
            - current_position
        )

        if remaining <= 0:
            break

        if block_length <= remaining:

            limited_blocks.append(block)

        else:

            new_sequences = []

            for sequence_id, sequence in sequences:

                new_sequences.append(
                    (
                        sequence_id,
                        sequence[:remaining]
                    )
                )

            new_consensus = block[
                "consensus"
            ][:remaining]

            limited_blocks.append(
                {
                    "sequences": new_sequences,
                    "consensus": new_consensus
                }
            )

        current_position += block_length

    return limited_blocks


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

                blocks = parse_clustal_blocks(
                    msa_text
                )

                region_info = msa_region_info.get(
                    protein_id,
                    {
                        "title":
                            "MSA region",
                        "range":
                            "Full alignment",
                        "description":
                            "Sequence conservation "
                            "is shown using Clustal "
                            "conservation symbols.",
                        "main_limit":
                            None,
                    }
                )

                # ------------------------------------------------
                # CONSERVED REGION INFORMATION
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
                        region_info["range"]
                    )

                with region_col2:

                    st.info(
                        region_info["description"]
                    )

                # ------------------------------------------------
                # MSA COLOR EXPLANATION
                # ------------------------------------------------

                st.markdown(
                    "### 🎨 Conservation Key"
                )

                legend1, legend2, legend3, legend4 = (
                    st.columns(4)
                )

                with legend1:

                    st.markdown(
                        '<span class="legend-box '
                        'legend-identical">'
                        'A</span> '
                        '<b>Identical</b> '
                        '— Clustal `*`',
                        unsafe_allow_html=True
                    )

                with legend2:

                    st.markdown(
                        '<span class="legend-box '
                        'legend-strong">'
                        'A</span> '
                        '<b>Strongly conserved</b> '
                        '— Clustal `:`',
                        unsafe_allow_html=True
                    )

                with legend3:

                    st.markdown(
                        '<span class="legend-box '
                        'legend-weak">'
                        'A</span> '
                        '<b>Weakly conserved</b> '
                        '— Clustal `.`',
                        unsafe_allow_html=True
                    )

                with legend4:

                    st.markdown(
                        "⬜ Variable / non-conserved"
                    )

                # ------------------------------------------------
                # CSS
                # ------------------------------------------------

                st.markdown(
                    """
                    <style>

                    .msa-wrapper {
                        width: 100%;
                        overflow-x: auto;
                        overflow-y: auto;
                        max-height: 720px;
                        border: 1px solid #d6d6d6;
                        border-radius: 10px;
                        background: #fafafa;
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
                        line-height: 1.65;
                        white-space: nowrap;
                    }

                    .msa-block {
                        margin-bottom: 18px;
                    }

                    .msa-row {
                        display: flex;
                        align-items: baseline;
                        min-height: 22px;
                    }

                    .msa-id {
                        display: inline-block;
                        flex-shrink: 0;
                        color: #333333;
                        font-weight: 600;
                        text-align: left;
                    }

                    .msa-sequence {
                        display: inline-block;
                        letter-spacing: 0;
                    }

                    .msa-residue {
                        display: inline-block;
                        width: 1ch;
                        text-align: center;
                        border-radius: 2px;
                    }

                    .msa-identical {
                        background-color: #b7f7b7;
                        color: #075b07;
                        font-weight: 700;
                    }

                    .msa-strong {
                        background-color: #b9dcff;
                        color: #063f78;
                        font-weight: 700;
                    }

                    .msa-weak {
                        background-color: #ffdca8;
                        color: #7a4100;
                        font-weight: 700;
                    }

                    .msa-consensus-row {
                        display: flex;
                        align-items: baseline;
                        min-height: 22px;
                        margin-top: 1px;
                    }

                    .msa-consensus {
                        display: inline-block;
                        color: #555555;
                        font-weight: 700;
                    }

                    .cons-star {
                        color: #087408;
                        font-weight: 900;
                    }

                    .cons-colon {
                        color: #075b9e;
                        font-weight: 900;
                    }

                    .cons-dot {
                        color: #b15d00;
                        font-weight: 900;
                    }

                    .legend-box {
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

                # ------------------------------------------------
                # MAIN CONSERVED REGION
                # ------------------------------------------------

                main_blocks = limit_msa_blocks(
                    blocks,
                    region_info["main_limit"]
                )

                main_html = build_msa_html(
                    main_blocks
                )

                st.markdown(
                    f"""
                    <div class="msa-wrapper">
                        <div class="msa-content">
                            {main_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ------------------------------------------------
                # PI-TA C-TERMINAL REGION
                # ------------------------------------------------

                if protein_id == "PROT_PITA":

                    conserved_limit = 840

                    divergent_blocks = []

                    current_position = 0

                    for block in blocks:

                        if not block["sequences"]:
                            continue

                        block_length = len(
                            block["sequences"][0][1]
                        )

                        block_start = current_position
                        block_end = (
                            current_position
                            + block_length
                        )

                        if block_end > conserved_limit:

                            start_index = max(
                                0,
                                conserved_limit
                                - block_start
                            )

                            new_sequences = []

                            for sequence_id, sequence in (
                                block["sequences"]
                            ):

                                new_sequences.append(
                                    (
                                        sequence_id,
                                        sequence[start_index:]
                                    )
                                )

                            new_consensus = (
                                block["consensus"]
                                [start_index:]
                            )

                            divergent_blocks.append(
                                {
                                    "sequences":
                                        new_sequences,
                                    "consensus":
                                        new_consensus
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
                            "Positions after approximately "
                            "840 aa show greater sequence "
                            "divergence and gaps between the "
                            "homologous sequences."
                        )

                        divergent_html = build_msa_html(
                            divergent_blocks
                        )

                        with st.expander(
                            "▶ View C-terminal divergent region"
                        ):

                            st.markdown(
                                f"""
                                <div class="msa-wrapper">
                                    <div class="msa-content">
                                        {divergent_html}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                # ------------------------------------------------
                # FULL ALIGNMENT OPTION
                # ------------------------------------------------

                with st.expander(
                    "▶ View Full Original Clustal Alignment"
                ):

                    full_html = build_msa_html(
                        blocks
                    )

                    st.markdown(
                        f"""
                        <div class="msa-wrapper">
                            <div class="msa-content">
                                {full_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.warning(
                    f"The MSA file `{msa_file}` is empty."
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
            "MSA information has not been added to the "
            "analysis database yet."
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

        with st.expander(
            "▶ View InterPro Results"
        ):

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
```
