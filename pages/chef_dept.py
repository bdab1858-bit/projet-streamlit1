import streamlit as st
import pandas as pd
from bd import get_connection

st.set_page_config(page_title="Chef de département", page_icon="🏫", layout="wide")

# ROLE CHECK
if st.session_state.get('user_role') != 'chef_dept':
    st.error("Accès refusé.")
    st.stop()

chef_id = st.session_state.get("user_id")
# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# --- RÉCUPÉRATION DES DONNÉES ---
try:
    conn = get_connection()
    cur = conn.cursor()

    # 1. Infos du Chef et son département
    cur.execute("""
        SELECT p.nom, p.specialite, p.id_dept 
        FROM professeur p WHERE p.id_prof = %s
    """, (chef_id,))
    nom_chef, specialite, id_dept_chef = cur.fetchone()

    # 2. Récupération des Examens du département avec Salle et Surveillant
    # On utilise LEFT JOIN pour voir l'examen même si le surveillant n'est pas encore assigné
    cur.execute("""
        SELECT 
            e.id_examen,
            m.nom AS module_nom,
            s.nom AS salle_nom,
            c.date_exam,
            c.heure_debut,
            p_surv.nom AS surveillant_nom,
            e.etat
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        LEFT JOIN salle s ON e.id_salle = s.id_salle
        LEFT JOIN creneau c ON e.id_creneau = c.id_creneau
        LEFT JOIN surveillance surv ON e.id_examen = surv.id_examen
        LEFT JOIN professeur p_surv ON surv.id_prof = p_surv.id_prof
        WHERE e.id_dept = %s
    """, (id_dept_chef,))
    
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "Module", "Salle", "Date", "Heure", "Surveillant", "Statut"])

    # --- HEADER ---
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #5B9DFF, #6EC6FF); padding: 25px; border-radius: 15px; color: white;">
        <h1>🏫 Département : {specialite}</h1>
        <p>Chef de département : <b>{nom_chef}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # --- TABLEAU DES EXAMENS ---
    st.subheader("📋 Planning des examens du département")
    if not df.empty:
        # On remplace les valeurs vides par "Non assigné"
        df.fillna("Non assigné", inplace=True)
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
        
        # --- VALIDATION INDIVIDUELLE ---
        st.subheader("✅ Validation des examens")
        exam_to_validate = st.selectbox("Choisir un examen à valider pour le Doyen", df["Module"].unique())
        
        if st.button(f"Valider l'examen : {exam_to_validate}"):
            cur.execute("UPDATE examen SET etat = 'Validé' WHERE id_dept = %s AND id_module = (SELECT id_module FROM module WHERE nom = %s)", (id_dept_chef, exam_to_validate))
            conn.commit()
            st.success(f"L'examen de {exam_to_validate} est maintenant visible comme 'Validé' pour le Doyen.")
            st.rerun()
    else:
        st.info("Aucun examen trouvé pour votre département.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur : {e}")

if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")
