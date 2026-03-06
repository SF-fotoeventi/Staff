import streamlit as st
import json
import os

st.set_page_config(page_title="Gestione Staff Sicura", page_icon="🔐")

# --- DATABASE UTENTI (Password) ---
# Puoi cambiare le password qui sotto come preferisci
utenti = {
    "Simone": "boss79",
    "Klaudia": "k98",
    "Leonardo": "leo123",
    "Thomas": "thom00",
    "Gianni": "giani77",
    "Lorena": "lori88",
    "Cristian": "cris99",
    "Cristina": "cri35",
    "Chiara": "chi34",
    "Francesco": "fra56",
    "FrancescoN": "fra07",
    "Giulia": "giu04",
    "Kristina": "kri36",
    "Matteo": "mat35",
    "Michela": "mic43",
    "Raffaele": "raf21",
    "Tomas": "tom45",
    "Ugo": "ugo90",
    "Valentina": "val75",
}

def carica_mese(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return []

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato")
    user = st.text_input("Nome utente (es. klaudia):").lower()
    password = st.text_input("Password:", type="password")
    
    if st.button("Entra"):
        if user in utenti and utenti[user] == password:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Nome utente o password errati!")
else:
    username = st.session_state.username
    st.sidebar.title(f"👋 {username.capitalize()}")
    
    mesi_disponibili = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_disponibili if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Nessun mese caricato.")
    else:
        scelta = st.sidebar.selectbox("Scegli il mese:", file_esistenti)
        dati_mese = carica_mese(scelta)
        
        st.header(f"📅 Impegni di {scelta.replace('.json', '').capitalize()}")
        
        for ev in dati_mese:
            # L'admin vede tutto, il collaboratore vede solo il suo
            if username == "admin" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    st.button("Conferma Presenza", key=ev['nome']+scelta)

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
