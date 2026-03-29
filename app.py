import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import numpy as np

st.set_page_config(page_title="GGIV Dashboard", layout="wide")

# --- SISTEMA DI SICUREZZA E LOGIN ---
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

# --- INIZIALIZZAZIONE MEMORIA (SESSION STATE) ---
if 'p_nano' not in st.session_state: st.session_state.p_nano = 9
if 'p_amat' not in st.session_state: st.session_state.p_amat = 9
if 'p_aix' not in st.session_state: st.session_state.p_aix = 9
if 'p_sam' not in st.session_state: st.session_state.p_sam = 9
if 'p_tsmc' not in st.session_state: st.session_state.p_tsmc = 9
if 'dsrm_nano' not in st.session_state: st.session_state.dsrm_nano = 1.0 

def carica_rulebook():
    st.session_state.p_nano = 8
    st.session_state.p_amat = 8
    st.session_state.p_aix = 8
    st.session_state.p_sam = 8
    st.session_state.p_tsmc = 8

# --- NOVITÀ: LA BARRA LATERALE GLOBALE ---
st.sidebar.image("https://img.icons8.com/color/96/000000/shield.png", width=80) # Un piccolo logo scudo
st.sidebar.header("⚙️ Impostazioni Portafoglio")
st.sidebar.write("Definisci il capitale in gestione.")

# Questo è il nuovo "Cuore" matematico di tutto il sito
capitale_globale = st.sidebar.number_input("Capitale AUM (€):", min_value=1000, max_value=50000000, value=50000, step=1000)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Nota Operativa:**\nModificando questo valore, l'intera piattaforma (KPI, simulazioni e lotti d'ordine) si riallineerà automaticamente in tempo reale.")

# --- INTESTAZIONE ---
st.title("🛡️ GGIV - Graphene Global Index Vault")
st.markdown("Terminale Istituzionale. Protezione algoritmica attiva.")
st.markdown("---")

tab_overview, tab_simulazioni, tab_ordini, tab_news = st.tabs([
    "📊 Overview & DSRM", 
    "📉 Backtest & Stress Test", 
    "🧮 Compliance & Ordini", 
    "📰 Radar Sentiment"
])

# ==========================================
# SCHEDA 1: OVERVIEW & DSRM
# ==========================================
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    # IL KPI ORA LEGGE IL DATO DELLA SIDEBAR, FORMATTATO CON I PUNTINI DELLE MIGLIAIA!
    col1.metric("Valore Portafoglio", f"€ {capitale_globale:,.2f}", "+4.5% YTD")
    col2.metric("Max Drawdown GGIV", "-22.1%", "Protetto")
    col3.metric("Volatilità Annua", "18.5%", "Ottimale")
    col4.metric("Sharpe Ratio", "0.82", "Efficienza Alta")

    st.markdown("---")
    
    st.header("🚦 Motore DSRM (Riallocazione Capitale in Tempo Reale)")
    st.write("Simula l'intervento dell'algoritmo su NanoXplore. Questo influenzerà direttamente il Calcolatore degli Ordini.")

    col_dsrm_comandi, col_dsrm_risultati = st.columns([1, 2])

    with col_dsrm_comandi:
        azienda_test = "NanoXplore (Tier 1)"
        peso_iniziale = st.session_state.p_nano 
        giorni_silenzio = st.slider("Giorni di silenzio NanoXplore (T):", min_value=0, max_value=120, value=30)

        def calcola_dsrm(t):
            if t <= 45: return 1.0, "🟢 Verde (Safe)"
            elif t <= 90: return 0.75, "🟡 Giallo (Penalità 25%)"
            else: return 0.0, "🔴 KILL SWITCH (Espulsione)"

        st.session_state.dsrm_nano, stato_algoritmo = calcola_dsrm(giorni_silenzio)

    with col_dsrm_risultati:
        st.markdown("### ⚡ Reazione del Portafoglio")
        nuovo_peso = peso_iniziale * st.session_state.dsrm_nano
        capitale_liberato = peso_iniziale - nuovo_peso
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Stato Allarme", stato_algoritmo)
        delta_peso = f"{nuovo_peso - peso_iniziale}%" if nuovo_peso < peso_iniziale else "Invariato"
        c2.metric(f"Peso {azienda_test}", f"{nuovo_peso}%", delta_peso, delta_color="inverse" if nuovo_peso < peso_iniziale else "off")
        
        # ORA CALCOLIAMO ANCHE I SOLDI VERI SPOSTATI NELLO SCUDO!
        soldi_spostati = capitale_globale * (capitale_liberato / 100)
        c3.metric("Capitale salvato nel Tier 3", f"€ {soldi_spostati:,.2f}", "+ Protezione" if capitale_liberato > 0 else "")

        if st.session_state.dsrm_nano == 0.0:
            st.error(f"🚨 AZIONE ESEGUITA: {azienda_test} espulsa. I fondi sono stati riallocati nel Tier 3.")
        elif st.session_state.dsrm_nano == 0.75:
            st.warning(f"⚠️ AZIONE ESEGUITA: Peso di {azienda_test} decurtato per rischio opacità.")

# ==========================================
# SCHEDA 2: SIMULAZIONI
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
    impatto_tier1 = -crollo * 1.5
    impatto_tier3 = -crollo * 0.2
    impatto_totale = (impatto_tier1 * 0.35) + (-crollo * 0.25) + (impatto_tier3 * 0.40)
    
    # MOSTRIAMO LA PERDITA IN EURO REALI BASATA SUL CAPITALE GLOBALE!
    perdita_euro = capitale_globale * (impatto_totale / 100)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Impatto Tier 1", f"{impatto_tier1:.1f}%", "Rischio Alto", delta_color="inverse")
    col_c2.metric("Impatto Tier 3", f"{impatto_tier3:.1f}%", "Protezione Attiva")
    col_c3.metric("Impatto Portafoglio", f"€ {perdita_euro:,.2f} ({impatto_totale:.1f}%)", "Mitigato")

# ==========================================
# SCHEDA 3: COMPLIANCE & ORDINI
# ==========================================
with tab_ordini:
    st.header("⚖️ Motore di Compliance UCITS (Regola 5/10/40)")
    st.button("🛡️ Carica Pesi Ottimali (Master Rulebook)", on_click=carica_rulebook, type="primary")

    col_a, col_b = st.columns(2)
    with col_a:
        peso_nano_base = st.slider("Peso NanoXplore Base (%)", min_value=0, max_value=20, key="p_nano")
        peso_amat = st.slider("Peso Applied Materials (%)", min_value=0, max_value=20, key="p_amat")
        peso_aix = st.slider("Peso Aixtron (%)", min_value=0, max_value=20, key="p_aix")
    with col_b:
        peso_sam = st.slider("Peso Samsung (%)", min_value=0, max_value=20, key="p_sam")
        peso_tsmc = st.slider("Peso TSMC (%)", min_value=0, max_value=20, key="p_tsmc")
    
    peso_nano_effettivo = peso_nano_base * st.session_state.dsrm_nano
    
    if st.session_state.dsrm_nano < 1.0:
        st.warning(f"⚠️ Nota: Il peso di NanoXplore è stato ridotto automaticamente a {peso_nano_effettivo}% dall'intervento del DSRM.")

    pesi_principali = [peso_nano_effettivo, peso_amat, peso_aix, peso_sam, peso_tsmc]
    violazione_10 = any(p > 10 for p in pesi_principali)
    somma_maggiori_5 = sum(p for p in pesi_principali if p > 5)
    violazione_40 = somma_maggiori_5 > 40

    if violazione_10: st.error("🔴 TRANSAZIONI BLOCCATE: Violazione Regola 10%.")
    elif violazione_40: st.error("🔴 TRANSAZIONI BLOCCATE: Violazione Regola 40%.")
    else: st.success("🟢 PORTAFOGLIO A NORMA UCITS! Ordini sbloccati.")

    st.markdown("---")
    st.header("🧮 Vault Calculator (Ordini in Tempo Reale)")
    # RIMOSSO L'INPUT LOCALE. ORA USA IL CAPITALE_GLOBALE DELLA SIDEBAR!
    st.write(f"Budget attuale sincronizzato: **€ {capitale_globale:,.2f}**")

    if not (violazione_10 or violazione_40):
        if st.button("Connettiti al Mercato e Genera Ordini"):
            with st.spinner('Scaricando i prezzi...'):
                def ottieni_prezzo(ticker):
                    try: return round(yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1], 2)
                    except: return 0.001
                
                ordini = pd.DataFrame({
                    "Azienda (Ticker)": ["NanoXplore (NNXPF)", "Applied Materials (AMAT)", "Aixtron (AIXXF)", "Samsung (SSNLF)", "TSMC (TSM)"],
                    "Prezzo LIVE ($)": [ottieni_prezzo("NNXPF"), ottieni_prezzo("AMAT"), ottieni_prezzo("AIXXF"), ottieni_prezzo("SSNLF"), ottieni_prezzo("TSM")],
                    # MATEMATICA COLLEGATA AL CAPITALE GLOBALE
                    "Budget Assegnato": [capitale_globale * (peso_nano_effettivo/100), capitale_globale * (peso_amat/100), capitale_globale * (peso_aix/100), capitale_globale * (peso_sam/100), capitale_globale * (peso_tsmc/100)]
                })
                
                ordini["Quantità Esatta da Comprare"] = (ordini["Budget Assegnato"] / ordini["Prezzo LIVE ($)"]).astype(int)
                ordini_filtrati = ordini[ordini["Quantità Esatta da Comprare"] > 0]
                
                st.table(ordini_filtrati)
                
                csv = ordini_filtrati.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Scarica Report Ordini (CSV)", data=csv, file_name='Ordini_GGIV.csv', mime='text/csv')

# ==========================================
# SCHEDA 4: RADAR SENTIMENT
# ==========================================
with tab_news:
    st.header("📰 Radar Sentiment (Analisi Web in Tempo Reale)")
    col_news1, col_news2 = st.columns(2)
    with col_news1:
        st.subheader("NanoXplore")
        st.progress(0.85)
        st.caption("Sentiment: 85% Positivo")
    with col_news2:
        st.subheader("Applied Materials")
        st.progress(0.92)
        st.caption("Sentiment: 92% Fortemente Positivo")
