# 🌾 RiceCare AI

AI-Powered Rice Disease & Molecular Information Analyzer — Version 1 (Rice only, 4 classes).

## 1. Run it locally

```bash
cd RiceCareAI
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## 2. Deploy it online (free options)

### Streamlit Community Cloud (easiest, free)
1. Push this folder to a **GitHub repo**.
2. Go to https://share.streamlit.io → "New app" → select the repo → set main file to `app.py`.
3. Deploy. You get a public `*.streamlit.app` URL you can share/embed anywhere, including a Google Site or a link on Google Drive/Docs.

### Google Cloud Run (Google-hosted)
1. Add a `Dockerfile` (basic example):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 8080
   CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
   ```
2. `gcloud run deploy ricecare-ai --source .` from the project folder (requires a GCP project with billing enabled).

### Render / Railway / Hugging Face Spaces
All support Streamlit apps directly from a GitHub repo with a `requirements.txt` — point them at `app.py` as the entry file.

## 3. Project structure

```
RiceCareAI/
├── app.py                          # Home page (multipage app entry point)
├── pages/
│   ├── 1_Analyze_My_Plant.py       # Core upload → predict → results flow
│   ├── 2_Explore_Rice_Diseases.py
│   ├── 3_Molecular_Information.py
│   ├── 3_Protein_Detail.py         # Protein detail sub-page (UniProt/BLAST/MSA/InterPro)
│   ├── 4_Model_Performance.py
│   ├── 5_How_It_Works.py
│   ├── 6_Feedback.py
│   └── 7_About.py
├── utils/
│   ├── data_loader.py              # All CSV reads/writes, disease↔protein joins
│   ├── model_utils.py              # Model loading + prediction (real model or demo mode)
│   └── styling.py                  # Shared premium/scientific/agricultural CSS theme
├── data/
│   ├── disease_information.csv
│   ├── protein_information.csv
│   ├── protein_analysis.csv        # BLAST / MSA / InterPro results (placeholders now)
│   ├── model_performance.csv       # Accuracy/precision/recall (placeholders now)
│   ├── confusion_matrix.csv        # Placeholder
│   ├── feedback.csv                # Real user feedback only, appended at runtime
│   └── sample_images/
│       ├── healthy/
│       ├── rice_blast/
│       ├── brown_spot/
│       └── bacterial_leaf_blight/
├── model/
│   └── (drop rice_disease_model.h5 or .keras here)
└── requirements.txt
```

## 4. Where to put your data

| What | Where |
|---|---|
| Trained CNN model | `model/rice_disease_model.h5` or `model/rice_disease_model.keras` — auto-detected, no code changes |
| Real leaf photos for comparison | `data/sample_images/<class_folder>/` — replaces the current clearly-labeled placeholder PNGs |
| Disease facts | `data/disease_information.csv` — already populated with 4 classes; edit/expand as needed |
| Protein records | `data/protein_information.csv` — 2 rows have **verified** UniProt IDs (Xa21 = Q40640, Pi-ta = E7BTM6) found via literature/UniProt lookup during this build; the rest are marked `VERIFY_ON_UNIPROT` / `NEEDS_VERIFICATION` and must be confirmed by you before being presented as fact |
| BLAST / MSA / InterPro results | `data/protein_analysis.csv` — currently all placeholder rows; replace `PLACEHOLDER_NEEDS_DATA` fields with your real analysis output |
| Model accuracy numbers | `data/model_performance.csv` and `data/confusion_matrix.csv` — filled in only after you evaluate the trained model on a held-out test set |

## 5. How prediction connects to information (data flow)

```
Upload image → utils/model_utils.predict() → {disease_id: probability} for all 4 classes
                                                        │
                                          highest-scoring disease_id
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        ▼                                                                ▼
        data_loader.get_disease_info(disease_id)                    data_loader.get_proteins_for_disease(disease_id)
        → symptoms, cause, management, description                  → protein cards → BLAST/MSA/InterPro (protein_analysis.csv)
                        │
        data_loader.get_sample_images(disease_id)
        → representative comparison photos
```

Everything is joined on `disease_id`, so adding a new disease later only requires new CSV rows and an image folder — no UI code changes.

## 6. What's still needed before this is scientifically complete

1. **A trained CNN model** (Colab workflow) — currently running in demo mode with a placeholder heuristic, clearly labeled everywhere it appears.
2. **Real leaf photographs** to replace the placeholder comparison images.
3. **Verification of the "NEEDS_VERIFICATION" protein rows** (PBZ1, OsPR1, Rab16) against UniProt — confirm accession numbers before treating them as fact.
4. **Real BLAST / MSA / InterPro output** for each protein, to replace the placeholder rows in `protein_analysis.csv`.
5. **Model evaluation metrics** (accuracy, precision, recall, F1, confusion matrix) from a real held-out test set.

## 7. What changed from the prior prototype

This is a full rebuild in the current session (the container that ran the earlier prototype is not persistent — files don't survive between sessions, only the project context does). Nothing from a previous working prediction pipeline was removed; this version re-implements it with a demo-mode fallback identical in spirit to the earlier design, plus the full 8-page navigation, dynamic disease→protein data flow, and the premium agricultural/scientific visual theme requested.
