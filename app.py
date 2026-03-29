import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np

st.set_page_config(page_title="GGIV Dashboard", layout="wide")

# ==========================================
# 🔗 CONFIGURAZIONE DATABASE (GOOGLE SHEETS)
# ==========================================

URL_DATABASE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?output=csv"

# --- FUNZIONE DI CARICAMENTO DATI ---
@st.cache_data(ttl=60) 
def carica_database(url):
    try:
        # Carica il CSV dal web
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        # Ritorna un dataframe di emergenza se il link fallisce
        return pd.DataFrame({
            "Ticker": ["NNXPF", "AMAT", "AIXXF", "SSNLF", "TSM"],
            "Azienda": ["NanoXplore", "Applied Materials", "Aixtron", "Samsung", "TSMC"],
            "Tier": ["Tier 1", "Tier 2", "Tier 2", "Tier 3", "Tier 3"],
            "Peso_Base": [15.0, 10.0, 10.0, 35.0, 30.0],
            "Giorni_Silenzio": [30, 15, 20, 5, 2],
            "Health_Score": [85, 92, 65, 88, 95]
        })


df_aziende = carica_database(URL_DATABASE)

# --- LOGICA DSRM AUTOMATICA ---
def applica_dsrm(giorni):
    if giorni <= 45: return 1.0
    elif giorni <= 90: return 0.75
    else: return 0.0

df_aziende['Fattore_DSRM'] = df_aziende['Giorni_Silenzio'].apply(applica_dsrm)
df_aziende['Peso_Effettivo'] = df_aziende['Peso_Base'] * df_aziende['Fattore_DSRM']

# --- SISTEMA DI SICUREZZA ---
if "accesso_consentito" not in st.session_state:
    st.session_state.accesso_consentito = False

if not st.session_state.accesso_consentito:
    st.title("🔒 Accesso Riservato GGIV")
    st.write("Inserisci la password istituzionale per sbloccare l'algoritmo.")
    password_inserita = st.text_input("Password di sblocco:", type="password")
    if st.button("Accedi"):
        if password_inserita == "Founder2026": 
            st.session_state.accesso_consentito = True
            st.rerun()
        else:
            st.error("Accesso negato. Credenziali non valide.")
    st.stop()

# --- SIDEBAR GLOBALE ---
st.sidebar.image("https://img.icons8.com/color/96/000000/shield.png", width=80)
st.sidebar.header("⚙️ Impostazioni")
capitale_globale = st.sidebar.number_input("Capitale AUM (€):", min_value=1000, value=50000, step=1000)
st.sidebar.markdown("---")
st.sidebar.info("📡 Database Google Sheets collegato con successo.")

# --- TITOLO E TAB ---
st.title("🛡️ GGIV - Graphene Global Index Vault")
st.markdown("---")

tab_overview, tab_simulazioni, tab_ordini, tab_news, tab_brevetti = st.tabs([
    "📊 Overview & DSRM", 
    "📉 Backtest & Stress Test", 
    "🧮 Rischio & Ordini", 
    "📰 Radar Sentiment",
    "🔬 Sensore Brevetti (IP)"
])

# ==========================================
# SCHEDA 1: OVERVIEW & DSRM
# ==========================================
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valore Portafoglio", f"€ {capitale_globale:,.2f}")
    col2.metric("Aziende Monitorate", str(len(df_aziende)))
    col3.metric("Status DSRM", "ATTIVO")
    col4.metric("Connessione DB", "LIVE")

    st.markdown("---")
    col_g, col_t = st.columns([2, 1])
    with col_g:
        st.subheader("Asset Allocation per Tier")
        df_tier = df_aziende.groupby('Tier')['Peso_Effettivo'].sum().reset_index()
        fig = px.pie(df_tier, values='Peso_Effettivo', names='Tier', hole=0.4,
                     color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99"])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_t:
        st.subheader("Stato Allerta DSRM")
        aziende_allerta = df_aziende[df_aziende['Fattore_DSRM'] < 1.0]
        if aziende_allerta.empty:
            st.success("✅ Tutte le aziende sono in Zona Verde.")
        else:
            for _, row in aziende_allerta.iterrows():
                if row['Fattore_DSRM'] == 0:
                    st.error(f"🚨 KILL SWITCH: {row['Azienda']}")
                else:
                    st.warning(f"⚠️ PENALITÀ: {row['Azienda']}")

# ==========================================
# SCHEDA 2: SIMULAZIONI
# ==========================================
with tab_simulazioni:
    st.header("📉 Stress Test di Portafoglio")
    crollo = st.slider("Simula crollo mercato tech (%):", 0, 50, 20)
    
    p_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Peso_Effettivo'].sum()
    p_t2 = df_aziende[df_aziende['Tier'] == 'Tier 2']['Peso_Effettivo'].sum()
    p_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
    
    impatto = (( -crollo * 1.5 * p_t1 ) + ( -crollo * p_t2 ) + ( -crollo * 0.2 * p_t3 )) / 100
    st.metric("Impatto stimato sul capitale", f"€ {capitale_globale * impatto:,.2f}", f"{impatto*100:.1f}%", delta_color="inverse")

# ==========================================
# SCHEDA 3: RISCHIO & ORDINI
# ==========================================
with tab_ordini:
    st.header("🎛️ Gestione Rischio & Profit Taker")
    limite = st.slider("Soglia Profit Taker (Max % titolo):", 5, 40, 15)
    
    peso_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
    
    if peso_shield < 30:
        st.error(f"🛡️ GOLDEN SHIELD VIOLATO: Tier 3 al {peso_shield:.1f}%. Ordini bloccati.")
        blocco = True
    else:
        st.success(f"🛡️ GOLDEN SHIELD ATTIVO ({peso_shield:.1f}%).")
        blocco = False

    for _, row in df_aziende.iterrows():
        if row['Peso_Effettivo'] > limite:
            st.warning(f"💰 PROFIT TAKER: {row['Azienda']} ha superato la soglia ({row['Peso_Effettivo']}%). Incassare eccedenza.")

    if st.button("Genera Lista Ordini"):
        if not blocco:
            with st.spinner('Scaricando prezzi live...'):
                def get_p(t):
                    try: return round(yf.Ticker(t).history(period="1d")['Close'].iloc[-1], 2)
                    except: return 0.01
                
                df_aziende['Prezzo'] = df_aziende['Ticker'].apply(get_p)
                df_aziende['Budget'] = capitale_globale * (df_aziende['Peso_Effettivo'] / 100)
                df_aziende['Quantità'] = (df_aziende['Budget'] / df_aziende['Prezzo']).astype(int)
                
                st.table(df_aziende[df_aziende['Quantità'] > 0][['Ticker', 'Azienda', 'Prezzo', 'Budget', 'Quantità']])
        else:
            st.error("Ripristina lo scudo (Tier 3) sopra il 30% per operare.")

# ==========================================
# SCHEDA 4 & 5: NEWS E BREVETTI
# ==========================================
with tab_news:
    st.header("📰 Radar Sentiment")
    st.info("Analisi testuale automatizzata prevista per la v2.0.")

with tab_brevetti:
    st.header("🔬 Sensore IP (Patent Health)")
    target = st.selectbox("Seleziona Azienda dal DB:", df_aziende['Azienda'].tolist())
    score = df_aziende[df_aziende['Azienda'] == target]['Health_Score'].values[0]
    
    st.metric("Patent Health Score", f"{score}/100", "Ottimale" if score > 80 else "Rischio")
    if score < 50:
        st.error("⚠️ Allerta: Fossato tecnologico in riduzione. Possibile obsolescenza.")
