
import streamlit as st
import json
import os

st.set_page_config(page_title="Gestione Staff 2026", page_icon="📅")

# --- FUNZIONE PER CARICARE I MESI ---
def carica_mese(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return []

# --- LOGIN ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Staff")
    user = st.text_input("Inserisci il tuo nome (es. Klaudia, Admin):")
    if st.button("Entra"):
        st.session_state.autenticato = True
        st.session_state.username = user
        st.rerun()
else:
    username = st.session_state.username
    st.sidebar.title(f"👋 Ciao {username}")
    
    # --- SELETTORE MESE ---
    mesi_disponibili = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_disponibili if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Carica i file .json su GitHub per vedere i dati.")
    else:
        scelta = st.sidebar.selectbox("Scegli il mese:", file_esistenti)
        dati_mese = carica_mese(scelta)
        
        st.header(f"📅 Programma di {scelta.replace('.json', '').capitalize()}")
        
        for ev in dati_mese:
            if username.lower() == "admin" or username in ev["staff"]:
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    st.button("Conferma Presenza", key=ev['nome']+scelta)

    if st.sidebar.button("Esci"):
        st.session_state.autenticato = False
        st.rerun()
