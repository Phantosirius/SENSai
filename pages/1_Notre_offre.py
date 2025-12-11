import streamlit as st

st.set_page_config(
    page_title="Notre Offre — SENSai",
    page_icon="👁️",
    layout="wide"
)

BLUE = "#1250A6"

# ------------------------------------------------------
# CSS — futuriste, cohérent avec la home
# ------------------------------------------------------
st.markdown(f"""
<style>

body {{
    background-color: #0D1117 !important;
}}

.section-title {{
    color: {BLUE};
    font-size: 2.3rem;
    text-align: center;
    margin-top: 45px;
    font-weight: 600;
}}

.subtitle {{
    max-width: 900px;
    color: #d3d3d3;
    font-size: 1.08rem;
    margin: 14px auto 30px auto;
    text-align: center;
    line-height: 1.55;
}}

.paragraph {{
    max-width: 980px;
    margin: 0 auto 12px auto;
    color: #e0e0e0;
    font-size: 1.02rem;
    line-height: 1.55;
}}

.paragraph b {{
    color: #ffffff;
}}

.step-card {{
    padding: 22px;
    border-radius: 16px;
    background: rgba(18,80,166,0.07);
    border: 1px solid rgba(18,80,166,0.7);
    height: 100%;
    min-height: 260px;                /* Hauteur uniforme */
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-shadow: 0 0 18px rgba(18,80,166,0.25);
    transition: 0.25s ease-in-out;
}}

.step-card:hover {{
    background: rgba(18,80,166,0.14);
    transform: translateY(-4px);
    box-shadow: 0 0 26px rgba(18,80,166,0.45);
}}

.step-title {{
    color: {BLUE};
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 8px;
}}

.step-index {{
    font-size: 0.9rem;
    color: #9ba3b0;
    margin-bottom: 2px;
}}

.sub-card {{
    padding: 20px;
    border-radius: 14px;
    background: rgba(18,80,166,0.06);
    border: 1px solid {BLUE};
    height: 100%;
    min-height: 260px;               /* Hauteur uniforme */
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    color: #e5e5e5;
    box-shadow: 0 0 12px rgba(18,80,166,0.18);
    transition: 0.25s ease-in-out;
}}

.sub-card:hover {{
    background: rgba(18,80,166,0.13);
    transform: translateY(-3px);
    box-shadow: 0 0 22px rgba(18,80,166,0.35);
}}

.sub-card-title {{
    color: {BLUE};
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 10px;
}}

.separator {{
    width: 70%;
    height: 1px;
    margin: 55px auto 25px auto;
    background: radial-gradient(circle, {BLUE} 0%, transparent 70%);
    opacity: 0.45;
}}

.offer-card {{
    padding: 32px;
    border-radius: 20px;
    border: 2px solid {BLUE};
    background: rgba(18,80,166,0.06);
    box-shadow: 0 0 22px rgba(18,80,166,0.25);
    height: 100%;
    min-height: 480px;

    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.offer-card:hover {{
    background: rgba(18,80,166,0.13);
    transform: translateY(-6px);
    box-shadow: 0 0 32px rgba(18,80,166,0.42);
}}

.offer-title {{
    color: {BLUE};
    font-size: 1.45rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}}

.offer-desc {{
    color: #dadada;
    font-size: 0.98rem;
    margin-bottom: 24px;
    line-height: 1.5;
}}

/* =============================== */
/*     BOUTONS NÉON CENTRÉS       */
/* =============================== */

/* Centrer le conteneur parent du bouton */
.offer-card .stPageLink,
.offer-card div[data-testid="stPageLink"] {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}}

/* Centrer le bouton lui-même */
.offer-card a {{
    margin-left: auto !important;
    margin-right: auto !important;
    width: 80% !important;
    text-align: center !important;
}}

div.stPageLink > a, .stPageLink a {{
    display: block !important;
    background: rgba(18,80,166,0.20) !important;
    color: white !important;
    padding: 14px 28px !important;
    border-radius: 14px !important;
    border: 2px solid {BLUE} !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    box-shadow:
        0 0 8px {BLUE},
        0 0 18px rgba(18,80,166,0.55),
        inset 0 0 8px rgba(18,80,166,0.3) !important;
    transition: 0.25s ease-in-out !important;
    margin-top: 18px !important;
}}

/* Nouveau système Streamlit (>= 1.32) */
a[href*="2_Contact"] {{
    background: rgba(18,80,166,0.20) !important;
    color: white !important;
    padding: 14px 28px !important;
    border-radius: 14px !important;
    border: 2px solid {BLUE} !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    width: 80% !important;
    display: block !important;
    margin-left: auto !important;
    margin-right: auto !important;
    text-align: center !important;
    box-shadow:
        0 0 8px {BLUE},
        0 0 18px rgba(18,80,166,0.55),
        inset 0 0 8px rgba(18,80,166,0.3) !important;
}}

a[href*="2_Contact"]:hover {{
    background: rgba(18,80,166,0.30) !important;
    transform: translateY(-3px) !important;

    box-shadow:
        0 0 14px {BLUE},
        0 0 32px rgba(18,80,166,0.85),
        inset 0 0 12px rgba(18,80,166,0.45) !important;
}}

</style>
""", unsafe_allow_html=True)


# =====================================================================
# 1 — INTRO
# =====================================================================
st.markdown("<h1 class='section-title'>Notre offre SENSai</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
SENSai est un coach e-sport assisté par IA qui transforme vos parties en un plan de progression clair.  
L’objectif n’est pas de vous noyer sous les statistiques, mais de vous donner des décisions concrètes
pour mieux jouer, match après match.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p class="paragraph">
<b>SENSai observe vos games</b>, reconstruit votre profil de joueur et identifie précisément 
où se situent les pertes de tempo, les erreurs de décision et les mauvaises habitudes qui freinent votre progression.
</p>
<p class="paragraph">
Sur cette base, la plateforme génère des <b>rapports structurés</b> et des <b>axes d’entraînement ciblés</b>,
pensés pour les joueurs sérieux, qu’ils soient en solo queue, en équipe ou intégrés à une structure.
</p>
""", unsafe_allow_html=True)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# =====================================================================
# 2 — COMMENT ÇA MARCHE ?
# =====================================================================
st.markdown("<h2 class='section-title'>Comment fonctionne SENSai ?</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

steps_cols = st.columns(3, gap="large")

with steps_cols[0]:
    st.markdown("""
    <div class="step-card">
        <div class="step-index">Étape 1</div>
        <div class="step-title">Connexion & collecte des données</div>
        SENSai analyse votre historique de matchs, scrims et replays pour comprendre votre style.
    </div>
    """, unsafe_allow_html=True)

with steps_cols[1]:
    st.markdown("""
    <div class="step-card">
        <div class="step-index">Étape 2</div>
        <div class="step-title">Analyse IA du gameplay</div>
        L’IA détecte vos forces, vos faiblesses et vos patterns de décision qui influencent vos performances.
    </div>
    """, unsafe_allow_html=True)

with steps_cols[2]:
    st.markdown("""
    <div class="step-card">
        <div class="step-index">Étape 3</div>
        <div class="step-title">Rapports & plan d’entraînement</div>
        Vous recevez des axes d’amélioration concrets pour vos prochaines sessions.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# =====================================================================
# 3 — ANALYSES
# =====================================================================
st.markdown("<h2 class='section-title'>Ce que SENSai analyse pour vous</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

info_cols = st.columns(3, gap="large")

with info_cols[0]:
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">Gameplay micro</div>
        Gestion des trades, mécanique, positionnement, conversion d'avantages.
    </div>
    """, unsafe_allow_html=True)

with info_cols[1]:
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">Vision macro & décisions</div>
        Tempo, rotations, objectifs, synchronisation avec l’équipe.
    </div>
    """, unsafe_allow_html=True)

with info_cols[2]:
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">Profil joueur & progression</div>
        Régularité, tilt, style dominant, évolution des indicateurs.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# =====================================================================
# 4 — OFFRES
# =====================================================================
st.markdown("<h2 class='section-title'>Nos offres SENSai</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

offer_cols = st.columns(3, gap="large")

# ---------------- STARTER ----------------
with offer_cols[0]:
    st.markdown("""
    <div class="offer-card">
        <div>
            <div class="offer-title">SENSai Starter</div>
            <div class="offer-desc">
                • Analyse IA limitée<br>
                • Rapports synthétiques<br>
                • Axes d'amélioration essentiels<br>
                • Idéal pour commencer votre progression
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.page_link("pages/2_Contact.py", label="Choisir Starter")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PRO ----------------
with offer_cols[1]:
    st.markdown("""
    <div class="offer-card">
        <div>
            <div class="offer-title">SENSai Pro</div>
            <div class="offer-desc">
                • Analyse illimitée<br>
                • Recommandations IA avancées<br>
                • Suivi détaillé de votre évolution<br>
                • Le meilleur rapport qualité/prix
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.page_link("pages/2_Contact.py", label="Choisir Pro")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ELITE ----------------
with offer_cols[2]:
    st.markdown("""
    <div class="offer-card">
        <div>
            <div class="offer-title">SENSai Elite</div>
            <div class="offer-desc">
                • Analyse avancée + extraction replay<br>
                • Détection de patterns invisibles<br>
                • Coaching premium pour la compétition<br>
                • Conçu pour les scrims et les équipes
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.page_link("pages/2_Contact.py", label="Choisir Elite")
    st.markdown("</div>", unsafe_allow_html=True)
