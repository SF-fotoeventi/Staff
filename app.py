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
        .stButton>button {width: 100%; border-radius: 5px;}
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

# Dizionario credenziali
utenti = {
    "simone": "boss79", "klaudia": "kla98", "leonardo": "leo123", "gianni": "gia77",
    "lorena": "lor88", "cristian": "cris99", "cristina": "cri35", "chiara": "chi34",
    "francesco": "fra56", "francescon": "fra07", "giulia": "giu04", "kristina": "kri36",
    "matteo": "mat35", "michela": "mic43", "raffaele": "raf21", "thomas": "tom45",
    "ugo": "ugo90", "valentina": "val75"
}

def scarica_registro():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except: pass
    return "Data,Evento,Collaboratore,OraInvio\n"

def invia_presenza(data_ev, evento, collaboratore, azione="aggiungi"):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    cont = base64.b64decode(res.json()["content"]).decode("utf-8") if res.status_code == 200 else "Data,Evento,Collaboratore,OraInvio\n"
    sha = res.json()["sha"] if res.status_code == 200 else None
    linee = cont.splitlines()
    nuove_linee = [linee[0]]
    chiave = f"{data_ev},{evento},{collaboratore}"
    for l in linee[1:]:
        if chiave not in l: nuove_linee.append(l)
    if azione == "aggiungi":
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    payload = {"message": f"{azione} {collaboratore}", "content": base64.b64encode(("\n".join(nuove_linee)+"\n").encode("utf-8")).decode("utf-8"), "sha": sha}
    requests.put(url, json=payload, headers=headers)

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "reg_cache" not in st.session_state:
    st.session_state.reg_cache = scarica_registro()

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff FotoEventi")
    u = st.text_input("Nome:").lower().strip()
    p = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if u in utenti and utenti[u] == p:
            st.session_state.autenticato, st.session_state.username = True, u
            st.rerun()
        else: st.error("Dati errati")
else:
    c1, c2 = st.columns([0.8, 0.2])
    with c1: st.title(f"👋 Ciao {st.session_state.username.capitalize()}!")
    with c2: 
        if st.button("Esci"):
            st.session_state.autenticato = False
            st.rerun()

    st.divider()

    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    for m in mesi:
        url_m = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{m}.json?v={int(time.time())}"
        res_m = requests.get(url_m)
        if res_m.status_code == 200:
            try:
                prog = res_m.json()
                st.markdown(f'<div class="month-header"><h3>📅 {m.capitalize()}</h3></div>', unsafe_allow_html=True)
                for ev in prog:
                    staff_evento_lower = [s.strip().lower() for s in ev.get("staff", [])]
                    if st.session_state.username == "simone" or st.session_state.username in staff_evento_lower:
                        with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                            # ORDINE TASSOSTATIVO
                            for n_fisso in ordine_staff_tassativo:
                                if n_fisso.lower() in staff_evento_lower:
                                    chiave = f"{ev['data']},{ev['nome']},{n_fisso}"
                                    if chiave in st.session_state.reg_cache:
                                        st.write(f"🟢 *{n_fisso}* (Confermato)")
                                    else: 
                                        st.write(f"🔴 {n_fisso} (In attesa...)")
                            
                            st.divider()
                            mio_nome = st.session_state.username.capitalize()
                            chiave_u = f"{ev['data']},{ev['nome']},{mio_nome}"
                            
                            # AZIONE ISTANTANEA
                            if chiave_u in st.session_state.reg_cache:
                                if st.button("❌ ANNULLA", key=f"del_{m}{ev['nome']}{ev['data']}"):
                                    invia_presenza(ev['data'], ev['nome'], mio_nome, "rimuovi")
                                    st.session_state.reg_cache = st.session_state.reg_cache.replace(f"{chiave_u},", "VOID,")
                                    st.rerun()
                            else:
                                if st.button("✅ CONFERMA", key=f"add_{m}{ev['nome']}{ev['data']}"):
                                    invia_presenza(ev['data'], ev['nome'], mio_nome, "aggiungi")
                                    st.session_state.reg_cache += f"{chiave_u},{datetime.now()}\n"
                                    st.rerun()
            except: continue
