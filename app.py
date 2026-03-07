import streamlit as st
import json
import requests
import base64
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Staff FotoEventi", page_icon="📸", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main {margin-top: -50px;}
        .month-header {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
            border-left: 5px solid #ff4b4b;
            margin-bottom: 20px;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
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

def aggiorna_github(data_ev, evento, collaboratore, azione="aggiungi"):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        f_data = res.json()
        cont = base64.b64decode(f_data["content"]).decode("utf-8")
        sha = f_data["sha"]
        linee = cont.splitlines()
        nuove_linee = [linee[0]]
        chiave = f"{data_ev},{evento},{collaboratore}"
        for l in linee[1:]:
            if chiave not in l: nuove_linee.append(l)
        if azione == "aggiungi":
            nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")
        nuovo_cont = "\n".join(nuove_linee) + "\n"
        payload = {"message": f"{azione} {collaboratore}", "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), "sha": sha}
        requests.put(url, json=payload, headers=headers)

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

# Caricamento presenze (Sempre fresco)
url_p = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
res_p = requests.get(url_p, headers={"Cache-Control": "no-cache"})
st.session_state.registro_locale = res_p.text if res_p.status_code == 200 else ""

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff FotoEventi")
    user = st.text_input("Nome:").lower().strip()
    pwd = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if user in utenti and utenti[user] == pwd:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else: st.error("Credenziali errate.")
else:
    username = st.session_state.username
    st.title(f"👋 Ciao {username.capitalize()}!")
    if st.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()

    st.divider()

    # --- LOGICA DI AUTODETEZIONE DEI FILE ---
    # Chiedo a GitHub la lista reale dei file nel repo
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/"
    res_files = requests.get(api_url, headers={"Authorization": f"token {GITHUB_TOKEN}", "Cache-Control": "no-cache"})
    
    if res_files.status_code == 200:
        tutti_i_file = res_files.json()
        # Prendo solo i file che contengono ".json" nel nome (anche se hanno errori di battitura)
        files_json = [f['name'] for f in tutti_i_file if ".json" in f['name'].lower()]
        
        # Ordine dei mesi per la visualizzazione
        ordine = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
        
        # Ordino i file trovati in base al mese
        files_ordinati = sorted(files_json, key=lambda x: next((i for i, m in enumerate(ordine) if m in x.lower()), 99))

        for nome_file in files_ordinati:
            url_f = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{nome_file}"
            res_f = requests.get(url_f, headers={"Cache-Control": "no-cache"})
            if res_f.status_code == 200:
                try:
                    dati = res_f.json()
                    if not dati: continue
                    
                    titolo = nome_file.split(".")[0].capitalize()
                    st.markdown(f'<div class="month-header"><h3>📅 Programma {titolo}</h3></div>', unsafe_allow_html=True)
                    
                    for ev in dati:
                        staff_check = [s.strip().lower() for s in ev.get("staff", [])]
                        if username == "simone" or username.lower() in staff_check:
                            with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                                for p in ev["staff"]:
                                    p_cap = p.strip().capitalize()
                                    check = f"{ev['data']},{ev['nome']},{p_cap}"
                                    icona = "🟢" if check in st.session_state.registro_locale else "🔴"
                                    st.write(f"{icona} {p_cap}")
                                
                                st.divider()
                                chiave_u = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                                if chiave_u not in st.session_state.registro_locale:
                                    if st.button("✅ CONFERMA", key="add"+nome_file+ev['nome']+ev['data']):
                                        aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "aggiungi")
                                        st.rerun()
                                else:
                                    if st.button("❌ ANNULLA", key="rem"+nome_file+ev['nome']+ev['data']):
                                        aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "rimuovi")
                                        st.rerun()
                except: continue
