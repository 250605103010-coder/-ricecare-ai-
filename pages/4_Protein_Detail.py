```python
import streamlit as st
from utils import styling, data_loader
from urllib.request import urlopen
from pathlib import Path
import html


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Protein Detail — RiceCare AI",
    page_icon="🧬",
    layout="wide"
)

styling.inject_global_css()


# ============================================================
# GET SELECTED PROTEIN
# ============================================================

protein_id = st.session_state.get("rc_selected_protein_id")

if not protein_id:
    st.warning(
        "No protein selected. Go to the Molecular Information page "
        "and click **View Analysis** on a protein card."
    )
    st.stop()


protein = data_loader.get_protein_by_id(protein_id)

if not protein:
    st.error(
        f"Protein `{protein_id}` not found in "
        "`data/protein_information.csv`."
    )
    st.stop()


# ============================================================
# PROTEIN INFORMATION
# ============================================================

st.markdown("## 🧬 Protein Information")


verified = (
    protein.get("verification_status")
    == "VERIFIED_SEARCH_RESULT"
)

badge = (
    "✅ Verified via source lookup"
    if verified
    else "⚠️ Needs verification on UniProt"
)


st.markdown(
    f"### {protein.get('protein_name', '')}"
)

st.caption(badge)


c1, c2 = st.columns(2)


with c1:

    st.markdown(
        f"**Gene name:** "
        f"{protein.get('gene_name', '—')}"
    )

    st.markdown(
        f"**UniProt accession:** "
        f"`{protein.get('uniprot_id', '—')}`"
    )

    st.markdown(
        f"**Organism:** "
        f"{protein.get('organism', '—')}"
    )


with c2:

    st.markdown(
        f"**Sequence length:** "
        f"{protein.get('sequence_length', '—')}"
    )

    st.markdown(
        f"**Associated condition:** "
        f"{protein.get('disease_id', '—')}"
    )


st.markdown("**Function**")

st.write(
    protein.get("function", "—")
)


# ============================================================
# FASTA SEQUENCE
# ============================================================

with st.expander("▶ View FASTA Sequence"):

    accession = str(
        protein.get("uniprot_id", "")
    ).strip()


    if (
        accession == "VERIFY_ON_UNIPROT"
        or not accession
    ):

        st.warning(
            "FASTA sequence is not available because a "
            "verified UniProt accession is required."
        )


    else:

        fasta_url = (
            f"https://rest.uniprot.org/"
            f"uniprotkb/{accession}.fasta"
        )


        try:

            with urlopen(
                fasta_url,
                timeout=10
            ) as response:

                fasta_sequence = (
                    response
                    .read()
                    .decode("utf-8")
                )


            st.success(
                "✅ FASTA sequence retrieved successfully "
                "from UniProt."
            )


            st.code(
                fasta_sequence,
                language="text"
            )


        except Exception:

            st.error(
                f"Unable to retrieve the FASTA sequence "
                f"for UniProt accession `{accession}`."
            )


            st.info(
                f"Please verify the UniProt accession "
                f"`{accession}`."
            )


st.markdown("---")


# ============================================================
# BLAST ANALYSIS
# ============================================================

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

    with st.expander(
        "▶ View Detailed BLAST Results"
    ):

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


# ============================================================
# MSA ANALYSIS
# ============================================================

st.markdown(
    "### 🧬 Multiple Sequence Alignment"
)


st.write(
    "Multiple Sequence Alignment compares related protein "
    "sequences and helps identify conserved regions."
)


msa_rows = data_loader.get_analysis_for_protein(
    protein_id,
    "MSA"
)


# ------------------------------------------------------------
# MSA FILE MAPPING
# ------------------------------------------------------------

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


msa_file = msa_files.get(protein_id)


# ------------------------------------------------------------
# CHECK MSA RESULT
# ------------------------------------------------------------

msa_completed = (
    msa_rows
    and msa_rows[0].get("status")
    != "AWAITING_USER_MSA_RESULTS"
)


if msa_completed and msa_file:

    msa_path = Path(msa_file)


    # --------------------------------------------------------
    # CHECK FILE EXISTS
    # --------------------------------------------------------

    if msa_path.exists():

        try:

            with open(
                msa_path,
                "r",
                encoding="utf-8"
            ) as file:

                msa_text = file.read()


            # ------------------------------------------------
            # MSA INFORMATION
            # ------------------------------------------------

            st.markdown(
                "#### 📊 MSA Result"
            )


            # Show the information stored in CSV
            st.dataframe(
                msa_rows,
                use_container_width=True
            )


            st.markdown(
                "#### 🧬 Complete Sequence Alignment"
            )


            st.caption(
                "The complete Clustal Omega alignment is shown below. "
                "Conserved residues are highlighted using the "
                "conservation symbols *, : and ."
            )


            # ------------------------------------------------
            # CREATE COLOURED MSA HTML
            # ------------------------------------------------

            html_lines = []


            for line in msa_text.splitlines():

                stripped = line.strip()


                # --------------------------------------------
                # CONSERVATION LINE
                # --------------------------------------------

                if (
                    stripped
                    and set(stripped).issubset(
                        set("*:. ")
                    )
                ):

                    coloured_line = ""


                    for character in line:

                        if character == "*":

                            coloured_line += (
                                '<span style="'
                                'color:#008000;'
                                'background-color:#e8f5e9;'
                                'font-weight:bold;'
                                '">*'
                                '</span>'
                            )


                        elif character == ":":

                            coloured_line += (
                                '<span style="'
                                'color:#1565c0;'
                                'background-color:#e3f2fd;'
                                'font-weight:bold;'
                                '">:'
                                '</span>'
                            )


                        elif character == ".":

                            coloured_line += (
                                '<span style="'
                                'color:#e65100;'
                                'background-color:#fff3e0;'
                                'font-weight:bold;'
                                '">.'
                                '</span>'
                            )


                        else:

                            coloured_line += " "


                    html_lines.append(
                        coloured_line
                    )


                # --------------------------------------------
                # NORMAL SEQUENCE LINE
                # --------------------------------------------

                else:

                    html_lines.append(
                        html.escape(line)
                    )


            # ------------------------------------------------
            # DISPLAY ALIGNMENT
            # ------------------------------------------------

            msa_html = (
                '<div style="'
                'overflow-x:auto;'
                'overflow-y:auto;'
                'max-height:650px;'
                'border:1px solid #cccccc;'
                'border-radius:10px;'
                'padding:16px;'
                'background-color:#fafafa;'
                '">'
                '<pre style="'
                'font-family:monospace;'
                'font-size:13px;'
                'line-height:1.6;'
                'margin:0;'
                'white-space:pre;'
                '">'
                + "\n".join(html_lines)
                + "</pre>"
                "</div>"
            )


            st.markdown(
                msa_html,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # CONSERVATION LEGEND
            # ------------------------------------------------

            st.markdown(
                "#### 🎨 Conservation Legend"
            )


            st.markdown(
                """
                <div style="
                    display:flex;
                    gap:20px;
                    flex-wrap:wrap;
                    margin-top:5px;
                    margin-bottom:10px;
                ">

                    <div>
                        <span style="
                            color:#008000;
                            background-color:#e8f5e9;
                            font-weight:bold;
                            padding:3px 7px;
                            border-radius:4px;
                        ">*</span>
                        Identical residue
                    </div>

                    <div>
                        <span style="
                            color:#1565c0;
                            background-color:#e3f2fd;
                            font-weight:bold;
                            padding:3px 7px;
                            border-radius:4px;
                        ">:</span>
                        Strongly conserved substitution
                    </div>

                    <div>
                        <span style="
                            color:#e65100;
                            background-color:#fff3e0;
                            font-weight:bold;
                            padding:3px 7px;
                            border-radius:4px;
                        ">.</span>
                        Weakly conserved substitution
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        except Exception as error:

            st.error(
                "Unable to read the MSA file."
            )

            st.code(
                str(error)
            )


    else:

        st.warning(
            f"MSA file not found: `{msa_file}`"
        )

        st.info(
            "Make sure the MSA file is uploaded to "
            "your GitHub repository at the correct path."
        )


elif msa_completed and not msa_file:

    st.info(
        "No MSA file has been configured for this protein."
    )


else:

    st.info(
        "No MSA results have been added yet for this protein. "
        "Populate `data/protein_analysis.csv` "
        "(analysis_type = MSA) with your actual alignment "
        "result to activate this section."
    )


st.markdown("---")
```

### One important thing, bro

For **PBZ1**, your GitHub structure must now be:

```text
data/
└── msa/
    └── pbz1_msa.txt
```

And the file must contain the **full PBZ1 Clustal Omega alignment** you gave me.

For the other proteins, the code is already prepared for:

```text
xa21_msa.txt
pi-ta_msa.txt
ospr1_msa.txt
rab16_msa.txt
```

So you **do not need to change the Python code again** when you add those MSA files. Just put the complete alignment into the corresponding `.txt` file.

One small correction from earlier: the alignment you just pasted is **PBZ1**, not Pi-ta. The code above correctly maps it to `PROT_PBZ1`.
