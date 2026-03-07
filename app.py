import streamlit as st
import json
import requests
import base64
import pandas as pd
from datetime import datetime
import time 
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

# --- FUNZIONI DI SINCRONIZZAZIONE ---
def scarica_registro_api():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PRESENZE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8")
    except:
        pass
    return "Data,Evento,Collaboratore,OraInvio\n"

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
    payload = {
        "message": f"{azione} {collaboratore}", 
        "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), 
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# --- LOGICA APP ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

# Scarico dati reali all'avvio
if "registro_locale" not in st.session_state:
    st.session_state.registro_locale = scarica_registro_api()

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
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title(f"👋 Ciao {username.capitalize()}!")
    with col2:
        # Pulsante manuale sempre visibile
        if st.button("Aggiorna Dati 🔄"):
            st.session_state.registro_locale = scarica_registro_api()
            st.rerun()
        if st.button("Esci"):
            st.session_state.autenticato = False
            st.rerun()

    if username == "simone":
        with st.expander("🛠️ AREA AMMINISTRATORE"):
            df = pd.read_csv(StringIO(st.session_state.registro_locale))
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.download_button("📥 SCARICA EXCEL", out.getvalue(), "Report.xlsx")

    st.divider()

    ordine_mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    
    for mese in ordine_mesi:
        url_mese = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{mese}.json?v={int(time.time())}"
        res_m = requests.get(url_mese)
        
        if res_m.status_code == 200:
            try:
                dati_mese = res_m.json()
                st.markdown(f'<div class="month-header"><h3>📅 Programma {mese.capitalize()}</h3></div>', unsafe_allow_html=True)
                
                for ev in dati_mese:
                    # Filtro staff per visualizzazione
                    staff_pulito = [s.strip().lower() for s in ev.get("staff", []) if s.strip()]
                    
                    if username == "simone" or username in staff_pulito:
                        with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                            
                            # MOSTRA I COLLABORATORI NELL'ORDINE CORRETTO
                            for coll in utenti.keys():
                                if coll.capitalize() in [s.strip().capitalize() for s in ev["staff"]]:
                                    p_cap = coll.capitalize()
                                    chiave_check = f"{ev['data']},{ev['nome']},{p_cap}"
                                    
                                    if chiave_check in st.session_state.registro_locale:
                                        st.write(f"🟢 {p_cap} (Confermato)")
                                    else:
                                        st.write(f"🔴 {p_cap} (In attesa...)")
                            
                            st.divider()
                            chiave_u = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                            
                            # AZIONI ISTANTANEE
                            if chiave_u in st.session_state.registro_locale:
                                if st.button("❌ ANNULLA", key=f"rem_{mese}{ev['nome']}{ev['data']}"):
                                    aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "rimuovi")
                                    # Update istantaneo locale del pallino
                                    st.session_state.registro_locale = st.session_state.registro_locale.replace(f"{chiave_u},", "RIMOSSO,")
                                    st.rerun()
                            else:
                                if st.button("✅ CONFERMA", key=f"add_{mese}{ev['nome']}{ev['data']}"):
                                    aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "aggiungi")
                                    # Update istantaneo locale del pallino
                                    st.session_state.registro_locale += f"{chiave_u},{datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                                    st.rerun()
            except:
                continue
