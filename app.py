import streamlit as st
import requests
import base64
from datetime import datetime
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Staff FotoEventi", layout="wide")

# CSS per pulizia interfaccia
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
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

ordine_tassativo = ["Simone", "Klaudia", "Leonardo", "Gianni", "Lorena", "Cristian", "Cristina", "Chiara", "Francesco", "Francescon", "Giulia", "Kristina", "Matteo", "Michela", "Raffaele", "Thomas", "Ugo", "Valentina"]
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

def scarica_registro():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except: pass
    return "Data,Evento,Collaboratore,OraInvio\n"

# --- NUOVA LOGICA AZIONE (CLICK SINGOLO) ---
def gestisci_presenza(data_ev, evento, nome, azione, mia_chiave):
    # 1. Aggiorna IMMEDIATAMENTE la cache in session_state
    if azione == "aggiungi":
        if mia_chiave not in st.session_state.cache:
            st.session_state.cache += f"{mia_chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    else:
        linee = st.session_state.cache.splitlines()
        st.session_state.cache = "\n".join([l for l in linee if mia_chiave not in l]) + "\n"

    # 2. Invia a GitHub (Processo in background)
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    cont = base64.b64decode(res.json()["content"]).decode("utf-8") if res.status_code == 200 else "Data,Evento,Collaboratore,OraInvio\n"
    sha = res.json()["sha"] if res.status_code == 200 else None
    
    linee_github = cont.splitlines()
    nuove_linee = [linee_github[0]]
    for l in linee_github[1:]:
        if mia_chiave not in l: nuove_linee.append(l)
    
    if azione == "aggiungi":
        nuove_linee.append(f"{mia_chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    payload = {
        "message": f"{azione} {nome}",
        "content": base64.b64encode(("\n".join(nuove_linee)+"\n").encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA CORE ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if "cache" not in st.session_state:
    st.session_state.cache = scarica_registro()

if not st.session_state.autenticato:
    st.title("🔐 Login Staff")
    u = st.text_input("Username:").lower().strip()
    p = st.text_input("Password:", type="password")
    if st.button("ACCEDI"):
        if u in utenti and utenti[u] == p:
            st.session_state.autenticato = True
            st.session_state.username = u
            st.rerun()
        else: st.error("Credenziali errate")
else:
    st.title(f"👋 Ciao {st.session_state.username.capitalize()}!")
    
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    for m in mesi:
        url_m = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{m}.json?v={int(time.time())}"
        res_m = requests.get(url_m)
        if res_m.status_code == 200:
            try:
                eventi = res_m.json()
                st.markdown(f'<div class="month-header"><h3>📅 {m.upper()}</h3></div>', unsafe_allow_html=True)
                for ev in eventi:
                    staff_ev_low = [s.strip().lower() for s in ev.get("staff", [])]
                    
                    if st.session_state.username == "simone" or st.session_state.username in staff_ev_low:
                        with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                            for n_fisso in ordine_tassativo:
                                if n_fisso.lower() in staff_ev_low:
                                    if f"{ev['data']},{ev['nome']},{n_fisso}" in st.session_state.cache:
                                        st.write(f"🟢 *{n_fisso}*")
                                    else: st.write(f"🔴 {n_fisso}")
                            
                            st.divider()
                            mio_nome = st.session_state.username.capitalize()
                            mia_chiave = f"{ev['data']},{ev['nome']},{mio_nome}"
                            
                            # USA ON_CLICK PER IL CLICK SINGOLO
                            if mia_chiave in st.session_state.cache:
                                st.button("❌ ANNULLA", 
                                          key=f"rm_{m}{ev['nome']}{ev['data']}", 
                                          on_click=gestisci_presenza, 
                                          args=(ev['data'], ev['nome'], mio_nome, "rimuovi", mia_chiave))
                            else:
                                st.button("✅ CONFERMA", 
                                          key=f"add_{m}{ev['nome']}{ev['data']}", 
                                          on_click=gestisci_presenza, 
                                          args=(ev['data'], ev['nome'], mio_nome, "aggiungi", mia_chiave))
            except: continue

    if st.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
