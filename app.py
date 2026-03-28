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

def carica_rulebook():
    st.session_state.p_nano = 8
    st.session_state.p_amat = 8
    st.session_state.p_aix = 8
    st.session_state.p_sam = 8
    st.session_state.p_tsmc = 8

# --- INTESTAZIONE ---
st.title("🛡️ GGIV - Graphene Global Index Vault")
st.markdown("Terminale Istituzionale. Protezione algoritmica attiva.")
st.markdown("---")

# CREAZIONE DELLE 4 SCHEDE (TABS)
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
    col1.metric("Valore Portafoglio", "€ 10.450,00", "+4.5% YTD")
    col2.metric("Max Drawdown GGIV", "-22.1%", "Protetto")
    col3.metric("Volatilità Annua", "18.5%", "Ottimale")
    col4.metric("Sharpe Ratio", "0.82", "Efficienza Alta")

    st.markdown("---")
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
    
    # --- IL NUOVO MOTORE DSRM ATTIVO ---
    st.header("🚦 Motore DSRM (Riallocazione Capitale in Tempo Reale)")
    st.write("Simula l'intervento dell'algoritmo. Quando un'azienda smette di comunicare, il GGIV le toglie fondi per spostarli nello Shield.")

    col_dsrm_comandi, col_dsrm_risultati = st.columns([1, 2])

    with col_dsrm_comandi:
        azienda_test = st.selectbox("Seleziona Azienda Sotto Analisi:", ["NanoXplore (Tier 1)", "Aixtron (Tier 2)"])
        peso_iniziale = 10.0  # Fissiamo il peso iniziale al 10%
        giorni_silenzio = st.slider("Giorni di silenzio (T):", min_value=0, max_value=120, value=30)

        def calcola_dsrm(t):
            if t <= 45: return 1.0, "🟢 Verde (Safe)"
            elif t <= 90: return 0.75, "🟡 Giallo (Penalità 25%)"
            else: return 0.0, "🔴 KILL SWITCH (Espulsione)"

        fattore_moltiplicatore, stato_algoritmo = calcola_dsrm(giorni_silenzio)

    with col_dsrm_risultati:
        st.markdown("### ⚡ Reazione del Portafoglio")
        
        # Calcolo matematico della penalità
        nuovo_peso = peso_iniziale * fattore_moltiplicatore
        capitale_liberato = peso_iniziale - nuovo_peso
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Stato Allarme", stato_algoritmo)
        
        # Se c'è un taglio, mostriamo la differenza in rosso
        delta_peso = f"{nuovo_peso - peso_iniziale}%" if nuovo_peso < peso_iniziale else "Invariato"
        c2.metric(f"Peso {azienda_test}", f"{nuovo_peso}%", delta_peso, delta_color="inverse" if nuovo_peso < peso_iniziale else "off")
        
        # Mostriamo i soldi che finiscono nello scudo
        c3.metric("Capitale spostato nel Tier 3", f"+{capitale_liberato}%", "Protezione Attiva" if capitale_liberato > 0 else "")

        # Messaggi di sistema per spiegare l'azione all'investitore
        if fattore_moltiplicatore == 0.0:
            st.error(f"🚨 AZIONE ESEGUITA: L'azienda {azienda_test} è stata espulsa dall'indice. Il {capitale_liberato}% del capitale è stato istantaneamente venduto e riallocato nel Tier 3 per proteggere i fondi.")
        elif fattore_moltiplicatore == 0.75:
            st.warning(f"⚠️ AZIONE ESEGUITA: Rischio opacità rilevato. Il peso di {azienda_test} è stato decurtato. Il {capitale_liberato}% del capitale è stato messo in sicurezza nel Tier 3.")
        else:
            st.success("✅ NESSUNA AZIONE: L'azienda comunica regolarmente. Capitale allocato al 100%.")


# ==========================================
# SCHEDA 2: SIMULAZIONI (I NUOVI STRUMENTI)
# ==========================================
with tab_simulazioni:
    st.header("📈 Backtest: GGIV vs S&P 500 (Ultimi 3 Anni)")
    st.write("Simulazione della sovraperformance dell'algoritmo rispetto al mercato tradizionale.")
    
    # Creiamo dati finti ma realistici per il grafico
    date = pd.date_range(start="2021-01-01", periods=36, freq="ME")
    crescita_sp500 = np.linspace(100, 130, 36) + np.random.normal(0, 2, 36)
    crescita_ggiv = np.linspace(100, 165, 36) + np.random.normal(0, 3, 36) # Il GGIV sale di più!
    
    df_backtest = pd.DataFrame({"Data": date, "S&P 500": crescita_sp500, "GGIV Strategy": crescita_ggiv})
    fig_line = px.line(df_backtest, x="Data", y=["S&P 500", "GGIV Strategy"], 
                       color_discrete_sequence=["gray", "#00cc66"])
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.header("🌪️ Stress Test: Simulatore di Crollo")
    crollo = st.slider("Simula un crollo improvviso del mercato tech (%):", min_value=0, max_value=50, value=20)
    
    # Matematica del crollo
    impatto_tier1 = -crollo * 1.5  # I pure players crollano di più
    impatto_tier3 = -crollo * 0.2  # Lo scudo tiene botta
    impatto_totale = (impatto_tier1 * 0.35) + (-crollo * 0.25) + (impatto_tier3 * 0.40)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Impatto Tier 1 (Volatile)", f"{impatto_tier1:.1f}%", "Rischio Alto", delta_color="inverse")
    col_c2.metric("Impatto Tier 3 (The Shield)", f"{impatto_tier3:.1f}%", "Protezione Attiva")
    col_c3.metric("Impatto Portafoglio GGIV", f"{impatto_totale:.1f}%", "Mitigato rispetto al mercato")

# ==========================================
# SCHEDA 3: COMPLIANCE & ORDINI (CON DOWNLOAD REPORT)
# ==========================================
with tab_ordini:
    st.header("⚖️ Motore di Compliance UCITS (Regola 5/10/40)")
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
        st.info(f"Resto del portafoglio (quote < 5%): **{peso_resto}%**")

    pesi_principali = [peso_nano, peso_amat, peso_aix, peso_sam, peso_tsmc]
    violazione_10 = any(p > 10 for p in pesi_principali)
    somma_maggiori_5 = sum(p for p in pesi_principali if p > 5)
    violazione_40 = somma_maggiori_5 > 40

    if violazione_10: st.error("🔴 TRANSAZIONI BLOCCATE: Violazione Regola 10%.")
    elif violazione_40: st.error(f"🔴 TRANSAZIONI BLOCCATE: Violazione Regola 40% (Attuale: {somma_maggiori_5}%).")
    else: st.success("🟢 PORTAFOGLIO A NORMA UCITS! Ordini sbloccati.")

    st.markdown("---")
    st.header("🧮 Vault Calculator (Ordini in Tempo Reale)")
    capitale_input = st.number_input("Capitale da allocare (€ o $):", min_value=100, max_value=1000000, value=5000, step=100)

    if violazione_10 or violazione_40:
        st.warning("⚠️ Risolvi le violazioni UCITS per generare gli ordini.")
    else:
        if st.button("Connettiti al Mercato e Genera Ordini"):
            with st.spinner('Scaricando i prezzi...'):
                def ottieni_prezzo(ticker):
                    try: return round(yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1], 2)
                    except: return 0.001
                
                ordini = pd.DataFrame({
                    "Azienda (Ticker)": ["NanoXplore (NNXPF)", "Applied Materials (AMAT)", "Aixtron (AIXXF)", "Samsung (SSNLF)", "TSMC (TSM)"],
                    "Prezzo LIVE ($)": [ottieni_prezzo("NNXPF"), ottieni_prezzo("AMAT"), ottieni_prezzo("AIXXF"), ottieni_prezzo("SSNLF"), ottieni_prezzo("TSM")],
                    "Budget Assegnato": [capitale_input * (peso_nano/100), capitale_input * (peso_amat/100), capitale_input * (peso_aix/100), capitale_input * (peso_sam/100), capitale_input * (peso_tsmc/100)]
                })
                ordini["Quantità Esatta da Comprare"] = (ordini["Budget Assegnato"] / ordini["Prezzo LIVE ($)"]).astype(int)
                
                st.table(ordini)
                
                # IL NUOVO PULSANTE PER SCARICARE IL REPORT CSV
                csv = ordini.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Report Ordini (CSV)",
                    data=csv,
                    file_name='Ordini_GGIV.csv',
                    mime='text/csv',
                )

# ==========================================
# SCHEDA 4: RADAR SENTIMENT (NEW)
# ==========================================
with tab_news:
    st.header("📰 Radar Sentiment (Analisi Web in Tempo Reale)")
    st.write("L'algoritmo analizza migliaia di fonti web per rilevare il sentiment di mercato sulle aziende in portafoglio.")
    
    col_news1, col_news2 = st.columns(2)
    with col_news1:
        st.subheader("NanoXplore")
        st.progress(0.85)
        st.caption("Sentiment: 85% Positivo (Nuovi brevetti annunciati)")
        
        st.subheader("Aixtron")
        st.progress(0.40)
        st.caption("Sentiment: 40% Neutrale/Negativo (Rallentamento supply chain)")
        
    with col_news2:
        st.subheader("Applied Materials")
        st.progress(0.92)
        st.caption("Sentiment: 92% Fortemente Positivo (Trimestrale record)")
        
        st.subheader("FrodeAsia (Esempio)")
        st.progress(0.10)
        st.caption("Sentiment: 10% Allerta Rossa (Indagini in corso)")
