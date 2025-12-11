# data/create_demo_db.py
from pathlib import Path
import sqlite3

DB = Path(__file__).with_name("sensai_demo.sqlite")
DB.unlink(missing_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.executescript("""
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1) RÉFÉRENTIELS
-- ============================================================

CREATE TABLE ligue (
  ligue_id INTEGER PRIMARY KEY,
  nom      TEXT NOT NULL UNIQUE,
  niveau   TEXT    -- T0 / T1 / T2
);

CREATE TABLE saison (
  saison_id  INTEGER PRIMARY KEY,
  nom        TEXT NOT NULL,
  date_debut TEXT NOT NULL,
  date_fin   TEXT NOT NULL
);

CREATE TABLE equipe (
  equipe_id INTEGER PRIMARY KEY,
  nom       TEXT NOT NULL UNIQUE,
  code      TEXT UNIQUE
);

-- Une équipe évolue dans une ligue pour une saison donnée
CREATE TABLE participation_equipe_ligue (
  equipe_id INTEGER NOT NULL REFERENCES equipe(equipe_id),
  saison_id INTEGER NOT NULL REFERENCES saison(saison_id),
  ligue_id  INTEGER NOT NULL REFERENCES ligue(ligue_id),
  PRIMARY KEY (equipe_id, saison_id)
);

-- ============================================================
-- 2) JOUEURS & AFFECTATIONS
-- ============================================================

CREATE TABLE joueur (
  joueur_id      INTEGER PRIMARY KEY,
  pseudo         TEXT UNIQUE,      -- Nom esports
  nom            TEXT NOT NULL,
  prenom         TEXT NOT NULL,
  nationalite    TEXT,
  date_naissance TEXT,
  role           TEXT NOT NULL CHECK (role IN ('TOP','JUNGLE','MID','ADC','SUPPORT'))
);

-- Historique des affectations joueur → équipe
CREATE TABLE affectation_joueur_equipe (
  joueur_id  INTEGER NOT NULL REFERENCES joueur(joueur_id),
  equipe_id  INTEGER NOT NULL REFERENCES equipe(equipe_id),
  date_debut TEXT NOT NULL,
  date_fin   TEXT,
  statut     TEXT NOT NULL DEFAULT 'TITULAIRE' CHECK (statut IN ('TITULAIRE','REMPLACANT')),
  type_mouvement TEXT NOT NULL DEFAULT 'NORMAL',
  PRIMARY KEY (joueur_id, equipe_id, date_debut)
);

-- ============================================================
-- 3) MATCHES & STATS
-- ============================================================

CREATE TABLE match_game (
  match_id            INTEGER PRIMARY KEY,
  saison_id           INTEGER NOT NULL REFERENCES saison(saison_id),
  ligue_id            INTEGER NOT NULL REFERENCES ligue(ligue_id),
  date_match          TEXT   NOT NULL,
  type_match          TEXT   NOT NULL CHECK (type_match IN ('OFFICIEL','SCRIM')),
  equipe_bleue_id     INTEGER NOT NULL REFERENCES equipe(equipe_id),
  equipe_rouge_id     INTEGER NOT NULL REFERENCES equipe(equipe_id),
  vainqueur_equipe_id INTEGER NULL REFERENCES equipe(equipe_id),
  CHECK (equipe_bleue_id <> equipe_rouge_id),
  CHECK (vainqueur_equipe_id IS NULL OR vainqueur_equipe_id IN (equipe_bleue_id, equipe_rouge_id))
);

CREATE TABLE stat_joueur (
  match_id          INTEGER NOT NULL REFERENCES match_game(match_id) ON DELETE CASCADE,
  joueur_id         INTEGER NOT NULL REFERENCES joueur(joueur_id),
  equipe_id_du_jour INTEGER NOT NULL REFERENCES equipe(equipe_id),
  kills   INTEGER NOT NULL DEFAULT 0,
  deaths  INTEGER NOT NULL DEFAULT 0,
  assists INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (match_id, joueur_id)
);

-- ============================================================
-- 4) STAFF, AFFECTATIONS & CONTRATS
-- ============================================================

CREATE TABLE staff (
  staff_id INTEGER PRIMARY KEY,
  nom      TEXT NOT NULL,
  prenom   TEXT NOT NULL,
  email    TEXT NOT NULL UNIQUE
);

CREATE TABLE staff_affectation (
  staff_affectation_id INTEGER PRIMARY KEY,
  staff_id   INTEGER NOT NULL REFERENCES staff(staff_id),
  equipe_id  INTEGER NOT NULL REFERENCES equipe(equipe_id),
  joueur_id  INTEGER NULL REFERENCES joueur(joueur_id),
  role       TEXT  NOT NULL CHECK (role IN (
       'HEAD_COACH','ASSISTANT_COACH','ANALYSTE','MANAGER',
       'PSYCHOLOGUE','PREPARATEUR_MENTAL','AGENT'
  )),
  date_debut TEXT NOT NULL,
  date_fin   TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_manager_unique_par_joueur
  ON staff_affectation (joueur_id)
  WHERE role='MANAGER' AND joueur_id IS NOT NULL AND date_fin IS NULL;

CREATE TABLE contrat (
  contrat_id INTEGER PRIMARY KEY,
  equipe_id  INTEGER NOT NULL REFERENCES equipe(equipe_id),
  joueur_id  INTEGER NULL REFERENCES joueur(joueur_id),
  staff_id   INTEGER NULL REFERENCES staff(staff_id),
  date_debut TEXT NOT NULL,
  date_fin   TEXT NOT NULL,
  salaire_mensuel REAL NOT NULL DEFAULT 0.0,
  statut     TEXT NOT NULL DEFAULT 'ACTIF' CHECK (statut IN ('ACTIF','SUSPENDU','TERMINE')),
  CHECK ((joueur_id IS NOT NULL AND staff_id IS NULL)
     OR  (joueur_id IS NULL AND staff_id IS NOT NULL))
);

-- ============================================================
-- 5) IA & RECOMMANDATIONS
-- ============================================================

CREATE TABLE coach_ia (
  coach_ia_id INTEGER PRIMARY KEY,
  nom_modele  TEXT NOT NULL,
  version     TEXT,
  domaine     TEXT,
  statut      TEXT NOT NULL DEFAULT 'ACTIF' CHECK (statut IN ('ACTIF','INACTIF')),
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE recommandation (
  recommandation_id INTEGER PRIMARY KEY,
  coach_ia_id INTEGER NOT NULL REFERENCES coach_ia(coach_ia_id),
  match_id    INTEGER NOT NULL REFERENCES match_game(match_id) ON DELETE CASCADE,
  equipe_id   INTEGER NOT NULL REFERENCES equipe(equipe_id),
  joueur_id   INTEGER NULL REFERENCES joueur(joueur_id),
  type        TEXT NOT NULL CHECK (type IN ('TACTIQUE','STRATEGIQUE','COMPORTEMENTALE')),
  resume      TEXT NOT NULL,
  details     TEXT,
  statut      TEXT NOT NULL DEFAULT 'ENVOYEE' CHECK (statut IN ('ENVOYEE','VALIDEE','REJETEE','IGNOREE')),
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE interaction_reco (
  interaction_id     INTEGER PRIMARY KEY,
  recommandation_id  INTEGER NOT NULL REFERENCES recommandation(recommandation_id) ON DELETE CASCADE,
  staff_id           INTEGER NOT NULL REFERENCES staff(staff_id),
  action             TEXT NOT NULL CHECK (action IN ('VALIDEE','REJETEE','IGNOREE')),
  commentaire        TEXT,
  created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- INSERTS RÉFÉRENTIELS
-- ============================================================

INSERT INTO ligue VALUES
 (1,'LEC','T0'),
 (2,'LFL','T1'),
 (3,'LFL Div.2','T2');

INSERT INTO saison VALUES
 (1,'2025 Split 1','2025-01-15','2025-04-30');

INSERT INTO equipe VALUES
 (1,'Karmine Corp (LEC)','KC'),
 (2,'Karmine Corp Blue (LFL)','KCB'),
 (3,'Karmine Corp Blue Stars (Div2)','KCBS');

INSERT INTO participation_equipe_ligue VALUES
 (1,1,1),
 (2,1,2),
 (3,1,3);

-- ============================================================
-- INSERTS JOUEURS & AFFECTATIONS
-- ============================================================

INSERT INTO joueur (joueur_id, pseudo, nom, prenom, nationalite, date_naissance, role)
VALUES
 -- LEC
 (1,'Canna','Kim','Chang-Dong','KR','2000-02-11','TOP'),
 (2,'Yike','Sundelin','Martin','SE','2001-08-07','JUNGLE'),
 (3,'Vladi','Kourtidis','Vladimiros','GR','2004-03-15','MID'),
 (4,'Caliste','Henry-Hennebert','Caliste','FR','2003-09-22','ADC'),
 (5,'Targamas','Crabbé','Raphaël','BE','1999-06-15','SUPPORT'),

 -- LFL
 (6,'Maynter','Sorokin','Volodymyr','UA','2004-01-20','TOP'),
 (7,'Yukino','Dang','Johnny','US','2002-10-12','JUNGLE'),
 (8,'SlowQ','Ye-bit','Seo','SE','2003-04-18','MID'),
 (9,'3XA','Foucou','Thomas','FR','2005-02-05','ADC'),
 (10,'Piero','Kim','Jeong-hoon','KR','2001-07-09','SUPPORT'),

 -- DIV2
 (11,'Tao','Hong Tao','Alessandro','IT','2002-12-14','TOP'),
 (12,'BAASHH','Klitfelt','Oliver','DK','2001-03-28','JUNGLE'),
 (13,'MathisV','Vannieuwenhuyse','Mathis','FR','2004-11-06','MID'),
 (14,'Hazel','Peştriţu','Costin','RO','2003-09-03','ADC'),
 (15,'Nsurr','Gergaud','Emilien','FR','2002-05-22','SUPPORT');

INSERT INTO affectation_joueur_equipe VALUES 
-- LEC 
(1,1,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(2,1,'2025-01-15',NULL,'TITULAIRE','NORMAL'),
(3,1,'2025-01-15',NULL,'TITULAIRE','NORMAL'),
(4,1,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(5,1,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
-- LFL
(6,2,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(7,2,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(8,2,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(9,2,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(10,2,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
-- DIV2 
(11,3,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(12,3,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(13,3,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(14,3,'2025-01-15',NULL,'TITULAIRE','NORMAL'), 
(15,3,'2025-01-15',NULL,'TITULAIRE','NORMAL');             

-- ============================================================
-- INSERTS STAFF, AFFECTATIONS & CONTRATS
-- ============================================================

INSERT INTO staff (staff_id, nom, prenom, email) VALUES
 -- LEC
 (1,'Ramanana','Reha','reha@kc.gg'),
 (2,'Benarbia','Wadi','wadi@kc.gg'),
 (3,'Thillier','Clément','clem@kc.gg'),

 -- LFL
 (4,'Paul','Ianis','blidzy@kc.gg'),
 (5,'Zahidi','Soufiane','souf@kc.gg'),

 -- DIV2
 (6,'De La Torre','Mario','cptmario@kc.gg'),
 (7,'Claudé','Raphaël','lingwi@kc.gg');

INSERT INTO staff_affectation 
(staff_affectation_id, staff_id, equipe_id, joueur_id, role, date_debut, date_fin)
VALUES
 -- LEC Staff
 (1,1,1,NULL,'HEAD_COACH','2025-01-10',NULL),
 (2,2,1,NULL,'ASSISTANT_COACH','2025-01-10',NULL),
 (3,3,1,NULL,'ANALYSTE','2025-01-10',NULL),

 -- LFL Staff
 (4,4,2,NULL,'ASSISTANT_COACH','2025-01-10',NULL),
 (5,5,2,NULL,'PREPARATEUR_MENTAL','2025-01-10',NULL),

 -- Div2 Staff
 (6,6,3,NULL,'HEAD_COACH','2025-01-10',NULL),
 (7,7,3,NULL,'ASSISTANT_COACH','2025-01-10',NULL);

-- CONTRATS (salaires réalistes)

-- LEC joueurs : ~14k–16k mensuel
INSERT INTO contrat (contrat_id, equipe_id, joueur_id, staff_id, date_debut, date_fin, salaire_mensuel, statut)
VALUES
 (1,1,1,NULL,'2025-01-15','2025-11-30',16000,'ACTIF'),
 (2,1,2,NULL,'2025-01-15','2025-11-30',15000,'ACTIF'),
 (3,1,3,NULL,'2025-01-15','2025-11-30',15000,'ACTIF'),
 (4,1,4,NULL,'2025-01-15','2025-11-30',14000,'ACTIF'),
 (5,1,5,NULL,'2025-01-15','2025-11-30',14000,'ACTIF'),

-- LFL joueurs : ~4k–7k
 (6,2,6,NULL,'2025-01-15','2025-11-30',7000,'ACTIF'),
 (7,2,7,NULL,'2025-01-15','2025-11-30',6000,'ACTIF'),
 (8,2,8,NULL,'2025-01-15','2025-11-30',6000,'ACTIF'),
 (9,2,9,NULL,'2025-01-15','2025-11-30',5000,'ACTIF'),
 (10,2,10,NULL,'2025-01-15','2025-11-30',5000,'ACTIF'),

-- DIV2 joueurs : ~2k–3k
 (11,3,11,NULL,'2025-01-15','2025-11-30',3000,'ACTIF'),
 (12,3,12,NULL,'2025-01-15','2025-11-30',2500,'ACTIF'),
 (13,3,13,NULL,'2025-01-15','2025-11-30',2500,'ACTIF'),
 (14,3,14,NULL,'2025-01-15','2025-11-30',2000,'ACTIF'),
 (15,3,15,NULL,'2025-01-15','2025-11-30',2000,'ACTIF'),

-- Staff LEC : ~8k–12k
 (16,1,NULL,1,'2025-01-10','2025-11-30',12000,'ACTIF'),
 (17,1,NULL,2,'2025-01-10','2025-11-30',9000,'ACTIF'),
 (18,1,NULL,3,'2025-01-10','2025-11-30',8000,'ACTIF'),

-- Staff LFL : ~4k–6k
 (19,2,NULL,4,'2025-01-10','2025-11-30',5500,'ACTIF'),
 (20,2,NULL,5,'2025-01-10','2025-11-30',4500,'ACTIF'),

-- Staff DIV2 : ~3k–4k
 (21,3,NULL,6,'2025-01-10','2025-11-30',4000,'ACTIF'),
 (22,3,NULL,7,'2025-01-10','2025-11-30',3000,'ACTIF');

-- ============================================================
-- MATCHES & STATS (10 matchs)
-- ============================================================

INSERT INTO match_game 
(match_id, saison_id, ligue_id, date_match, type_match, equipe_bleue_id, equipe_rouge_id, vainqueur_equipe_id)
VALUES
 -- LEC
 (1,1,1,'2025-01-20','OFFICIEL',1,2,1),
 (2,1,1,'2025-01-27','OFFICIEL',3,1,1),
 (3,1,1,'2025-02-03','OFFICIEL',1,3,3),
 (4,1,1,'2025-02-10','OFFICIEL',2,1,1),

 -- LFL
 (5,1,2,'2025-01-22','OFFICIEL',2,3,2),
 (6,1,2,'2025-01-29','OFFICIEL',3,2,3),
 (7,1,2,'2025-02-05','OFFICIEL',2,1,2),

 -- DIV2
 (8,1,3,'2025-01-21','OFFICIEL',3,2,3),
 (9,1,3,'2025-01-28','OFFICIEL',3,1,1),
 (10,1,3,'2025-02-04','OFFICIEL',1,3,1);

-- STATS JOUEURS (cf. bloc précédent, recopiées telles quelles)

-- MATCH 1
INSERT INTO stat_joueur VALUES
 (1,1,1,5,1,7),
 (1,2,1,3,2,8),
 (1,3,1,4,3,6),
 (1,4,1,7,1,5),
 (1,5,1,1,2,12),
 (1,6,2,2,5,3),
 (1,7,2,1,6,4),
 (1,8,2,0,4,5),
 (1,9,2,3,5,3),
 (1,10,2,0,6,8);

-- MATCH 2
INSERT INTO stat_joueur VALUES
 (2,1,1,6,1,10),
 (2,2,1,4,3,7),
 (2,3,1,5,2,9),
 (2,4,1,8,1,3),
 (2,5,1,2,2,14),
 (2,11,3,1,6,4),
 (2,12,3,3,5,2),
 (2,13,3,1,4,7),
 (2,14,3,2,6,1),
 (2,15,3,0,6,5);

-- MATCH 3
INSERT INTO stat_joueur VALUES
 (3,1,1,2,4,3),
 (3,2,1,1,3,6),
 (3,3,1,3,5,4),
 (3,4,1,5,2,2),
 (3,5,1,0,3,10),
 (3,11,3,7,1,8),
 (3,12,3,6,1,9),
 (3,13,3,4,2,7),
 (3,14,3,2,1,11),
 (3,15,3,1,2,14);

-- MATCH 4
INSERT INTO stat_joueur VALUES
 (4,1,1,6,2,4),
 (4,2,1,4,2,10),
 (4,3,1,8,3,7),
 (4,4,1,5,1,6),
 (4,5,1,1,3,15),
 (4,6,2,3,6,4),
 (4,7,2,2,5,7),
 (4,8,2,1,4,9),
 (4,9,2,4,3,4),
 (4,10,2,0,4,10);

-- MATCH 5
INSERT INTO stat_joueur VALUES
 (5,6,2,5,3,11),
 (5,7,2,4,2,9),
 (5,8,2,6,4,7),
 (5,9,2,3,3,8),
 (5,10,2,1,3,14),
 (5,11,3,2,5,3),
 (5,12,3,1,6,5),
 (5,13,3,3,4,4),
 (5,14,3,2,6,6),
 (5,15,3,1,7,7);

-- MATCH 6
INSERT INTO stat_joueur VALUES
 (6,6,2,2,6,5),
 (6,7,2,1,7,4),
 (6,8,2,0,6,6),
 (6,9,2,3,6,4),
 (6,10,2,1,5,9),
 (6,11,3,7,2,6),
 (6,12,3,4,3,8),
 (6,13,3,6,2,7),
 (6,14,3,3,1,9),
 (6,15,3,2,2,12);

-- MATCH 7
INSERT INTO stat_joueur VALUES
 (7,6,2,6,2,10),
 (7,7,2,4,1,8),
 (7,8,2,5,3,7),
 (7,9,2,3,2,11),
 (7,10,2,1,3,13),
 (7,1,1,2,5,4),
 (7,2,1,1,4,7),
 (7,3,1,3,4,5),
 (7,4,1,4,3,3),
 (7,5,1,0,3,10);

-- MATCH 8
INSERT INTO stat_joueur VALUES
 (8,11,3,6,3,7),
 (8,12,3,5,3,9),
 (8,13,3,4,2,10),
 (8,14,3,3,1,11),
 (8,15,3,1,2,15),
 (8,6,2,2,6,4),
 (8,7,2,1,6,5),
 (8,8,2,0,5,6),
 (8,9,2,3,4,7),
 (8,10,2,1,5,8);

-- MATCH 9
INSERT INTO stat_joueur VALUES
 (9,1,1,7,1,6),
 (9,2,1,4,1,9),
 (9,3,1,6,2,8),
 (9,4,1,5,2,7),
 (9,5,1,2,3,14),
 (9,11,3,3,5,3),
 (9,12,3,2,6,4),
 (9,13,3,1,4,6),
 (9,14,3,2,6,3),
 (9,15,3,0,6,10);

-- MATCH 10
INSERT INTO stat_joueur VALUES
 (10,1,1,5,1,8),
 (10,2,1,3,2,7),
 (10,3,1,7,2,6),
 (10,4,1,6,1,5),
 (10,5,1,1,2,12),
 (10,11,3,4,4,4),
 (10,12,3,3,5,3),
 (10,13,3,2,4,7),
 (10,14,3,1,5,7),
 (10,15,3,0,6,11);

-- ============================================================
-- COACH IA, RECOMMANDATIONS & INTERACTIONS
-- ============================================================

INSERT INTO coach_ia (coach_ia_id, nom_modele, version, domaine, statut)
VALUES
 (1,'SENSAI-Tactician','1.0','Tactique','ACTIF'),
 (2,'SENSAI-Strategy','2.1','Macro-Game','ACTIF'),
 (3,'SENSAI-Behavior','1.4','Mental & Discipline','ACTIF');

INSERT INTO recommandation 
(recommandation_id, coach_ia_id, match_id, equipe_id, joueur_id, type, resume, details, statut)
VALUES
 (1,1,1,1,NULL,'TACTIQUE',
  'Améliorer la pression top-side en early game.',
  '{"focus":"top","comment":"Canna doit mieux contrôler la wave pour éviter les ganks tôt."}',
  'ENVOYEE'),

 (2,2,1,1,NULL,'STRATEGIQUE',
  'Manque de vision profonde avant les objectifs.',
  '{"vision_score_low":true,"zone":"Baron Nashor"}',
  'VALIDEE'),

 (3,1,2,1,2,'TACTIQUE',
  'Optimiser le pathing jungle de Yike.',
  '{"suggested_path":"red -> krugs -> mid gank","issue":"tempo perdu early"}',
  'ENVOYEE'),

 (4,3,2,1,NULL,'COMPORTEMENTALE',
  'Communication excellente, à encourager.',
  '{"comms":"positive","players":["Vladi","Targamas"]}',
  'VALIDEE'),

 (5,2,3,1,NULL,'STRATEGIQUE',
  'Macro-game trop passive après 15 minutes.',
  '{"problem":"no contest dragons","fix":"setup vision 40s before"}',
  'REJETEE'),

 (6,1,3,1,4,'TACTIQUE',
  'Caliste doit mieux gérer ses spikes d’items.',
  '{"timing":"mythic late","impact":"low dps in mid-game"}',
  'ENVOYEE'),

 (7,1,5,2,NULL,'TACTIQUE',
  'Meilleur positionnement en teamfight nécessaire.',
  '{"issue":"ADC exposé","player":"3XA"}',
  'IGNOREE'),

 (8,2,7,2,NULL,'STRATEGIQUE',
  'Bonne utilisation des timings Herald.',
  '{"heralds_taken":2,"comment":"excellent macro"}',
  'VALIDEE'),

 (9,3,9,1,3,'COMPORTEMENTALE',
  'Vladi montre une bonne adaptation mentale après la défaite précédente.',
  '{"focus":"resilience","observation":"tilt control"}',
  'VALIDEE'),

 (10,1,10,1,NULL,'TACTIQUE',
  'KC doit sécuriser plus vite la zone avant le Nashor.',
  '{"warning":"risque steal","team":"KC"}',
  'ENVOYEE');

INSERT INTO interaction_reco 
(interaction_id, recommandation_id, staff_id, action, commentaire)
VALUES
 (1,1,1,'VALIDEE','On va travailler le early top-side.'),
 (2,2,1,'VALIDEE','Bonne analyse macro.'),
 (3,3,2,'IGNOREE','On priorise un autre point en scrim.'),
 (4,5,1,'REJETEE','Pas aligné avec nos objectifs actuels.'),
 (5,6,2,'VALIDEE','Caliste a déjà commencé à corriger.'),
 (6,7,3,'IGNOREE','Pas prioritaire mentalement.'),
 (7,8,1,'VALIDEE','Très bon timing Herald.'),
 (8,9,3,'VALIDEE','Progression mentale notable.'),
 (9,10,2,'VALIDEE','Nashor setup sera revu en review.');
""")
                            
conn.commit()
conn.close()
print(f"OK → {DB}")
