"""
model_utils.py
----------------
Handles RiceCare AI model loading and prediction.

Trained model:
models/rice_leaf_disease_efficientnetb0.keras

Classes:
0 -> bacterial_leaf_blight
1 -> brown_spot
2 -> healthy
3 -> leaf_blast
"""

import os
import numpy as np
from PIL import Image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODEL_DIR, "rice_leaf_disease_efficientnetb0.keras")

CLASS_PATH = os.path.join(MODEL_DIR, "rice_leaf_disease_classes.txt")


# ============================================================
# MODEL SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)

CLASS_ORDER = [
    "bacterial_leaf_blight",
    "brown_spot",
    "healthy",
    "leaf_blast",
]


# ============================================================
# MODEL CACHE
# ============================================================

_model_cache = {
    "model": None,
    "loaded": False,
    "path": None,
    "error": None,
}


# ============================================================
# FIND MODEL
# ============================================================

def find_model_path():
    """Return the trained model path if it exists."""
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    return None


# ============================================================
# DEMO MODE CHECK
# ============================================================

def is_demo_mode() -> bool:
    """Returns True only when the model file itself is not present."""
    return find_model_path() is None


# ============================================================
# LOAD CLASS NAMES
# ============================================================

def load_class_names():
    """
    Loads class names from the class text file.
    Falls back to CLASS_ORDER if the file cannot be read.
    """
    if os.path.exists(CLASS_PATH):
        try:
            with open(CLASS_PATH, "r", encoding="utf-8") as f:
                classes = [line.strip() for line in f.readlines() if line.strip()]

            if len(classes) == 4:
                return classes

        except Exception as e:
            print("[model_utils] Could not read class file:", e)

    return CLASS_ORDER


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Loads and caches the trained TensorFlow/Keras model.

    If loading fails, the actual error is stored so it can
    be displayed instead of silently returning 0% scores.
    """
    if _model_cache["loaded"]:
        return _model_cache["model"]

    path = find_model_path()

    if path is None:
        error = (
            "Trained model file was not found.\n"
            f"Expected location: {MODEL_PATH}"
        )
        print("[model_utils]", error)

        _model_cache["loaded"] = True
        _model_cache["model"] = None
        _model_cache["error"] = error

        return None

    try:
        import tensorflow as tf

        print("[model_utils] TensorFlow version:", tf.__version__)
        print("[model_utils] Loading model:", path)

        model = tf.keras.models.load_model(path, compile=False)

        _model_cache["model"] = model
        _model_cache["path"] = path
        _model_cache["error"] = None

        print("[model_utils] Model loaded successfully.")
        print("[model_utils] Input shape:", model.input_shape)
        print("[model_utils] Output shape:", model.output_shape)

    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        print("[model_utils] ERROR loading model:", error)

        _model_cache["model"] = None
        _model_cache["error"] = error

    finally:
        _model_cache["loaded"] = True

    return _model_cache["model"]


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def _preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """
    Converts uploaded image into the format expected
    by the EfficientNetB0 model.

    IMPORTANT: do NOT divide by 255 here. The trained model
    already rescales and normalizes pixels internally, so it
    expects raw 0-255 values.
    """
    if pil_image is None:
        raise ValueError("No image was provided.")

    # Convert to RGB
    img = pil_image.convert("RGB")

    # Resize
    img = img.resize(IMAGE_SIZE)

    # Convert to NumPy (raw 0-255 values, no manual scaling)
    arr = np.asarray(img, dtype=np.float32)

    # Add batch dimension
    arr = np.expand_dims(arr, axis=0)

    return arr


# ============================================================
# PREDICTION
# ============================================================

def predict(pil_image: Image.Image) -> dict:
    """
    Runs prediction using the trained EfficientNetB0 model.

    Returns:
    {
        "bacterial_leaf_blight": probability,
        "brown_spot": probability,
        "healthy": probability,
        "leaf_blast": probability
    }
    """
    model = load_model()

    # MODEL NOT AVAILABLE
    if model is None:
        error = _model_cache.get("error", "Unknown model loading error.")

        raise RuntimeError(
            "Rice disease model could not be loaded.\n\n"
            f"Expected model:\n{MODEL_PATH}\n\n"
            f"Actual error:\n{error}"
        )

    # PREPROCESS
    x = _preprocess_image(pil_image)

    # PREDICT
    try:
        preds = model.predict(x, verbose=0)

    except Exception as e:
        raise RuntimeError(
            "The model failed while making a prediction.\n\n"
            f"{type(e).__name__}: {e}"
        ) from e

    # CONVERT OUTPUT
    preds = np.asarray(preds, dtype=np.float64)

    if preds.ndim == 2:
        preds = preds[0]

    # CHECK NUMBER OF CLASSES
    if len(preds) != len(CLASS_ORDER):
        raise RuntimeError(
            "Model output does not match the expected "
            "number of classes.\n\n"
            f"Expected classes: {len(CLASS_ORDER)}\n"
            f"Model returned: {len(preds)}"
        )

    # CHECK VALUES
    if not np.all(np.isfinite(preds)):
        raise RuntimeError("The model returned invalid prediction values.")

    # NORMALIZE
    total = preds.sum()

    if total <= 0:
        raise RuntimeError(
            "The model returned prediction values whose total is zero."
        )

    preds = preds / total

    # CREATE SCORE DICTIONARY
    scores = {}

    for class_name, probability in zip(CLASS_ORDER, preds):
        scores[class_name] = float(probability)

    return scores


# ============================================================
# TOP PREDICTION
# ============================================================

def get_top_prediction(scores: dict):
    """
    Returns:
        top class
        confidence score
    """
    if not scores:
        return None, 0.0

    top_id = max(scores, key=scores.get)
    confidence = float(scores[top_id])

    return top_id, confidence


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():
    """Returns information about the trained model."""
    model = load_model()

    if model is None:
        return {
            "loaded": False,
            "model_exists": os.path.exists(MODEL_PATH),
            "class_file_exists": os.path.exists(CLASS_PATH),
            "model_path": MODEL_PATH,
            "classes": load_class_names(),
            "error": _model_cache.get("error"),
        }

    return {
        "loaded": True,
        "model_exists": True,
        "class_file_exists": os.path.exists(CLASS_PATH),
        "model_path": MODEL_PATH,
        "classes": load_class_names(),
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
        "error": None,
    }
