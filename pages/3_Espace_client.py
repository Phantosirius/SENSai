import os
import re
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

# ==========================================================
# CONFIG PAGE
# ==========================================================
st.set_page_config(
    page_title="SENSAI — Espace client",
    layout="wide",
)

# ==========================================================
# PATHS / DB
# ==========================================================
APP_ROOT = Path(__file__).resolve().parents[1]
os.chdir(APP_ROOT)

DB = APP_ROOT / "data" / st.secrets["APP"]["DB_NAME"]


# ==========================================================
# STYLES MODERNES AVEC EFFETS NÉON SUBTILS
# ==========================================================
PRIMARY = "#1250a6"
ERROR_RED = "#d32f2f"

st.markdown(
    f"""
    <style>
    :root {{
        --sensai-primary: {PRIMARY};
        --sensai-error: {ERROR_RED};
    }}
    
    /* Titre principal avec effet HALO NÉON */
    .sensai-title {{
        color: #ffffff;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        text-shadow: 
            0 0 5px #fff,
            0 0 10px #fff,
            0 0 15px #fff,
            0 0 20px {PRIMARY},
            0 0 35px {PRIMARY},
            0 0 40px {PRIMARY},
            0 0 50px {PRIMARY},
            0 0 75px {PRIMARY};
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }}
    
    /* Badge avec effet néon subtil */
    .sensai-badge {{
        background: rgba(18, 80, 166, 0.1);
        color: {PRIMARY};
        border-radius: 20px;
        padding: 0.4rem 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        border: 1px solid rgba(18, 80, 166, 0.3);
        box-shadow: 0 0 10px rgba(18, 80, 166, 0.2);
    }}
    
    /* Boutons avec bordure néon au survol */
    .stButton>button {{
        background: #ffffff;
        color: {PRIMARY};
        border-radius: 8px;
        border: 2px solid {PRIMARY};
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        box-shadow: 0 0 15px {PRIMARY};
        border-color: {PRIMARY};
    }}
    
    /* Effet spécial pour PrimeOut (NÉON ROUGE) */
    .primeout-container {{
        background: rgba(0, 0, 0, 0.85);
        color: white;
        text-align: center;
        padding: 3rem 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px solid #ff0000;
        box-shadow: 
            0 0 20px #ff0000,
            inset 0 0 20px rgba(255, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .primeout-container::before {{
        content: '';
        position: absolute;
        top: -10px;
        left: -10px;
        right: -10px;
        bottom: -10px;
        background: linear-gradient(45deg, 
            transparent 20%, 
            rgba(255, 0, 0, 0.1) 40%, 
            rgba(255, 0, 0, 0.2) 60%, 
            rgba(255, 0, 0, 0.1) 80%, 
            transparent 100%);
        z-index: -1;
        animation: scan 3s linear infinite;
    }}
    
    @keyframes scan {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    
    .primeout-title {{
        color: #ff0000;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 
            0 0 5px #ff0000,
            0 0 10px #ff0000,
            0 0 15px #ff0000,
            0 0 20px #ff0000,
            0 0 30px #ff0000;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        animation: pulse 1.5s infinite alternate;
    }}
    
    @keyframes pulse {{
        from {{ text-shadow: 0 0 5px #ff0000, 0 0 10px #ff0000, 0 0 15px #ff0000; }}
        to {{ text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000, 0 0 30px #ff0000, 0 0 40px #ff0000; }}
    }}
    
    .primeout-subtitle {{
        color: #ff6666;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(255, 102, 102, 0.5);
    }}
    
    .primeout-message {{
        background: rgba(0, 0, 0, 0.5);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 3px solid #ff0000;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: left;
    }}
    
    /* Panels avec effet futuriste */
    .sensai-panel {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }}
    
    /* Pour les titres de section */
    .section-title {{
        color: #ffffff;
        font-weight: 700;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(18, 80, 166, 0.5);
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
    }}
    
    /* Pour les onglets */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: rgba(0, 0, 0, 0.2);
        padding: 4px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: #cccccc;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: rgba(18, 80, 166, 0.2);
        color: #ffffff;
        box-shadow: 0 0 10px rgba(18, 80, 166, 0.3);
    }}
    
    /* Background futuriste */
    .stApp {{
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }}
    
    /* Input fields */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    .stTextInput>div>div>input:focus {{
        border-color: {PRIMARY};
        box-shadow: 0 0 10px rgba(18, 80, 166, 0.3);
    }}
    
    /* Dataframes */
    .stDataFrame {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Metrics */
    .stMetric {{
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid {PRIMARY};
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }}
    
    /* Séparateurs avec effet néon */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(18, 80, 166, 0.5), 
            rgba(18, 80, 166, 0.8), 
            rgba(18, 80, 166, 0.5), 
            transparent);
        margin: 2rem 0;
        box-shadow: 0 0 5px rgba(18, 80, 166, 0.3);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# DB HELPER : LECTURE AVEC SCOPE
# ==========================================================
def run_select(sql: str, scope: str | None) -> pd.DataFrame:
    """
    Lecture seule sur la base SQLite, avec restriction LEC si scope == 'LEC'.
    """
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Lecture seule : entre un SELECT.")

    with sqlite3.connect(DB, check_same_thread=False) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")

        # ----- SCOPE LEC -----
        if scope == "LEC":
            conn.executescript(
                """
                DROP VIEW IF EXISTS scope_equipe;
                DROP VIEW IF EXISTS scope_joueur;
                DROP VIEW IF EXISTS scope_affectation_joueur_equipe;
                DROP VIEW IF EXISTS scope_match_game;
                DROP VIEW IF EXISTS scope_stat_joueur;

                CREATE TEMP VIEW scope_equipe AS
                  SELECT e.* FROM equipe e
                  JOIN participation_equipe_ligue pel ON pel.equipe_id = e.equipe_id
                  JOIN ligue l ON l.ligue_id = pel.ligue_id
                  WHERE l.nom = 'LEC';

                CREATE TEMP VIEW scope_joueur AS
                  SELECT j.*
                  FROM joueur j
                  JOIN affectation_joueur_equipe a
                    ON a.joueur_id = j.joueur_id
                   AND a.date_fin IS NULL
                  JOIN scope_equipe se ON se.equipe_id = a.equipe_id;

                CREATE TEMP VIEW scope_affectation_joueur_equipe AS
                  SELECT a.*
                  FROM affectation_joueur_equipe a
                  JOIN scope_equipe se ON se.equipe_id = a.equipe_id;

                CREATE TEMP VIEW scope_match_game AS
                  SELECT m.*
                  FROM match_game m
                  JOIN ligue l ON l.ligue_id = m.ligue_id
                  WHERE l.nom = 'LEC';

                CREATE TEMP VIEW scope_stat_joueur AS
                  SELECT s.*
                  FROM stat_joueur s
                  JOIN scope_match_game m ON m.match_id = s.match_id;
                """
            )

            # Réécriture : tables globales → vues scope_*
            repl = {
                r"\bjoueur\b": "scope_joueur",
                r"\bequipe\b": "scope_equipe",
                r"\baffectation_joueur_equipe\b": "scope_affectation_joueur_equipe",
                r"\bmatch_game\b": "scope_match_game",
                r"\bstat_joueur\b": "scope_stat_joueur",
            }
            for pat, rep in repl.items():
                sql = re.sub(pat, rep, sql, flags=re.IGNORECASE)

        # Sécurisation pour le rôle COACH LEC : staff / contrats / IA interdits
        forbidden = {
            "contrat",
            "staff",
            "staff_affectation",
            "recommandation",
            "interaction_reco",
            "coach_ia",
        }
        if scope == "LEC":
            low = sql.lower()
            touched = {t for t in forbidden if re.search(rf"\b{t}\b", low)}
            if touched:
                raise ValueError("Accès restreint à ces tables pour ce rôle.")

        return pd.read_sql_query(sql, conn)


# ==========================================================
# AUTH / GATE AVEC EASTER EGG PRIMEOUT
# ==========================================================
st.markdown('<h1 class="sensai-title">SENSAI — ESPACE CLIENT</h1>', unsafe_allow_html=True)
st.caption(f"Base de données : {DB.name}")

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None
    st.session_state.scope = None

pwd = st.text_input("Code d'accès sécurisé", type="password")

if st.button("CONNEXION", use_container_width=True):
    P = st.secrets["APP"]
    
     # EASTER EGG PRIMEOUT - ÉVÉNEMENT SPÉCIAL
    if pwd == P["PASS_PRIMEOUT"]:
        st.session_state.auth = False
        st.session_state.role = "PRIMEOUT"
        st.session_state.scope = None

        # Construction du message en plusieurs parties
        message_html = '''
        <div class="primeout-container">
            <div class="primeout-title">PRIME OUT</div>
            <div class="primeout-subtitle">ACCÈS DÉFINITIVEMENT REJETÉ</div>
        '''
        
        # Partie 1 : Titre de la déclaration
        message_html += '<strong>DÉCLARATION OFFICIELLE SENSAI TECHNOLOGIES :</strong><br><br>'
        
        # Partie 2 : Texte principal
        message_html += 'Suite aux événements récents concernant PrimeOut et ses actions controversées '
        message_html += 'vis-à-vis de la Karmine Corp, l\'accès à nos systèmes lui est définitivement refusé.<br><br>'
        
        # Partie 3 : Liste
        message_html += '• Données sensibles de la KC protégées<br>'
        message_html += '• Intégrité de l\'écosystème esport préservée<br>'
        message_html += '• Confiance avec nos partenaires maintenue<br><br>'
        
        # Partie 4 : Citation
        message_html += '<em>"Le respect des valeurs esportives prime sur tout."</em><br>'
        message_html += '— Direction SensAI Technologies'
        
        # Fermeture du message
        message_html += '''            
            <div style="margin-top: 2rem; font-size: 1.2rem; color: #ff6666; font-weight: bold;">
                STATUT : BANNI PERMANENT • CODE : PRIMEOUT-2025-BAN
            </div>
        </div>
        '''
        
        st.markdown(message_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Note interne (également en construction séparée)
        note_html = '<div style="text-align: center; color: #999; font-style: italic; padding: 1rem;">'
        note_html += 'Note interne : Ce code est réservé à des fins démonstratives uniquement.<br>'
        note_html += 'La Karmine Corp et SensAI Technologies restent unis contre toute tentative de déstabilisation.'
        note_html += '</div>'
        
        st.markdown(note_html, unsafe_allow_html=True)
        
        st.stop()

    elif pwd == P["PASS_ADMIN"]:
        st.session_state.auth = True
        st.session_state.role = "ADMIN"
        st.session_state.scope = None
        st.success("ACCÈS ADMINISTRATEUR ACCORDÉ - Privilèges complets activés")

    elif pwd == P["PASS_LEC"]:
        st.session_state.auth = True
        st.session_state.role = "COACH_LEC"
        st.session_state.scope = "LEC"
        st.success("ACCÈS COACH LEC ACCORDÉ - Scope limité à la ligue LEC")
        
    else:
        st.session_state.auth = False
        st.session_state.role = None
        st.session_state.scope = None
        st.error("CODE INVALIDE - Veuillez vérifier vos identifiants")

if not st.session_state.auth:
    st.stop()


# ==========================================================
# CONTENT — ADMIN vs COACH LEC
# ==========================================================

role = st.session_state.role
scope = st.session_state.scope

st.markdown(f'<div class="sensai-badge">Rôle actif : {role}</div>', unsafe_allow_html=True)
st.write("")

# ----------------------------------------------------------
# ONGLETS ADMIN
# ----------------------------------------------------------
if role == "ADMIN":
    tab_dashboard, tab_players, tab_staff, tab_ia, tab_sql, tab_cdc = st.tabs(
        [
            "DASHBOARD",
            "JOUEURS & ÉQUIPES",
            "STAFF & CONTRATS",
            "IA & RECOMMANDATIONS",
            "SQL LIBRE",
            "CAHIER DES CHARGES",
        ]
    )

    # ====================== TAB 1 : DASHBOARD ======================
    with tab_dashboard:
        st.markdown('<div class="section-title">VUE SYNTHÉTIQUE DU SYSTÈME</div>', unsafe_allow_html=True)
        
        colA, colB, colC, colD = st.columns(4)
        try:
            n_joueurs = run_select("SELECT COUNT(*) AS n FROM joueur;", scope).iloc[0, 0]
            n_equipes = run_select("SELECT COUNT(*) AS n FROM equipe;", scope).iloc[0, 0]
            n_matchs = run_select("SELECT COUNT(*) AS n FROM match_game;", scope).iloc[0, 0]
            n_staff = run_select("SELECT COUNT(*) AS n FROM staff;", scope).iloc[0, 0]
        except Exception:
            n_joueurs = n_equipes = n_matchs = n_staff = "N/A"

        colA.metric("Joueurs Actifs", n_joueurs)
        colB.metric("Équipes", n_equipes)
        colC.metric("Matchs Joués", n_matchs)
        colD.metric("Membres Staff", n_staff)

        st.markdown('<div class="section-title">VUES ANALYTIQUES PRÉ-CONFIGURÉES</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Effectif Actuel par Équipe**")
            q = """
            SELECT
              e.code AS equipe,
              j.pseudo,
              j.role,
              j.nationalite
            FROM affectation_joueur_equipe a
            JOIN joueur j ON j.joueur_id = a.joueur_id
            JOIN equipe e ON e.equipe_id = a.equipe_id
            WHERE a.date_fin IS NULL
            ORDER BY e.code, j.role;
            """
            try:
                df = run_select(q, scope)
                st.dataframe(df, use_container_width=True, height=250)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")

        with c2:
            st.markdown("**Répartition des Joueurs par Ligue**")
            q = """
            SELECT
              l.nom AS ligue,
              COUNT(DISTINCT j.joueur_id) AS nb_joueurs,
              COUNT(DISTINCT e.equipe_id) AS nb_equipes
            FROM joueur j
            JOIN affectation_joueur_equipe a ON a.joueur_id = j.joueur_id
            JOIN equipe e ON e.equipe_id = a.equipe_id
            JOIN participation_equipe_ligue pel ON pel.equipe_id = e.equipe_id
            JOIN ligue l ON l.ligue_id = pel.ligue_id
            WHERE a.date_fin IS NULL
            GROUP BY l.nom
            ORDER BY nb_joueurs DESC;
            """
            try:
                df = run_select(q, scope)
                st.dataframe(df, use_container_width=True, height=250)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")

    # ================= TAB 2 : JOUEURS / ÉQUIPES / MATCHS =================
    with tab_players:
        st.markdown('<div class="section-title">GESTION DES JOUEURS & PERFORMANCES</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("FICHES JOUEURS DÉTAILLÉES", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  j.joueur_id,
                  j.pseudo,
                  j.nom,
                  j.prenom,
                  j.nationalite,
                  j.date_naissance,
                  j.role,
                  e.code AS equipe_actuelle
                FROM joueur j
                LEFT JOIN affectation_joueur_equipe a ON a.joueur_id = j.joueur_id AND a.date_fin IS NULL
                LEFT JOIN equipe e ON e.equipe_id = a.equipe_id
                ORDER BY j.role, j.pseudo;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            if st.button("EFFECTIF PAR ÉQUIPE & LIGUE", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  l.nom AS ligue,
                  e.code AS equipe,
                  j.pseudo,
                  j.role,
                  j.nationalite
                FROM affectation_joueur_equipe a
                JOIN joueur j ON j.joueur_id = a.joueur_id
                JOIN equipe e ON e.equipe_id = a.equipe_id
                JOIN participation_equipe_ligue pel ON pel.equipe_id = e.equipe_id
                JOIN ligue l ON l.ligue_id = pel.ligue_id
                WHERE a.date_fin IS NULL
                ORDER BY l.nom, e.code, j.role;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">ANALYSE DES MATCHS & STATISTIQUES</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)

        with c3:
            if st.button("HISTORIQUE DES MATCHS", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  m.match_id,
                  m.date_match,
                  l.nom AS ligue,
                  eb.code AS equipe_bleue,
                  er.code AS equipe_rouge,
                  ev.code AS vainqueur,
                  CASE WHEN m.vainqueur_equipe_id IS NOT NULL THEN 'TERMINÉ' ELSE 'EN COURS' END AS statut
                FROM match_game m
                JOIN ligue l ON l.ligue_id = m.ligue_id
                JOIN equipe eb ON eb.equipe_id = m.equipe_bleue_id
                JOIN equipe er ON er.equipe_id = m.equipe_rouge_id
                LEFT JOIN equipe ev ON ev.equipe_id = m.vainqueur_equipe_id
                ORDER BY m.date_match DESC, m.match_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            if st.button("STATS CUMULÉES PAR JOUEUR", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  j.pseudo,
                  j.role,
                  e.code AS equipe,
                  COUNT(s.match_id) AS nb_matchs,
                  SUM(s.kills) AS total_kills,
                  SUM(s.deaths) AS total_deaths,
                  SUM(s.assists) AS total_assists,
                  ROUND((SUM(s.kills) + SUM(s.assists)) / NULLIF(SUM(s.deaths), 0), 2) AS kda_ratio
                FROM stat_joueur s
                JOIN joueur j ON j.joueur_id = s.joueur_id
                JOIN equipe e ON e.equipe_id = s.equipe_id_du_jour
                GROUP BY j.joueur_id, e.code
                ORDER BY kda_ratio DESC;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

    # ================= TAB 3 : STAFF & CONTRATS =================
    with tab_staff:
        st.markdown('<div class="section-title">GESTION ADMINISTRATIVE & FINANCIÈRE</div>', unsafe_allow_html=True)

        colS1, colS2 = st.columns(2)

        with colS1:
            if st.button("STAFF PAR ÉQUIPE", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  e.code AS equipe,
                  s.nom AS nom_staff,
                  s.prenom,
                  sa.role,
                  sa.date_debut,
                  sa.date_fin,
                  CASE WHEN sa.date_fin IS NULL THEN 'ACTIF' ELSE 'INACTIF' END AS statut
                FROM staff_affectation sa
                JOIN staff s ON s.staff_id = sa.staff_id
                JOIN equipe e ON e.equipe_id = sa.equipe_id
                ORDER BY e.code, sa.role, s.nom;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        with colS2:
            if st.button("CONTRATS JOUEURS", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  e.code AS equipe,
                  j.pseudo,
                  c.date_debut,
                  c.date_fin,
                  c.salaire_mensuel,
                  c.statut,
                  CASE WHEN date(c.date_fin) < date('now') THEN 'EXPIRÉ'
                       WHEN date(c.date_fin) < date('now', '+90 days') THEN 'RENOUVELLEMENT'
                       ELSE 'VALIDE' END AS alerte
                FROM contrat c
                JOIN equipe e ON e.equipe_id = c.equipe_id
                JOIN joueur j ON j.joueur_id = c.joueur_id
                ORDER BY e.code, c.salaire_mensuel DESC;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">ANALYSE FINANCIÈRE</div>', unsafe_allow_html=True)
        q = """
        SELECT
          e.code AS equipe,
          COUNT(DISTINCT c.contrat_id) AS nb_contrats,
          SUM(c.salaire_mensuel) AS masse_salariale_mensuelle,
          SUM(c.salaire_mensuel) * 12 AS masse_salariale_annuelle
        FROM contrat c
        JOIN equipe e ON e.equipe_id = c.equipe_id
        WHERE c.statut = 'ACTIF'
        GROUP BY e.code
        ORDER BY SUM(c.salaire_mensuel) DESC;
        """
        try:
            df = run_select(q, scope)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    # ================= TAB 4 : IA & RECOMMANDATIONS =================
    with tab_ia:
        st.markdown('<div class="section-title">INTELLIGENCE ARTIFICIELLE & COACHING</div>', unsafe_allow_html=True)

        colIA1, colIA2 = st.columns(2)

        with colIA1:
            if st.button("MODÈLES IA DISPONIBLES", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  coach_ia_id,
                  nom_modele,
                  version,
                  domaine,
                  statut,
                  created_at
                FROM coach_ia
                ORDER BY coach_ia_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        with colIA2:
            if st.button("RECOMMANDATIONS PAR MATCH", use_container_width=True):
                st.markdown('<div class="sensai-panel">', unsafe_allow_html=True)
                q = """
                SELECT
                  r.recommandation_id,
                  m.date_match,
                  e.code AS equipe,
                  j.pseudo AS joueur_cible,
                  r.type,
                  SUBSTR(r.resume, 1, 50) AS resume_court,
                  r.statut
                FROM recommandation r
                JOIN match_game m ON m.match_id = r.match_id
                JOIN equipe e ON e.equipe_id = r.equipe_id
                LEFT JOIN joueur j ON j.joueur_id = r.joueur_id
                ORDER BY m.date_match DESC, r.recommandation_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">INTERACTIONS STAFF / RECOMMANDATIONS</div>', unsafe_allow_html=True)
        q = """
        SELECT
          r.recommandation_id,
          s.nom || ' ' || s.prenom AS staff,
          i.action,
          SUBSTR(i.commentaire, 1, 80) AS commentaire_court,
          i.created_at
        FROM interaction_reco i
        JOIN recommandation r ON r.recommandation_id = i.recommandation_id
        JOIN staff s ON s.staff_id = i.staff_id
        ORDER BY i.created_at DESC
        LIMIT 20;
        """
        try:
            df = run_select(q, scope)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    # ================= TAB 5 : SQL LIBRE =================
    with tab_sql:
        st.markdown('<div class="section-title">INTERFACE SQL AVANCÉE</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sensai-panel">
        <p><strong>ATTENTION :</strong> Cette interface permet l'exécution de requêtes SQL en lecture seule.</p>
        <p>Les opérations de modification (INSERT, UPDATE, DELETE) sont désactivées pour des raisons de sécurité.</p>
        </div>
        """, unsafe_allow_html=True)
        
        default_sql = """-- Exemple : Liste des joueurs avec leur KDA (supprimer cette ligne avant de lancer la requête)
SELECT 
  j.pseudo,
  j.role,
  COUNT(s.match_id) AS nb_matchs,
  SUM(s.kills) AS total_kills,
  SUM(s.deaths) AS total_deaths,
  SUM(s.assists) AS total_assists,
  ROUND((SUM(s.kills) + SUM(s.assists)) / NULLIF(SUM(s.deaths), 0), 2) AS kda_ratio
FROM joueur j
LEFT JOIN stat_joueur s ON s.joueur_id = j.joueur_id
GROUP BY j.joueur_id
ORDER BY kda_ratio DESC
LIMIT 10;"""
        
        user_sql = st.text_area("ÉCRIVEZ VOTRE REQUÊTE SQL CI-DESSOUS :", default_sql, height=200)
        
        col_exec, col_clear = st.columns([3, 1])
        
        with col_exec:
            if st.button("EXÉCUTER LA REQUÊTE", use_container_width=True):
                try:
                    df = run_select(user_sql, scope)
                    if df.empty:
                        st.info("Requête exécutée avec succès, mais aucun résultat retourné.")
                    else:
                        st.success(f"Requête exécutée avec succès - {len(df)} lignes retournées")
                        st.dataframe(df, use_container_width=True)
                        
                        col_stats1, col_stats2, col_stats3 = st.columns(3)
                        with col_stats1:
                            st.metric("Lignes", len(df))
                        with col_stats2:
                            st.metric("Colonnes", len(df.columns))
                        with col_stats3:
                            st.metric("Taille", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                        
                except Exception as e:
                    st.error(f"ERREUR SQL : {str(e)}")
        
        with col_clear:
            if st.button("EFFACER", use_container_width=True):
                st.rerun()

    # ================= TAB 6 : CAHIER DES CHARGES =================
    # NE PAS MODIFIER - GARDER TEL QUEL
    with tab_cdc:
        st.markdown("""
        <div class="sensai-panel" style="border-left: 4px solid #1250a6;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="color: #1250a6; margin: 0; font-weight: 800;">CAHIER DES CHARGES</h2>
                    <h3 style="color: #333; margin: 5px 0 0 0; font-weight: 600;">SENSAI TECHNOLOGIES</h3>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 2px 0; color: #666; font-size: 0.9em;"><strong>Version :</strong> 3.0 | 2026</p>
                    <p style="margin: 2px 0; color: #666; font-size: 0.9em;"><strong>Client :</strong> KARMINE CORP</p>
                    <p style="margin: 2px 0; color: #666; font-size: 0.9em;"><strong>Statut :</strong> APPROUVÉ</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. CONTEXTE ET BESOIN CLIENT
        with st.expander("1. CONTEXTE ET BESOIN CLIENT", expanded=True):
            col_ctx1, col_ctx2 = st.columns(2)
            
            with col_ctx1:
                st.markdown("""
                #### Présentation du Client
                
                **KARMINE CORP** - Organisation esport leader en Europe
                - 3 équipes compétitives (LEC, LFL, Div2)
                - 15 joueurs professionnels sous contrat
                - 7 membres de staff technique
                - Budget annuel > 5M€
                
                **Problématiques identifiées :**
                1. Données fragmentées entre plusieurs outils
                2. Analyse manuelle chronophage post-match
                3. Difficulté à capitaliser sur l'historique
                4. Absence d'outil dédié au coaching IA
                5. Gestion contractuelle non centralisée
                """)
            
            with col_ctx2:
                st.markdown("""
                #### Objectifs Stratégiques
                
                | Objectif | Métrique | Échéance |
                |----------|----------|----------|
                | Centralisation données | 100% des données 2025 | Mars 2026 |
                | Automatisation analyse | Réduction 70% temps manuel | Juin 2026 |
                | ROI coaching IA | 15% amélioration perf. | Sept 2026 |
                | Scalabilité plateforme | Support 3 orgs additionnelles | Déc 2026 |
                
                **Budget alloué :** 3M€
                **Durée projet :** 12 mois (Jan-Déc 2026)
                """)
        
        # 2. MODÉLISATION CONCEPTUELLE
        with st.expander("2. MODÉLISATION CONCEPTUELLE (MCD)", expanded=False):
            st.markdown("""
            #### Entités et Attributs Identifiés
            
            **14 Entités Métier Structurées :**
            """)
            
            entities_data = {
                "Entité": ["LIGUE", "SAISON", "EQUIPE", "JOUEUR", "STAFF", "MATCH_GAME", "STAT_JOUEUR", 
                          "CONTRAT", "AFFECTATION_JOUEUR_EQUIPE", "STAFF_AFFECTATION", 
                          "PARTICIPATION_EQUIPE_LIGUE", "COACH_IA", "RECOMMANDATION", "INTERACTION_RECO"],
                "Attributs Clés": [
                    "ligue_id PK, nom UK, niveau",
                    "saison_id PK, nom, date_debut, date_fin",
                    "equipe_id PK, nom UK, code UK",
                    "joueur_id PK, nom, prenom, nationalite, date_naissance, role CHECK, pseudo, riot_puuid UK",
                    "staff_id PK, nom, prenom, email UK",
                    "match_id PK, date_match, type_match CHECK, vainqueur_equipe_id FK",
                    "kills, deaths, assists, (match_id+joueur_id PK composite)",
                    "contrat_id PK, date_debut, date_fin, salaire_mensuel, statut CHECK",
                    "date_debut, date_fin, statut CHECK, type_mouvement CHECK, (joueur_id+equipe_id+date_debut PK)",
                    "date_debut, date_fin, role CHECK, staff_affectation_id PK",
                    "(equipe_id+saison_id PK composite), ligue_id FK",
                    "coach_ia_id PK, nom_modele, version, domaine, statut CHECK, created_at DEFAULT",
                    "recommandation_id PK, type CHECK, resume, details, statut CHECK, created_at DEFAULT",
                    "interaction_id PK, action CHECK, commentaire, created_at DEFAULT"
                ]
            }
            
            st.dataframe(pd.DataFrame(entities_data), use_container_width=True)
            
            st.markdown("""
            #### Contraintes Métier Critiques
            
            ```sql
            -- Contrainte XOR pour CONTRAT
            CHECK ((joueur_id IS NOT NULL AND staff_id IS NULL)
                OR (joueur_id IS NULL AND staff_id IS NOT NULL))
            
            -- Équipes distinctes dans un match
            CHECK (equipe_bleue_id <> equipe_rouge_id)
            
            -- Vainqueur parmi les participants
            CHECK (vainqueur_equipe_id IS NULL 
                OR vainqueur_equipe_id IN (equipe_bleue_id, equipe_rouge_id))
            
            -- Rôles joueurs validés
            role TEXT NOT NULL CHECK (role IN ('TOP','JUNGLE','MID','ADC','SUPPORT'))
            ```
            """)
        
        # 3. MODÈLE LOGIQUE DE DONNÉES
        with st.expander("3. MODÈLE LOGIQUE DE DONNÉES (MLD)", expanded=False):
            tab_mld1, tab_mld2 = st.tabs(["Tables Principales", "Documentation Technique"])
            
            with tab_mld1:
                st.markdown("""
                #### Tables de Référentiels
                
                **LIGUE** *(ligue_id PK, nom UK, niveau)*  
                **SAISON** *(saison_id PK, nom, date_debut, date_fin)*  
                **EQUIPE** *(equipe_id PK, nom UK, code UK)*  
                **JOUEUR** *(joueur_id PK, nom, prenom, nationalite, date_naissance, role CHECK, pseudo)*  
                **STAFF** *(staff_id PK, nom, prenom, email UK)*  
                **COACH_IA** *(coach_ia_id PK, nom_modele, version, domaine, statut CHECK)*
                """)
            
            with tab_mld2:
                st.markdown("""
                #### Architecture Data
                
                **Normalisation Appliquée (3FN) :**
                - Élimination complète des dépendances transitives
                - Décomposition des attributs multi-valués
                - Préservation des dépendances fonctionnelles
                - Préservation des jointures sans perte de données
                
                **Contraintes d'Intégrité Avancées :**
                - FK composites pour relations ternaires
                - Contraintes CHECK métier intégrées
                - Unicité conditionnelle (manager unique par joueur)
                - Cohérence temporelle (dates début ≤ fin)
                """)
        
        # 4. IMPLÉMENTATION SQL
        with st.expander("4. IMPLÉMENTATION SQL ET MANIPULATION", expanded=False):
            st.markdown("""
            #### Requêtes Répondant aux Besoins Métier
            
            **Masse salariale par équipe :**
            ```sql
            SELECT e.code AS equipe, 
                   SUM(c.salaire_mensuel) AS masse_salariale,
                   COUNT(*) AS nb_contrats
            FROM contrat c
            JOIN equipe e ON e.equipe_id = c.equipe_id
            WHERE c.statut = 'ACTIF'
            GROUP BY e.code
            ORDER BY masse_salariale DESC;
            ```
            
            **Performance moyenne par joueur (KDA) :**
            ```sql
            SELECT j.pseudo, 
                   j.role,
                   AVG(s.kills) AS avg_kills,
                   AVG(s.deaths) AS avg_deaths,
                   AVG(s.assists) AS avg_assists,
                   ROUND((SUM(s.kills) + SUM(s.assists)) / NULLIF(SUM(s.deaths), 0), 2) AS kda_ratio
            FROM stat_joueur s
            JOIN joueur j ON j.joueur_id = s.joueur_id
            GROUP BY j.joueur_id
            ORDER BY kda_ratio DESC;
            ```
            """)
        
        # 5. ARCHITECTURE TECHNIQUE
        with st.expander("5. ARCHITECTURE TECHNIQUE", expanded=False):
            col_tech1, col_tech2 = st.columns(2)
            
            with col_tech1:
                st.markdown("""
                #### Stack Technologique
                
                **Backend & Data :**
                - Python 3.11+
                - SQLite/PostgreSQL
                - SQLAlchemy ORM
                - Pandas / NumPy
                
                **Frontend & UI :**
                - Streamlit
                - Plotly/D3.js
                - CSS3 Custom
                - Responsive Design
                """)
            
            with col_tech2:
                st.markdown("""
                #### Infrastructure
                
                **Sécurité :**
                - Authentification multi-rôles
                - RBAC granulaire
                - Chiffrement bcrypt
                - Audit logs complets
                
                **Performance :**
                - RTO : 1 heure
                - RPO : 24 heures
                - SLA : 99.9%
                - Latence API : < 100ms
                """)
        
        # 6. PROFESSIONNALISME
        with st.expander("6. PROFESSIONNALISME ET LIVRABLE", expanded=False):
            col_pro1, col_pro2 = st.columns(2)
            
            with col_pro1:
                st.markdown("""
                #### Équipe de Développement
                
                **Chef de projet :** KEHAL CHAHINEZ & NOUIOURA NAJOUA
                - Gestion de projet
                - Coordination technique
                - Relation client
                - Documentation
                
                **Date de création :** Octobre 2025
                **Date de livraison :** Décembre 2025
                **Environnement :** Académique - Projet final
                """)
            
            with col_pro2:
                st.markdown("""
                #### Identité Professionnelle
                
                **Nom de l'ESN :** SENSAI TECHNOLOGIES
                **Secteur :** Intelligence Artificielle pour l'Esport
                **Couleur corporative :** #1250A6 (Bleu SensAI)
                
                **Contacts :**
                - Email : sensai.labsense@gmail.com
                - Site : https://sensaicoachingesport.streamlit.app
                """)
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; color: #666; font-size: 0.9em; padding: 1rem;">
            <strong>SENSAI TECHNOLOGIES</strong> - Projet académique - Promotion 2025<br>
            Développé par NOUIOURA NAJOUA & KEHAL CHAHINEZ<br>
            Document confidentiel - Tous droits réservés © 2025
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------
# ONGLETS COACH LEC (scope limité)
# ----------------------------------------------------------
elif role == "COACH_LEC":
    tab_lec_dashboard, tab_lec_players, tab_lec_sql = st.tabs(
        [
            "VUE LEC",
            "JOUEURS & MATCHS LEC",
            "SQL LEC",
        ]
    )

    with tab_lec_dashboard:
        st.markdown('<div class="section-title">SYNTHÈSE LEC</div>', unsafe_allow_html=True)
        
        colA, colB, colC = st.columns(3)
        try:
            n_joueurs = run_select("SELECT COUNT(*) AS n FROM joueur;", scope).iloc[0, 0]
            n_matchs = run_select("SELECT COUNT(*) AS n FROM match_game;", scope).iloc[0, 0]
            n_equipes = run_select("SELECT COUNT(*) AS n FROM equipe;", scope).iloc[0, 0]
        except Exception:
            n_joueurs = n_matchs = n_equipes = "N/A"

        colA.metric("Joueurs LEC", n_joueurs)
        colB.metric("Matchs LEC", n_matchs)
        colC.metric("Équipes LEC", n_equipes)

        st.markdown('<div class="section-title">EFFECTIF LEC ACTUEL</div>', unsafe_allow_html=True)
        q = """
        SELECT
          j.pseudo,
          j.role,
          j.nationalite,
          e.code AS equipe
        FROM joueur j
        JOIN affectation_joueur_equipe a ON a.joueur_id = j.joueur_id
        JOIN equipe e ON e.equipe_id = a.equipe_id
        WHERE a.date_fin IS NULL
        ORDER BY j.role, j.pseudo;
        """
        try:
            st.dataframe(run_select(q, scope), use_container_width=True, height=300)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    with tab_lec_players:
        st.markdown('<div class="section-title">ANALYSE PERFORMANCES LEC</div>', unsafe_allow_html=True)
        
        # Bouton 1 : Stats cumulées par joueur
        st.markdown("### STATS CUMULÉES PAR JOUEUR")
        
        if st.button("AFFICHER LES STATS CUMULÉES PAR JOUEUR", use_container_width=True, key="btn_stats_cumulees"):
            st.markdown("**Résultats : Stats cumulées par joueur**")
            q = """
            SELECT
              j.pseudo,
              j.role,
              COUNT(s.match_id) AS nb_matchs,
              SUM(s.kills) AS total_kills,
              SUM(s.deaths) AS total_deaths,
              SUM(s.assists) AS total_assists,
              ROUND((SUM(s.kills) + SUM(s.assists)) / NULLIF(SUM(s.deaths), 0), 2) AS kda_ratio
            FROM stat_joueur s
            JOIN joueur j ON j.joueur_id = s.joueur_id
            GROUP BY j.joueur_id, j.pseudo, j.role
            ORDER BY kda_ratio DESC;
            """
            try:
                df = run_select(q, scope)
                if df.empty:
                    st.warning("⚠️ Aucune statistique trouvée.")
                    st.info("Essayez cette requête de test dans l'onglet SQL LEC :")
                    st.code("SELECT * FROM scope_stat_joueur LIMIT 5;")
                else:
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")
        else:
            st.info("Cliquez sur le bouton ci-dessus pour afficher les stats cumulées par joueur")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Séparateur visuel
        st.divider()
        
        # Bouton 2 : KDA par rôle
        st.markdown("### KDA PAR RÔLE")
        
        if st.button("AFFICHER LE KDA PAR RÔLE", use_container_width=True, key="btn_kda_role"):
            st.markdown("**Résultats : KDA par rôle**")
            q_role = """
            SELECT
              j.role,
              COUNT(DISTINCT j.joueur_id) AS nb_joueurs,
              ROUND(AVG(s.kills), 2) AS avg_kills,
              ROUND(AVG(s.deaths), 2) AS avg_deaths,
              ROUND(AVG(s.assists), 2) AS avg_assists,
              ROUND(
                (SUM(s.kills) + SUM(s.assists)) / NULLIF(SUM(s.deaths), 0), 
                2
              ) AS kda_ratio_role
            FROM joueur j
            LEFT JOIN stat_joueur s ON s.joueur_id = j.joueur_id
            GROUP BY j.role
            ORDER BY j.role;
            """
            try:
                df_role = run_select(q_role, scope)
                if df_role.empty:
                    st.warning("Aucune donnée KDA par rôle disponible")
                else:
                    st.dataframe(df_role, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")
        else:
            st.info("Cliquez sur le bouton ci-dessus pour afficher le KDA par rôle")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_lec_sql:
        st.markdown('<div class="section-title">INTERFACE SQL LEC</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sensai-panel">
        <p><strong>RESTRICTION :</strong> Votre accès est limité aux données de la ligue LEC uniquement.</p>
        <p>Les tables sensibles (contrats, staff, données IA) ne sont pas accessibles.</p>
        </div>
        """, unsafe_allow_html=True)
        
        default_sql_lec = """-- Exemple : Voir les joueurs LEC avec leur rôle
SELECT pseudo, role, nationalite 
FROM joueur 
ORDER BY role, pseudo;"""
        
        user_sql_lec = st.text_area("REQUÊTE SQL LEC :", default_sql_lec, height=150)
        
        if st.button("EXÉCUTER REQUÊTE LEC", use_container_width=True):
            try:
                df = run_select(user_sql_lec, scope)
                if df.empty:
                    st.info("Requête exécutée - Aucun résultat")
                else:
                    st.success(f"{len(df)} lignes retournées")
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"ERREUR : {str(e)}")