import streamlit as st

st.set_page_config(
    page_title="Notre Offre — SENSai",
    page_icon="👁️",
    layout="wide"
)

BLUE = "#1250A6"
GOLD = "#FFD700"  # Jaune or pour la banderole

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
    min-height: 260px;
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
    min-height: 260px;
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
    min-height: 500px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}}

.offer-card:hover {{
    background: rgba(18,80,166,0.13);
    transform: translateY(-6px);
    box-shadow: 0 0 32px rgba(18,80,166,0.42);
}}

/* Banderole jaune "La plus populaire" sur le côté - CORRIGÉE */
.popular-ribbon {{
    position: absolute;
    top: 20px;
    right: -40px;
    background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
    color: #8B4513 !important;
    padding: 10px 50px;
    font-weight: 800;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
    z-index: 10;
    transform: rotate(45deg);
    border: 2px solid rgba(255, 255, 255, 0.3);
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
    animation: ribbonGlow 2s ease-in-out infinite alternate;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 180px;
    text-align: center;
    line-height: 1.2;
}}

/* Version alternative si la première ne marche pas */
.popular-ribbon-fixed {{
    position: absolute;
    top: 25px;
    right: -45px;
    background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
    color: #8B4513 !important;
    padding: 12px 60px;
    font-weight: 800;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
    z-index: 10;
    transform: rotate(45deg);
    border: 2px solid rgba(255, 255, 255, 0.3);
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
    animation: ribbonGlow 2s ease-in-out infinite alternate;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 200px;
    height: 40px;
    text-align: center;
}}

/* Effet de brillance sur la banderole */
@keyframes ribbonGlow {{
    0% {{
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
    }}
    100% {{
        box-shadow: 0 5px 25px rgba(255, 215, 0, 0.7);
        background: linear-gradient(45deg, #FFEE00, #FFB300, #FFEE00);
    }}
}}

/* Effet de texture sur la banderole */
.popular-ribbon:before,
.popular-ribbon-fixed:before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
        transparent 10%, 
        rgba(255, 255, 255, 0.2) 50%, 
        transparent 90%);
    pointer-events: none;
}}

.offer-title {{
    color: {BLUE};
    font-size: 1.45rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 20px;
    margin-top: 15px;
    padding-top: 10px;
}}

/* Liste des fonctionnalités plus propre */
.feature-list {{
    color: #dadada;
    font-size: 0.98rem;
    line-height: 1.5;
    margin-bottom: 30px;
    flex-grow: 1;
}}

.feature-list li {{
    margin-bottom: 12px;
    position: relative;
    padding-left: 24px;
}}

.feature-list li:before {{
    content: "▶";
    color: {BLUE};
    position: absolute;
    left: 0;
    font-size: 0.8rem;
}}

.feature-list strong {{
    color: #ffffff;
    font-weight: 600;
}}

/* Message de contact */
.contact-message {{
    text-align: center;
    color: #a0c8ff;
    font-size: 1.05rem;
    margin-top: 50px;
    margin-bottom: 20px;
    padding: 20px;
    background: rgba(18,80,166,0.1);
    border-radius: 15px;
    border: 1px solid rgba(18,80,166,0.3);
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
    backdrop-filter: blur(10px);
}}

.contact-message strong {{
    color: #ffffff;
    font-weight: 700;
}}

/* =============================== */
/*     BOUTONS NÉON CENTRÉS       */
/* =============================== */
.offer-card .stPageLink,
.offer-card div[data-testid="stPageLink"] {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin-top: 15px;
}}

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
    margin-top: 10px !important;
}}

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

/* Bouton pour l'offre Pro avec effet spécial */
.popular-button a[href*="2_Contact"] {{
    background: linear-gradient(45deg, rgba(18,80,166,0.25), rgba(255,215,0,0.15)) !important;
    border: 2px solid {GOLD} !important;
    box-shadow:
        0 0 12px {GOLD},
        0 0 25px rgba(255,215,0,0.5),
        inset 0 0 10px rgba(255,215,0,0.3) !important;
}}

.popular-button a[href*="2_Contact"]:hover {{
    background: linear-gradient(45deg, rgba(18,80,166,0.35), rgba(255,215,0,0.25)) !important;
    box-shadow:
        0 0 20px {GOLD},
        0 0 40px rgba(255,215,0,0.7),
        inset 0 0 15px rgba(255,215,0,0.5) !important;
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
L'objectif n'est pas de vous noyer sous les statistiques, mais de vous donner des décisions concrètes
pour mieux jouer, match après match.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p class="paragraph">
<b>SENSai observe vos games</b>, reconstruit votre profil de joueur et identifie précisément 
où se situent les pertes de tempo, les erreurs de décision et les mauvaises habitudes qui freinent votre progression.
</p>
<p class="paragraph">
Sur cette base, la plateforme génère des <b>rapports structurés</b> et des <b>axes d'entraînement ciblés</b>,
pensés pour les joueurs sérieux, qu'ils soient en solo queue, en équipe ou intégrés à une structure.
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
        L'IA détecte vos forces, vos faiblesses et vos patterns de décision qui influencent vos performances.
    </div>
    """, unsafe_allow_html=True)

with steps_cols[2]:
    st.markdown("""
    <div class="step-card">
        <div class="step-index">Étape 3</div>
        <div class="step-title">Rapports & plan d'entraînement</div>
        Vous recevez des axes d'amélioration concrets pour vos prochaines sessions.
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
        Tempo, rotations, objectifs, synchronisation avec l'équipe.
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
            <div class="feature-list">
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li><strong>Analyse IA limitée</strong> - 10 analyses par mois</li>
                    <li><strong>Rapports synthétiques</strong> avec les points clés</li>
                    <li><strong>Axes d'amélioration</strong> essentiels identifiés</li>
                    <li><strong>Historique basique</strong> de vos progrès</li>
                    <li>Idéal pour <strong>débuter</strong> votre progression</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.page_link("pages/2_Contact.py", label="Choisir Starter")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PRO (La plus populaire) ----------------
with offer_cols[1]:
    st.markdown("""
    <div class="offer-card">
        <div class="popular-ribbon">La plus populaire</div>
        <div>
            <div class="offer-title">SENSai Pro</div>
            <div class="feature-list">
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li><strong>Analyse illimitée</strong> - toutes vos games</li>
                    <li><strong>Recommandations IA</strong> avancées et détaillées</li>
                    <li><strong>Suivi d'évolution</strong> avec graphiques détaillés</li>
                    <li><strong>Comparaisons</strong> avec votre historique</li>
                    <li>Le meilleur <strong>rapport qualité/prix</strong></li>
                    <li><strong>Support prioritaire</strong> par email</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Utiliser un conteneur avec une classe spéciale pour le bouton de l'offre populaire
    st.markdown('<div class="popular-button">', unsafe_allow_html=True)
    st.page_link("pages/2_Contact.py", label="Choisir Pro")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ELITE ----------------
with offer_cols[2]:
    st.markdown("""
    <div class="offer-card">
        <div>
            <div class="offer-title">SENSai Elite</div>
            <div class="feature-list">
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li><strong>Analyse avancée</strong> + extraction replay</li>
                    <li><strong>Détection de patterns</strong> invisibles à l'œil nu</li>
                    <li><strong>Coaching premium</strong> pour la compétition</li>
                    <li><strong>Rapports d'équipe</strong> pour les scrims</li>
                    <li><strong>Consultation personnalisée</strong> mensuelle</li>
                    <li><strong>API d'intégration</strong> pour les structures</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.page_link("pages/2_Contact.py", label="Choisir Elite")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 5 — MESSAGE DE CONTACT
# =====================================================================
st.markdown("""
<div class="contact-message">
💡 <strong>Une offre vous plaît mais vous souhaitez l'adapter à vos besoins spécifiques ?</strong><br>
Envoyez-nous les détails de votre projet (jeu, niveau, objectifs, taille d'équipe) et nous vous préparerons un <strong>devis personnalisé gratuitement</strong>.
</div>
""", unsafe_allow_html=True)

# Option alternative si la première banderole ne fonctionne pas
st.markdown("""
<style>
/* Option alternative pour la banderole */
@media (min-width: 768px) {{
    .offer-card:nth-child(2) .popular-ribbon {{
        right: -42px !important;
        top: 22px !important;
        padding: 11px 55px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)