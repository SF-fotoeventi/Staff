import streamlit as st
import json
import requests
import base64
from datetime import datetime
import time

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
        .stButton>button {width: 100%; border-radius: 8px; height: 3em; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PRESENZE = "presenze.csv"

# --- ORDINE COLLABORATORI TASSOSTATIVO (Dalla tua immagine) ---
ordine_staff_tassativo = [
    "Simone", "Klaudia", "Leonardo", "Gianni", "Lorena", "Cristian", 
    "Cristina", "Chiara", "Francesco", "Francescon", "Giulia", 
    "Kristina", "Matteo", "Michela", "Raffaele", "Thomas", "Ugo", "Valentina"
]

utenti = {
    "simone": "boss79", "klaudia": "kla98", "leonardo": "leo123", "gianni": "gia77",
    "lorena": "lor88", "cristian": "cris99", "cristina": "cri35", "chiara": "chi34",
    "francesco": "fra56", "francescon": "fra07", "giulia": "giu04", "kristina": "kri36",
    "matteo": "mat35", "michela": "mic43", "raffaele": "raf21", "thomas": "tom45",
    "ugo": "ugo90", "valentina": "val75"
}

# --- FUNZIONI DI SINCRONIZZAZIONE ---
def get_registro_totale():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except: pass
    return "Data,Evento,Collaboratore,OraInvio\n"

def aggiorna_presenza_remota(data_ev, evento, nome_staff, azione="aggiungi"):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    cont = base64.b64decode(res.json()["content"]).decode("utf-8") if res.status_code == 200 else "Data,Evento,Collaboratore,OraInvio\n"
    sha = res.json()["sha"] if res.status_code == 200 else None
    
    linee = cont.splitlines()
    header = linee[0]
    nuove_linee = [header]
    chiave = f"{data_ev},{evento},{nome_staff}"
    
    for l in linee[1:]:
        if chiave not in l: nuove_linee.append(l)
    
    if azione == "aggiungi":
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    nuovo_cont_str = "\n".join(nuove_linee) + "\n"
    payload = {
        "message": f"Update: {azione} {nome_staff}",
        "content": base64.b64encode(nuovo_cont_str.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA APP ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "local_reg" not in st.session_state:
    st.session_state.local_reg = get_registro_totale()

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff")
    u = st.text_input("Username:").lower().strip()
    p = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if u in utenti and utenti[u] == p:
            st.session_state.autenticato, st.session_state.username = True, u
            st.rerun()
        else: st.error("Credenziali non valide
