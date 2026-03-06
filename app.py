import streamlit as st
import json
import os
import requests
import base64
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PRESENZE = "presenze.csv"

utenti = {
    "simone": "boss79", "klaudia": "kla98", "leonardo": "leo123", "gianni": "gia77",
    "lorena": "lor88", "cristian": "cris99", "cristina": "cri35", "chiara": "chi34",
    "francesco": "fra56", "francescon": "fra07", "giulia": "giu04", "kristina": "kri36",
    "matteo": "mat35", "michela": "mic43", "raffaele": "raf21", "thomas": "tom45",
    "ugo": "ugo90", "valentina": "val75"
}

def invia_presenza_a_github(data_ev, evento, collaboratore):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        file_data = res.json()
        contenuto_vecchio = base64.b64decode(file_data["content"]).decode("utf-8")
        sha = file_data["sha"]
    else:
        contenuto_vecchio = "Data,Evento,Collaboratore,OraInvio\n"
        sha = None

    ora_invio = datetime.now().strftime("%d/%m/%Y %H:%M")
    nuova_riga = f"{data_ev},{evento},{collaboratore},{ora_invio}\n"
    nuovo_contenuto = contenuto_vecchio + nuova_riga
    
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
    st.title("🔐 Accesso Staff FotoEventi")
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
    
    # --- AREA ADMIN (SOLO PER SIMONE) ---
    if username == "simone":
        st.sidebar.divider()
        st.sidebar.subheader("🛠️ Area Admin")
        
        # Scarico i dati correnti per l'admin
        url_raw = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
        res_p = requests.get(url_raw)
        
        if res_p.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(res_p.text))
            
            # Bottone per scaricare il file Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Presenze')
            
            st.sidebar.download_button(
                label="📥 Scarica Report Excel",
                data=output.getvalue(),
                file_name=f"Presenze_Staff_{datetime.now().strftime('%d_%m')}.xlsx",
                mime="application/vnd.ms-excel"
            )
        st.sidebar.divider()

    mesi = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    esistenti = [m for m in mesi if os.path.exists(m)]
    scelta = st.sidebar.selectbox("Scegli mese:", esistenti)
    
    if scelta:
        with open(scelta, "r") as f:
            dati = json.load(f)
        
        url_raw = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
        res_p = requests.get(url_raw)
        registro_presenze = res_p.text if res_p.status_code == 200 else ""

        st.header(f"📅 Programma {scelta.replace('.json', '').capitalize()}")
        
        for ev in dati:
            if username == "simone" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write("*Stato Convocazioni:*")
                    
                    for persona in ev["staff"]:
                        check = f"{ev['data']},{ev['nome']},{persona.capitalize()}"
                        if check in registro_presenze:
                            st.write(f"🟢 {persona} (Confermato)")
                        else:
                            st.write(f"🔴 {persona} (In attesa...)")
                    
                    st.divider()
                    
                    chiave_utente = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                    if chiave_utente not in registro_presenze:
                        if st.button("CONFERMA PRESENZA", key=ev['nome']+ev['data']+scelta):
                            invia_presenza_a_github(ev['data'], ev['nome'], username.capitalize())
                            st.success("Presenza salvata!")
                            st.rerun()
                    else:
                        st.info("Hai già confermato la tua presenza.")

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
