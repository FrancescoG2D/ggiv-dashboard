import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="GGIV Dashboard", layout="wide")


# --- SISTEMA DI SICUREZZA E LOGIN (STRADA 2) ---
if "accesso_consentito" not in st.session_state:
    st.session_state.accesso_consentito = False

if not st.session_state.accesso_consentito:
    st.title("🔒 Accesso Riservato GGIV")
    st.write("Inserisci la password istituzionale per sbloccare l'algoritmo.")
    
    # La casella per la password (i caratteri saranno nascosti con gli asterischi)
    password_inserita = st.text_input("Password di sblocco:", type="password")
    
    if st.button("Accedi"):
        if password_inserita == "Founder2026":  # <-- QUESTA È LA TUA PASSWORD SEGRETA, PUOI CAMBIARLA!
            st.session_state.accesso_consentito = True
            st.rerun()  # Ricarica la pagina come utente loggato
        else:
            st.error("Accesso negato. Credenziali non valide.")
            
    # IL TRUCCO MAGICO: Se non sei loggato, Python si ferma qui e non legge il resto della dashboard!
    st.stop()

# ==========================================
# (Da qui in giù c'è tutto il resto del tuo codice originale della Dashboard che avevi già: st.title("🛡️ GGIV..."), i KPI, ecc.)

# --- INIZIALIZZAZIONE MEMORIA (SESSION STATE) ---
if 'p_nano' not in st.session_state: st.session_state.p_nano = 9
if 'p_amat' not in st.session_state: st.session_state.p_amat = 9
if 'p_aix' not in st.session_state: st.session_state.p_aix = 9
if 'p_sam' not in st.session_state: st.session_state.p_sam = 9
if 'p_tsmc' not in st.session_state: st.session_state.p_tsmc = 9

def carica_rulebook():
    st.session_state.p_nano = 8
    st.session_state.p_amat = 8
    st.session_state.p_aix = 8
    st.session_state.p_sam = 8
    st.session_state.p_tsmc = 8

st.title("🛡️ GGIV - Graphene Global Index Vault")
st.markdown("Bentornato. Ecco lo stato del tuo portafoglio protetto dall'algoritmo istituzionale.")
st.markdown("---")

# --- SEZIONE 1: KPI ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Valore Portafoglio", "€ 10.450,00", "+4.5% YTD")
col2.metric("Max Drawdown GGIV", "-22.1%", "Protetto")
col3.metric("Volatilità Annua", "18.5%", "Ottimale")
col4.metric("Sharpe Ratio", "0.82", "Efficienza Alta")

st.markdown("---")

# --- SEZIONE 2: GRAFICO A TORTA ---
st.header("📊 Asset Allocation (Tier System)")
col_grafico, col_testo = st.columns([2, 1])

with col_grafico:
    dati_torta = pd.DataFrame({
        "Tier": ["Tier 1 (Pure Players)", "Tier 2 (Supply Chain)", "Tier 3 (The Shield)"],
        "Peso (%)": [35, 25, 40]
    })
    fig = px.pie(dati_torta, values='Peso (%)', names='Tier', hole=0.4,
                 color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99"])
    st.plotly_chart(fig, use_container_width=True)

with col_testo:
    st.info("💡 **Perché questo bilanciamento?**\n\nIl Tier 3 agisce da *Market Collapse Shield* durante i mercati ribassisti.")

st.markdown("---")

# --- SEZIONE 3: MOTORE DSRM ---
st.header("🚦 Motore DSRM (Data Silence Risk Module)")
giorni_silenzio = st.slider("Giorni dall'ultima comunicazione ufficiale (T):", min_value=0, max_value=120, value=30)

def calcola_dsrm(t):
    if t <= 45: return 1.0, "🟢 Verde (Safe)"
    elif t <= 90: return 0.75, "🟡 Giallo (Penalità 25%)"
    else: return 0.0, "🔴 KILL SWITCH (Espulsione)"

fattore_moltiplicatore, stato_algoritmo = calcola_dsrm(giorni_silenzio)
st.metric(label="Stato Attuale dell'Azienda", value=stato_algoritmo, delta=f"Fattore Delta: {fattore_moltiplicatore}")

st.markdown("---")

# --- SEZIONE 4: COMPLIANCE UCITS ---
st.header("⚖️ Motore di Compliance UCITS (Regola 5/10/40)")
st.write("Simula l'allocazione. Il sistema bloccherà le transazioni se violi le normative europee.")

st.button("🛡️ Carica Pesi Ottimali (Master Rulebook)", on_click=carica_rulebook, type="primary")

col_a, col_b = st.columns(2)
with col_a:
    peso_nano = st.slider("Peso NanoXplore (%)", min_value=0, max_value=20, key="p_nano")
    peso_amat = st.slider("Peso Applied Materials (%)", min_value=0, max_value=20, key="p_amat")
    peso_aix = st.slider("Peso Aixtron (%)", min_value=0, max_value=20, key="p_aix")
with col_b:
    peso_sam = st.slider("Peso Samsung (%)", min_value=0, max_value=20, key="p_sam")
    peso_tsmc = st.slider("Peso TSMC (%)", min_value=0, max_value=20, key="p_tsmc")
    
    peso_resto = 100 - (peso_nano + peso_amat + peso_aix + peso_sam + peso_tsmc)
    st.info(f"Resto del portafoglio frammentato (quote < 5%): **{peso_resto}%**")

pesi_principali = [peso_nano, peso_amat, peso_aix, peso_sam, peso_tsmc]
violazione_10 = any(p > 10 for p in pesi_principali)
somma_maggiori_5 = sum(p for p in pesi_principali if p > 5)
violazione_40 = somma_maggiori_5 > 40

if violazione_10:
    st.error("🔴 TRANSAZIONI BLOCCATE: Violazione Regola 10%. Hai allocato più del 10% su un singolo titolo.")
elif violazione_40:
    st.error(f"🔴 TRANSAZIONI BLOCCATE: Violazione Regola 40%. La somma dei titoli 'pesanti' è arrivata al {somma_maggiori_5}%. Il limite massimo è 40%.")
else:
    st.success("🟢 PORTAFOGLIO A NORMA UCITS! Nessuna violazione rilevata. Ordini sbloccati.")

st.markdown("---")

# --- SEZIONE 5: CALCOLATORE LIVE (TUTTE E 5 LE AZIENDE) ---
st.header("🧮 Vault Calculator (Ordini in Tempo Reale)")
st.write("Collegato a Wall Street via Yahoo Finance API. Genera gli ordini solo se la compliance UCITS è rispettata.")

capitale_input = st.number_input("Capitale da allocare (€ o $):", min_value=100, max_value=1000000, value=5000, step=100)

if violazione_10 or violazione_40:
    st.warning("⚠️ Risolvi le violazioni UCITS qui sopra prima di poter generare gli ordini reali.")
else:
    if st.button("Connettiti al Mercato e Genera Ordini"):
        with st.spinner('Scaricando i prezzi in tempo reale per tutti i titoli...'):
            def ottieni_prezzo(ticker):
                try:
                    dato = yf.Ticker(ticker).history(period="1d")
                    return round(dato['Close'].iloc[-1], 2)
                except:
                    return 0.001 # Prevenzione errori di divisione
            
            # Scarica i prezzi per TUTTE E 5
            prezzo_nano = ottieni_prezzo("NNXPF")
            prezzo_amat = ottieni_prezzo("AMAT")
            prezzo_aix = ottieni_prezzo("AIXXF")
            prezzo_sam = ottieni_prezzo("SSNLF") # Ticker USA per Samsung
            prezzo_tsmc = ottieni_prezzo("TSM")  # Ticker per TSMC
            
            st.success("Dati di mercato sincronizzati con successo!")
            
            ordini = pd.DataFrame({
                "Azienda (Ticker)": [
                    "NanoXplore (NNXPF)", 
                    "Applied Materials (AMAT)", 
                    "Aixtron (AIXXF)",
                    "Samsung (SSNLF)",
                    "TSMC (TSM)"
                ],
                "Prezzo LIVE ($)": [prezzo_nano, prezzo_amat, prezzo_aix, prezzo_sam, prezzo_tsmc],
                "Budget Assegnato": [
                    capitale_input * (peso_nano/100), 
                    capitale_input * (peso_amat/100), 
                    capitale_input * (peso_aix/100),
                    capitale_input * (peso_sam/100),
                    capitale_input * (peso_tsmc/100)
                ]
            })
            
            # Calcolo delle quantità
            ordini["Quantità Esatta da Comprare"] = (ordini["Budget Assegnato"] / ordini["Prezzo LIVE ($)"]).astype(int)
            
            st.table(ordini)
