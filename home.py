import streamlit as st
from pathlib import Path
import base64

# ------------------------
# CONFIG GLOBALE
# ------------------------
st.set_page_config(
    page_title="SENS•ai",
    page_icon="👁️",
    layout="wide"
)

BLUE = "#1250A6"

# ------------------------
# STYLES CSS — FUTURISTE COMPLET
# ------------------------
st.markdown(f"""
<style>

body {{
    background-color: #0D1117 !important;
    color: #E6E6E6;
    font-family: 'Segoe UI', sans-serif;
}}

/* =============================
   HALO GLOBAL (ambiance IA)
   ============================= */
body::before {{
    content: "";
    position: fixed;
    top: -200px;
    left: 50%;
    transform: translateX(-50%);
    width: 1100px;
    height: 1100px;
    background: radial-gradient(
        circle,
        rgba(18,80,166,0.28),
        rgba(18,80,166,0.05),
        transparent 70%
    );
    filter: blur(80px);
    z-index: -1;
    pointer-events: none;
}}

/* =============================
   LIGNES NÉON HAUT / BAS
   ============================= */
.neon-line {{
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, {BLUE}, transparent);
    box-shadow: 0 0 12px {BLUE}, 0 0 24px {BLUE};
    margin: 40px 0;
}}

/* =============================
   BLOCS AVEC GLOW
   ============================= */
.block {{
    border: 2px solid {BLUE};
    border-radius: 14px;
    padding: 22px;
    background-color: rgba(18, 80, 166, 0.08);
    backdrop-filter: blur(4px);
    transition: 0.25s ease-in-out;
    box-shadow: 0 0 0px {BLUE};
}}
.block:hover {{
    background-color: rgba(18, 80, 166, 0.16);
    transform: translateY(-4px);
    box-shadow: 0 0 18px {BLUE};
}}

.section-title {{
    color: {BLUE};
    font-size: 2rem;
    text-align: center;
    margin-top: 50px;
}}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# LOGO + HALO
# --------------------------------------------------------

st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)

logo_path = Path("images/sensai_logo.png")

def get_base64_image(path: Path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

if logo_path.exists():
    img_base64 = get_base64_image(logo_path)
    st.markdown(
        f"""
        <style>
        .glow-logo {{
            width: 260px;
            filter: drop-shadow(0 0 18px {BLUE})
                    drop-shadow(0 0 28px {BLUE})
                    drop-shadow(0 0 40px {BLUE});
            animation: pulseGlow 3s ease-in-out infinite;
        }}

        @keyframes pulseGlow {{
            0%   {{ filter: drop-shadow(0 0 14px {BLUE}); }}
            50%  {{ filter: drop-shadow(0 0 28px {BLUE}); }}
            100% {{ filter: drop-shadow(0 0 14px {BLUE}); }}
        }}
        </style>

        <div style="display:flex; justify-content:center; margin-top:20px;">
            <img class="glow-logo" src="data:image/png;base64,{img_base64}">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("⚠️ Logo introuvable : place le fichier dans /images/sensai_logo.png")

# ------------------------
# TAGLINE
# ------------------------
st.markdown(
    f"""
    <div style="text-align:center; font-size:22px; color:{BLUE}; margin-top:15px;">
        Le coach e-sport intelligent qui analyse, comprend et améliore votre gameplay.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)


# ------------------------
# SECTION : Pourquoi SENSai ?
# ------------------------
st.markdown("<h2 class='section-title'>Pourquoi SENSai ?</h2>", unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align: center; max-width: 900px; margin: auto; font-size: 1.05rem;'>
SENSai est une plateforme conçue pour les joueurs compétitifs souhaitant progresser 
de manière structurée, objective et efficace.<br><br>
Grâce à son moteur d’analyse IA, SENSai détecte vos patterns, vos erreurs récurrentes,
vos forces et vos faiblesses, et génère des axes d’amélioration cohérents et actionnables.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)

# ------------------------
# SECTION : Ce que SENSai apporte
# ------------------------
st.markdown("<h2 class='section-title'>Ce que SENSai apporte</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    st.markdown(f"""
    <div class="block">
        <h3 style='color:{BLUE};'>Analyse intelligente</h3>
        <p>SENSai examine chaque match, détecte vos erreurs récurrentes
        et révèle des opportunités d'amélioration invisibles en jeu.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="block">
        <h3 style='color:{BLUE};'>Coaching personnalisé</h3>
        <p>Recommandations adaptées à votre rôle, votre style et votre profil.
        Un véritable coach orienté performance.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="block">
        <h3 style='color:{BLUE};'>Suivi de progression</h3>
        <p>Visualisez votre évolution à travers des rapports clairs, 
        des insights IA et des indicateurs précis.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)

# ------------------------
# SECTION CTA
# ------------------------
st.markdown("<h2 class='section-title'>Envie d'aller plus loin ?</h2>", unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align:center; font-size:1.05rem; margin-bottom: 25px;'>
La section <b>Notre Offre</b> présente en détail nos analyses IA, 
les outils d'entraînement et les fonctionnalités avancées de SENSai.
</div>
""", unsafe_allow_html=True)
