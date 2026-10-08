"""
model_utils.py
----------------
Handles RiceCare AI model loading and prediction.

Uses the trained EfficientNetB0 rice leaf disease model:

models/
    rice_leaf_disease_efficientnetb0.keras
    rice_leaf_disease_classes.txt

Model classes:
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

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "rice_leaf_disease_efficientnetb0.keras"
)

CLASS_PATH = os.path.join(
    MODEL_DIR,
    "rice_leaf_disease_classes.txt"
)


# ============================================================
# MODEL SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)

# IMPORTANT:
# This order MUST match the order used during model training.
CLASS_ORDER = [
    "bacterial_leaf_blight",
    "brown_spot",
    "healthy",
    "leaf_blast"
]


# ============================================================
# MODEL CACHE
# ============================================================

_model_cache = {
    "model": None,
    "loaded": False,
    "path": None
}


# ============================================================
# FIND MODEL
# ============================================================

def find_model_path():
    """
    Returns the path to the trained model if it exists.
    """

    if os.path.exists(MODEL_PATH):
        return MODEL_PATH

    return None


# ============================================================
# DEMO MODE CHECK
# ============================================================

def is_demo_mode() -> bool:
    """
    Returns True only if the trained model is unavailable.
    """

    return find_model_path() is None


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Loads and caches the trained TensorFlow/Keras model.

    Returns:
        Loaded Keras model, or None if loading fails.
    """

    if _model_cache["loaded"]:
        return _model_cache["model"]

    path = find_model_path()

    if path is None:
        print(
            "[model_utils] Trained model not found at:"
            f" {MODEL_PATH}"
        )

        _model_cache["loaded"] = True
        _model_cache["model"] = None

        return None

    try:
        import tensorflow as tf

        print(
            "[model_utils] Loading trained model:"
            f" {path}"
        )

        model = tf.keras.models.load_model(path)

        _model_cache["model"] = model
        _model_cache["path"] = path

        print("[model_utils] Model loaded successfully.")

    except Exception as e:

        print(
            "[model_utils] ERROR loading trained model:"
            f" {e}"
        )

        _model_cache["model"] = None

    finally:
        _model_cache["loaded"] = True

    return _model_cache["model"]


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def _preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """
    Converts uploaded PIL image into the format expected
    by the EfficientNetB0 model.
    """

    # Convert image to RGB
    img = pil_image.convert("RGB")

    # Resize to model input size
    img = img.resize(IMAGE_SIZE)

    # Convert to NumPy array
    arr = np.asarray(
        img,
        dtype=np.float32
    )

    # Normalize pixel values from 0-255 to 0-1
    arr = arr / 255.0

    # Add batch dimension
    arr = np.expand_dims(arr, axis=0)

    return arr


# ============================================================
# PREDICTION
# ============================================================

def predict(pil_image: Image.Image) -> dict:
    """
    Predicts the rice leaf disease.

    Returns:
        Dictionary containing probability for each disease.

    Example:

        {
            "bacterial_leaf_blight": 0.02,
            "brown_spot": 0.10,
            "healthy": 0.85,
            "leaf_blast": 0.03
        }
    """

    model = load_model()

    # --------------------------------------------------------
    # If model is unavailable
    # --------------------------------------------------------

    if model is None:

        print(
            "[model_utils] No trained model available."
        )

        return {
            class_name: 0.0
            for class_name in CLASS_ORDER
        }

    try:

        # ----------------------------------------------------
        # Preprocess image
        # ----------------------------------------------------

        x = _preprocess_image(pil_image)

        # ----------------------------------------------------
        # Model prediction
        # ----------------------------------------------------

        preds = model.predict(
            x,
            verbose=0
        )[0]

        preds = np.asarray(
            preds,
            dtype=np.float64
        )

        # ----------------------------------------------------
        # Make sure output has 4 classes
        # ----------------------------------------------------

        if len(preds) != len(CLASS_ORDER):

            raise ValueError(
                f"Model returned {len(preds)} predictions, "
                f"but {len(CLASS_ORDER)} classes are expected."
            )

        # ----------------------------------------------------
        # Normalize probabilities
        # ----------------------------------------------------

        total = preds.sum()

        if total > 0:
            preds = preds / total

        # ----------------------------------------------------
        # Create result dictionary
        # ----------------------------------------------------

        scores = dict(
            zip(
                CLASS_ORDER,
                preds
            )
        )

        return scores

    except Exception as e:

        print(
            "[model_utils] Prediction failed:"
            f" {e}"
        )

        return {
            class_name: 0.0
            for class_name in CLASS_ORDER
        }


# ============================================================
# TOP PREDICTION
# ============================================================

def get_top_prediction(scores: dict):
    """
    Returns the class with the highest prediction probability.
    """

    top_id = max(
        scores,
        key=scores.get
    )

    confidence = scores[top_id]

    return top_id, confidence


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():
    """
    Returns basic information about the trained model.
    """

    model = load_model()

    if model is None:

        return {
            "loaded": False,
            "model_path": MODEL_PATH,
            "classes": CLASS_ORDER
        }

    return {
        "loaded": True,
        "model_path": MODEL_PATH,
        "classes": CLASS_ORDER,
        "input_shape": model.input_shape,
        "output_shape": model.output_shape
    }
