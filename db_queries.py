import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost", database="edt_universitaire",
        user="postgres", password="0000", port="5432"
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
    """Compte les examens de la même formation au même créneau"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT e.id_creneau, mf.id_form
            FROM examen e
            JOIN module_formation mf ON e.id_module = mf.id_module
            WHERE e.id_creneau IS NOT NULL
            GROUP BY e.id_creneau, mf.id_form
            HAVING COUNT(*) > 1
        ) as sub
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
