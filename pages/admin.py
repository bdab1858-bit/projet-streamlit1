import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))

try:
    from generate_edt import generate_exam_schedule, persist_schedule_to_db
    from db_queries import (
        count_examens, count_salles, count_conflicts, 
        count_salles_utilisees, exams_per_day
    )
except ImportError as e:
    st.error(f"Fichier manquant : {e}")
    st.stop()

st.set_page_config(page_title="Admin | Dashboard", layout="wide")

st.markdown('<div style="background:#5B9DFF;padding:20px;border-radius:15px;color:white;"><h1>🛠 Administrateur des Examens</h1></div>', unsafe_allow_html=True)
# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)
# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Total Examens", count_examens())
c2.metric("Conflits", count_conflicts())
c3.metric("Salles Occupées", f"{count_salles_utilisees()} / {count_salles()}")

st.write("---")

def highlight_status(row):
    color = '#d4edda' if row['etat'] == 'Validé' else '#fff3cd'
    return [f'background-color: {color}'] * len(row)

if st.button("⚙️ Générer / Actualiser les examens"):
    with st.spinner("Planification en cours..."):
        data = generate_exam_schedule() 
        
        if data:
            df = pd.DataFrame(data)
            # Affichage de TOUTES les colonnes demandées
            cols = ["module", "salle_nom", "surveillant", "date", "heure", "etat"]
            
            st.dataframe(
                df[cols].style.apply(highlight_status, axis=1), 
                use_container_width=True
            )
            
            persist_schedule_to_db(data)
            st.success("Base de données mise à jour ! (Les examens validés n'ont pas été modifiés)")
        else:
            st.error("Aucune donnée générée.")

st.subheader("📊 Répartition par jour")
rows = exams_per_day()
if rows:
    chart_df = pd.DataFrame(rows, columns=["Date", "Nombre"])
    st.bar_chart(chart_df.set_index("Date"))
    # ================== LOGOUT ==================
if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")
