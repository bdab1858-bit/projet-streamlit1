from bd import get_connection
import random
from datetime import date, time

conn = get_connection()
cur = conn.cursor()

# =========================
# 1️⃣ DEPARTEMENTS
# =========================
departements = [
    ("Informatique",),
    ("Mathématiques",),
    ("Electronique",),
]

cur.executemany(
    "INSERT INTO departement (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING",
    departements
)

# =========================
# 2️⃣ FORMATIONS (SANS nb_modules ❌)
# =========================
cur.execute("SELECT id_dept FROM departement ORDER BY id_dept")
dept_ids = [row[0] for row in cur.fetchall()]

formations = [
    ("Licence Informatique", dept_ids[0]),
    ("Master Informatique", dept_ids[0]),
]

cur.executemany(
    "INSERT INTO formation (nom, id_dept) VALUES (%s, %s)",
    formations
)

# =========================
# 3️⃣ PROFESSEURS (prenom EXISTE chez toi ✅)
# =========================
professeurs = []
for i in range(1, 11):
    professeurs.append((
        f"Prof{i}",
        f"Prenom{i}",
        random.choice(dept_ids),
        "Informatique"
    ))

cur.executemany(
    "INSERT INTO professeur (nom, prenom, id_dept, specialite) VALUES (%s, %s, %s, %s)",
    professeurs
)

# =========================
# 4️⃣ SALLES
# =========================
salles = []
for i in range(1, 31):
    salles.append((
        f"Salle {i}",
        random.choice([30, 50, 100, 200]),
        random.choice(["TD", "TP", "Amphi"]),
        "Bloc A"
    ))

cur.executemany(
    "INSERT INTO salle (nom, capacite, type, batiment) VALUES (%s, %s, %s, %s)",
    salles
)

# =========================
# 5️⃣ MODULES
# =========================
cur.execute("SELECT id_form FROM formation")
form_ids = [row[0] for row in cur.fetchall()]

modules = [
    ("Bases de Données", 3, form_ids[0]),
    ("Algorithmes", 4, form_ids[0]),
    ("IA", 3, form_ids[1]),
    ("Réseaux", 3, form_ids[1]),
]

cur.executemany(
    "INSERT INTO module (nom, credits, id_form) VALUES (%s, %s, %s)",
    modules
)

# =========================
# 6️⃣ ETUDIANTS (1000)
# =========================
etudiants = []
for i in range(1, 1001):
    etudiants.append((
        f"Nom{i}",
        f"Prenom{i}",
        random.choice(form_ids),
        2025
    ))

cur.executemany(
    "INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES (%s, %s, %s, %s)",
    etudiants
)

# =========================
# 7️⃣ INSCRIPTIONS
# =========================
cur.execute("SELECT id_etud FROM etudiant")
etud_ids = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id_module FROM module")
module_ids = [row[0] for row in cur.fetchall()]

inscriptions = []
for etud in etud_ids:
    for mod in random.sample(module_ids, k=2):
        inscriptions.append((etud, mod))

cur.executemany(
    "INSERT INTO inscription (id_etud, id_module) VALUES (%s, %s) ON CONFLICT DO NOTHING",
    inscriptions
)

# =========================
# 8️⃣ CRENEAUX
# =========================
creneaux = []
dates = [date(2026, 1, 20), date(2026, 1, 21)]
heures = [
    (time(9, 0), time(11, 0)),
    (time(14, 0), time(16, 0)),
]

for d in dates:
    for h in heures:
        creneaux.append((d, h[0], h[1]))

cur.executemany(
    "INSERT INTO creneau (date_exam, heure_debut, heure_fin) VALUES (%s, %s, %s)",
    creneaux
)

# =========================
# FIN
# =========================
conn.commit()
cur.close()
conn.close()

print("✅ BASE DE DONNÉES REMPLIE AVEC SUCCÈS")
