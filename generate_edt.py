import psycopg2
import random

def get_connection():
    return psycopg2.connect(
        host="dpg-d5lsqtumcj7s73bm6k1g-a.oregon-postgres.render.com",
        database="edt_universitaire",
        user="admin",
        password="8ne6EUYzDjKXxv3d9axZElqbrV7w0skv",
        port="5432"
    )
def generate_exam_schedule():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Charger TOUS les examens avec les noms et l'HEURE (via JOIN creneau)
    cur.execute("""
        SELECT 
            e.id_examen, m.nom, e.id_form, e.etat, e.id_salle, 
            e.id_creneau, e.date_examen, s.nom, c.heure_debut
        FROM examen e 
        JOIN module m ON e.id_module = m.id_module
        LEFT JOIN salle s ON e.id_salle = s.id_salle
        LEFT JOIN creneau c ON e.id_creneau = c.id_creneau
    """)
    examens_db = cur.fetchall()

    # 2. Charger les ressources disponibles
    cur.execute("SELECT id_creneau, date_exam, heure_debut FROM creneau")
    creneaux_db = cur.fetchall()
    
    cur.execute("SELECT id_salle, nom, capacite FROM salle")
    salles = cur.fetchall()

    cur.execute("SELECT id_prof, nom FROM professeur WHERE role = 'enseignant'")
    enseignants = cur.fetchall()

    cur.execute("SELECT id_form, COUNT(id_etud) FROM etudiant GROUP BY id_form")
    etudiants_par_form = dict(cur.fetchall())

    salle_occupee = set()     
    formation_occupee = set() 
    prof_occupe = set()
    planning_final = []
    a_generer = []

    # 3. BLOQUER les ressources des examens déjà "Validé"
    for id_ex, nom_mod, id_f, etat, id_s, id_c, d_ex, nom_s, h_debut in examens_db:
        if etat == 'Validé' and id_s and id_c:
            salle_occupee.add((id_c, id_s))
            formation_occupee.add((id_c, id_f))
            
            # Récupérer le surveillant actuel
            cur.execute("""
                SELECT p.id_prof, p.nom 
                FROM surveillance sv 
                JOIN professeur p ON sv.id_prof = p.id_prof 
                WHERE sv.id_examen = %s
            """, (id_ex,))
            prof_data = cur.fetchone()
            p_id = prof_data[0] if prof_data else None
            p_nom = prof_data[1] if prof_data else "Aucun"
            
            if p_id: prof_occupe.add((id_c, p_id))

            planning_final.append({
                "id_examen": id_ex, "module": nom_mod, "id_salle": id_s, "salle_nom": nom_s,
                "date": str(d_ex), "heure": str(h_debut), "id_creneau": id_c, 
                "id_prof": p_id, "surveillant": p_nom, "etat": "Validé"
            })
        else:
            # On stocke pour générer plus tard
            a_generer.append((id_ex, nom_mod, id_f))

    # 4. GÉNÉRER UNIQUEMENT POUR "EN ATTENTE"
    random.shuffle(creneaux_db)
    for id_exam, nom_mod, id_form in a_generer:
        nb_participants = etudiants_par_form.get(id_form, 0)
        placed = False
        
        for id_c, d_exam, h_exam in creneaux_db:
            if placed: break
            if (id_c, id_form) in formation_occupee: continue
            
            for id_s, nom_salle, cap in salles:
                if (id_c, id_s) not in salle_occupee and nb_participants <= cap:
                    # Trouver prof libre
                    id_surveillant, surveillant_nom = None, "Aucun"
                    for id_p, nom_p in enseignants:
                        if (id_c, id_p) not in prof_occupe:
                            id_surveillant, surveillant_nom = id_p, nom_p
                            prof_occupe.add((id_c, id_p))
                            break
                    
                    planning_final.append({
                        "id_examen": id_exam, "module": nom_mod, "id_salle": id_s, "salle_nom": nom_salle,
                        "date": str(d_exam), "heure": str(h_exam), "id_creneau": id_c,
                        "id_prof": id_surveillant, "surveillant": surveillant_nom, "etat": "En attente"
                    })
                    salle_occupee.add((id_c, id_s))
                    formation_occupee.add((id_c, id_form))
                    placed = True
                    break
    
    cur.close()
    conn.close()
    return planning_final

def persist_schedule_to_db(data):
    conn = get_connection()
    cur = conn.cursor()
    try:
        for row in data:
            # On ne met à jour QUE ceux qui sont 'En attente'
            if row['etat'] == 'En attente':
                cur.execute("""
                    UPDATE examen 
                    SET id_salle = %s, id_creneau = %s, date_examen = %s 
                    WHERE id_examen = %s
                """, (row['id_salle'], row['id_creneau'], row['date'], row['id_examen']))
                
                if row['id_prof']:
                    # On remplace la surveillance pour cet examen
                    cur.execute("DELETE FROM surveillance WHERE id_examen = %s", (row['id_examen'],))
                    cur.execute("INSERT INTO surveillance (id_prof, id_examen) VALUES (%s, %s)", 
                                (row['id_prof'], row['id_examen']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erreur: {e}")
    finally:
        cur.close()
        conn.close()
