"""
styling.py
-----------
Shared visual language for RiceCare AI: a calm, premium, scientific,
agricultural theme (not a generic neon AI dashboard).

Palette:
  - Deep rice-field green   #1F4A34
  - Warm paddy gold         #C69B3D
  - Soft cream background   #FAF7F0
  - Ink text                #22301F
  - Molecular accent teal   #2B6E6E
"""

import streamlit as st

PRIMARY_GREEN = "#1F4A34"
ACCENT_GOLD = "#C69B3D"
BG_CREAM = "#FAF7F0"
INK = "#22301F"
TEAL = "#2B6E6E"
SOFT_GREEN_BG = "#EEF3EA"


def inject_global_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"]  {{
            font-family: 'Inter', sans-serif;
            color: {INK};
        }}

        .stApp {{
            background: linear-gradient(180deg, {BG_CREAM} 0%, #F4EFE3 100%);
        }}

        h1, h2, h3 {{
            font-family: 'Fraunces', serif;
            color: {PRIMARY_GREEN};
        }}

        /* Hero */
        .rc-hero {{
            text-align: center;
            padding: 3.2rem 1rem 2.2rem 1rem;
            animation: rc-fade-in 900ms ease-out;
        }}
        .rc-hero h1 {{
            font-size: 3rem;
            margin-bottom: 0.2rem;
        }}
        .rc-hero .rc-subtitle {{
            font-size: 1.25rem;
            color: {TEAL};
            font-weight: 600;
            margin-bottom: 0.8rem;
        }}
        .rc-hero .rc-support {{
            max-width: 700px;
            margin: 0 auto;
            color: #4B5744;
            font-size: 1.02rem;
            line-height: 1.55;
        }}

        @keyframes rc-fade-in {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Flow / molecular strip */
        .rc-flow {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.9rem;
            flex-wrap: wrap;
            font-size: 1.6rem;
            margin: 1.4rem 0 2.2rem 0;
            opacity: 0;
            animation: rc-fade-in 1200ms ease-out 200ms forwards;
        }}
        .rc-flow .rc-arrow {{
            color: {ACCENT_GOLD};
            font-size: 1.1rem;
        }}

        /* Cards */
        .rc-card {{
            background: #FFFFFF;
            border: 1px solid #E5DEC9;
            border-radius: 14px;
            padding: 1.3rem 1.2rem;
            box-shadow: 0 2px 10px rgba(31,74,52,0.05);
            transition: transform 220ms ease, box-shadow 220ms ease;
            height: 100%;
        }}
        .rc-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 24px rgba(31,74,52,0.12);
        }}
        .rc-card h4 {{
            font-family: 'Fraunces', serif;
            color: {PRIMARY_GREEN};
            margin-bottom: 0.4rem;
        }}
        .rc-card p {{
            color: #4B5744;
            font-size: 0.93rem;
            line-height: 1.45;
        }}

        /* Badges */
        .rc-badge {{
            display: inline-block;
            background: {SOFT_GREEN_BG};
            color: {PRIMARY_GREEN};
            border-radius: 999px;
            padding: 0.2rem 0.75rem;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 0.4rem;
        }}
        .rc-badge-gold {{
            background: #FBF1DC;
            color: #8A6A16;
        }}
        .rc-badge-teal {{
            background: #E4F1F1;
            color: {TEAL};
        }}

        /* Disclaimer box */
        .rc-disclaimer {{
            background: #FBF6E9;
            border-left: 4px solid {ACCENT_GOLD};
            border-radius: 8px;
            padding: 0.8rem 1rem;
            font-size: 0.85rem;
            color: #5A4E2E;
            margin: 1.2rem 0;
        }}

        /* Result headline */
        .rc-result-headline {{
            background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, #2C6247 100%);
            color: #FAF7F0;
            border-radius: 16px;
            padding: 1.6rem 1.4rem;
            text-align: center;
            margin-bottom: 1.2rem;
            animation: rc-fade-in 500ms ease-out;
        }}
        .rc-result-headline .rc-label {{
            font-size: 0.85rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.85;
        }}
        .rc-result-headline .rc-disease-name {{
            font-family: 'Fraunces', serif;
            font-size: 2rem;
            margin: 0.3rem 0;
        }}

        /* Footer */
        .rc-footer {{
            text-align: center;
            color: #8A8A75;
            font-size: 0.8rem;
            padding: 2rem 0 1rem 0;
        }}

        section[data-testid="stSidebar"] {{
            background: #F4EFE3;
            border-right: 1px solid #E5DEC9;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, support_text: str):
    st.markdown(
        f"""
        <div class="rc-hero">
            <h1>{title}</h1>
            <div class="rc-subtitle">{subtitle}</div>
            <div class="rc-support">{support_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def flow_diagram(steps: list):
    """steps: list of strings like ['🌾 Rice field', '🧬 Molecular', '🤖 AI']"""
    arrow = '<span class="rc-arrow">➜</span>'
    html = arrow.join(f"<span>{s}</span>" for s in steps)
    st.markdown(f'<div class="rc-flow">{html}</div>', unsafe_allow_html=True)


def disclaimer():
    st.markdown(
        """
        <div class="rc-disclaimer">
        ⚠️ <b>Scientific &amp; Safety Disclaimer:</b> AI predictions are based on image patterns
        and should not be considered a definitive diagnosis. Disease information and general
        management guidance should be verified with appropriate agricultural experts and
        locally recommended sources before making treatment decisions. Molecular information
        is provided for research/educational purposes and is <b>not</b> directly detected from
        the uploaded photograph.
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """
        <div class="rc-footer">
        🌾 RiceCare AI — AI-Powered Rice Disease &amp; Molecular Information Analyzer<br/>
        Built for research &amp; educational use · Version 1 (Rice only)
        </div>
        """,
        unsafe_allow_html=True,
    )
