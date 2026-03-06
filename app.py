import streamlit as st
import json
import os
import requests
import base64
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

# Recupero segreti da Streamlit Cloud
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"] # Es: "tuo-utente/tuo-repo"
FILE_PRESENZE = "presenze.csv"

utenti = {
    "simone": "boss79",
    "klaudia": "kla98",
    "leonardo": "leo123",
    "gianni": "gia77",
    "lorena": "lor88",
    "cristian": "cris99",
    "cristina": "cri35",
    "chiara": "chi34",
    "francesco": "fra56",
    "francescon": "fra07",
    "giulia": "giu04",
    "kristina": "kri36",
    "matteo": "mat35",
    "michela": "mic43",
    "raffaele": "raf21",
    "thomas": "tom45",
    "ugo": "ugo90",
    "valentina": "val75"
}

def invia_presenza_a_github(data_ev, evento, collaboratore):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. Prendo il file attuale per non cancellare le vecchie presenze
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        file_data = res.json()
        contenuto_vecchio = base64.b64decode(file_data["content"]).decode("utf-8")
        sha = file_data["sha"]
    else:
        contenuto_vecchio = "Data,Evento,Collaboratore,OraInvio\n"
        sha = None

    # 2. Aggiungo la nuova riga
    ora_invio = datetime.now().strftime("%d/%m/%Y %H:%M")
    nuova_riga = f"{data_ev},{evento},{collaboratore},{ora_invio}\n"
    nuovo_contenuto = contenuto_vecchio + nuova_riga
    
    # 3. Carico tutto su GitHub
    payload = {
        "message": f"Conferma da {collaboratore}",
        "content": base64.b64encode(nuovo_contenuto.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA APP ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff")
    user = st.text_input("Nome utente:").lower().strip()
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
    
    # Selezione Mese
    mesi = ["marzo.json", "aprile.json", "maggio.json"]
    esistenti = [m for m in mesi if os.path.exists(m)]
    scelta = st.sidebar.selectbox("Scegli mese:", esistenti)
    
    if scelta:
        with open(scelta, "r") as f:
            dati = json.load(f)
        
        st.header(f"📅 Programma {scelta.capitalize()}")
        for ev in dati:
            if username == "simone" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    
                    if st.button("CONFERMA PRESENZA", key=ev['nome']+ev['data']):
                        invia_presenza_a_github(ev['data'], ev['nome'], username.capitalize())
                        st.success("Presenza salvata nel registro!")

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
