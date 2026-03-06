import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Gare Marzo", layout="centered")

# --- DATABASE SEMPLIFICATO (Lo modificheremo insieme) ---
# Qui ho inserito alcuni dati presi dalla tua foto
eventi_marzo = [
    {"data": "15 Marzo", "nome": "BOLOGNA JHONNY", "staff": ["Leonardo", "Thomas"]},
    {"data": "15 Marzo", "nome": "MSP AURORA", "staff": ["Gianni", "Lorena"]},
    {"data": "22 Marzo", "nome": "DANZA VEN", "staff": ["Klaudia", "Cristian"]},
    {"data": "29 Marzo", "nome": "MILANO JHONNY", "staff": ["Kristina", "Francesco", "Matteo"]},
]

# --- LOGIN SEMPLICE ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff")
    user = st.text_input("Inserisci il tuo nome (es. Klaudia, Leonardo, Admin):")
    if st.button("Entra"):
        st.session_state.autenticato = True
        st.session_state.username = user
        st.rerun()
else:
    # --- INTERFACCIA APP ---
    username = st.session_state.username
    st.title(f"📅 Ciao {username}!")
    st.write("Ecco i tuoi impegni per il mese di Marzo:")

    # Filtriamo gli eventi in base a chi entra
    for ev in eventi_marzo:
        if username.lower() == "admin" or username in ev["staff"]:
            with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                st.write(f"*Team:* {', '.join(ev['staff'])}")
                if st.button(f"Confermo la presenza per {ev['nome']}", key=ev['nome']):
                    st.success("Presenza segnata! (Nota: per ora è solo una prova)")

    if st.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
