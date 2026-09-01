"""
data_loader.py
----------------
Central data-access layer for RiceCare AI.
Keeps all disease / protein / analysis / feedback data separate from UI code
so the presentation layer never hard-codes scientific content.

All lookups here are keyed by `disease_id`, which is the single source of
truth connecting: AI prediction -> disease info -> sample images -> proteins
-> protein analysis (BLAST / MSA / InterPro).
"""

import os
import csv
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

DISEASE_CSV = os.path.join(DATA_DIR, "disease_information.csv")
PROTEIN_CSV = os.path.join(DATA_DIR, "protein_information.csv")
ANALYSIS_CSV = os.path.join(DATA_DIR, "protein_analysis.csv")
PERFORMANCE_CSV = os.path.join(DATA_DIR, "model_performance.csv")
CONFUSION_CSV = os.path.join(DATA_DIR, "confusion_matrix.csv")
FEEDBACK_CSV = os.path.join(DATA_DIR, "feedback.csv")
SAMPLE_IMAGE_DIR = os.path.join(DATA_DIR, "sample_images")

# disease_id -> folder name under sample_images/
DISEASE_ID_TO_FOLDER = {
    "HEALTHY": "healthy",
    "RICE_BLAST": "rice_blast",
    "BROWN_SPOT": "brown_spot",
    "BACTERIAL_LEAF_BLIGHT": "bacterial_leaf_blight",
}

# Ordered class list used everywhere the four-way prediction is displayed
DISEASE_CLASSES = ["HEALTHY", "RICE_BLAST", "BROWN_SPOT", "BACTERIAL_LEAF_BLIGHT"]


def _safe_read_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def load_disease_data():
    """Returns a DataFrame indexed by disease_id."""
    df = _safe_read_csv(DISEASE_CSV)
    if df.empty:
        return df
    return df.set_index("disease_id", drop=False)


def get_disease_info(disease_id: str) -> dict:
    """Returns a dict of disease info for one disease_id, or a placeholder if missing."""
    df = load_disease_data()
    if df.empty or disease_id not in df.index:
        return {
            "disease_id": disease_id,
            "disease_name": disease_id.replace("_", " ").title(),
            "emoji": "❓",
            "causative_agent": "PLACEHOLDER_MISSING_DATA",
            "causal_organism": "PLACEHOLDER_MISSING_DATA",
            "symptoms": [],
            "management": [],
            "description": "No verified information found for this disease in disease_information.csv. "
                           "Please add a row for this disease_id.",
        }
    row = df.loc[disease_id]
    return {
        "disease_id": row["disease_id"],
        "disease_name": row["disease_name"],
        "emoji": row.get("emoji", "🌾"),
        "causative_agent": row.get("causative_agent", ""),
        "causal_organism": row.get("causal_organism", ""),
        "symptoms": [s.strip() for s in str(row.get("symptoms", "")).split("|") if s.strip()],
        "management": [m.strip() for m in str(row.get("management", "")).split("|") if m.strip()],
        "description": row.get("description", ""),
    }


def load_protein_data():
    return _safe_read_csv(PROTEIN_CSV)


def get_proteins_for_disease(disease_id: str) -> list:
    """Returns list of protein dicts associated with a disease_id (data-driven join)."""
    df = load_protein_data()
    if df.empty:
        return []
    matches = df[df["disease_id"] == disease_id]
    return matches.to_dict(orient="records")


def get_protein_by_id(protein_id: str) -> dict:
    df = load_protein_data()
    if df.empty:
        return {}
    matches = df[df["protein_id"] == protein_id]
    if matches.empty:
        return {}
    return matches.iloc[0].to_dict()


def load_analysis_data():
    return _safe_read_csv(ANALYSIS_CSV)


def get_analysis_for_protein(protein_id: str, analysis_type: str = None) -> list:
    """analysis_type: one of BLAST, MSA, INTERPRO, or None for all."""
    df = load_analysis_data()
    if df.empty:
        return []
    matches = df[df["protein_id"] == protein_id]
    if analysis_type:
        matches = matches[matches["analysis_type"] == analysis_type.upper()]
    return matches.to_dict(orient="records")


def load_model_performance() -> dict:
    df = _safe_read_csv(PERFORMANCE_CSV)
    if df.empty:
        return {}
    return dict(zip(df["metric"], df["value"]))


def performance_is_evaluated() -> bool:
    perf = load_model_performance()
    if not perf:
        return False
    val = perf.get("test_accuracy", None)
    return val is not None and str(val).strip() not in ("", "nan")


def load_confusion_matrix():
    return _safe_read_csv(CONFUSION_CSV)


def get_sample_images(disease_id: str, max_images: int = 4) -> list:
    """Returns list of file paths for representative images of a predicted class."""
    folder = DISEASE_ID_TO_FOLDER.get(disease_id)
    if not folder:
        return []
    dir_path = os.path.join(SAMPLE_IMAGE_DIR, folder)
    if not os.path.isdir(dir_path):
        return []
    files = sorted(
        f for f in os.listdir(dir_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    return [os.path.join(dir_path, f) for f in files[:max_images]]


def submit_feedback(name: str, role: str, rating: int, feedback: str):
    """Appends a real user-submitted feedback row. Never generates fake reviews."""
    import datetime
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(FEEDBACK_CSV) and os.path.getsize(FEEDBACK_CSV) > 0
    with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow(["timestamp", "name", "role", "rating", "feedback"])
        writer.writerow([
            datetime.datetime.now().isoformat(timespec="seconds"),
            name or "Anonymous",
            role or "",
            rating,
            feedback,
        ])


def load_feedback() -> pd.DataFrame:
    return _safe_read_csv(FEEDBACK_CSV)
