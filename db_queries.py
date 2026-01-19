import psycopg2

def get_connection():
    return psycopg2.connect(
        host="dpg-d5lsqtumcj7s73bm6k1g-a.oregon-postgres.render.com",
        database="edt_universitaire",
        user="admin",
        password="8ne6EUYzDjKXxv3d9axZElqbrV7w0skv",
        port="5432"
    )

def count_examens():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM examen")
    res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res

def count_salles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM salle")
    res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res

def count_salles_utilisees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT id_salle) FROM examen WHERE id_salle IS NOT NULL")
    res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res

def count_conflicts():
    conn = get_connection()
    cur = conn.cursor()
    # On ne compte les conflits QUE pour les examens qui ont une salle et un créneau assigné
    cur.execute("""
        SELECT COUNT(*) 
        FROM examen e1
        JOIN examen e2 ON e1.id_examen < e2.id_examen
        WHERE e1.id_creneau = e2.id_creneau 
        AND e1.date_examen = e2.date_examen
        AND (e1.id_salle = e2.id_salle OR e1.id_form = e2.id_form)
        AND e1.id_salle IS NOT NULL 
        AND e1.id_creneau IS NOT NULL
    """)
    res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res
    
def exams_per_day():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.date_exam, COUNT(e.id_examen) 
        FROM examen e
        JOIN creneau c ON e.id_creneau = c.id_creneau
        GROUP BY c.date_exam ORDER BY c.date_exam
    """)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res
