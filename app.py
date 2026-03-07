import streamlit as st
import json
import requests
import base64
import pandas as pd
from datetime import datetime
from io import StringIO

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
    else:
        cont = "Data,Evento,Collaboratore,OraInvio\n"
        sha = None

    linee = cont.splitlines()
    nuove_linee = [linee[0]]
    chiave = f"{data_ev},{evento},{collaboratore}"
    
    found = False
    for l in linee[1:]:
        if chiave in l:
            found = True
            if azione == "aggiungi":
                nuove_linee.append(l) # Mantiene se già c'è
            # Se azione è "rimuovi", non la aggiunge (quindi la elimina)
        else:
            nuove_linee.append(l)
    
    if azione == "aggiungi" and not found:
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")

    nuovo_cont = "\n".join(nuove_linee) + "\n"
    payload = {
        "message": f"{azione} {collaboratore}", 
        "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), 
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

# Scarica registro sempre fresco
url_p = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
res_p = requests.get(url_p, headers={"Cache-Control": "no-cache"})
st.session_state.registro_locale = res_p.text if res_p.status_code == 200 else "Data,Evento,Collaboratore,OraInvio\n"

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff FotoEventi")
    user = st.text_input("Nome:").lower().strip()
    pwd = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if user in utenti and utenti[user] == pwd:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Credenziali errate.")
else:
    username = st.session_state.username
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(f"👋 Ciao {username.capitalize()}!")
    with col2:
        if st.button("Esci"):
            st.session_state.autenticato = False
            st.rerun()

    st.divider()

    mesi_anno = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

    for mese in mesi_anno:
        url_m = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{mese}.json"
        res_m = requests.get(url_m, headers={"Cache-Control": "no-cache"})
        
        if res_m.status_code == 200:
            try:
                dati_mese = res_m.json()
                if not dati_mese: continue
                
                st.markdown(f'<div class="month-header"><h3>📅 Programma {mese.capitalize()}</h3></div>', unsafe_allow_html=True)
                
                for ev in dati_mese:
                    staff_nomi = [s.strip().capitalize() for s in ev.get("staff", [])]
                    if username == "simone" or username.capitalize() in staff_nomi:
                        with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                            for p in ev["staff"]:
                                p_cap = p.strip().capitalize()
                                # Controllo esatto nel registro CSV
                                check = f"{ev['data']},{ev['nome']},{p_cap}"
                                if check in st.session_state.registro_locale:
                                    st.write(f"🟢 {p_cap} (Confermato)")
                                else:
                                    st.write(f"🔴 {p_cap} (In attesa...)")
                            
                            st.divider()
                            chiave_u = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                            
                            # Logica Pulsanti ORIGINALE
                            if chiave_u not in st.session_state.registro_locale:
                                if st.button("✅ CONFERMA DISPONIBILITÀ", key=f"add_{mese}{ev['nome']}{ev['data']}"):
                                    aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "aggiungi")
                                    st.rerun()
                            else:
                                if st.button("❌ ANNULLA DISPONIBILITÀ", key=f"rem_{mese}{ev['nome']}{ev['data']}"):
                                    aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "rimuovi")
                                    st.rerun()
            except:
                continue
