import streamlit as st
import json
import os
import requests
import base64
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Staff FotoEventi", page_icon="📸", layout="centered")

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

# Funzione veloce per aggiornare GitHub
def aggiorna_github(data_ev, evento, collaboratore, azione="aggiungi"):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        f_data = res.json()
        cont = base64.b64decode(f_data["content"]).decode("utf-8")
        sha = f_data["sha"]
    else:
        cont = "Data,Evento,Collaboratore,OraInvio\n"
        sha = None

    linee = cont.splitlines()
    nuove_linee = [linee[0]]
    chiave = f"{data_ev},{evento},{collaboratore}"
    
    for l in linee[1:]:
        if chiave not in l:
            nuove_linee.append(l)
    
    if azione == "aggiungi":
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")

    nuovo_cont = "\n".join(nuove_linee) + "\n"
    payload = {"message": f"{azione} {collaboratore}", "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), "sha": sha}
    requests.put(url, json=payload, headers=headers)

# --- INIZIALIZZAZIONE MEMORIA LOCALE ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "registro_locale" not in st.session_state:
    # Scarichiamo il registro solo una volta all'avvio
    url_raw = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
    res = requests.get(url_raw)
    st.session_state.registro_locale = res.text if res.status_code == 200 else ""

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff")
    user = st.text_input("Nome:").lower().strip()
    pwd = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if user in utenti and utenti[user] == pwd:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
else:
    username = st.session_state.username
    st.sidebar.title(f"👋 {username.capitalize()}")
    
    # Area Admin (Simone)
    if username == "simone":
        if st.sidebar.button("📥 Scarica Excel"):
            df = pd.read_csv(StringIO(st.session_state.registro_locale))
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.sidebar.download_button("Clicca qui per il download", out.getvalue(), "Presenze.xlsx")

    mesi = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    esistenti = [m for m in mesi if os.path.exists(m)]
    scelta = st.sidebar.selectbox("Mese:", esistenti)
    
    if scelta:
        with open(scelta, "r") as f:
            dati = json.load(f)
        
        st.header(f"📅 {scelta.replace('.json', '').capitalize()}")
        
        for ev in dati:
            if username == "simone" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    for p in ev["staff"]:
                        check = f"{ev['data']},{ev['nome']},{p.capitalize()}"
                        # Controlla nella memoria locale (veloce)
                        if check in st.session_state.registro_locale:
                            st.write(f"🟢 {p} (Confermato)")
                        else:
                            st.write(f"🔴 {p} (In attesa...)")
                    
                    chiave_u = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                    
                    if chiave_u not in st.session_state.registro_locale:
                        if st.button("CONFERMA", key="add"+ev['nome']+ev['data']):
                            # Aggiorna subito la memoria locale
                            st.session_state.registro_locale += chiave_u + "\n"
                            # Invia a GitHub senza bloccare l'utente
                            aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "aggiungi")
                            st.rerun()
                    else:
                        if st.button("❌ ANNULLA", key="rem"+ev['nome']+ev['data']):
                            # Rimuove subito dalla memoria locale
                            st.session_state.registro_locale = st.session_state.registro_locale.replace(chiave_u + "\n", "")
                            # Invia a GitHub
                            aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "rimuovi")
                            st.rerun()

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
