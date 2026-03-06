import streamlit as st
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestione Staff FotoEventi", page_icon="🔐", layout="centered")

# --- DATABASE UTENTI (Nomi e Password) ---
# Le chiavi (nomi) sono tutte minuscole per il login.
# Le password sono modificabili in qualsiasi momento.
utenti = {
    "Simone": "boss79",
    "Klaudia": "k98",
    "Leonardo": "leo123",
    "Thomas": "thom00",
    "Gianni": "giani77",
    "Lorena": "lori88",
    "Cristian": "cris99",
    "Cristina": "cri35",
    "Chiara": "chi34",
    "Francesco": "fra56",
    "FrancescoN": "fra07",
    "Giulia": "giu04",
    "Kristina": "kri36",
    "Matteo": "mat35",
    "Michela": "mic43",
    "Raffaele": "raf21",
    "Tomas": "tom45",
    "Ugo": "ugo90",
    "Valentina": "val75"
}

# --- FUNZIONE CARICAMENTO DATI ---
def carica_mese(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "r") as f:
            return json.load(f)
    return []

# --- GESTIONE LOGIN ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Riservato Staff")
    st.write("Inserisci le tue credenziali per vedere gli impegni.")
    
    user = st.text_input("Nome utente (tutto minuscolo):").lower().strip()
    password = st.text_input("Password:", type="password")
    
    if st.button("Entra"):
        if user in utenti and utenti[user] == password:
            st.session_state.autenticato = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Nome utente o password non corretti.")
else:
    # --- APP DOPO IL LOGIN ---
    username = st.session_state.username
    st.sidebar.title(f"👋 Ciao {username.capitalize()}")
    
    # Lista dei file mesi che l'app proverà a cercare
    mesi_previsti = ["marzo.json", "aprile.json", "maggio.json", "giugno.json", "luglio.json"]
    file_esistenti = [m for m in mesi_previsti if os.path.exists(m)]
    
    if not file_esistenti:
        st.warning("Nessun piano eventi caricato su GitHub. Contatta l'amministratore.")
    else:
        scelta_file = st.sidebar.selectbox("Seleziona il mese da visualizzare:", file_esistenti)
        dati_mese = carica_mese(scelta_file)
        
        nome_mese_pulito = scelta_file.replace('.json', '').capitalize()
        st.header(f"📅 Programma Eventi - {nome_mese_pulito}")
        
        trovati = False
        for ev in dati_mese:
            # L'admin vede tutto, i collaboratori vedono solo dove compare il loro nome
            # (Il codice controlla il nome con la prima lettera maiuscola)
            if username == "admin" or username.capitalize() in ev["staff"]:
                trovati = True
                with st.expander(f"📍 {ev['nome']} - {ev['data']}"):
                    st.write(f"*Data:* {ev['data']}")
                    st.write(f"*Team:* {', '.join(ev['staff'])}")
                    
                    # Tasto di conferma presenza
                    if st.button(f"Conferma Presenza per {ev['nome']}", key=ev['nome']+scelta_file):
                        st.success(f"Grazie {username.capitalize()}, presenza registrata!")
        
        if not trovati and username != "admin":
            st.info(f"Non risultano convocazioni per te nel mese di {nome_mese_pulito}.")

    # Tasto Logout
    if st.sidebar.button("Esci / Logout"):
        st.session_state.autenticato = False
        st.rerun()
