import streamlit as st
from utils import styling, data_loader

st.set_page_config(page_title="Explore Rice Diseases — RiceCare AI", page_icon="🔬", layout="wide")
styling.inject_global_css()

st.markdown("## 🔬 Explore Rice Diseases")
st.caption("Browse all conditions currently supported by RiceCare AI Version 1.")

df = data_loader.load_disease_data()

if df.empty:
    st.error("No disease data found. Please check `data/disease_information.csv`.")
else:
    for disease_id in data_loader.DISEASE_CLASSES:
        info = data_loader.get_disease_info(disease_id)
        with st.expander(f"{info['emoji']} {info['disease_name']}", expanded=False):
            if disease_id != "HEALTHY":
                st.markdown(f"**🧫 Caused by:** {info['causal_organism']} ({info['causative_agent']})")
            st.write(info["description"])

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🔎 Common Symptoms**")
                for s in info["symptoms"]:
                    st.markdown(f"- {s}")
            with c2:
                st.markdown("**🌾 General Management**")
                for m in info["management"]:
                    st.markdown(f"- {m}")

            sample_paths = data_loader.get_sample_images(disease_id)
            if sample_paths:
                st.markdown("**Sample Images**")
                cols = st.columns(len(sample_paths))
                for c, path in zip(cols, sample_paths):
                    c.image(path, use_container_width=True)

            proteins = data_loader.get_proteins_for_disease(disease_id)
            if proteins:
                st.markdown(f"**🧬 {len(proteins)} related protein record(s)** — see Molecular Information page.")

styling.disclaimer()
styling.footer()
