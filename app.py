import streamlit as st
import json
import os

st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

utenti = {
    "Simone": "boss79",
    "Klaudia": "kla98",
    "Leonardo": "leo123",
    "Gianni": "gia77",
    "Lorena": "lor88",
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
    "Thomas": "tom45",
    "Ugo": "ugo90",
    "Valentina": "val75"
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
    mesi_previsti = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_previsti if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Nessun piano eventi caricato.")
    else:
        scelta_file = st.sidebar.selectbox("Scegli il mese:", file_esistenti)
        dati_mese = carica_mese(scelta_file)
        st.header(f"📅 Programma di {scelta_file.replace('.json', '').capitalize()}")
        
        trovati = False
        for ev in dati_mese:
            if username == "simone" or username.capitalize() in ev["staff"]:
                trovati = True
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    # AGGIORNATO: Key unica usando nome + data + file
                    st.button("Conferma Presenza", key=ev['nome'] + ev['data'] + scelta_file)
        
        if not trovati and username != "simone":
            st.info("Non ci sono convocazioni per te.")

    if st.sidebar.button("Esci / Logout"):
        st.session_state.autenticato = False
        st.rerun()
