import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE
# ==========================================
st.set_page_config(page_title="GGIV Terminal", layout="wide")

st.title("🛡️ GGIV - Graphene Global Index Vault")
st.caption("Terminale Istituzionale Quantitativo. Connesso al Database Centrale.")

# ==========================================
# 2. SISTEMA DI LOGIN
# ==========================================
if not st.session_state.get('accesso_consentito', False):
    st.write("Inserisci la password istituzionale per sbloccare l'algoritmo.")
    password_inserita = st.text_input("Password di sblocco:", type="password")
    if st.button("Accedi"):
        if password_inserita == "Founder2026":
            st.session_state.accesso_consentito = True
            st.rerun()
        else:
            st.error("Accesso negato. Credenziali non valide.")
    st.stop()

# ==========================================
# 3. CONNESSIONE AL DATABASE (LINK CSV DIRETTI)
# ==========================================
# 🟢 INCOLLA QUI TRA LE VIRGOLETTE I DUE LINK "PUBBLICA SUL WEB" 🟢
url_db = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?gid=0&single=true&output=csv"
url_wl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?gid=577137332&single=true&output=csv"

@st.cache_data(ttl=60)
def carica_dati(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Errore connessione API: {e}")
        return pd.DataFrame()

# Caricamento
df_aziende = carica_dati(url_db)
df_wl = carica_dati(url_wl)

# ==========================================
# 4. MOTORE LOGICO: PULIZIA E DSRM GLOBALE
# ==========================================
def elabora_dati(df):
    if df.empty: return df
    
    if 'Data_Ultima_News' in df.columns:
        # 1. Forza la lettura nel formato Europeo (Giorno prima del Mese)
        df['Data_Ultima_News'] = pd.to_datetime(df['Data_Ultima_News'], dayfirst=True, errors='coerce')
        
        # 2. Normalizza l'orologio: taglia via ore e minuti annullando i problemi di fuso orario
        oggi = pd.Timestamp.now().normalize()
        
        # 3. Calcolo chirurgico dei giorni netti
        df['Giorni_Silenzio'] = (oggi - df['Data_Ultima_News']).dt.days
        
        # 4. Se la data è mancante, inserisce 999 per attivare il Kill Switch per sicurezza
        df['Giorni_Silenzio'] = df['Giorni_Silenzio'].fillna(999).astype(int)
        
    return df

def applica_dsrm(giorni):
    if giorni <= 45: return 1.0
    elif giorni <= 90: return 0.75
    else: return 0.0

df_aziende = elabora_dati(df_aziende)
df_wl = elabora_dati(df_wl)

if not df_aziende.empty and 'Giorni_Silenzio' in df_aziende.columns:
    df_aziende['Fattore_DSRM'] = df_aziende['Giorni_Silenzio'].apply(applica_dsrm)
    df_aziende['Peso_Effettivo'] = df_aziende['Peso_Base'] * df_aziende['Fattore_DSRM']
    df_aziende['Percentuale_Persa'] = df_aziende['Peso_Base'] - df_aziende['Peso_Effettivo']

# ==========================================
# 5. UI ISTITUZIONALE: TICKER & ANELLO
# ==========================================
ticker_text = "🟢 GGIV INDEX: 10,245.50 (+1.4%) &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 🛡️ GOLDEN SHIELD: ATTIVO &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 🚀 TIER 1 PIONIERI: PESO OTTIMALE"

st.markdown(f"""
<style>
    .ticker-wrap {{ position: fixed; top: 0; left: 0; width: 100vw; height: 45px; background-color: #0e1117; border-bottom: 2px solid #1f77b4; z-index: 9999999; overflow: hidden; display: flex; align-items: center; }}
    .ticker-text {{ white-space: nowrap; font-family: 'Courier New', monospace; font-size: 16px; color: #00ff00; font-weight: bold; animation: ticker 25s linear infinite; position: absolute; }}
    @keyframes ticker {{ 0% {{ transform: translateX(100vw); }} 100% {{ transform: translateX(-100%); }} }}
    [data-testid="collapsedControl"] {{ top: 65px; left: 0px; width: 60px; height: 60px; background: radial-gradient(circle, #ffdf00 0%, #b8860b 100%); border-radius: 0 50% 50% 0; z-index: 10000000; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(255, 215, 0, 0.6); transition: all 0.3s ease-in-out; }}
    [data-testid="collapsedControl"]::before {{ content: "💍"; font-size: 30px; }}
    [data-testid="collapsedControl"] svg {{ display: none; }}
    [data-testid="collapsedControl"]:hover {{ transform: scale(1.1); box-shadow: 0 0 25px rgba(255, 215, 0, 1); }}
    div[data-testid="stTabs"] > div:first-child {{ position: sticky; top: 45px; z-index: 999999; background-color: white; padding: 10px 0; border-bottom: 2px solid #1f77b4; }}
    .main .block-container {{ padding-top: 5rem; }}
</style>
<div class="ticker-wrap"><div class="ticker-text">{ticker_text}</div></div>
""", unsafe_allow_html=True)

# ==========================================
# 6. SIDEBAR
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/shield.png", width=80)
st.sidebar.header("⚙️ Parametri Portafoglio")
capitale_globale = st.sidebar.number_input("Capitale AUM (€):", min_value=1000, value=100000, step=1000)
st.sidebar.markdown("---")

# ==========================================
# 7. LE 6 SCHEDE OPERATIVE
# ==========================================
tab_overview, tab_watchlist, tab_backtest, tab_rischio, tab_sentiment, tab_brevetti = st.tabs([
    "📊 Database & DSRM", "🔭 Incubatore", "📉 Backtest", "🧮 Rischio & Ordini", "📰 Sentiment", "🔬 Brevetti"
])

# --- SCHEDA 1: OVERVIEW ---
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valore Portafoglio", f"€ {capitale_globale:,.2f}", "+4.5% YTD")
    col2.metric("Aziende in Indice", str(len(df_aziende)) if not df_aziende.empty else "0", "Sincronizzato")
    col3.metric("Volatilità Annua", "18.5%", "Ottimale")
    col4.metric("Sharpe Ratio", "0.82", "Efficienza Alta")

    st.markdown("---")
    st.header("🚦 Motore Quantitativo & DSRM")
    
    if not df_aziende.empty:
        # 1. Creazione del sistema a Semaforo
        def genera_semaforo(giorni):
            if giorni <= 45: return "🟢"
            elif giorni <= 90: return "🟡"
            else: return "🔴"
            
        df_aziende['Status'] = df_aziende['Giorni_Silenzio'].apply(genera_semaforo)
        
        # 2. Selezione chirurgica delle colonne da mostrare
        colonne_eleganti = ['Status', 'Ticker', 'Azienda', 'Tier', 'Giorni_Silenzio', 'Peso_Effettivo']
        df_display = df_aziende[colonne_eleganti].copy()
        
        # Rinominiamo le colonne per renderle più leggibili all'investitore
        df_display.rename(columns={'Giorni_Silenzio': 'Giorni Silenzio', 'Peso_Effettivo': 'Peso Reale (%)'}, inplace=True)
        
        # 3. Mostra la tabella pulita, nascondendo i numeri di riga (hide_index)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # --- (Il resto del codice rimane uguale da qui in giù) ---
        aziende_penalizzate = df_aziende[df_aziende['Fattore_DSRM'] < 1.0]
        capitale_salvato_totale = (df_aziende['Percentuale_Persa'].sum() / 100) * capitale_globale
        capitale_salvato_totale = (df_aziende['Percentuale_Persa'].sum() / 100) * capitale_globale

        col_dsrm1, col_dsrm2 = st.columns(2)
        with col_dsrm1:
            st.metric("Capitale Totale spostato nello Shield", f"€ {capitale_salvato_totale:,.2f}", "+ Protezione Attiva")
            
        with col_dsrm2:
            if aziende_penalizzate.empty:
                st.success("✅ Tutte le aziende comunicano regolarmente.")
            else:
                for _, row in aziende_penalizzate.iterrows():
                    soldi_tolti = (row['Percentuale_Persa'] / 100) * capitale_globale
                    if row['Fattore_DSRM'] == 0:
                        st.error(f"🚨 KILL SWITCH: {row['Azienda']} ({row['Giorni_Silenzio']} gg). € {soldi_tolti:,.2f} blindati.")
                    else:
                        st.warning(f"⚠️ PENALITÀ: {row['Azienda']} ({row['Giorni_Silenzio']} gg). € {soldi_tolti:,.2f} allo Shield.")
    else:
        st.warning("🔄 Connessione al database in corso o file non accessibile. Controlla i link CSV.")

# --- SCHEDA 2: WATCHLIST ---
with tab_watchlist:
    st.header("Aziende in Osservazione")
    if not df_wl.empty:
        st.write("Queste aziende sono sotto scansione per un eventuale ingresso.")
        colonne_da_mostrare = ['Ticker', 'Azienda']
        if 'Data_Ultima_News' in df_wl.columns: colonne_da_mostrare.extend(['Data_Ultima_News', 'Giorni_Silenzio'])
        st.dataframe(df_wl[colonne_da_mostrare])
    else:
        st.info("La Watchlist è attualmente vuota o in fase di caricamento.")

# --- SCHEDA 3: BACKTEST ---
with tab_backtest:
    st.header("📈 Backtest & Stress Test")
    date = pd.date_range(start="2021-01-01", periods=36, freq="ME")
    df_backtest = pd.DataFrame({"Data": date, "S&P 500": np.linspace(100, 130, 36) + np.random.normal(0, 2, 36), "GGIV": np.linspace(100, 165, 36) + np.random.normal(0, 3, 36)})
    st.plotly_chart(px.line(df_backtest, x="Data", y=["S&P 500", "GGIV"], color_discrete_sequence=["gray", "#00cc66"]), use_container_width=True)

# --- SCHEDA 4: RISCHIO & ORDINI ---
with tab_rischio:
    st.header("🛡️ Gestione Rischio & Ordini")
    limite_rischio = st.slider("Termometro Rischio (Max %):", 5, 40, 15)
    
    if not df_aziende.empty:
        peso_totale_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
        blocco_scudo = peso_totale_shield < 30
        
        if blocco_scudo: st.error(f"🔴 BLOCCO: Tier 3 al {peso_totale_shield:.1f}%. Minimo: 30%.")
        else: st.success(f"🟢 GOLDEN SHIELD: Tier 3 al {peso_totale_shield:.1f}%.")

        somma_pesi = df_aziende['Peso_Effettivo'].sum()
        df_aziende['Peso_Normalizzato'] = (df_aziende['Peso_Effettivo'] / somma_pesi) * 100 if somma_pesi > 0 else 0

        if not blocco_scudo and st.button("Calcola Lotti"):
            with st.spinner('Scaricando prezzi...'):
                df_aziende['Prezzo_LIVE_$'] = df_aziende['Ticker'].apply(lambda t: round(yf.Ticker(t).history(period="1d")['Close'].iloc[-1], 2) if len(yf.Ticker(t).history(period="1d")) > 0 else 0.001)
                df_aziende['Budget_€'] = capitale_globale * (df_aziende['Peso_Normalizzato'] / 100)
                df_aziende['Azioni'] = (df_aziende['Budget_€'] / df_aziende['Prezzo_LIVE_$']).astype(int)
                st.table(df_aziende[df_aziende['Azioni'] > 0][['Ticker', 'Azienda', 'Prezzo_LIVE_$', 'Budget_€', 'Azioni']])

# --- SCHEDA 5 & 6 ---
with tab_sentiment:
    st.header("📰 Radar Sentiment")
    st.progress(0.85); st.caption("Graphene: 85% Positivo")
    
with tab_brevetti:
    st.header("🔬 Sensore Brevetti")
    if not df_aziende.empty and 'Health_Score' in df_aziende.columns:
        target = st.selectbox("Seleziona Azienda:", df_aziende['Azienda'].tolist())
        score = df_aziende[df_aziende['Azienda'] == target]['Health_Score'].values[0]
        st.metric("Score IP", f"{score}/100")
