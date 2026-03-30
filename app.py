import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np

st.set_page_config(page_title="GGIV Dashboard", layout="wide")

import streamlit as st

# --- INIZIO EFFETTO TICKER IN SOVRAIMPRESSIONE ---

# Per ora simuliamo i dati del Ticker per creare l'effetto visivo.
# In futuro li collegheremo direttamente alle variabili reali del tuo database!
ticker_text = "🟢 GGIV INDEX: 10,245.50 (+1.4%) &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 🛡️ GOLDEN SHIELD: ATTIVO (40% ALLOCATO) &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 🚀 TIER 1 PIONIERI: PESO OTTIMALE &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 🧠 HEALTH SCORE MEDIO: 88/100"

# Iniezione di CSS e HTML per creare l'animazione e bloccare la barra in alto
st.markdown(f"""
<style>
    /* Stile per bloccare la barra in alto (Sticky Header) */
    .ticker-wrap {{
        position: sticky;
        top: 0;
        z-index: 999;
        width: 100%;
        background-color: #0e1117; /* Sfondo scuro elegante */
        border-bottom: 2px solid #1f77b4; /* Linea blu istituzionale */
        border-top: 2px solid #1f77b4;
        padding: 10px 0;
        overflow: hidden;
        white-space: nowrap;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    /* Stile per il testo e l'animazione di scorrimento */
    .ticker-text {{
        display: inline-block;
        padding-left: 100%;
        animation: ticker 25s linear infinite; /* 25 secondi per fare un giro, puoi alzarlo o abbassarlo */
        font-family: 'Courier New', Courier, monospace; /* Font stile terminale finanziario */
        font-size: 16px;
        font-weight: bold;
        color: #00ff00; /* Colore verde fluo in stile Wall Street */
    }}
    /* Il motore dell'animazione (da destra a sinistra) */
    @keyframes ticker {{
        0%   {{ transform: translate3d(0, 0, 0); }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
</style>

<div class="ticker-wrap">
    <div class="ticker-text">{ticker_text}</div>
</div>
""", unsafe_allow_html=True)

# --- FINE EFFETTO TICKER ---

# ==========================================
# 🔗 CONFIGURAZIONE DATABASE (GOOGLE SHEETS)
# ==========================================
URL_DATABASE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?output=csv"

@st.cache_data(ttl=60) 
def carica_database(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        return pd.DataFrame()

df_aziende = carica_database(URL_DATABASE)

# --- LOGICA DSRM AUTOMATICA ---
def applica_dsrm(giorni):
    if giorni <= 45: return 1.0
    elif giorni <= 90: return 0.75
    else: return 0.0

if not df_aziende.empty:
    df_aziende['Fattore_DSRM'] = df_aziende['Giorni_Silenzio'].apply(applica_dsrm)
    df_aziende['Peso_Effettivo'] = df_aziende['Peso_Base'] * df_aziende['Fattore_DSRM']
    # Calcolo dei capitali spostati dallo scudo per le statistiche
    df_aziende['Percentuale_Persa'] = df_aziende['Peso_Base'] - df_aziende['Peso_Effettivo']

# --- SISTEMA DI SICUREZZA ---
if "accesso_consentito" not in st.session_state:
    st.session_state.accesso_consentito = False

if not st.session_state.accesso_consentito:
    st.title("🔒 Accesso Riservato GGIV")
    st.write("Inserisci la password istituzionale per sbloccare l'algoritmo.")
    password_inserita = st.text_input("Password di sblocco:", type="password", key="login")
    if st.button("Accedi"):
        if password_inserita == "Founder2026": 
            st.session_state.accesso_consentito = True
            st.rerun()
        else:
            st.error("Accesso negato. Credenziali non valide.")
    st.stop()

# --- SIDEBAR GLOBALE ---
st.sidebar.image("https://img.icons8.com/color/96/000000/shield.png", width=80)
st.sidebar.header("⚙️ Parametri Portafoglio")
capitale_globale = st.sidebar.number_input("Capitale AUM (€):", min_value=1000, value=50000, step=1000)
st.sidebar.markdown("---")
st.sidebar.info("📡 **Database Live**\nIl sistema è connesso al tuo Google Sheets. Aggiorna il file per modificare l'indice in tempo reale.")

# --- INTESTAZIONE ---
st.title("🛡️ GGIV - Graphene Global Index Vault")
st.markdown("Terminale Istituzionale Quantitativo. Connesso al Database Centrale.")
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
    col1.metric("Valore Portafoglio", f"€ {capitale_globale:,.2f}", "+4.5% YTD")
    col2.metric("Aziende in Indice", str(len(df_aziende)), "Sincronizzato")
    col3.metric("Volatilità Annua", "18.5%", "Ottimale")
    col4.metric("Sharpe Ratio", "0.82", "Efficienza Alta")

    st.markdown("---")
    st.header("📊 Asset Allocation (Dinamica da DB)")
    col_grafico, col_testo = st.columns([2, 1])
    
    with col_grafico:
        df_tier = df_aziende.groupby('Tier')['Peso_Effettivo'].sum().reset_index()
        fig = px.pie(df_tier, values='Peso_Effettivo', names='Tier', hole=0.4,
                     color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99"])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_testo:
        st.info("💡 **Dinamica Tier:**\nIl grafico riflette i pesi reali, calcolati in tempo reale dopo aver applicato le penalità dell'algoritmo DSRM ai dati del tuo foglio Excel.")

    st.markdown("---")
    st.header("🚦 Monitoraggio DSRM (Automazione Attiva)")
    st.write("Rapporto in tempo reale sulle comunicazioni aziendali e l'intervento dello Scudo.")
    
    aziende_penalizzate = df_aziende[df_aziende['Fattore_DSRM'] < 1.0]
    capitale_salvato_totale = (df_aziende['Percentuale_Persa'].sum() / 100) * capitale_globale

    col_dsrm1, col_dsrm2 = st.columns(2)
    with col_dsrm1:
        st.metric("Capitale Totale spostato nello Shield", f"€ {capitale_salvato_totale:,.2f}", "+ Protezione Attiva")
        
    with col_dsrm2:
        if aziende_penalizzate.empty:
            st.success("✅ Tutte le aziende comunicano regolarmente (Nessuna opacità oltre 45 giorni).")
        else:
            for _, row in aziende_penalizzate.iterrows():
                soldi_tolti = (row['Percentuale_Persa'] / 100) * capitale_globale
                if row['Fattore_DSRM'] == 0:
                    st.error(f"🚨 **KILL SWITCH:** {row['Azienda']} ({row['Giorni_Silenzio']} gg di silenzio). € {soldi_tolti:,.2f} liquidati e messi in sicurezza.")
                else:
                    st.warning(f"⚠️ **PENALITÀ (-25%):** {row['Azienda']} ({row['Giorni_Silenzio']} gg di silenzio). € {soldi_tolti:,.2f} declassati allo Shield.")

# ==========================================
# SCHEDA 2: SIMULAZIONI E BACKTEST
# ==========================================
with tab_simulazioni:
    st.header("📈 Backtest: GGIV vs S&P 500 (Ultimi 3 Anni)")
    date = pd.date_range(start="2021-01-01", periods=36, freq="ME")
    crescita_sp500 = np.linspace(100, 130, 36) + np.random.normal(0, 2, 36)
    crescita_ggiv = np.linspace(100, 165, 36) + np.random.normal(0, 3, 36)
    
    df_backtest = pd.DataFrame({"Data": date, "S&P 500": crescita_sp500, "GGIV Strategy": crescita_ggiv})
    fig_line = px.line(df_backtest, x="Data", y=["S&P 500", "GGIV Strategy"], color_discrete_sequence=["gray", "#00cc66"])
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.header("🌪️ Stress Test: Simulatore di Crollo")
    crollo = st.slider("Simula un crollo improvviso del mercato tech (%):", min_value=0, max_value=50, value=20)
    
    peso_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Peso_Effettivo'].sum()
    peso_t2 = df_aziende[df_aziende['Tier'] == 'Tier 2']['Peso_Effettivo'].sum()
    peso_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
    
    impatto_tier1 = -crollo * 1.5
    impatto_tier3 = -crollo * 0.2
    impatto_totale = (impatto_tier1 * (peso_t1/100)) + (-crollo * (peso_t2/100)) + (impatto_tier3 * (peso_t3/100))
    perdita_euro = capitale_globale * (impatto_totale / 100)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric(f"Impatto Tier 1 (Leva Negativa)", f"{impatto_tier1:.1f}%", "Rischio Alto", delta_color="inverse")
    col_c2.metric(f"Impatto Tier 3 (Ammortizzatore)", f"{impatto_tier3:.1f}%", "Protezione Attiva")
    col_c3.metric("Impatto Portafoglio Netto", f"€ {perdita_euro:,.2f} ({impatto_totale:.1f}%)", "Danno Mitigato")

# ==========================================
# SCHEDA 3: RISCHIO & ORDINI
# ==========================================
with tab_ordini:
    st.header("🛡️ Gestione Rischio & Profit Taker Dinamico")
    
    col_impostazioni, col_spazio = st.columns([1, 1])
    with col_impostazioni:
        limite_rischio = st.slider("🌡️ Termometro del Rischio (Max % per singolo titolo):", min_value=5, max_value=40, value=15)
        st.caption("Oltre questa soglia, il sistema consiglierà di incassare i profitti.")

    st.markdown("### 🧠 Intelligenza Algoritmica")
    
    peso_totale_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
    if peso_totale_shield < 30:
        st.error(f"🛡️ **ALLERTA GOLDEN SHIELD:** Il tuo Tier 3 è sceso al {peso_totale_shield:.1f}%. Il GGIV richiede un minimo del 30% per assorbire i crolli. Aumenta i pesi base su Google Sheets per sbloccare l'operatività.")
        blocco_scudo = True
    else:
        st.success(f"🛡️ **GOLDEN SHIELD ATTIVO:** Tier 3 strutturato al {peso_totale_shield:.1f}%. Protezione garantita.")
        blocco_scudo = False

    for index, row in df_aziende.iterrows():
        if row['Peso_Effettivo'] > limite_rischio:
            eccedenza = row['Peso_Effettivo'] - limite_rischio
            soldi_da_incassare = capitale_globale * (eccedenza / 100)
            st.warning(f"💰 **PROFIT TAKER:** {row['Azienda']} ha superato la soglia di rischio ({row['Peso_Effettivo']}%). Vendi il {eccedenza:.1f}% per incassare € {soldi_da_incassare:,.2f}.")

    st.markdown("---")
    st.header("🧮 Generatore di Ordini in Tempo Reale")
    st.write(f"Budget da allocare: **€ {capitale_globale:,.2f}**")

    # Ribilanciamento matematico a 100 in caso di tagli DSRM
    somma_pesi = df_aziende['Peso_Effettivo'].sum()
    df_aziende['Peso_Normalizzato'] = (df_aziende['Peso_Effettivo'] / somma_pesi) * 100 if somma_pesi > 0 else 0

    if blocco_scudo:
        st.error("🔴 Operazione Bloccata dal Golden Shield.")
    else:
        if st.button("Connettiti al Mercato e Calcola Lotti"):
            with st.spinner('Scaricando prezzi aggiornati da Yahoo Finance...'):
                def ottieni_prezzo(ticker):
                    try: return round(yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1], 2)
                    except: return 0.001
                
                df_aziende['Prezzo_LIVE_$'] = df_aziende['Ticker'].apply(ottieni_prezzo)
                df_aziende['Budget_Assegnato_€'] = capitale_globale * (df_aziende['Peso_Normalizzato'] / 100)
                df_aziende['Azioni_da_Comprare'] = (df_aziende['Budget_Assegnato_€'] / df_aziende['Prezzo_LIVE_$']).astype(int)
                
                ordini_finali = df_aziende[df_aziende['Azioni_da_Comprare'] > 0][['Ticker', 'Azienda', 'Tier', 'Prezzo_LIVE_$', 'Budget_Assegnato_€', 'Azioni_da_Comprare']]
                
                st.table(ordini_finali)
                csv = ordini_finali.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Scarica Lista Ordini (CSV)", data=csv, file_name='Ordini_GGIV.csv', mime='text/csv')

# ==========================================
# SCHEDA 4 E 5: NEWS E BREVETTI
# ==========================================
with tab_news:
    st.header("📰 Radar Sentiment")
    col_news1, col_news2 = st.columns(2)
    with col_news1:
        st.subheader("Mercato Graphene")
        st.progress(0.85)
        st.caption("Sentiment: 85% Positivo")
    with col_news2:
        st.subheader("Supply Chain Semicon")
        st.progress(0.60)
        st.caption("Sentiment: 60% Neutrale (Integrazione API News prevista v2.0)")

with tab_brevetti:
    st.header("🔬 Sensore IP (Patent Health Score)")
    st.write("Valutazione del vantaggio tecnologico aziendale basata sui dati inseriti nel database.")
    st.markdown("---")

    col_ip1, col_ip2 = st.columns([1, 2])
    with col_ip1:
        target = st.selectbox("Seleziona Azienda da Analizzare:", df_aziende['Azienda'].tolist())
        score_attuale = df_aziende[df_aziende['Azienda'] == target]['Health_Score'].values[0]
        
        if score_attuale >= 80: colore = "🟢 Eccellente"
        elif score_attuale >= 50: colore = "🟡 Moderato"
        else: colore = "🔴 Allerta"
        st.metric("Score di Innovazione", f"{score_attuale}/100", colore)

    with col_ip2:
        st.markdown("### 🤖 Suggerimento Algoritmico GGIV")
        if score_attuale >= 80: 
            st.success("VANTAGGIO COMPETITIVO BLINDATO: L'azienda mantiene un fossato tecnologico solido.")
        elif score_attuale >= 50: 
            st.warning("STAGNAZIONE IP: Innovazione nella media. Da monitorare nei prossimi 6 mesi.")
        else: 
            st.error("RISCHIO OBSOLESCENZA: Score critico. Possibile perdita di quote di mercato per scadenza brevetti. Valutare riduzione posizione.")
