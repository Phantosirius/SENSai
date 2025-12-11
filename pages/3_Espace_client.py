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
# STYLES (BLEU #1250A6)
# ==========================================================
PRIMARY = "#1250a6"

st.markdown(
    f"""
    <style>
    :root {{
        --sensai-primary: {PRIMARY};
    }}

    .sensai-title {{
        color: {PRIMARY};
        font-weight: 800;
        letter-spacing: 0.04em;
    }}

    .sensai-subtitle {{
        color: #333333;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }}

    .sensai-badge {{
        background-color: rgba(18,80,166,0.08);
        color: {PRIMARY};
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }}

    .stButton>button {{
        background-color: {PRIMARY};
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.35rem 0.9rem;
        font-weight: 600;
    }}

    .stButton>button:hover {{
        background-color: #0f3f82;
        color: white;
    }}

    .sensai-panel {{
        border-radius: 10px;
        padding: 0.8rem 1.1rem;
        background-color: rgba(18,80,166,0.03);
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 0.8rem;
    }}

    .sensai-denied {{
        text-align: center;
        padding: 3rem 1rem;
    }}

    .sensai-denied h1 {{
        color: {PRIMARY};
        font-size: 2.1rem;
        margin-bottom: 0.3rem;
    }}

    .sensai-denied h2 {{
        color: #444444;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.7rem;
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
# AUTH / GATE
# ==========================================================
st.markdown('<h1 class="sensai-title">SENSAI — Espace client</h1>', unsafe_allow_html=True)
st.caption(f"Base : {DB.name}")

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None       # "ADMIN" / "COACH_LEC"
    st.session_state.scope = None      # None / "LEC"

pwd = st.text_input("Code d’accès", type="password")

if st.button("Se connecter"):
    P = st.secrets["APP"]
    if pwd == P["PASS_PRIMEOUT"]:
        # Accès totalement refusé
        st.session_state.auth = False
        st.session_state.role = "PRIMEOUT"
        st.session_state.scope = None

        st.markdown(
            """
            <div class="sensai-denied">
                <h1>PRIME OUT</h1>
                <h2>Accès refusé à l’espace client</h2>
                <p>Ce code ne permet pas de consulter les données ni le cahier des charges.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    elif pwd == P["PASS_ADMIN"]:
        st.session_state.auth = True
        st.session_state.role = "ADMIN"
        st.session_state.scope = None
        st.success("Accès ADMIN accordé.")

    elif pwd == P["PASS_LEC"]:
        st.session_state.auth = True
        st.session_state.role = "COACH_LEC"
        st.session_state.scope = "LEC"
        st.success("Accès COACH LEC accordé (scope limité à la LEC).")
    else:
        st.session_state.auth = False
        st.session_state.role = None
        st.session_state.scope = None
        st.error("Code invalide.")

if not st.session_state.auth:
    st.stop()


# ==========================================================
# CONTENT — ADMIN vs COACH LEC
# ==========================================================

role = st.session_state.role
scope = st.session_state.scope

st.markdown(
    f'<div class="sensai-badge">Rôle connecté : {role}</div>',
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------
# ONGLETS ADMIN
# ----------------------------------------------------------
if role == "ADMIN":
    tab_dashboard, tab_players, tab_staff, tab_ia, tab_sql, tab_cdc, tab_model = st.tabs(
        [
            "Dashboard",
            "Joueurs / Équipes / Matchs",
            "Staff & Contrats",
            "IA & recommandations",
            "SQL libre",
            "Cahier des charges",
            "Modèle de données",
        ]
    )

    # ====================== TAB 1 : DASHBOARD ======================
    with tab_dashboard:
        st.markdown("### Vue synthétique")

        colA, colB, colC, colD = st.columns(4)
        try:
            n_joueurs = run_select("SELECT COUNT(*) AS n FROM joueur;", scope).iloc[0, 0]
            n_equipes = run_select("SELECT COUNT(*) AS n FROM equipe;", scope).iloc[0, 0]
            n_matchs = run_select("SELECT COUNT(*) AS n FROM match_game;", scope).iloc[0, 0]
            n_staff = run_select("SELECT COUNT(*) AS n FROM staff;", scope).iloc[0, 0]
        except Exception:
            n_joueurs = n_equipes = n_matchs = n_staff = "?"

        colA.metric("Joueurs", n_joueurs)
        colB.metric("Équipes", n_equipes)
        colC.metric("Matchs joués", n_matchs)
        colD.metric("Membres du staff", n_staff)

        st.markdown("### Exemples de vues utiles")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Effectif actuel par équipe")
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
                st.dataframe(run_select(q, scope), use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")

        with c2:
            st.markdown("#### Répartition des joueurs par ligue")
            q = """
            SELECT
              l.nom AS ligue,
              COUNT(DISTINCT j.joueur_id) AS nb_joueurs
            FROM joueur j
            JOIN affectation_joueur_equipe a ON a.joueur_id = j.joueur_id
            JOIN equipe e ON e.equipe_id = a.equipe_id
            JOIN participation_equipe_ligue pel
              ON pel.equipe_id = e.equipe_id
            JOIN ligue l ON l.ligue_id = pel.ligue_id
            WHERE a.date_fin IS NULL
            GROUP BY l.nom
            ORDER BY nb_joueurs DESC;
            """
            try:
                st.dataframe(run_select(q, scope), use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")

    # ================= TAB 2 : JOUEURS / ÉQUIPES / MATCHS =================
    with tab_players:
        st.markdown("### Joueurs & équipes")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Joueurs – fiche détaillée"):
                q = """
                SELECT
                  j.joueur_id,
                  j.pseudo,
                  j.nom,
                  j.prenom,
                  j.nationalite,
                  j.date_naissance,
                  j.role
                FROM joueur j
                ORDER BY j.role, j.pseudo;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        with col2:
            if st.button("Effectif actuel par équipe & ligue"):
                q = """
                SELECT
                  l.nom AS ligue,
                  e.code AS equipe,
                  j.pseudo,
                  j.role
                FROM affectation_joueur_equipe a
                JOIN joueur j ON j.joueur_id = a.joueur_id
                JOIN equipe e ON e.equipe_id = a.equipe_id
                JOIN participation_equipe_ligue pel
                  ON pel.equipe_id = e.equipe_id
                JOIN ligue l ON l.ligue_id = pel.ligue_id
                WHERE a.date_fin IS NULL
                ORDER BY l.nom, e.code, j.role;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        st.markdown("### Matchs & performances")

        c3, c4 = st.columns(2)

        with c3:
            if st.button("Historique des matchs (vue simple)"):
                q = """
                SELECT
                  m.match_id,
                  m.date_match,
                  l.nom AS ligue,
                  eb.code AS equipe_bleue,
                  er.code AS equipe_rouge,
                  ev.code AS vainqueur
                FROM match_game m
                JOIN ligue l ON l.ligue_id = m.ligue_id
                JOIN equipe eb ON eb.equipe_id = m.equipe_bleue_id
                JOIN equipe er ON er.equipe_id = m.equipe_rouge_id
                LEFT JOIN equipe ev ON ev.equipe_id = m.vainqueur_equipe_id
                ORDER BY m.date_match, m.match_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        with c4:
            if st.button("Stats cumulées par joueur (kills/deaths/assists)"):
                q = """
                SELECT
                  j.pseudo,
                  e.code AS equipe,
                  SUM(s.kills)   AS total_kills,
                  SUM(s.deaths)  AS total_deaths,
                  SUM(s.assists) AS total_assists
                FROM stat_joueur s
                JOIN joueur j ON j.joueur_id = s.joueur_id
                JOIN equipe e ON e.equipe_id = s.equipe_id_du_jour
                GROUP BY j.pseudo, e.code
                ORDER BY total_kills DESC;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

    # ================= TAB 3 : STAFF & CONTRATS =================
    with tab_staff:
        st.markdown("### Staff & contrats")

        colS1, colS2 = st.columns(2)

        with colS1:
            if st.button("Staff par équipe"):
                q = """
                SELECT
                  e.code AS equipe,
                  s.nom   AS nom_staff,
                  s.prenom,
                  sa.role,
                  sa.date_debut,
                  sa.date_fin
                FROM staff_affectation sa
                JOIN staff s ON s.staff_id = sa.staff_id
                JOIN equipe e ON e.equipe_id = sa.equipe_id
                ORDER BY e.code, sa.role;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        with colS2:
            if st.button("Contrats joueurs (salaires mensuels)"):
                q = """
                SELECT
                  e.code AS equipe,
                  j.pseudo,
                  c.date_debut,
                  c.date_fin,
                  c.salaire_mensuel,
                  c.statut
                FROM contrat c
                JOIN equipe e ON e.equipe_id = c.equipe_id
                JOIN joueur j ON j.joueur_id = c.joueur_id
                ORDER BY e.code, c.salaire_mensuel DESC;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        st.markdown("#### Masse salariale par équipe")
        q = """
        SELECT
          e.code AS equipe,
          SUM(c.salaire_mensuel) AS masse_salariale_mensuelle
        FROM contrat c
        JOIN equipe e ON e.equipe_id = c.equipe_id
        GROUP BY e.code
        ORDER BY masse_salariale_mensuelle DESC;
        """
        try:
            st.dataframe(run_select(q, scope), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    # ================= TAB 4 : IA & RECOMMANDATIONS =================
    with tab_ia:
        st.markdown("### Coach IA & recommandations")

        colIA1, colIA2 = st.columns(2)

        with colIA1:
            if st.button("Modèles IA disponibles"):
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

        with colIA2:
            if st.button("Recommandations par match"):
                q = """
                SELECT
                  r.recommandation_id,
                  m.match_id,
                  m.date_match,
                  e.code AS equipe,
                  j.pseudo AS joueur_cible,
                  r.type,
                  r.resume,
                  r.statut
                FROM recommandation r
                JOIN match_game m ON m.match_id = r.match_id
                JOIN equipe e ON e.equipe_id = r.equipe_id
                LEFT JOIN joueur j ON j.joueur_id = r.joueur_id
                ORDER BY m.date_match, r.recommandation_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        st.markdown("#### Interactions staff / recommandations")
        q = """
        SELECT
          r.recommandation_id,
          s.nom AS staff_nom,
          s.prenom AS staff_prenom,
          i.action,
          i.commentaire,
          i.created_at
        FROM interaction_reco i
        JOIN recommandation r ON r.recommandation_id = i.recommandation_id
        JOIN staff s ON s.staff_id = i.staff_id
        ORDER BY i.created_at DESC;
        """
        try:
            st.dataframe(run_select(q, scope), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    # ================= TAB 5 : SQL LIBRE =================
    with tab_sql:
        st.markdown("### SQL libre (lecture seule)")

        default_sql = "SELECT * FROM joueur LIMIT 10;"
        user_sql = st.text_area("Écris une requête SQL (SELECT uniquement) :", default_sql, height=120)

        if st.button("Exécuter la requête SQL"):
            try:
                df = run_select(user_sql, scope)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")

    # ================= TAB 6 : CAHIER DES CHARGES =================
# ================= TAB 6 : CAHIER DES CHARGES =================
    with tab_cdc:
        st.markdown("### CAHIER DES CHARGES SENSAI - PLATEFORME D'INTELLIGENCE ESPORT")
        
        # En-tête futuriste
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(18, 80, 166, 0.1) 0%, rgba(18, 80, 166, 0.05) 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(18, 80, 166, 0.2);
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        '>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3 style='color: #1250A6; margin: 0 0 5px 0; font-weight: 700;'>SENSAI TECHNOLOGIES</h3>
                <p style='color: #333; margin: 0; font-size: 0.9em;'>Plateforme d'Intelligence Artificielle pour l'Esport Professionnel</p>
            </div>
            <div style='text-align: right;'>
                <p style='color: #666; margin: 0; font-size: 0.85em;'><strong>Version :</strong> 3.0</p>
                <p style='color: #666; margin: 0; font-size: 0.85em;'><strong>Date :</strong> Q4 2024</p>
                <p style='color: #666; margin: 0; font-size: 0.85em;'><strong>Client :</strong> KARMINE CORP</p>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. CONTEXTE ET OBJECTIFS STRATEGIQUES
        with st.expander("1. CONTEXTE ET OBJECTIFS STRATEGIQUES", expanded=True):
            col_ctx1, col_ctx2 = st.columns([2, 1])
            
            with col_ctx1:
                st.markdown("""
                #### 1.1 Contexte d'Innovation
                
                **SensAI** représente la convergence entre l'intelligence artificielle de pointe et l'excellence esportive. 
                Dans un environnement compétitif où les marges de progression se réduisent, la data devient l'ultime avantage 
                concurrentiel. La Karmine Corp, organisation pionnière, nécessite une plateforme capable de transformer 
                des terabytes de données brutes en insights actionnables.
                
                **Problématique Identifiée :**
                - Fragmentation des données de performance
                - Latence dans l'analyse post-match
                - Subjectivité dans l'évaluation des joueurs
                - Difficulté à mesurer le ROI du coaching
                - Absence de capitalisation des connaissances tactiques
                """)
            
            with col_ctx2:
                st.markdown("""
                #### 1.2 Chiffres Clés
                """)
                st.markdown("---")
                st.markdown("""
                **15** tables de données structurées  
                **10+** matchs analysés quotidiennement  
                **50+** indicateurs de performance  
                **3** modèles IA spécialisés  
                **24/7** disponibilité requise  
                **< 100ms** latence maximale
                """)
            
            st.markdown("""
            #### 1.3 Objectifs Stratégiques
            
            | Période | Objectif | Indicateur de Succès |
            |---------|----------|----------------------|
            | Court Terme (Q1 2025) | Centralisation complète des données historiques Karmine Corp | 100% des données 2024 intégrées |
            | Moyen Terme (Q2 2025) | Implémentation des algorithmes prédictifs de performance | Précision >85% sur les résultats matchs |
            | Long Terme (Q3 2025+) | Commercialisation de la plateforme à d'autres organisations | 3 organisations tierces utilisatrices |
            
            #### 1.4 Valeur Ajoutée Quantifiée
            
            - **Pour les Joueurs :** Réduction de 40% du temps d'analyse personnelle
            - **Pour les Coaches :** Augmentation de 30% de l'efficacité des entraînements
            - **Pour la Direction :** Visibilité temps réel sur les investissements et ROI
            - **Pour les Analystes :** Automatisation de 70% des rapports standards
            """)
        
        # 2. ARCHITECTURE FONCTIONNELLE
        with st.expander("2. ARCHITECTURE FONCTIONNELLE", expanded=False):
            st.markdown("""
            #### 2.1 Matrice des Fonctionnalités par Module
            
            """)
            
            # Tableau des fonctionnalités
            features_data = {
                "Module": ["CORE ESPORT", "INTELLIGENCE ARTIFICIELLE", "GESTION ADMINISTRATIVE", "ANALYTICS AVANCES"],
                "Fonctionnalités Principales": [
                    "Gestion joueurs/équipes, Suivi matchs, Statistiques temps réel",
                    "Recommandations IA, Modèles prédictifs, NLP pour analyse vocale",
                    "Contrats et salaires, Gestion staff, Permissions RBAC",
                    "Dashboards interactifs, Reporting automatisé, API d'export"
                ],
                "Complexité": ["Élevée", "Très Élevée", "Moyenne", "Élevée"],
                "Priorité": ["P0", "P0", "P1", "P1"]
            }
            
            st.dataframe(pd.DataFrame(features_data), use_container_width=True)
            
            st.markdown("""
            #### 2.2 Flux de Données Critique
            
            **Match Data Pipeline :**
            1. Capture données via Riot Games API
            2. Validation et nettoyage automatique
            3. Stockage dans la base transactionnelle
            4. Processing par les modèles IA
            5. Génération de recommandations
            6. Notification aux staff concernés
            7. Tracking des interactions et feedback
            
            #### 2.3 Sécurité et Conformité
            
            - **RBAC (Role-Based Access Control) :** 5 niveaux de permissions
            - **Chiffrement :** AES-256 pour les données sensibles
            - **Audit Trail :** Logs complets de toutes les actions
            - **RGPD :** Conformité totale pour les données personnelles
            - **Backup :** Sauvegarde incrémentielle horaire
            """)
        
        # 3. SPECIFICATIONS TECHNIQUES
        with st.expander("3. SPECIFICATIONS TECHNIQUES", expanded=False):
            col_tech1, col_tech2, col_tech3 = st.columns(3)
            
            with col_tech1:
                st.markdown("""
                #### 3.1 Stack Technologique
                
                **Backend :**
                - Python 3.11+
                - FastAPI / Streamlit
                - SQLAlchemy 2.0
                - Pandas / NumPy
                
                **Base de Données :**
                - PostgreSQL 15 (Production)
                - Redis pour le caching
                - Elasticsearch pour la recherche
                
                **Infrastructure :**
                - Docker & Kubernetes
                - AWS/GCP Cloud
                - GitHub Actions CI/CD
                """)
            
            with col_tech2:
                st.markdown("""
                #### 3.2 Architecture Data
                
                **Current State :**
                - 15 tables relationnelles
                - 10+ relations complexes
                - Contraintes métier intégrées
                - Historisation native
                
                **Future State :**
                - Data Lake S3
                - Data Warehouse Redshift
                - Stream Processing (Kafka)
                - ML Feature Store
                """)
            
            with col_tech3:
                st.markdown("""
                #### 3.3 Performances Cibles
                
                **Temps Réponse :**
                - API : < 100ms (p95)
                - Queries : < 500ms
                - Export : < 2s
                
                **Disponibilité :**
                - SLA : 99.9%
                - RTO : 15 minutes
                - RPO : 5 minutes
                
                **Scalabilité :**
                - 1000+ requêtes/minute
                - 50 utilisateurs concurrents
                - 1TB+ de données
                """)
            
            st.markdown("""
            #### 3.4 Intégrations Systèmes
            
            | Système | Type | Fréquence | Sécurité |
            |---------|------|-----------|----------|
            | Riot Games API | REST API | Temps réel | OAuth 2.0 |
            | Tools of Legends | Scraping | Quotidien | API Key |
            | Google Workspace | SSO | Continu | SAML 2.0 |
            | ERP Interne | API Custom | Horaire | VPN + MTLS |
            """)
        
        # 4. ROADMAP DE DEVELOPPEMENT
        with st.expander("4. ROADMAP DE DEVELOPPEMENT", expanded=False):
            st.markdown("""
            #### 4.1 Phasage du Projet
            """)
            
            # Timeline avancée
            timeline_details = {
                "Phase": [
                    "PHASE ALPHA : Foundation", 
                    "PHASE BETA : Analytics", 
                    "PHASE GAMMA : Intelligence", 
                    "PHASE DELTA : Scale"
                ],
                "Période": [
                    "Jan 2024 - Mar 2024", 
                    "Avr 2024 - Juin 2024", 
                    "Juil 2024 - Sep 2024", 
                    "Oct 2024 - Déc 2024"
                ],
                "Budget": [
                    "150K €", 
                    "200K €", 
                    "250K €", 
                    "300K €"
                ],
                "Équipe": [
                    "3 Devs + 1 DS", 
                    "5 Devs + 2 DS", 
                    "6 Devs + 3 DS", 
                    "8 Devs + 4 DS"
                ],
                "Statut": [
                    "COMPLETED", 
                    "IN PROGRESS", 
                    "PLANNED", 
                    "FUTURE"
                ]
            }
            
            st.dataframe(pd.DataFrame(timeline_details), use_container_width=True)
            
            st.markdown("""
            #### 4.2 Livrables Principaux
            
            **Q1 2024 - MVP Interne :**
            - Base de données complète avec données historiques
            - Interface d'administration Streamlit
            - Système d'authentification et permissions
            - API REST de base
            
            **Q2 2024 - Analytics Suite :**
            - Dashboards interactifs personnalisables
            - Module de reporting automatisé
            - Visualisations avancées (heatmaps, timelines)
            - Export multi-formats (PDF, Excel, JSON)
            
            **Q3 2024 - Intelligence Module :**
            - Moteur de recommandations IA
            - Modèles prédictifs de performance
            - Analyse NLP des communications
            - Système de feedback et apprentissage
            
            **Q4 2024 - Scale & Commercial :**
            - Architecture microservices
            - API publique documentée
            - Portail client multi-organisation
            - Application mobile companion
            """)
        
        # 5. GOVERNANCE ET METRICS
        with st.expander("5. GOVERNANCE ET METRICS", expanded=False):
            col_gov1, col_gov2 = st.columns(2)
            
            with col_gov1:
                st.markdown("""
                #### 5.1 Comité de Pilotage
                
                **Fréquence :** Réunion bimensuelle
                
                **Participants :**
                - Directeur Esport Karmine Corp
                - Head Coach LEC
                - Head of Data Science
                - Lead Developer SensAI
                - Représentant Joueurs
                
                **Décisions :**
                - Priorisation des features
                - Allocation budget
                - Validation des livrables
                - Stratégie produit
                """)
            
            with col_gov2:
                st.markdown("""
                #### 5.2 KPIs de Performance
                
                **Techniques :**
                - Uptime : 99.9%
                - Latence API : < 100ms
                - Erreurs : < 0.1%
                - Backup Success : 100%
                
                **Business :**
                - Adoption Rate : > 90%
                - User Satisfaction : NPS > 50
                - ROI Calculable : Mensuel
                - Time Saved : > 30h/semaine
                """)
            
            st.markdown("""
            #### 5.3 Matrice RACI
            
            | Activité | Product Owner | Lead Dev | Data Scientist | Coach LEC |
            |----------|---------------|----------|----------------|-----------|
            | Définition Requirements | A | C | C | R |
            | Développement Features | C | A | R | I |
            | Validation Métier | R | I | I | A |
            | Déploiement Production | C | A | I | I |
            | Support Utilisateurs | A | R | C | C |
            
            **Légende :** R = Responsible, A = Accountable, C = Consulted, I = Informed
            """)
        
        # 6. CONTRAINTES ET RISQUES
        with st.expander("6. CONTRAINTES ET RISQUES", expanded=False):
            col_risk1, col_risk2 = st.columns(2)
            
            with col_risk1:
                st.markdown("""
                #### 6.1 Contraintes Identifiées
                
                **Techniques :**
                - Compatibilité avec les APIs Riot Games
                - Performances temps réel exigées
                - Sécurité données sensibles
                - Intégration systèmes existants
                
                **Business :**
                - Budget développement limité
                - Délais compétition esport
                - Confidentialité stratégique
                - ROI mesurable exigé
                
                **Légales :**
                - Conformité RGPD stricte
                - Droits d'image joueurs
                - Propriété intellectuelle
                - Contrats partenariats
                """)
            
            with col_risk2:
                st.markdown("""
                #### 6.2 Matrice des Risques
                
                | Risque | Probabilité | Impact | Mitigation |
                |--------|-------------|--------|------------|
                | Changement API Riot | Élevée | Critique | Abstraction layer + monitoring |
                | Fuite données | Faible | Critique | Chiffrement + audit complet |
                | Rejet utilisateurs | Moyenne | Élevé | Formation + support dédié |
                | Dépassement budget | Moyenne | Élevé | Contrôle coûts mensuel |
                | Concurrence solution | Faible | Moyen | Innovation continue + roadmap |
                """)
            
            st.markdown("""
            #### 6.3 Plan de Contingence
            
            **Scénario 1 : Échec déploiement majeur**
            - Rollback automatique vers version stable
            - Communication immédiate aux stakeholders
            - Analyse post-mortem sous 24h
            
            **Scénario 2 : Perte de données**
            - Restauration depuis backup le plus récent
            - Reconstruction données manquantes
            - Audit de sécurité complet
            
            **Scénario 3 : Non-adoption par les coaches**
            - Programme de formation intensif
            - Adaptation interface aux feedbacks
            - Période de transition assistée
            """)
        
        # 7. ANNEXES ET REFERENCES
        with st.expander("7. ANNEXES ET REFERENCES", expanded=False):
            tab_annex1, tab_annex2, tab_annex3, tab_annex4 = st.tabs([
                "Glossaire", 
                "Références Techniques", 
                "Contacts", 
                "Versions"
            ])
            
            with tab_annex1:
                st.markdown("""
                #### Terminologie Spécialisée
                
                **KDA :** Ratio Kills/Deaths/Assists - Métrique fondamentale de performance individuelle
                **LEC :** League of Legends EMEA Championship - Plus haut niveau compétitif européen
                **LFL :** La Ligue Française - Division 1 française de League of Legends
                **EUM :** European Masters - Tournoi continental regroupant les meilleures équipes régionales
                **ROI :** Return On Investment - Mesure de rentabilité des investissements en coaching IA
                **RBAC :** Role-Based Access Control - Système de permissions basé sur les rôles utilisateurs
                **SLA :** Service Level Agreement - Contrat de niveau de service garantissant les performances
                """)
            
            with tab_annex2:
                st.markdown("""
                #### Documentation Technique Référente
                
                **APIs Officielles :**
                - Riot Games Developer Portal : https://developer.riotgames.com/
                - Data Dragon API Documentation
                - Match v5 Endpoint Specifications
                
                **Standards de Sécurité :**
                - RGPD Règlement Général sur la Protection des Données
                - OWASP Top 10 Security Risks
                - ISO 27001 Information Security Management
                
                **Benchmarks Performance :**
                - League of Legends Esports Stats Center
                - Oracle's Elixir Database
                - Games of Legends Historical Data
                """)
            
            with tab_annex3:
                st.markdown("""
                #### Équipe Projet SensAI
                
                **Direction Produit :**
                - Product Owner : [NOM PO]
                - Scrum Master : [NOM SM]
                
                **Développement Technique :**
                - Lead Developer : [VOTRE NOM]
                - Backend Engineer : [NOM BE]
                - Frontend Engineer : [NOM FE]
                - DevOps Engineer : [NOM DEVOPS]
                
                **Data Science :**
                - Head of Data Science : [NOM DS]
                - Machine Learning Engineer : [NOM MLE]
                - Data Analyst : [NOM DA]
                
                **Sponsors Métier :**
                - Directeur Esport Karmine Corp : Kameto
                - Head Coach LEC : Reha
                - Performance Analyst : [NOM ANALYST]
                """)
            
            with tab_annex4:
                st.markdown("""
                #### Historique des Versions
                
                **Version 1.0 - Janvier 2024**
                - MVP : Base de données + interface admin
                - Scope : Données historiques Karmine Corp 2023
                - Équipe : 2 développeurs, 1 data scientist
                
                **Version 1.5 - Mars 2024**
                - Analytics : Dashboards de base
                - Features : Requêtes SQL, exports simples
                - Amélioration : Performance ×3 sur les requêtes
                
                **Version 2.0 - Mai 2024**
                - Intelligence : Premiers modèles IA
                - Integration : Riot Games API temps réel
                - Sécurité : RBAC complet + audit logs
                
                **Version 3.0 - Juillet 2024 (actuelle)**
                - Scale : Architecture microservices
                - Commercial : Multi-organisation support
                - Mobile : Application companion iOS/Android
                """)
        
        # Footer avec actions
        st.markdown("---")
        
        col_footer1, col_footer2, col_footer3, col_footer4 = st.columns(4)
        
        with col_footer1:
            if st.button("GENERER PDF", type="primary"):
                st.info("Génération du document PDF en cours...")
        
        with col_footer2:
            if st.button("EXPORT DONNEES"):
                st.info("Export des données du CDC en JSON")
        
        with col_footer3:
            if st.button("PARTAGER DOCUMENT"):
                st.info("Options de partage disponibles")
        
        with col_footer4:
            if st.button("METTRE A JOUR"):
                st.success("Cahier des charges synchronisé")
        
        # Watermark
        st.markdown("""
        <div style='
            text-align: center;
            color: #666;
            font-size: 0.8em;
            margin-top: 30px;
            padding: 10px;
            border-top: 1px solid #eee;
        '>
        <strong>SENSAI TECHNOLOGIES</strong> - Propriété intellectuelle protégée - Document confidentiel<br>
        © 2024 SensAI - Tous droits réservés - Version 3.0
        </div>
        """, unsafe_allow_html=True)


    # ================= TAB 7 : MODÈLE DE DONNÉES =================
    with tab_model:
        st.markdown("### Modèle de données (synthèse MCD / MLD)")

        with st.expander("Entités principales (MCD)", expanded=True):
            st.markdown(
                """
                - **LIGUE**(ligue_id, nom, niveau)
                - **SAISON**(saison_id, nom, date_debut, date_fin)
                - **EQUIPE**(equipe_id, nom, code)
                - **JOUEUR**(joueur_id, pseudo, nom, prenom, nationalite, date_naissance, role)
                - **STAFF**(staff_id, nom, prenom, email)
                - **MATCH_GAME**(match_id, date_match, type_match, vainqueur_equipe_id, saison_id, ligue_id, equipe_bleue_id, equipe_rouge_id)
                - **STAT_JOUEUR**(match_id, joueur_id, kills, deaths, assists, equipe_id_du_jour)
                - **CONTRAT**(contrat_id, date_debut, date_fin, salaire_mensuel, statut)
                - **AFFECTATION_JOUEUR_EQUIPE**(joueur_id, equipe_id, date_debut, date_fin, statut, type_mouvement)
                - **STAFF_AFFECTATION**(staff_affectation_id, staff_id, equipe_id, joueur_id, date_debut, date_fin, role)
                - **PARTICIPATION_EQUIPE_LIGUE**(equipe_id, saison_id, ligue_id)
                - **COACH_IA**(coach_ia_id, nom_modele, version, domaine, statut, created_at)
                - **RECOMMANDATION**(recommandation_id, type, resume, details, statut, created_at)
                - **INTERACTION_RECO**(interaction_id, action, commentaire, created_at)
                """
            )

        with st.expander("Modèle logique (MLD) — quelques exemples de PK / FK", expanded=False):
            st.markdown(
                """
                - **PARTICIPATION_EQUIPE_LIGUE**  
                  PK = (equipe_id, saison_id)  
                  FK equipe_id → EQUIPE, saison_id → SAISON, ligue_id → LIGUE

                - **AFFECTATION_JOUEUR_EQUIPE**  
                  PK = (joueur_id, equipe_id, date_debut)  
                  FK joueur_id → JOUEUR, equipe_id → EQUIPE

                - **MATCH_GAME**  
                  PK = (match_id)  
                  FK saison_id → SAISON  
                  FK ligue_id → LIGUE  
                  FK equipe_bleue_id, equipe_rouge_id, vainqueur_equipe_id → EQUIPE  
                  + contraintes métier : équipes distinctes, vainqueur ∈ {bleue, rouge}

                - **STAT_JOUEUR**  
                  PK = (match_id, joueur_id)  
                  FK match_id → MATCH_GAME, joueur_id → JOUEUR, equipe_id_du_jour → EQUIPE

                - **CONTRAT**  
                  PK = (contrat_id)  
                  FK equipe_id → EQUIPE  
                  FK joueur_id → JOUEUR (nullable)  
                  FK staff_id → STAFF (nullable)  
                  + contrainte XOR : joueur OU staff, mais pas les deux.
                """
            )

        with st.expander("Résumé d’architecture data", expanded=False):
            st.markdown(
                """
                Le modèle articule :

                - un **noyau sportif** (ligue, saison, équipe, joueur, staff),
                - des **associations temporelles** (participation, affectations, contrats),
                - un **sous-système de performance** (matchs, statistiques par joueur),
                - un **sous-système IA** (coach IA, recommandations, interactions).

                Ce découpage permet :
                - de répondre aux besoins de suivi opérationnel du club,
                - de supporter l’analyse de performance,
                - de tracer la valeur ajoutée des outils IA,
                - de garantir une intégrité forte et une extensibilité du schéma.
                """
            )


# ----------------------------------------------------------
# ONGLETS COACH LEC (scope limité)
# ----------------------------------------------------------
elif role == "COACH_LEC":
    tab_lec_dashboard, tab_lec_players, tab_lec_sql = st.tabs(
        [
            "Vue LEC",
            "Joueurs & matchs LEC",
            "SQL (scope LEC uniquement)",
        ]
    )

    with tab_lec_dashboard:
        st.markdown("### Vue LEC — synthèse")

        colA, colB, colC = st.columns(3)
        try:
            n_joueurs = run_select("SELECT COUNT(*) AS n FROM joueur;", scope).iloc[0, 0]
            n_matchs = run_select("SELECT COUNT(*) AS n FROM match_game;", scope).iloc[0, 0]
            n_equipes = run_select("SELECT COUNT(*) AS n FROM equipe;", scope).iloc[0, 0]
        except Exception:
            n_joueurs = n_matchs = n_equipes = "?"

        colA.metric("Joueurs LEC", n_joueurs)
        colB.metric("Matchs LEC", n_matchs)
        colC.metric("Équipes dans la LEC", n_equipes)

        st.markdown("#### Effectif LEC (scope)")

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
            st.dataframe(run_select(q, scope), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

    with tab_lec_players:
        st.markdown("### Joueurs & matchs LEC")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Stats cumulées par joueur (LEC)"):
                q = """
                SELECT
                  j.pseudo,
                  SUM(s.kills)   AS total_kills,
                  SUM(s.deaths)  AS total_deaths,
                  SUM(s.assists) AS total_assists
                FROM stat_joueur s
                JOIN joueur j ON j.joueur_id = s.joueur_id
                GROUP BY j.pseudo
                ORDER BY total_kills DESC;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

        with c2:
            if st.button("Historique des matchs LEC"):
                q = """
                SELECT
                  m.match_id,
                  m.date_match,
                  eb.code AS equipe_bleue,
                  er.code AS equipe_rouge,
                  ev.code AS vainqueur
                FROM match_game m
                JOIN equipe eb ON eb.equipe_id = m.equipe_bleue_id
                JOIN equipe er ON er.equipe_id = m.equipe_rouge_id
                LEFT JOIN equipe ev ON ev.equipe_id = m.vainqueur_equipe_id
                ORDER BY m.date_match, m.match_id;
                """
                try:
                    st.dataframe(run_select(q, scope), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")

    with tab_lec_sql:
        st.markdown("### SQL (LEC uniquement)")

        default_sql_lec = "SELECT pseudo, role, nationalite FROM joueur ORDER BY role, pseudo;"
        user_sql_lec = st.text_area("Écris un SELECT sur ton scope LEC :", default_sql_lec, height=120)

        if st.button("Exécuter la requête LEC"):
            try:
                df = run_select(user_sql_lec, scope)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")
