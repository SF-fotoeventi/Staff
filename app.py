import streamlit as st
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

# --- DATABASE UTENTI ---
utenti = {
    "simone": "boss79",
    "claudia": "k98",
    "leonardo": "leo123",
    "tommaso": "thom00",
    "gianni": "giani77",
    "lorena": "lori88",
    "cristiano": "cris99",
    "cristina": "cri35",
    "chiara": "chi34",
    "francesco": "fra56",
    "francescon": "fra07",
    "giulia": "giu04",
    "kristina": "kri36",
    "matteo": "mat35",
    "michela": "mic43",
    "raffaele": "raf21",
    "tomas": "tom45",
    "ugo": "ugo90",
    "valentina": "va175"
}

def carica_mese(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return []

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato Staff")
    user = st.text_input("Nome utente (minuscolo):").lower().strip()
    password = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if user in utenti and utenti[user] == password:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Credenziali errate.")
else:
    username = st.session_state.username
    st.sidebar.title(f"👋 Ciao {username.capitalize()}")
    mesi_disponibili = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_disponibili if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Nessun piano eventi caricato.")
    else:
        scelta = st.sidebar.selectbox("Scegli il mese:", file_esistenti)
        dati = carica_mese(scelta)
        st.header(f"📅 Programma di {scelta.replace('.json', '').capitalize()}")
        for ev in dati:
            if username == "simone" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    st.button("Conferma Presenza", key=ev['nome']+scelta)

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
