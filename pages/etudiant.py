import streamlit as st
import pandas as pd
from bd import get_connection

# ================== ROLE CHECK ==================
if st.session_state.get("user_role") != "etudiant":
    st.error("Accès refusé. Cette page est réservée aux étudiants.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Étudiant | Mon Planning",
    page_icon="🎓",
    layout="wide"
)

# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ================== STYLE ==================
st.markdown("""
<style>
.stApp { background-color: #F1F4F9; }
.card {
    background-color: white;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    border-left: 6px solid #4CAF50;
    margin-bottom: 20px;
}
.header {
    background: linear-gradient(90deg, #4CAF50, #66BB6A);
    padding: 28px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}
.info-box {
    background-color: #E8F5E9;
    padding: 16px;
    border-radius: 10px;
    border-left: 4px solid #4CAF50;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
etudiant_id = st.session_state.get("user_id")

try:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Infos Étudiant + Formation + Département
    cur.execute("""
        SELECT e.nom, e.prenom, f.nom, d.nom
        FROM etudiant e
        JOIN formation f ON e.id_form = f.id_form
        JOIN departement d ON f.id_dept = d.id_dept
        WHERE e.id_etud = %s
    """, (etudiant_id,))
    etud_info = cur.fetchone()

    if etud_info:
        nom_etud, prenom_etud, nom_form, nom_dept = etud_info
        st.markdown(f"""
        <div class="header">
            <h1>🎓 Mon Espace Examen</h1>
            <p>Étudiant : <b>{prenom_etud} {nom_etud}</b></p>
        </div>
        <div class="info-box">
            🏛️ <b>Département :</b> {nom_dept} | 📚 <b>Formation :</b> {nom_form}
        </div>
        """, unsafe_allow_html=True)

    # ================== EXAMENS VALIDÉS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Calendrier des Examens")
    st.info("💡 Seuls les examens validés par l'administration sont affichés ci-dessous.")

    # Requête SQL : Filtre par id_form de l'étudiant ET état = 'Validé'
    cur.execute("""
        SELECT 
            m.nom AS "Module",
            s.nom AS "Salle",
            c.date_exam AS "Date",
            c.heure_debut AS "Heure",
            d.nom AS "Département"
        FROM examen ex
        JOIN module m ON ex.id_module = m.id_module
        JOIN departement d ON ex.id_dept = d.id_dept
        JOIN formation f ON ex.id_form = f.id_form
        JOIN salle s ON ex.id_salle = s.id_salle
        JOIN creneau c ON ex.id_creneau = c.id_creneau
        JOIN etudiant et ON et.id_form = f.id_form
        WHERE et.id_etud = %s AND ex.etat = 'Validé'
        ORDER BY c.date_exam, c.heure_debut
    """, (etudiant_id,))

    exams = cur.fetchall()

    if exams:
        df = pd.DataFrame(exams, columns=["Module", "Salle", "Date", "Heure", "Département"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aucun examen n'a encore été validé pour votre formation.")

    st.markdown('</div>', unsafe_allow_html=True)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")

# ================== LOGOUT ==================
if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")

st.caption("Projet universitaire — Interface de consultation étudiante")
