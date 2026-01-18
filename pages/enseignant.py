import streamlit as st
import pandas as pd
from bd import get_connection

# ================== ROLE CHECK ==================
if st.session_state.get("user_role") != "enseignant":
    st.error("Accès refusé.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Enseignant | Examens",
    page_icon="👨‍🏫",
    layout="wide"
)

# ================== STYLE & HIDE SIDEBAR ==================
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #F1F4F9; }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.05);
        border-left: 6px solid #5B9DFF;
        margin-bottom: 20px;
    }
    .header {
        background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
        padding: 25px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
    }
    .kpi { font-size: 34px; font-weight: bold; color: #5B9DFF; }
    .info-box {
        background-color: #E3F2FD;
        padding: 16px;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ================== HEADER & DATA ==================
prof_id = st.session_state.get("user_id")

try:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Infos Enseignant + son Module
    cur.execute("""
        SELECT p.nom, d.nom, p.nom_module, p.id_module
        FROM professeur p
        JOIN departement d ON p.id_dept = d.id_dept
        WHERE p.id_prof = %s
    """, (prof_id,))
    prof_info = cur.fetchone()
    
    if prof_info:
        prof_nom, dept_nom, module_enseigne, id_module_prof = prof_info

        st.markdown(f"""
        <div class="header">
            <h1>👨‍🏫 Bienvenue, {prof_nom}</h1>
            <p>Département : <b>{dept_nom}</b> | Module : <b>{module_enseigne if module_enseigne else 'Non assigné'}</b></p>
        </div>
        """, unsafe_allow_html=True)

    # ================== KPI (Calcul dynamique) ==================
    # Count examens du module
    cur.execute("SELECT COUNT(*) FROM examen WHERE id_module = %s", (id_module_prof,))
    nb_exams = cur.fetchone()[0]

    # Count surveillances assignées
    cur.execute("SELECT COUNT(*) FROM surveillance WHERE id_prof = %s", (prof_id,))
    nb_surv = cur.fetchone()[0]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card"><h3>📝 Examens de mon module</h3><div class="kpi">{nb_exams}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><h3>👁️ Mes Surveillances</h3><div class="kpi">{nb_surv}</div></div>', unsafe_allow_html=True)

    # ================== TABLEAU 1 : SES EXAMENS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planning des examens de mon module")
    
    cur.execute("""
        SELECT m.nom, s.nom, c.date_exam, c.heure_debut, e.etat
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        LEFT JOIN salle s ON e.id_salle = s.id_salle
        LEFT JOIN creneau c ON e.id_creneau = c.id_creneau
        WHERE e.id_module = %s
        ORDER BY c.date_exam
    """, (id_module_prof,))
    
    rows_exam = cur.fetchall()
    if rows_exam:
        df_ex = pd.DataFrame(rows_exam, columns=["Module", "Salle", "Date", "Heure", "Statut"])
        st.dataframe(df_ex, use_container_width=True)
    else:
        st.info("Aucun examen prévu pour votre module.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ================== TABLEAU 2 : SES SURVEILLANCES ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🛡️ Mes Surveillances Assignées")
    
    cur.execute("""
        SELECT m.nom, s.nom, c.date_exam, c.heure_debut
        FROM surveillance surv
        JOIN examen e ON surv.id_examen = e.id_examen
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN creneau c ON e.id_creneau = c.id_creneau
        WHERE surv.id_prof = %s
        ORDER BY c.date_exam
    """, (prof_id,))
    
    rows_surv = cur.fetchall()
    if rows_surv:
        df_surv = pd.DataFrame(rows_surv, columns=["Examen à surveiller", "Salle", "Date", "Heure"])
        st.table(df_surv) # Utilisation de st.table pour une vue plus claire des surveillances
    else:
        st.success("Vous n'avez aucune surveillance assignée pour le moment.")
    st.markdown('</div>', unsafe_allow_html=True)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur de connexion : {e}")

# ================== LOGOUT ==================
if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")
