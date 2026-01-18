import streamlit as st

st.set_page_config(
    page_title="Optimisation Examens",
    page_icon="🎓",
    layout="centered"
)

# Init session
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# 🚫 HIDE SIDEBAR
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Plateforme d’Optimisation des Examens")
st.caption("Projet universitaire")

st.markdown("""
### Bienvenue 👋  
Veuillez vous connecter pour accéder à votre espace.
""")

if st.button("🔐 Se connecter"):
    st.switch_page("pages/login.py")
