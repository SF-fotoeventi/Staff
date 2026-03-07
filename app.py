import streamlit as st
import json
import requests
import base64
import pandas as pd
from datetime import datetime
import time 
from io import BytesIO, StringIO

# --- CONFIGURAZIONE PAGINA ---
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

# --- SEGRETI GITHUB ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PRESENZE = "presenze.csv"

# --- ORDINE COLLABORATORI TASSOSTATIVO ---
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

# --- FUNZIONI DI SISTEMA ---
def scarica_registro_fresco():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except:
        pass
    return "Data,Evento,Collaboratore,OraInvio\n"

def scrivi_su_github(data_ev, evento, collaboratore, azione="aggiungi"):
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
    payload = {
        "message": f"{azione} {collaboratore}", 
        "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), 
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA DI ACCESSO ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if "registro_locale" not in st.session_state:
    st.session_state.registro_locale = scarica_registro_fresco()

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff FotoEventi")
    u = st.text_input("Nome:").lower().strip()
    p = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if u in utenti and utenti[u] == p:
            st.session_state.autenticato = True
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Credenziali errate.")
else:
    # --- INTERFACCIA UTENTE ---
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title(f"👋 Ciao {st.session_state.username.capitalize()}!")
    with col2:
        if st.button("Aggiorna Dati 🔄"):
            st.session_state.registro_locale = scarica_registro_fresco()
            st.rerun()
        if st.button("Esci"):
            st.session_state.autenticato = False
            st.rerun()

    st.divider()

    # --- VISUALIZZAZIONE PROGRAMMI ---
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    
    for mese in mesi:
        # Cache killer per GitHub
        url_m = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{mese}.json?v={int(time.time())}"
        res_m = requests.get(url_m)
        
        if res_m.status_code == 200:
            try:
                dati_m = res_m.json()
                st.markdown(f'<div class="month-header"><h3>📅 Programma {mese.capitalize()}</h3></div>', unsafe_allow_html=True)
                
                for ev in dati_m:
                    staff_pulito = [s.strip().lower() for s in ev.get("staff", []) if s.strip()]
                    
                    if st.session_state.username == "simone" or st.session_state.username in staff_pulito:
                        with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                            
                            # LISTA COLLABORATORI IN ORDINE TASSOSTATIVO
                            for coll_nome in utenti.keys():
                                if coll_nome.capitalize() in [s.strip().capitalize() for s in ev["staff"]]:
                                    n_cap = coll_nome.capitalize()
                                    chiave_check = f"{ev['data']},{ev['nome']},{n_cap}"
                                    
                                    if chiave_check in st.session_state.registro_locale:
                                        st.write(f"🟢 {n_cap} (Confermato)")
                                    else:
                                        st.write(f"🔴 {n_cap} (In attesa...)")
                            
                            st.divider()
                            chiave_u = f"{ev['data']},{ev['nome']},{st.session_state.username.capitalize()}"
                            
                            # LOGICA TEMPO REALE
                            if chiave_u in st.session_state.registro_locale:
                                if st.button("❌ ANNULLA", key=f"del_{mese}{ev['nome']}{ev['data']}"):
                                    scrivi_github(ev['data'], ev['nome'], st.session_state.username.capitalize(), "rimuovi")
                                    # Aggiornamento immediato del pallino nello stato locale
                                    st.session_state.registro_locale = st.session_state.registro_locale.replace(f"{chiave_u},", "RIMOSSO,")
                                    st.rerun()
                            else:
                                if st.button("✅ CONFERMA", key=f"add_{mese}{ev['nome']}{ev['data']}"):
                                    scrivi_github(ev['data'], ev['nome'], st.session_state.username.capitalize(), "aggiungi")
                                    # Aggiornamento immediato del pallino nello stato locale
                                    st.session_state.registro_locale += f"{chiave_u},{datetime.now()}\n"
                                    st.rerun()
            except:
                continue
