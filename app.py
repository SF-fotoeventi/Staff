import streamlit as st
import json
import os
import requests
import base64
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Staff FotoEventi", page_icon="📸", layout="wide")

# CSS per nascondere il menu laterale e migliorare la grafica
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
    "simone": "boss79", "klaudia": "kla98", "leonardo": "leo123", "gianni": "gia77",
    "lorena": "lor88", "cristian": "cris99", "cristina": "cri35", "chiara": "chi34",
    "francesco": "fra56", "francescon": "fra07", "giulia": "giu04", "kristina": "kri36",
    "matteo": "mat35", "michela": "mic43", "raffaele": "raf21", "thomas": "tom45",
    "ugo": "ugo90", "valentina": "val75"
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
    
    for l in linee[1:]:
        if chiave not in l:
            nuove_linee.append(l)
    
    if azione == "aggiungi":
        nuove_linee.append(f"{chiave},{datetime.now().strftime('%d/%m/%Y %H:%M')}")

    nuovo_cont = "\n".join(nuove_linee) + "\n"
    payload = {"message": f"{azione} {collaboratore}", "content": base64.b64encode(nuovo_cont.encode("utf-8")).decode("utf-8"), "sha": sha}
    requests.put(url, json=payload, headers=headers)

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "registro_locale" not in st.session_state:
    url_raw = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{FILE_PRESENZE}"
    res = requests.get(url_raw)
    st.session_state.registro_locale = res.text if res.status_code == 200 else ""

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

    if username == "simone":
        with st.expander("🛠️ AREA AMMINISTRATORE - Scarica Report"):
            df = pd.read_csv(StringIO(st.session_state.registro_locale))
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.download_button("📥 SCARICA EXCEL PRESENZE", out.getvalue(), "Report_Staff.xlsx")

    st.divider()

    # --- ORDINE CRONOLOGICO DEI MESI ---
    # Definiamo l'ordine manuale per essere sicuri che marzo sia prima di aprile
    ordine_mesi = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    mesi_presenti = [m for m in ordine_mesi if os.path.exists(m)]
    
    for mese_file in mesi_presenti:
        with open(mese_file, "r") as f:
            dati_mese = json.load(f)
        
        nome_mese = mese_file.replace(".json", "").capitalize()
        st.markdown(f'<div class="month-header"><h3>📅 Programma {nome_mese}</h3></div>', unsafe_allow_html=True)
        
        for ev in dati_mese:
            if username == "simone" or username.capitalize() in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write("*Convocati:*")
                    for p in ev["staff"]:
                        check = f"{ev['data']},{ev['nome']},{p.capitalize()}"
                        if check in st.session_state.registro_locale:
                            st.write(f"🟢 {p} (Confermato)")
                        else:
                            st.write(f"🔴 {p} (In attesa...)")
                    
                    st.divider()
                    
                    chiave_u = f"{ev['data']},{ev['nome']},{username.capitalize()}"
                    if chiave_u not in st.session_state.registro_locale:
                        if st.button("✅ CONFERMA", key="add"+ev['nome']+ev['data']+mese_file):
                            st.session_state.registro_locale += chiave_u + "\n"
                            aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "aggiungi")
                            st.rerun()
                    else:
                        if st.button("❌ ANNULLA DISPONIBILITÀ", key="rem"+ev['nome']+ev['data']+mese_file):
                            st.session_state.registro_locale = st.session_state.registro_locale.replace(chiave_u + "\n", "")
                            aggiorna_github(ev['data'], ev['nome'], username.capitalize(), "rimuovi")
                            st.rerun()
