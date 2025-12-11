import streamlit as st

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Contact SENSai", layout="wide")

BLUE = "#1250A6"
BG = "#0D1117"

# -------------------------
# GLOBAL CSS FIX (CORRIGE LE DECALAGE)
# -------------------------
st.markdown(f"""
<style>

html, body {{
    background-color: {BG} !important;
}}

.main > div {{
    padding-top: 0 !important;
}}

h2.section-title {{
    color: {BLUE};
    text-shadow: 0 0 14px rgba(18, 80, 166, 0.8);
    letter-spacing: 2px;
    text-align: center;
    margin-bottom: 5px;
}}

.sub-desc {{
    color: #c8d3f5;
    text-shadow: 0 0 6px rgba(18,80,166,0.4);
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 50px;
    max-width: 650px;
    margin-left: auto;
    margin-right: auto;
}}

/* PLUS AUCUN BLOC — FORMULAIRE 100% FLUIDE */
.form-wrapper {{
    width: 650px;
    margin: auto;
}}

/* Champs futuristes simples */
input, textarea, select {{
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(18,80,166,0.35) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px;
    font-size: 1rem;
    box-shadow: 0 0 8px rgba(18,80,166,0.2);
    transition: 0.25s;
}}

input:focus, textarea:focus, select:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 14px {BLUE};
}}

/* Bouton futuriste */
.submit-btn {{
    width: 100%;
    background: rgba(18,80,166,0.25);
    border: 1px solid {BLUE};
    color: white;
    padding: 12px;
    border-radius: 10px;
    font-size: 1.1rem;
    transition: 0.25s;
}}

.submit-btn:hover {{
    background: {BLUE};
    box-shadow: 0 0 18px {BLUE};
}}

</style>
""", unsafe_allow_html=True)


# -------------------------
# TITRE
# -------------------------
st.markdown("<h2 class='section-title'>Contact & Souscription</h2>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='sub-desc'>
    Remplissez ce formulaire pour discuter d’une offre, d’un accompagnement ou d'un projet e-sport.  
    Nous revenons vers vous rapidement.
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# FORMULAIRE — CENTRÉ SANS DÉCALAGE
# -------------------------
st.markdown("<div class='block-center'>", unsafe_allow_html=True)
st.markdown("<div class='form-card'>", unsafe_allow_html=True)

# Champs structurés
col1, col2 = st.columns(2)
with col1:
    nom = st.text_input("Nom complet")
with col2:
    email = st.text_input("Adresse email")

offre = st.selectbox("Offre choisie", ["SENSai Starter", "SENSai Pro", "SENSai Elite"])
message = st.text_area("Votre message", "Décrivez vos besoins ou vos objectifs e-sport.")

# Bouton
submitted = st.button("Envoyer", key="submit_btn")

# Validation
if submitted:
    if nom.strip() == "" or email.strip() == "":
        st.error("Veuillez remplir votre nom et votre adresse email.")
    else:
        st.success("Votre message a été envoyé. L’équipe SENSai vous contactera rapidement.")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
