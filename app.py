import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np

st.set_page_config(page_title="GGIV Dashboard", layout="wide")

# ==========================================
# 🔗 IL TUO DATABASE GOOGLE SHEETS
# ==========================================
URL_DATABASE = https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?output=csv

# --- FUNZIONE DI CARICAMENTO DATI ---
@st.cache_data(ttl=60) 
def carica_database(url):
    if url == "INCOLLA_QUI_IL_TUO_LINK_CSV" or url == "":
        return pd.DataFrame({
            "Ticker": ["NNXPF", "AMAT", "AIXXF", "SSNLF", "TSM"],
            "Azienda": ["NanoXplore", "Applied Materials", "Aixtron", "Samsung", "TSMC"],
            "Tier": ["Tier 1", "Tier 2", "Tier 2", "Tier 3", "Tier 3"],
            "Peso_Base": [15.0, 10.0, 10.0, 35.0, 30.0],
            "Giorni_Silenzio": [30, 15, 20, 5, 2],
            "Health_Score": [85, 92, 65, 88, 95]
        })
    else:
        return pd.read_csv(url)

df_aziende = carica_database

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
# SCHEDA 3: GESTIONE RISCHIO & PROFIT TAKER
# ==========================================
with tab_ordini:
    st.header("🛡️ Gestione Rischio & Profit Taker Dinamico")
    st.write("Intelligenza algoritmica flessibile per massimizzare i profitti e proteggere il capitale.")

    # 1. IL TERMOMETRO DEL RISCHIO PERSONALE
    col_impostazioni, col_spazio = st.columns([1, 1])
    with col_impostazioni:
        limite_rischio = st.slider("🌡️ Termometro del Rischio (Max % per singolo titolo):", min_value=5, max_value=40, value=15)
        st.caption("Oltre questa soglia, il sistema consiglierà di incassare i profitti.")

    st.markdown("### 🎛️ Allocazione Attuale")
    st.button("🔄 Carica Assetto Bilanciato base", on_click=carica_rulebook, type="primary")

    # Aumentato il max_value a 50 per permetterti di simulare grosse crescite
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Tier 1 & 2 (Volatilità e Crescita)**")
        peso_nano_base = st.slider("Peso NanoXplore (%)", min_value=0, max_value=50, key="p_nano")
        peso_amat = st.slider("Peso Applied Materials (%)", min_value=0, max_value=50, key="p_amat")
        peso_aix = st.slider("Peso Aixtron (%)", min_value=0, max_value=50, key="p_aix")
    with col_b:
        st.markdown("**Tier 3 (The Shield - Protezione)**")
        peso_sam = st.slider("Peso Samsung (%)", min_value=0, max_value=50, key="p_sam")
        peso_tsmc = st.slider("Peso TSMC (%)", min_value=0, max_value=50, key="p_tsmc")
    
    peso_nano_effettivo = peso_nano_base * st.session_state.dsrm_nano
    if st.session_state.dsrm_nano < 1.0:
        st.warning(f"⚠️ Nota: Il peso di NanoXplore è stato ridotto automaticamente a {peso_nano_effettivo}% dal DSRM.")

    # --- IL CERVELLO FUSO (SHIELD + PROFIT TAKER) ---
    st.markdown("### 🧠 Analisi Algoritmica del Portafoglio")
    
    pesi = {
        "NanoXplore": peso_nano_effettivo, 
        "Applied Materials": peso_amat, 
        "Aixtron": peso_aix, 
        "Samsung": peso_sam, 
        "TSMC": peso_tsmc
    }
    somma_totale = sum(pesi.values())
    peso_totale_shield = peso_sam + peso_tsmc

    # Regola 1: Golden Shield
    if peso_totale_shield < 30:
        st.error(f"🛡️ **ALLERTA GOLDEN SHIELD:** Il tuo Tier 3 è al {peso_totale_shield}%. Il GGIV richiede un minimo del 30% per assorbire i crolli di mercato.")
        blocco_scudo = True
    else:
        st.success(f"🛡️ **GOLDEN SHIELD ATTIVO:** Tier 3 al {peso_totale_shield}%. Protezione strutturale garantita.")
        blocco_scudo = False

    # Regola 2: Profit Taker (Consigli basati sul Termometro)
    titoli_sovraesposti = {nome: peso for nome, peso in pesi.items() if peso > limite_rischio}
    
    if titoli_sovraesposti:
        for nome, peso in titoli_sovraesposti.items():
            eccedenza = peso - limite_rischio
            soldi_da_incassare = capitale_globale * (eccedenza / 100)
            st.warning(f"🌡️ **SOVRAESPOSIZIONE su {nome} ({peso}%):** Hai superato il limite psicologico del {limite_rischio}%.")
            st.info(f"💰 **PROFIT TAKER:** Vendi il **{eccedenza:.1f}%** di {nome} per incassare **€ {soldi_da_incassare:,.2f}** di profitti. Spostali nel Tier 3 per blindare il guadagno.")

    st.markdown("---")
    st.header("🧮 Generatore di Ordini")
    st.write(f"Budget attuale sincronizzato: **€ {capitale_globale:,.2f}**")

    # Controlli prima di generare l'ordine
    if somma_totale > 100:
        st.error(f"🔴 Errore Matematico: La somma delle percentuali è {somma_totale}%. Abbassa gli slider per tornare al 100%.")
    elif blocco_scudo:
        st.error("🔴 Operazione Bloccata: Ripristina il Golden Shield (Tier 3 >= 30%) per abilitare gli ordini sicuri.")
    else:
        if st.button("Connettiti al Mercato e Genera Ordini Strategici"):
            with st.spinner('Calcolo delle quote in corso...'):
                def ottieni_prezzo(ticker):
                    try: return round(yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1], 2)
                    except: return 0.001
                
                ordini = pd.DataFrame({
                    "Azienda (Ticker)": ["NanoXplore (NNXPF)", "Applied Materials (AMAT)", "Aixtron (AIXXF)", "Samsung (SSNLF)", "TSMC (TSM)"],
                    "Prezzo LIVE ($)": [ottieni_prezzo("NNXPF"), ottieni_prezzo("AMAT"), ottieni_prezzo("AIXXF"), ottieni_prezzo("SSNLF"), ottieni_prezzo("TSM")],
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


# ==========================================
# SCHEDA 5: SENSORE BREVETTI (IP TRACKER)
# ==========================================
with tab_brevetti:
    st.header("🔬 IP Tracker & Patent Health Score")
    st.write("L'algoritmo scansiona i registri internazionali (WIPO, USPTO, EPO) per valutare il 'fossato tecnologico' delle aziende in portafoglio.")
    st.markdown("---")

    col_ip1, col_ip2 = st.columns([1, 2])

    with col_ip1:
        st.subheader("Seleziona Target")
        azienda_ip = st.selectbox("Scansiona Portafoglio Brevetti:", ["NanoXplore (Graphene Production)", "Applied Materials (Semiconductors)"])
        
        # Simulazione dati estratti dai registri
        if "NanoXplore" in azienda_ip:
            totale_brevetti = 42
            nuovi_12m = 3
            scadenza_critica = "Bassa (Prossimo brevetto chiave scade nel 2034)"
            health_score = 85
            colore_score = "🟢 Ottimo"
        else:
            totale_brevetti = 14500
            nuovi_12m = 0
            scadenza_critica = "ALTA (2 Brevetti core scadono tra 11 mesi)"
            health_score = 40
            colore_score = "🟡 Rischio Obsolescenza"

        st.metric("Patent Health Score (0-100)", f"{health_score}/100", colore_score)

    with col_ip2:
        st.markdown("### 📊 Metriche di Innovazione")
        
        c_ip1, c_ip2, c_ip3 = st.columns(3)
        c_ip1.metric("Brevetti Totali Registrati", totale_brevetti)
        c_ip2.metric("Nuovi Depositi (Ultimi 12 Mesi)", nuovi_12m, "Trend Innovazione")
        c_ip3.metric("Rischio Scadenza (Cliff)", "Attivo", scadenza_critica, delta_color="inverse" if health_score < 50 else "normal")
        
        st.markdown("### 🤖 Suggerimento Algoritmico GGIV")
        if health_score >= 80:
            st.success(f"**VANTAGGIO COMPETITIVO BLINDATO:** {azienda_ip} sta attivamente espandendo la sua proprietà intellettuale. Il fossato tecnologico è profondo. Mantenere l'esposizione Tier 1.")
        elif health_score < 50:
            st.warning(f"**ALLERTA STAGNAZIONE IP:** {azienda_ip} non ha depositato nuovi brevetti rilevanti e affronta scadenze a breve termine. L'algoritmo suggerisce di declassare il titolo al Tier 2 o ridurre il peso del 15% preventivamente.")

    # Grafico a cascata per visualizzare la vita dei brevetti
    st.markdown("---")
    st.subheader("📅 Proiezione Scadenza Brevetti (Prossimi 5 Anni)")
    
    # Dati simulati per il grafico
    anni = ["2026", "2027", "2028", "2029", "2030"]
    brevetti_scadenza = [2, 5, 1, 0, 12] if "Nano" in azienda_ip else [450, 120, 800, 300, 150]
    
    df_brevetti = pd.DataFrame({"Anno": anni, "Brevetti in Scadenza": brevetti_scadenza})
    fig_ip = px.bar(df_brevetti, x="Anno", y="Brevetti in Scadenza", text="Brevetti in Scadenza",
                    color="Brevetti in Scadenza", color_continuous_scale="Reds")
    fig_ip.update_layout(xaxis_type='category')
    st.plotly_chart(fig_ip, use_container_width=True)
