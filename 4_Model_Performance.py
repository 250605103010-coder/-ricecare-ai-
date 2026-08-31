import streamlit as st
from utils import styling, data_loader, model_utils

st.set_page_config(page_title="Model Performance — RiceCare AI", page_icon="📊", layout="wide")
styling.inject_global_css()

st.markdown("## 📊 AI Model Performance")

if model_utils.is_demo_mode():
    st.info("⚙️ No trained model file found in `/model`. Metrics below reflect `data/model_performance.csv` only.")

if not data_loader.performance_is_evaluated():
    st.warning("📈 Model evaluation will appear here after the test evaluation is completed. "
               "Update `data/model_performance.csv` with real metrics once your Colab-trained "
               "model has been evaluated on a held-out test set.")
else:
    perf = data_loader.load_model_performance()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Test Accuracy", f"{perf.get('test_accuracy','—')}")
    m2.metric("Precision", f"{perf.get('precision','—')}")
    m3.metric("Recall", f"{perf.get('recall','—')}")
    m4.metric("F1 Score", f"{perf.get('f1_score','—')}")

    m5, m6 = st.columns(2)
    m5.metric("Training Accuracy", f"{perf.get('train_accuracy','—')}")
    m6.metric("Validation Accuracy", f"{perf.get('validation_accuracy','—')}")

    st.markdown("**Dataset size**")
    st.write(
        f"Training images: {perf.get('num_training_images','—')} · "
        f"Validation images: {perf.get('num_validation_images','—')} · "
        f"Test images: {perf.get('num_test_images','—')}"
    )

    st.markdown("### Confusion Matrix")
    cm = data_loader.load_confusion_matrix()
    if not cm.empty:
        st.dataframe(cm.set_index(cm.columns[0]), use_container_width=True)

st.markdown("<br/>", unsafe_allow_html=True)
st.caption(
    "To populate this page: train your CNN classifier in Google Colab, evaluate it on a held-out "
    "test set, then fill in `data/model_performance.csv` and `data/confusion_matrix.csv` with the "
    "actual results. Numbers are never invented."
)

styling.disclaimer()
styling.footer()
