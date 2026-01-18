import streamlit as st
import pandas as pd
from bd import get_connection

# ================== CONFIGURATION ==================
st.set_page_config(
    page_title="Doyen | Supervision Globale",
    page_icon="📊",
    layout="wide"
)
# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# 🚫 Masquer la sidebar et styles
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #F8F9FA; }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.get('user_role') != 'doyen':
    st.error("Accès refusé.")
    st.stop()

# ================== RÉCUPÉRATION DES DONNÉES ==================
try:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Infos Doyen
    cur.execute("SELECT nom FROM professeur WHERE id_prof = %s", (st.session_state.get("user_id"),))
    res_doyen = cur.fetchone()
    doyen_nom = res_doyen[0] if res_doyen else "Doyen"

    # 2. Liste des départements
    cur.execute("SELECT id_dept, nom FROM departement ORDER BY nom")
    depts_data = cur.fetchall()
    dict_depts = {d[1]: d[0] for d in depts_data} 
    liste_noms_depts = list(dict_depts.keys())

    # 3. Nombre TOTAL de salles dans l'université
    cur.execute("SELECT COUNT(*) FROM salle")
    total_salles_uni = cur.fetchone()[0]

    # ================== HEADER ==================
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px;">
        <h1>📊 Supervision du Planning Global</h1>
        <p>Utilisateur : <b>Dr. {doyen_nom}</b> (Doyen)</p>
    </div>
    """, unsafe_allow_html=True)

    # ================== FILTRE & STATS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 Analyse par département")
    
    dept_nom_choisi = st.selectbox("Choisir le département à superviser :", ["Tous les départements"] + liste_noms_depts)

    # Calcul des salles réservées pour le département choisi
    if dept_nom_choisi == "Tous les départements":
        cur.execute("SELECT COUNT(DISTINCT id_salle) FROM examen WHERE id_salle IS NOT NULL")
    else:
        id_filtre = dict_depts[dept_nom_choisi]
        cur.execute("SELECT COUNT(DISTINCT id_salle) FROM examen WHERE id_salle IS NOT NULL AND id_dept = %s", (id_filtre,))
    
    salles_reservees = cur.fetchone()[0]

    # Affichage des KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Salles Université", total_salles_uni)
    with col2:
        st.metric(f"Salles utilisées ({dept_nom_choisi})", salles_reservees)
    with col3:
        dispo = total_salles_uni - salles_reservees
        st.metric("Salles encore libres", dispo if dispo >= 0 else 0)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ================== TABLEAU DU PLANNING ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Détails du Planning")

    query = """
        SELECT 
            d.nom AS "Département",
            f.nom AS "Formation",
            m.nom AS "Module",
            s.nom AS "Salle",
            c.date_exam AS "Date",
            c.heure_debut AS "Heure",
            p.nom AS "Surveillant",
            e.etat AS "Statut"
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN departement d ON e.id_dept = d.id_dept
        JOIN formation f ON e.id_form = f.id_form
        LEFT JOIN salle s ON e.id_salle = s.id_salle
        LEFT JOIN creneau c ON e.id_creneau = c.id_creneau
        LEFT JOIN surveillance surv ON e.id_examen = surv.id_examen
        LEFT JOIN professeur p ON surv.id_prof = p.id_prof
    """

    if dept_nom_choisi != "Tous les départements":
        id_filtre = dict_depts[dept_nom_choisi]
        query += " WHERE d.id_dept = %s"
        cur.execute(query, (id_filtre,))
    else:
        cur.execute(query)

    rows = cur.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=["Département", "Formation", "Module", "Salle", "Date", "Heure", "Surveillant", "Statut"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aucun examen trouvé.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur : {e}")

# ================== DÉCONNEXION ==================
if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")
