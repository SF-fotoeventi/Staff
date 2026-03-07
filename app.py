import streamlit as st
import requests
import base64
from datetime import datetime
import time

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Staff FotoEventi", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main {margin-top: -50px;}
        .month-header {
            background: #f0f2f6; padding: 10px; border-radius: 10px;
            border-left: 5px solid #ff4b4b; margin: 20px 0;
        }
        .stButton>button {width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em;}
    </style>
    """, unsafe_allow_html=True)

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PRESENZE = "presenze.csv"

# --- ORDINE COLLABORATORI TASSOSTATIVO (Dalla tua foto) ---
ordine_tassativo = [
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
def scarica_registro():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except: pass
    return "Data,Evento,Collaboratore,OraInvio\n"

def salva_su_github(data_ev, evento, nome, azione):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    cont = base64.b64decode(res.json()["content"]).decode("utf-8") if res.status_code == 200 else "Data,Evento,Collaboratore,OraInvio\n"
    sha = res.json()["sha"] if res.status_code == 200 else None
    
    linee = cont.splitlines()
    header = linee[0]
    nuove_linee = [header]
    chiave = f"{data_ev},{evento},{nome}"
    
    for l in linee[1:]:
        if chiave not in l: nuove_linee.append(l)
    
    if azione == "aggiungi":
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    payload = {
        "message": f"{azione} {nome}",
        "content": base64.b64encode(("\n".join(nuove_linee)+"\n").encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA APPLICATIVA ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if "cache" not in st.session_state:
    st.session_state.cache = scarica_registro()

if not st.session_state.autenticato:
    st.title("🔐 Login Staff FotoEventi")
    u = st.text_input("Username:").lower().strip()
    p = st.text_input("Password:", type="password")
    if st.button("ACCEDI"):
        if u in utenti and utenti[u] == p:
            st.session_state.autenticato, st.session_state.username = True, u
            st.rerun()
        else: st.error("Accesso negato")
else:
    st.title(f"👋 Ciao {st.session_state.username.capitalize()}!")
    
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    for m in mesi:
        url_m = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{m}.json?v={int(time.time())}"
        res_m = requests.get(url_m)
        if res_m.status_code == 20
