import streamlit as st
from utils import styling, data_loader

st.set_page_config(page_title="Feedback — RiceCare AI", page_icon="⭐", layout="wide")
styling.inject_global_css()

st.markdown("## ⭐ Help Us Improve RiceCare AI")

with st.form("feedback_form", clear_on_submit=True):
    name = st.text_input("Name (optional)")
    role = st.selectbox("Role", ["Farmer", "Researcher", "Student", "Agronomist", "Other"])
    rating = st.slider("Rating", 1, 5, 5)
    feedback_text = st.text_area("Your feedback")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not feedback_text.strip():
            st.error("Please write some feedback before submitting.")
        else:
            data_loader.submit_feedback(name, role, rating, feedback_text.strip())
            st.success("Thank you! Your feedback has been recorded.")

st.markdown("---")
st.markdown("### What people are saying")

df = data_loader.load_feedback()
if df.empty:
    st.caption("No feedback submitted yet. Be the first!")
else:
    for _, row in df.sort_values("timestamp", ascending=False).iterrows():
        stars = "⭐" * int(row.get("rating", 0))
        st.markdown(
            f"""<div class="rc-card" style="margin-bottom:0.6rem;">
            <p>{stars}<br/><i>"{row.get('feedback','')}"</i><br/>
            <span style="color:#8A8A75; font-size:0.8rem;">
            — {row.get('name','Anonymous')} ({row.get('role','')}), {row.get('timestamp','')}
            </span></p>
            </div>""",
            unsafe_allow_html=True,
        )

styling.footer()
