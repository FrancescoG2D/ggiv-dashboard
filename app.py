import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf # Aggiunta per recuperare dati indici
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
url_db = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?output=csv"
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
# 5. UI ISTITUZIONALE: TICKER & ANELLO (Aggiornato Stile Bloomberg)
# ==========================================

# Funzione per ottenere dati di un indice (nuova)
def get_index_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            close = data['Close'].iloc[-1]
            prev_close = data['Open'].iloc[0] # Approssimazione per la variazione
            change = close - prev_close
            change_percent = (change / prev_close) * 100
            return {
                'ticker': ticker.split('^')[-1] if '^' in ticker else ticker,
                'price': close,
                'change_percent': change_percent
            }
        return None
    except:
        return None

# Recupero dati per indici globali (nuovo)
indici_globali = {
    'S&P 500': '^GSPC',
    'Nasdaq': '^IXIC',
    'Gold': 'GC=F',
    'Oil': 'CL=F'
}

data_indici = []
with st.spinner('Scaricando dati indici...'):
    for name, ticker in indici_globali.items():
        data = get_index_data(ticker)
        if data:
            data['name'] = name
            data_indici.append(data)

# Il tuo indice (con valori simulati/recuperati se possibile)
# In un'applicazione reale, questo verrebbe calcolato dai dati del tuo fondo.
info_tuo_indice = {
    'ticker': 'GGIV INDEX',
    'price': 10245.50,
    'change_percent': 1.4
}

# Funzione per formattare il testo del ticker con colori (nuova)
def format_ticker_text(item):
    name = item.get('name', item['ticker'])
    price = f"{item['price']:,.2f}"
    change = item['change_percent']
    color = "color: #00ff00;" if change >= 0 else "color: #ff4b4b;"
    sign = "+" if change >= 0 else ""
    return f'<span class="ticker-item">{name} <span class="ticker-price">{price}</span> <span class="ticker-change" style="{color}">{sign}{change:.1f}%</span></span>'

# Testo del ticker (modificato per non andare in loop)
testo_tuo_indice = f'<span class="ticker-item main-index">{info_tuo_indice["ticker"]} <span class="ticker-price">{info_tuo_indice["price"]:,.2f}</span> <span class="ticker-change" style="color: #00ff00;">+{info_tuo_indice["change_percent"]:.1f}%</span></span>'
testo_indici_globali = ' | '.join([format_ticker_text(item) for item in data_indici])

st.markdown(f"""
<style>
    /* 1. FORZA IL TICKER IN ALTO, FISSO A SINISTRA (Stile Bloomberg) */
    .ticker-wrap {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 60px !important; /* Altezza aumentata */
        background-color: #0e1117 !important;
        border-bottom: 2px solid #1f77b4 !important;
        z-index: 9999999 !important; /* Livello massimo */
        display: flex !important;
        align-items: center !important;
        padding-left: 20px !important;
        font-family: 'Courier New', monospace !important;
        overflow-x: auto !important; /* Permette lo scorrimento orizzontale se necessario */
        white-space: nowrap !important;
    }}
    
    .ticker-item {{
        display: inline-block !important;
        margin-right: 25px !important; /* Spaziatura tra elementi */
        font-weight: bold !important;
        color: #f0f2f6 !important; /* Colore di base */
    }}
    
    /* Stile per il tuo indice principale */
    .main-index {{
        font-size: 20px !important; /* Dimensione maggiore */
        color: #00ff00 !important; /* Colore verde */
    }}

    .ticker-price {{
        font-weight: normal !important;
    }}

    .ticker-change {{
        /* Il colore è gestito inline in format_ticker_text */
    }}
    
    /* 2. FORGIA DELL'ANELLO (Visibile quando la sidebar è CHIUSA) */
    [data-testid="collapsedControl"] {{
        top: 80px !important; /* Spostato più in basso a causa del ticker più alto */
        left: 0px !important; 
        width: 60px !important;
        height: 60px !important;
        background: radial-gradient(circle, #ffdf00 0%, #b8860b 100%) !important;
        border-radius: 0 50% 50% 0 !important; /* Forma a segnalibro tondo */
        z-index: 10000000 !important; /* Sopra anche al ticker */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
        transition: all 0.3s ease-in-out !important;
    }}

    /* Inserisce l'Anello fisico */
    [data-testid="collapsedControl"]::before {{
        content: "💍" !important;
        font-size: 30px !important;
    }}

    /* Nasconde la freccetta originale che darebbe fastidio */
    [data-testid="collapsedControl"] svg {{
        display: none !important;
    }}

    [data-testid="collapsedControl"]:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 0 25px rgba(255, 215, 0, 1) !important;
    }}

    /* 3. CALAMITA PER I TAB */
    div[data-testid="stTabs"] > div:first-child {{
        position: sticky !important;
        top: 60px !important; /* Appena sotto il ticker più alto */
        z-index: 999999 !important;
        background-color: white !important;
        padding: 10px 0 !important;
        border-bottom: 2px solid #1f77b4 !important;
    }}

    /* Sposta il resto del contenuto per non farlo coprire */
    .main .block-container {{
        padding-top: 7rem !important; /* Padding aumentato */
    }}
</style>

<div class="ticker-wrap">{testo_tuo_indice} | {testo_indici_globali}</div>
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
    "📊 Database & DSRM", 
    "🔭 Incubatore", 
    "📉 Backtest & Stress Test", 
    "🧮 Rischio & Ordini", 
    "📰 Radar Sentiment", 
    "🔬 Sensore Brevetti"
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
        # Mostra tabella colorata
        st.dataframe(df_aziende.style.apply(lambda x: ['background-color: #ff4b4b' if i==True else '' for i in (x == x)], axis=1, subset=pd.IndexSlice[df_aziende['Giorni_Silenzio'] > 90, :]))
        
        aziende_penalizzate = df_aziende[df_aziende['Fattore_DSRM'] < 1.0]
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
    st.header("📈 Backtest & Stress Test (Ultimi 3 Anni)")
    date = pd.date_range(start="2021-01-01", periods=36, freq="ME")
    df_backtest = pd.DataFrame({"Data": date, "S&P 500": np.linspace(100, 130, 36) + np.random.normal(0, 2, 36), "GGIV Strategy": np.linspace(100, 165, 36) + np.random.normal(0, 3, 36)})
    st.plotly_chart(px.line(df_backtest, x="Data", y=["S&P 500", "GGIV Strategy"], color_discrete_sequence=["gray", "#00cc66"]), use_container_width=True)

    st.markdown("---")
    crollo = st.slider("Simula Crollo Mercato (%):", 0, 50, 20)
    peso_t1, peso_t2, peso_t3 = [df_aziende[df_aziende['Tier'] == t]['Peso_Effettivo'].sum() for t in ['Tier 1', 'Tier 2', 'Tier 3']]
    impatto_tot = (-crollo * 1.5 * (peso_t1/100)) + (-crollo * (peso_t2/100)) + (-crollo * 0.2 * (peso_t3/100))
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Impatto Tier 1", f"{-crollo * 1.5:.1f}%", "Rischio Alto", delta_color="inverse")
    col_c2.metric("Impatto Tier 3", f"{-crollo * 0.2:.1f}%", "Protezione")
    col_c3.metric("Impatto Portafoglio Netto", f"€ {capitale_globale * (impatto_tot / 100):,.2f} ({impatto_tot:.1f}%)")

# --- SCHEDA 4: RISCHIO & ORDINI ---
with tab_rischio:
    st.header("🛡️ Gestione Rischio & Ordini")
    limite_rischio = st.slider("Termometro Rischio (Max %):", 5, 40, 15)
    
    peso_totale_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum()
    blocco_scudo = peso_totale_shield < 30
    
    if blocco_scudo: st.error(f"🔴 BLOCCO OPERATIVITÀ: Tier 3 al {peso_totale_shield:.1f}%. Minimo richiesto: 30%.")
    else: st.success(f"🟢 GOLDEN SHIELD ATTIVO: Tier 3 al {peso_totale_shield:.1f}%.")

    for _, row in df_aziende[df_aziende['Peso_Effettivo'] > limite_rischio].iterrows():
        st.warning(f"💰 PROFIT TAKER: {row['Azienda']} eccede ({row['Peso_Effettivo']}%). Vendi {row['Peso_Effettivo'] - limite_rischio:.1f}%.")

    st.markdown("---")
    somma_pesi = df_aziende['Peso_Effettivo'].sum()
    df_aziende['Peso_Normalizzato'] = (df_aziende['Peso_Effettivo'] / somma_pesi) * 100 if somma_pesi > 0 else 0

    if not blocco_scudo and st.button("Calcola Lotti"):
        with st.spinner('Scaricando prezzi...'):
            df_aziende['Prezzo_LIVE_$'] = df_aziende['Ticker'].apply(lambda t: round(yf.Ticker(t).history(period="1d")['Close'].iloc[-1], 2) if len(yf.Ticker(t).history(period="1d")) > 0 else 0.001)
            df_aziende['Budget_€'] = capitale_globale * (df_aziende['Peso_Normalizzato'] / 100)
            # Modifica per supportare azioni frazionate (Opzione B discussa in precedenza)
            df_aziende['Azioni'] = (df_aziende['Budget_€'] / df_aziende['Prezzo_LIVE_$']).round(4) 
            ordini = df_aziende[df_aziende['Azioni'] > 0][['Ticker', 'Azienda', 'Prezzo_LIVE_$', 'Budget_€', 'Azioni']]
            st.table(ordini)

# --- SCHEDA 5 & 6 ---
with tab_sentiment:
    st.header("📰 Radar Sentiment")
    st.progress(0.85); st.caption("Graphene: 85% Positivo")
    st.progress(0.60); st.caption("Semiconductors: 60% Neutrale")

with tab_brevetti:
    st.header("🔬 Sensore IP (Brevetti)")
    target = st.selectbox("Seleziona Azienda:", df_aziende['Azienda'].tolist())
    score = df_aziende[df_aziende['Azienda'] == target]['Health_Score'].values[0] if not df_aziende.empty else 0
    st.metric("Score", f"{score}/100", "🟢 Eccellente" if score >= 80 else "🟡 Moderato" if score >= 50 else "🔴 Allerta")
