import streamlit as st
import json
import os

st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

# Nomi tutti minuscoli qui per garantire il login corretto
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

def carica_mese(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return []

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato Staff")
    user = st.text_input("Nome utente (es: simone):").lower().strip()
    password = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if user in utenti and utenti[user] == password:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Credenziali errate.")
else:
    username = st.session_state.username
    st.sidebar.title(f"👋 Ciao {username.capitalize()}")
    mesi_previsti = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_previsti if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Nessun piano eventi caricato.")
    else:
        scelta_file = st.sidebar.selectbox("Scegli il mese:", file_esistenti)
        dati_mese = carica_mese(scelta_file)
        st.header(f"📅 Programma di {scelta_file.replace('.json', '').capitalize()}")
        
        trovati = False
        for ev in dati_mese:
            # L'admin simone vede tutto, gli altri vedono solo se il loro nome (Capitalized) è nello staff
            if username == "simone" or username.capitalize() in ev["staff"]:
                trovati = True
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    # KEY UNICA: risolve l'errore rosso 'DuplicateElementKey'
                    st.button("Conferma Presenza", key=ev['nome'] + ev['data'] + scelta_file)
        
        if not trovati and username != "simone":
            st.info("Non ci sono convocazioni per te.")

    if st.sidebar.button("Esci / Logout"):
        st.session_state.autenticato = False
        st.rerun()
