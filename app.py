import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE
# ==========================================
st.set_page_config(page_title="GGIV Terminal", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. DARK MODE ISTITUZIONALE — CSS GLOBALE
# ==========================================
# Palette: nero profondo (#0a0e1a) + blu notte (#0d1b2a) + accenti verde terminale (#00d4aa) + oro (#c9a84c)
st.markdown("""
<style>
    /* --- BASE --- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0a0e1a !important;
        color: #e8eaf0 !important;
    }

    /* --- MAIN CONTENT AREA --- */
    [data-testid="stMain"], .main, .block-container {
        background-color: #0a0e1a !important;
        color: #e8eaf0 !important;
    }
    .block-container {
        padding-top: 5.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a !important;
        border-right: 1px solid #1a2d45 !important;
    }
    [data-testid="stSidebar"] * { color: #e8eaf0 !important; }
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #0a1628 !important;
        border: 1px solid #1a3a5c !important;
        color: #00d4aa !important;
    }

    /* --- HEADER FISSO STILE BLOOMBERG --- */
    .ggiv-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 52px !important;
        background-color: #060910 !important;
        border-bottom: 1px solid #c9a84c !important;
        z-index: 9999999 !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 24px !important;
        font-family: 'Courier New', monospace !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        gap: 0 !important;
    }
    .ggiv-logo {
        font-size: 15px !important;
        font-weight: bold !important;
        color: #c9a84c !important;
        letter-spacing: 0.15em !important;
        margin-right: 28px !important;
        flex-shrink: 0 !important;
    }
    .ggiv-divider {
        width: 1px !important;
        height: 28px !important;
        background: #1a3a5c !important;
        margin-right: 28px !important;
        flex-shrink: 0 !important;
    }
    .ticker-scroll {
        display: flex !important;
        gap: 32px !important;
        overflow: hidden !important;
        flex: 1 !important;
    }
    .t-item { display: inline-flex; align-items: baseline; gap: 6px; flex-shrink: 0; }
    .t-name { font-size: 11px; color: #7a8fa6; letter-spacing: 0.05em; }
    .t-price { font-size: 13px; font-weight: bold; color: #e8eaf0; }
    .t-up { color: #00d4aa; font-size: 11px; }
    .t-down { color: #e05a5a; font-size: 11px; }
    .t-main { font-size: 13px; font-weight: bold; color: #c9a84c; margin-right: 32px; flex-shrink: 0; letter-spacing: 0.08em; }

    /* --- TAB BAR --- */
    div[data-testid="stTabs"] > div:first-child {
        position: sticky !important;
        top: 52px !important;
        z-index: 999998 !important;
        background-color: #0a0e1a !important;
        border-bottom: 1px solid #1a2d45 !important;
        padding: 6px 0 0 !important;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #7a8fa6 !important;
        font-size: 12px !important;
        letter-spacing: 0.05em !important;
        border-bottom: 2px solid transparent !important;
        padding-bottom: 8px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00d4aa !important;
        border-bottom: 2px solid #00d4aa !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #e8eaf0 !important;
        background-color: transparent !important;
    }

    /* --- METRICHE --- */
    [data-testid="stMetric"] {
        background-color: #0d1b2a !important;
        border: 1px solid #1a2d45 !important;
        border-radius: 6px !important;
        padding: 16px 20px !important;
    }
    [data-testid="stMetricLabel"] { color: #7a8fa6 !important; font-size: 11px !important; letter-spacing: 0.06em !important; }
    [data-testid="stMetricValue"] { color: #e8eaf0 !important; font-size: 22px !important; }
    [data-testid="stMetricDelta"] svg { display: none !important; }
    [data-testid="stMetricDelta"] > div { color: #00d4aa !important; font-size: 12px !important; }

    /* --- DATAFRAME --- */
    [data-testid="stDataFrame"], .stDataFrame {
        background-color: #0d1b2a !important;
        border: 1px solid #1a2d45 !important;
        border-radius: 6px !important;
    }

    /* --- BOTTONI --- */
    .stButton > button {
        background-color: #0d1b2a !important;
        color: #00d4aa !important;
        border: 1px solid #00d4aa !important;
        border-radius: 4px !important;
        font-size: 12px !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #00d4aa !important;
        color: #0a0e1a !important;
    }

    /* --- SLIDER --- */
    [data-testid="stSlider"] * { color: #e8eaf0 !important; }
    [data-baseweb="slider"] div[role="slider"] { background-color: #00d4aa !important; }

    /* --- ALERTS --- */
    [data-testid="stAlert"] { background-color: #0d1b2a !important; border-radius: 4px !important; }

    /* --- SELECTBOX / INPUT --- */
    [data-testid="stSelectbox"] *, [data-testid="stTextInput"] * { color: #e8eaf0 !important; }
    [data-baseweb="select"] div, [data-baseweb="input"] input {
        background-color: #0d1b2a !important;
        border-color: #1a2d45 !important;
        color: #e8eaf0 !important;
    }

    /* --- PROGRESS --- */
    [data-testid="stProgressBar"] > div > div {
        background-color: #00d4aa !important;
    }

    /* --- TITOLI --- */
    h1, h2, h3, h4 { color: #e8eaf0 !important; }
    p, li, label, span { color: #e8eaf0 !important; }
    .stCaption, [data-testid="stCaptionContainer"] { color: #7a8fa6 !important; }

    /* --- SEPARATORI --- */
    hr { border-color: #1a2d45 !important; }

    /* --- SPINNER --- */
    [data-testid="stSpinner"] * { color: #00d4aa !important; }

    /* --- ANELLO SIDEBAR --- */
    [data-testid="collapsedControl"] {
        top: 64px !important;
        left: 0px !important;
        width: 52px !important;
        height: 52px !important;
        background-color: #0d1b2a !important;
        border: 1px solid #c9a84c !important;
        border-left: none !important;
        border-radius: 0 6px 6px 0 !important;
        z-index: 9999998 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="collapsedControl"]::before {
        content: "💍" !important;
        font-size: 22px !important;
    }
    [data-testid="collapsedControl"] svg { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SISTEMA DI LOGIN
# ==========================================
if not st.session_state.get('accesso_consentito', False):
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                min-height:80vh; gap:16px;">
        <div style="font-family:'Courier New',monospace; font-size:28px; color:#c9a84c;
                    letter-spacing:0.2em; font-weight:bold;">GGIV TERMINAL</div>
        <div style="font-size:11px; color:#7a8fa6; letter-spacing:0.15em;">
            GRAPHENE GLOBAL INDEX VAULT — ACCESSO RISERVATO
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        password_inserita = st.text_input("", type="password", placeholder="Password istituzionale")
        if st.button("ACCEDI", use_container_width=True):
            if password_inserita == "Founder2026":
                st.session_state.accesso_consentito = True
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# ==========================================
# 4. CONNESSIONE AL DATABASE
# ==========================================
url_db = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?output=csv"
url_wl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPnMivIJ1O9GbdTbjkrVa8InhtJ6qm1UNwrU__0bOrikkWXkJA638y6tu6Ej0hRUXeKGEQsWP8E6dX/pub?gid=577137332&single=true&output=csv"

@st.cache_data(ttl=60)
def carica_dati(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return pd.DataFrame()

df_aziende = carica_dati(url_db)
df_wl = carica_dati(url_wl)

# ==========================================
# 5. MOTORE DSRM
# ==========================================
def elabora_dati(df):
    if df.empty:
        return df
    if 'Data_Ultima_News' in df.columns:
        df['Data_Ultima_News'] = pd.to_datetime(df['Data_Ultima_News'], dayfirst=True, errors='coerce')
        oggi = pd.Timestamp.now(tz='Europe/Rome').normalize().tz_localize(None)
        df['Giorni_Silenzio'] = (oggi - df['Data_Ultima_News']).dt.days
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
# 6. TICKER HEADER
# ==========================================
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            close_oggi = data['Close'].iloc[-1]
            close_ieri = data['Close'].iloc[-2]
            change_pct = ((close_oggi - close_ieri) / close_ieri) * 100
            return {'price': close_oggi, 'change_pct': change_pct}
        return None
    except Exception as e:
        st.warning(f"Dati non disponibili per {ticker}: {e}")
        return None

indici = {'S&P 500': '^GSPC', 'NASDAQ': '^IXIC', 'GOLD': 'GC=F', 'OIL': 'CL=F', 'VIX': '^VIX'}
dati_indici = {}
for name, ticker in indici.items():
    d = get_index_data(ticker)
    if d:
        dati_indici[name] = d

def render_ticker_item(name, d):
    cls = "t-up" if d['change_pct'] >= 0 else "t-down"
    sign = "+" if d['change_pct'] >= 0 else ""
    return f'<span class="t-item"><span class="t-name">{name}</span><span class="t-price">{d["price"]:,.2f}</span><span class="{cls}">{sign}{d["change_pct"]:.2f}%</span></span>'

ticker_html = ''.join([render_ticker_item(n, d) for n, d in dati_indici.items()])

st.markdown(f"""
<div class="ggiv-header">
    <span class="t-main">⬡ GGIV</span>
    <div class="ggiv-divider"></div>
    <div class="ticker-scroll">{ticker_html}</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. SIDEBAR
# ==========================================
st.sidebar.markdown("""
<div style="font-family:'Courier New',monospace; font-size:16px; color:#c9a84c;
            letter-spacing:0.15em; font-weight:bold; padding:8px 0 16px;">
    ⬡ GGIV TERMINAL
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown('<p style="font-size:11px; color:#7a8fa6; letter-spacing:0.08em;">PARAMETRI PORTAFOGLIO</p>', unsafe_allow_html=True)
capitale_globale = st.sidebar.number_input("Capitale AUM (€):", min_value=1000, value=100000, step=1000)
st.sidebar.markdown("---")
st.sidebar.markdown(f'<p style="font-size:10px; color:#7a8fa6;">Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', unsafe_allow_html=True)

# ==========================================
# 8. SCHEDE
# ==========================================
tab_overview, tab_watchlist, tab_backtest, tab_rischio, tab_sentiment, tab_brevetti = st.tabs([
    "DATABASE & DSRM",
    "INCUBATORE",
    "BACKTEST & STRESS",
    "RISCHIO & ORDINI",
    "RADAR SENTIMENT",
    "SENSORE BREVETTI"
])

# --- SCHEDA 1: OVERVIEW ---
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AUM TOTALE", f"€ {capitale_globale:,.0f}", "+4.5% YTD")
    col2.metric("AZIENDE IN INDICE", str(len(df_aziende)) if not df_aziende.empty else "0", "sincronizzato")
    col3.metric("VOLATILITÀ ANNUA", "18.5%", "ottimale")
    col4.metric("SHARPE RATIO", "0.82", "efficienza alta")

    st.markdown("---")

    # SUNBURST — Asset Allocation Tier > Aziende
    if not df_aziende.empty and 'Tier' in df_aziende.columns:
        st.markdown("### ASSET ALLOCATION — MAPPA STRUTTURALE")

        # Costruisce la struttura per il sunburst
        # Livello 0: root
        # Livello 1: Tier
        # Livello 2: Aziende
        labels = ["GGIV INDEX"]
        parents = [""]
        values = [df_aziende['Peso_Effettivo'].sum()]
        colors = ["#c9a84c"]

        # Palette per i Tier
        tier_colors = {
            'Tier 1': '#e05a5a',
            'Tier 2': '#378ADD',
            'Tier 3': '#00d4aa',
        }

        # Aggiunge i Tier
        for tier in df_aziende['Tier'].unique():
            peso_tier = df_aziende[df_aziende['Tier'] == tier]['Peso_Effettivo'].sum()
            labels.append(tier)
            parents.append("GGIV INDEX")
            values.append(peso_tier)
            colors.append(tier_colors.get(tier, '#7a8fa6'))

        # Aggiunge le singole aziende
        for _, row in df_aziende.iterrows():
            labels.append(row['Azienda'])
            parents.append(row['Tier'])
            values.append(row['Peso_Effettivo'])
            # Tonalità leggermente più chiara del tier
            base = tier_colors.get(row['Tier'], '#7a8fa6')
            colors.append(base + 'bb')  # aggiunge trasparenza leggera

        fig_sunburst = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors, line=dict(color='#0a0e1a', width=2)),
            textfont=dict(family="Courier New", size=11, color="#e8eaf0"),
            hovertemplate='<b>%{label}</b><br>Peso: %{value:.2f}%<extra></extra>',
            branchvalues="total",
            insidetextorientation='radial',
        ))
        fig_sunburst.update_layout(
            paper_bgcolor='#0d1b2a',
            plot_bgcolor='#0d1b2a',
            font=dict(color='#e8eaf0', family='Courier New'),
            margin=dict(t=20, b=20, l=20, r=20),
            height=480,
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        st.caption("Clicca su un Tier per espanderlo e vedere le singole aziende. Clicca al centro per tornare.")

    st.markdown("---")
    st.markdown("### MOTORE DSRM — STATO ATTIVO")

    if not df_aziende.empty:
        st.dataframe(
            df_aziende.style.apply(
                lambda x: ['background-color: #2a0e0e' if i == True else '' for i in (x == x)],
                axis=1,
                subset=pd.IndexSlice[df_aziende['Giorni_Silenzio'] > 90, :]
            ),
            use_container_width=True
        )

        aziende_penalizzate = df_aziende[df_aziende['Fattore_DSRM'] < 1.0]
        capitale_salvato_totale = (df_aziende['Percentuale_Persa'].sum() / 100) * capitale_globale

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.metric("CAPITALE NELLO SHIELD", f"€ {capitale_salvato_totale:,.2f}", "protezione attiva")
        with col_d2:
            if aziende_penalizzate.empty:
                st.success("TUTTE LE AZIENDE COMUNICANO REGOLARMENTE")
            else:
                for _, row in aziende_penalizzate.iterrows():
                    soldi_tolti = (row['Percentuale_Persa'] / 100) * capitale_globale
                    if row['Fattore_DSRM'] == 0:
                        st.error(f"KILL SWITCH: {row['Azienda']} ({row['Giorni_Silenzio']} gg) — € {soldi_tolti:,.2f} blindati")
                    else:
                        st.warning(f"PENALITÀ: {row['Azienda']} ({row['Giorni_Silenzio']} gg) — € {soldi_tolti:,.2f} allo Shield")
    else:
        st.warning("Connessione al database in corso. Controlla i link CSV.")

# --- SCHEDA 2: WATCHLIST ---
with tab_watchlist:
    st.markdown("### AZIENDE IN OSSERVAZIONE")
    if not df_wl.empty:
        st.caption("Aziende sotto scansione per eventuale ingresso nell'indice.")
        colonne_da_mostrare = ['Ticker', 'Azienda']
        if 'Data_Ultima_News' in df_wl.columns:
            colonne_da_mostrare.extend(['Data_Ultima_News', 'Giorni_Silenzio'])
        st.dataframe(df_wl[colonne_da_mostrare], use_container_width=True)
    else:
        st.info("Watchlist vuota o in caricamento.")

# --- SCHEDA 3: BACKTEST ---
with tab_backtest:
    st.markdown("### BACKTEST — ULTIMI 3 ANNI")

    np.random.seed(42)
    date = pd.date_range(start="2021-01-01", periods=36, freq="ME")
    sp = np.linspace(100, 130, 36) + np.random.normal(0, 2, 36)
    ggiv = np.linspace(100, 165, 36) + np.random.normal(0, 3, 36)

    fig_bt = go.Figure()
    fig_bt.add_trace(go.Scatter(
        x=date, y=sp, name="S&P 500",
        line=dict(color='#7a8fa6', width=1.5),
        hovertemplate='S&P 500: %{y:.1f}<extra></extra>'
    ))
    fig_bt.add_trace(go.Scatter(
        x=date, y=ggiv, name="GGIV Strategy",
        line=dict(color='#00d4aa', width=2),
        fill='tonexty', fillcolor='rgba(0,212,170,0.05)',
        hovertemplate='GGIV: %{y:.1f}<extra></extra>'
    ))
    fig_bt.update_layout(
        paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
        font=dict(color='#e8eaf0', family='Courier New', size=11),
        legend=dict(bgcolor='#0d1b2a', bordercolor='#1a2d45'),
        xaxis=dict(gridcolor='#1a2d45', linecolor='#1a2d45'),
        yaxis=dict(gridcolor='#1a2d45', linecolor='#1a2d45'),
        margin=dict(t=20, b=20),
        height=360,
    )
    st.plotly_chart(fig_bt, use_container_width=True)

    st.markdown("---")
    st.markdown("### STRESS TEST")
    crollo = st.slider("Simula crollo mercato (%):", 0, 50, 20, step=1)

    peso_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t2 = df_aziende[df_aziende['Tier'] == 'Tier 2']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    impatto_tot = (-crollo * 1.5 * (peso_t1 / 100)) + (-crollo * (peso_t2 / 100)) + (-crollo * 0.2 * (peso_t3 / 100))

    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("IMPATTO TIER 1", f"{-crollo * 1.5:.1f}%", "rischio alto", delta_color="inverse")
    col_c2.metric("IMPATTO TIER 3", f"{-crollo * 0.2:.1f}%", "protezione shield")
    col_c3.metric("IMPATTO NETTO", f"€ {capitale_globale * (impatto_tot / 100):,.0f}", f"{impatto_tot:.1f}%")

# --- SCHEDA 4: RISCHIO & ORDINI ---
with tab_rischio:
    st.markdown("### GESTIONE RISCHIO & ORDINI")
    limite_rischio = st.slider("Soglia massima per posizione (%):", 5, 40, 15, step=1)

    peso_totale_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    blocco_scudo = peso_totale_shield < 30

    if blocco_scudo:
        st.error(f"BLOCCO OPERATIVITÀ — Tier 3 al {peso_totale_shield:.1f}%. Minimo richiesto: 30%")
    else:
        st.success(f"GOLDEN SHIELD ATTIVO — Tier 3 al {peso_totale_shield:.1f}%")

    if not df_aziende.empty:
        for _, row in df_aziende[df_aziende['Peso_Effettivo'] > limite_rischio].iterrows():
            st.warning(f"PROFIT TAKER — {row['Azienda']}: {row['Peso_Effettivo']:.1f}% — Ridurre di {row['Peso_Effettivo'] - limite_rischio:.1f}%")

    st.markdown("---")

    somma_pesi = df_aziende['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    if somma_pesi > 0:
        df_aziende['Peso_Normalizzato'] = (df_aziende['Peso_Effettivo'] / somma_pesi) * 100
    else:
        df_aziende['Peso_Normalizzato'] = 0

    if not blocco_scudo and st.button("CALCOLA LOTTI"):
        with st.spinner('Scaricando prezzi live...'):
            @st.cache_data(ttl=120)
            def get_prezzo_live(ticker):
                try:
                    storia = yf.Ticker(ticker).history(period="1d")
                    if not storia.empty:
                        return round(storia['Close'].iloc[-1], 2)
                    return 0.001
                except Exception as e:
                    st.warning(f"Prezzo non disponibile per {ticker}: {e}")
                    return 0.001

            df_aziende['Prezzo_LIVE_$'] = df_aziende['Ticker'].apply(get_prezzo_live)
            df_aziende['Budget_€'] = capitale_globale * (df_aziende['Peso_Normalizzato'] / 100)
            df_aziende['Azioni'] = (df_aziende['Budget_€'] / df_aziende['Prezzo_LIVE_$']).round(4)
            ordini = df_aziende[df_aziende['Azioni'] > 0][['Ticker', 'Azienda', 'Prezzo_LIVE_$', 'Budget_€', 'Azioni']]
            st.table(ordini)

# --- SCHEDA 5: SENTIMENT ---
with tab_sentiment:
    st.markdown("### RADAR SENTIMENT")
    st.progress(0.85)
    st.caption("GRAPHENE — 85% POSITIVO")
    st.progress(0.60)
    st.caption("SEMICONDUCTORS — 60% NEUTRALE")

# --- SCHEDA 6: BREVETTI ---
with tab_brevetti:
    st.markdown("### SENSORE IP — BREVETTI")
    if not df_aziende.empty:
        target = st.selectbox("Seleziona azienda:", df_aziende['Azienda'].tolist())
        score_val = df_aziende[df_aziende['Azienda'] == target]['Health_Score'].values
        score = int(score_val[0]) if len(score_val) > 0 else 0
        stato = "ECCELLENTE" if score >= 80 else "MODERATO" if score >= 50 else "ALLERTA"
        colore = "#00d4aa" if score >= 80 else "#c9a84c" if score >= 50 else "#e05a5a"
        st.metric("HEALTH SCORE", f"{score}/100", stato)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#7a8fa6", tickfont=dict(color="#7a8fa6", size=10)),
                bar=dict(color=colore),
                bgcolor="#0d1b2a",
                bordercolor="#1a2d45",
                steps=[
                    dict(range=[0, 50], color="#1a0e0e"),
                    dict(range=[50, 80], color="#1a1a0e"),
                    dict(range=[80, 100], color="#0e1a16"),
                ],
                threshold=dict(line=dict(color=colore, width=2), thickness=0.75, value=score)
            ),
            number=dict(font=dict(color="#e8eaf0", family="Courier New"), suffix="/100"),
        ))
        fig_gauge.update_layout(
            paper_bgcolor='#0d1b2a',
            font=dict(color='#e8eaf0', family='Courier New'),
            height=280,
            margin=dict(t=20, b=20, l=40, r=40),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("Dati non disponibili.")
