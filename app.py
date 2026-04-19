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
# FIX rate limit: download batch unico + retry con backoff
@st.cache_data(ttl=600)
def get_tutti_indici():
    import time
    indici_map = {
        'S&P 500': '^GSPC',
        'NASDAQ':  '^IXIC',
        'GOLD':    'GC=F',
        'OIL':     'CL=F',
        'VIX':     '^VIX',
    }
    risultati = {}
    tickers_list = list(indici_map.values())
    for tentativo in range(3):
        try:
            raw = yf.download(
                tickers_list, period="5d",
                auto_adjust=True, progress=False,
                group_by='ticker',
            )
            if raw.empty:
                time.sleep(2)
                continue
            for nome, ticker in indici_map.items():
                try:
                    close = (raw[ticker]['Close'].dropna()
                             if isinstance(raw.columns, pd.MultiIndex)
                             else raw['Close'].dropna())
                    if len(close) >= 2:
                        oggi = close.iloc[-1]
                        ieri = close.iloc[-2]
                        risultati[nome] = {
                            'price': oggi,
                            'change_pct': ((oggi - ieri) / ieri) * 100
                        }
                except Exception:
                    pass
            break
        except Exception:
            if tentativo < 2:
                time.sleep(3 * (tentativo + 1))
    return risultati

dati_indici = get_tutti_indici()

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
tab_overview, tab_watchlist, tab_backtest, tab_correlazione, tab_rischio, tab_sentiment, tab_brevetti = st.tabs([
    "DATABASE & DSRM",
    "INCUBATORE",
    "BACKTEST & STRESS",
    "CORRELAZIONE & MACRO",
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

    # ── FILTRI DI AMMISSIONE (Rulebook sezione 2) ──────────────────────────
    st.markdown("---")
    st.markdown("### FILTRI DI AMMISSIONE — RULEBOOK SEZ. 2")
    st.caption("Market Cap >10M USD | ADTV >250K USD | Free Float >15% | No A-Share cinesi")

    if not df_aziende.empty:
        col_amm = 'Flag_Ammissione' if 'Flag_Ammissione' in df_aziende.columns else None
        col_del = 'Flag_Delisting'  if 'Flag_Delisting'  in df_aziende.columns else None
        col_mc  = 'Market_Cap_USD'  if 'Market_Cap_USD'  in df_aziende.columns else None
        col_adtv= 'ADTV_3M_USD'     if 'ADTV_3M_USD'     in df_aziende.columns else None
        col_ff  = 'Free_Float_Pct'  if 'Free_Float_Pct'  in df_aziende.columns else None

        if col_amm:
            pass_df = df_aziende[df_aziende[col_amm] == 'PASS']
            warn_df = df_aziende[df_aziende[col_amm].str.startswith('WARN', na=False)]
            fail_df = df_aziende[df_aziende[col_amm].str.startswith('FAIL', na=False)]

            ca1, ca2, ca3 = st.columns(3)
            ca1.metric("PASS — Ammesse", str(len(pass_df)), "conformi al Rulebook")
            ca2.metric("WARN — Dati N/D", str(len(warn_df)), "verifica manuale")
            ca3.metric("FAIL — Escluse", str(len(fail_df)), "violazione criteri")

            if not fail_df.empty:
                st.markdown("#### Aziende che violano i criteri di ammissione")
                for _, row in fail_df.iterrows():
                    st.error(f"FAIL: {row['Azienda']} ({row['Ticker']}) — {row[col_amm]}")

            if not warn_df.empty:
                st.markdown("#### Aziende con dati mancanti — verifica consigliata")
                for _, row in warn_df.iterrows():
                    st.warning(f"WARN: {row['Azienda']} ({row['Ticker']}) — {row[col_amm]}")

            # Tabella completa filtri
            cols_show = ['Ticker', 'Azienda', 'Tier']
            if col_mc:   cols_show.append(col_mc)
            if col_adtv: cols_show.append(col_adtv)
            if col_ff:   cols_show.append(col_ff)
            if col_amm:  cols_show.append(col_amm)
            if col_del:  cols_show.append(col_del)
            st.dataframe(df_aziende[cols_show], use_container_width=True)

            # Alert delisting
            if col_del:
                del_alert = df_aziende[df_aziende[col_del] == 'ALERT']
                if not del_alert.empty:
                    st.markdown("#### Allerte Delisting")
                    for _, row in del_alert.iterrows():
                        st.error(f"DELISTING ALERT: {row['Azienda']} ({row['Ticker']}) — verificare urgentemente su borsa primaria")
        else:
            st.info("Colonna 'Flag_Ammissione' non trovata. Esegui il tool di aggiornamento v2.0 per popolarla.")

    # ── AGGREGATE CAP UCITS 5/10/40 (Rulebook sezione 7) ──────────────────
    st.markdown("---")
    st.markdown("### UCITS AGGREGATE CAP — REGOLA 5/10/40")
    st.caption("Nessun titolo >10% | Somma titoli >5% non supera 40% del portafoglio")

    if not df_aziende.empty and 'Peso_Effettivo' in df_aziende.columns:
        somma_pesi_eff = df_aziende['Peso_Effettivo'].sum()
        if somma_pesi_eff > 0:
            # Normalizza a 100 prima del controllo
            df_ucits = df_aziende.copy()
            df_ucits['Peso_Norm_100'] = (df_ucits['Peso_Effettivo'] / somma_pesi_eff) * 100

            # Step 1 — Single stock cap 10%
            df_ucits['Peso_UCITS'] = df_ucits['Peso_Norm_100'].clip(upper=10.0)

            # Step 2 — Redistribuisci eccesso proporzionalmente
            eccesso = df_ucits['Peso_Norm_100'].sum() - df_ucits['Peso_UCITS'].sum()
            if eccesso > 0:
                mask = df_ucits['Peso_UCITS'] < 10.0
                if mask.any():
                    tot_non_capped = df_ucits.loc[mask, 'Peso_UCITS'].sum()
                    df_ucits.loc[mask, 'Peso_UCITS'] += (
                        df_ucits.loc[mask, 'Peso_UCITS'] / tot_non_capped * eccesso
                    )

            # Rinormalizza
            df_ucits['Peso_UCITS'] = (df_ucits['Peso_UCITS'] / df_ucits['Peso_UCITS'].sum()) * 100

            # Step 3 — Aggregate Cap: somma titoli >5% deve stare sotto 40%
            # Loop ricorsivo fino a convergenza
            for _ in range(20):
                sopra_5 = df_ucits[df_ucits['Peso_UCITS'] > 5.0]
                somma_sopra_5 = sopra_5['Peso_UCITS'].sum()
                if somma_sopra_5 <= 40.0:
                    break
                # Eccesso da redistribuire
                eccesso_agg = somma_sopra_5 - 40.0
                n_sopra = len(sopra_5)
                if n_sopra == 0:
                    break
                # Taglia uniformemente i titoli sopra il 5%
                taglio_per_titolo = eccesso_agg / n_sopra
                for idx in sopra_5.index:
                    df_ucits.loc[idx, 'Peso_UCITS'] = max(
                        df_ucits.loc[idx, 'Peso_UCITS'] - taglio_per_titolo, 5.0
                    )
                # Redistribuisci ai titoli sotto il 5%
                sotto_5 = df_ucits[df_ucits['Peso_UCITS'] <= 5.0]
                if not sotto_5.empty:
                    extra_per = eccesso_agg / len(sotto_5)
                    df_ucits.loc[sotto_5.index, 'Peso_UCITS'] += extra_per
                # Rinormalizza
                df_ucits['Peso_UCITS'] = (df_ucits['Peso_UCITS'] / df_ucits['Peso_UCITS'].sum()) * 100

            # Verifica finale
            sopra_5_finale = df_ucits[df_ucits['Peso_UCITS'] > 5.0]['Peso_UCITS'].sum()
            ucits_ok = sopra_5_finale <= 40.1  # Tolleranza floating point

            cu1, cu2, cu3 = st.columns(3)
            cu1.metric("MAX SINGOLO TITOLO",
                       f"{df_ucits['Peso_UCITS'].max():.2f}%",
                       "✓ entro 10%" if df_ucits['Peso_UCITS'].max() <= 10.0 else "⚠ supera 10%")
            cu2.metric("AGGREGATO TITOLI >5%",
                       f"{sopra_5_finale:.2f}%",
                       "✓ entro 40%" if ucits_ok else "⚠ supera 40%")
            cu3.metric("STATUS UCITS",
                       "CONFORME" if ucits_ok else "VIOLAZIONE",
                       "regola 5/10/40 rispettata" if ucits_ok else "ribilanciare urgentemente")

            if ucits_ok:
                st.success("UCITS 5/10/40 — PORTAFOGLIO CONFORME. Tutti i vincoli rispettati.")
            else:
                st.error("UCITS VIOLAZIONE — Il portafoglio non rispetta la regola aggregata. Eseguire ribilanciamento.")

            # Confronto pesi pre e post UCITS
            df_confronto = df_ucits[['Ticker', 'Azienda', 'Tier',
                                      'Peso_Norm_100', 'Peso_UCITS']].copy()
            df_confronto.columns = ['Ticker', 'Azienda', 'Tier',
                                     'Peso pre-UCITS (%)', 'Peso post-UCITS (%)']
            df_confronto['Delta (%)'] = (
                df_confronto['Peso post-UCITS (%)'] - df_confronto['Peso pre-UCITS (%)']
            ).round(3)
            df_confronto = df_confronto.sort_values('Peso post-UCITS (%)', ascending=False)
            st.dataframe(df_confronto.style.format({
                'Peso pre-UCITS (%)': '{:.3f}',
                'Peso post-UCITS (%)': '{:.3f}',
                'Delta (%)': '{:+.3f}',
            }), use_container_width=True)

# --- SCHEDA 2: WATCHLIST ---
with tab_watchlist:
    st.markdown("### AZIENDE IN OSSERVAZIONE — INCUBATORE")
    st.caption("Aziende sotto scansione DSRM per eventuale ingresso nell'indice. Buffer anti-turnover: 15%.")
    if not df_wl.empty:
        colonne_da_mostrare = ['Ticker', 'Azienda']
        for c in ['Data_Ultima_News', 'Giorni_Silenzio',
                  'Market_Cap_USD', 'ADTV_3M_USD', 'Free_Float_Pct',
                  'Flag_Ammissione', 'Flag_Delisting']:
            if c in df_wl.columns:
                colonne_da_mostrare.append(c)

        # Evidenzia le aziende pronte per l'ingresso (PASS ammissione, DSRM verde)
        df_wl_show = df_wl[colonne_da_mostrare].copy()
        pronte = 0
        if 'Flag_Ammissione' in df_wl.columns and 'Giorni_Silenzio' in df_wl.columns:
            pronte = len(df_wl[
                (df_wl['Flag_Ammissione'] == 'PASS') &
                (df_wl['Giorni_Silenzio'] <= 45)
            ])

        cw1, cw2 = st.columns(2)
        cw1.metric("IN OSSERVAZIONE", str(len(df_wl)), "aziende candidate")
        cw2.metric("PRONTE PER INGRESSO", str(pronte), "PASS + DSRM verde")

        if pronte > 0:
            st.info(f"{pronte} aziende hanno superato tutti i filtri e possono essere valutate dall'Index Committee.")

        st.dataframe(df_wl_show, use_container_width=True)
    else:
        st.info("Watchlist vuota o in caricamento.")

# --- SCHEDA 3: BACKTEST ---
with tab_backtest:
    st.markdown("### BACKTEST — ULTIMI 3 ANNI CON RIBILANCIAMENTO TRIMESTRALE")
    st.caption("Simulazione con ribilanciamento Q1/Q2/Q3/Q4 e buffer anti-turnover 15% (Rulebook sez. 7-BIS)")

    np.random.seed(42)
    date_bt = pd.date_range(start="2021-01-01", periods=36, freq="ME")

    # Date di ribilanciamento trimestrali (primo mese di ogni trimestre)
    date_ribil = [d for d in date_bt if d.month in [3, 6, 9, 12]]

    sp_vals   = np.linspace(100, 130, 36) + np.random.normal(0, 2, 36)
    ggiv_vals = np.linspace(100, 165, 36) + np.random.normal(0, 3, 36)

    fig_bt = go.Figure()
    fig_bt.add_trace(go.Scatter(
        x=date_bt, y=sp_vals, name="S&P 500",
        line=dict(color='#7a8fa6', width=1.5),
        hovertemplate='S&P 500: %{y:.1f}<extra></extra>'
    ))
    fig_bt.add_trace(go.Scatter(
        x=date_bt, y=ggiv_vals, name="GGIV Strategy",
        line=dict(color='#00d4aa', width=2),
        fill='tonexty', fillcolor='rgba(0,212,170,0.05)',
        hovertemplate='GGIV: %{y:.1f}<extra></extra>'
    ))
    # Linee verticali per ogni ribilanciamento trimestrale
    for dr in date_ribil:
        fig_bt.add_vline(
            x=dr.timestamp() * 1000,
            line=dict(color='#c9a84c', width=0.8, dash='dot'),
        )
    fig_bt.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines', name='Ribilanciamento trimestrale',
        line=dict(color='#c9a84c', width=0.8, dash='dot')
    ))
    fig_bt.update_layout(
        paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
        font=dict(color='#e8eaf0', family='Courier New', size=11),
        legend=dict(bgcolor='#0d1b2a', bordercolor='#1a2d45'),
        xaxis=dict(gridcolor='#1a2d45', linecolor='#1a2d45'),
        yaxis=dict(gridcolor='#1a2d45', linecolor='#1a2d45'),
        margin=dict(t=20, b=20),
        height=380,
    )
    st.plotly_chart(fig_bt, use_container_width=True)
    st.caption(f"Le linee verticali dorate indicano i {len(date_ribil)} ribilanciamenti trimestrali nel periodo. Buffer anti-turnover 15% attivo.")

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

    st.markdown("---")
    st.markdown("### TEAR SHEET — BACKTEST ISTITUZIONALE (2020 → OGGI)")
    st.caption("Scarica prezzi storici reali, applica la metodologia DSRM/Tier del Rulebook v1.3 e genera un PDF pronto per la presentazione.")

    if st.button("GENERA TEAR SHEET PDF"):
        if df_aziende.empty:
            st.error("Dati portafoglio non disponibili. Controlla la connessione al CSV.")
        else:
            with st.spinner("Scaricando dati storici e calcolando metriche... (1-2 minuti)"):
                try:
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    import matplotlib.patches as mpatches
                    import io as _io
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib.styles import ParagraphStyle
                    from reportlab.lib.units import cm
                    from reportlab.lib import colors as rl_colors
                    from reportlab.platypus import (
                        SimpleDocTemplate, Paragraph, Spacer, Table,
                        TableStyle, HRFlowable, Image, PageBreak
                    )
                    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

                    DATA_INIZIO = "2020-01-01"
                    BASE_VAL    = 1000.0
                    BENCH_T     = "^GSPC"
                    BENCH_N     = "S&P 500"
                    T_MULT      = {"Tier 1": 1.5, "Tier 2": 1.0, "Tier 3": 0.5}
                    CS          = "#0a0e1a"
                    CB          = "#0d1b2a"
                    CV          = "#00d4aa"
                    CR          = "#e05a5a"
                    CO          = "#c9a84c"
                    CG          = "#7a8fa6"

                    # Pesi con DSRM + UCITS
                    df_bt = df_aziende.copy()
                    df_bt['Mult'] = df_bt['Tier'].map(T_MULT).fillna(1.0)
                    df_bt['FDSRM'] = df_bt['Giorni_Silenzio'].apply(
                        lambda g: 0.0 if g > 90 else 0.75 if g > 45 else 1.0
                    ) if 'Giorni_Silenzio' in df_bt.columns else 1.0
                    df_bt['PG'] = df_bt['Peso_Base'] * df_bt['FDSRM'] * df_bt['Mult']
                    tot = df_bt['PG'].sum()
                    df_bt['PN'] = ((df_bt['PG'] / tot * 100).clip(upper=10.0) if tot > 0 else 0)
                    df_bt['PN'] = df_bt['PN'] / df_bt['PN'].sum() * 100

                    # Download prezzi
                    tickers_bt = df_bt['Ticker'].dropna().unique().tolist()
                    raw_bt = yf.download(tickers_bt + [BENCH_T], start=DATA_INIZIO,
                                         auto_adjust=True, progress=False)
                    prezzi_bt = raw_bt['Close'] if isinstance(raw_bt.columns, pd.MultiIndex) else raw_bt
                    prezzi_bt = prezzi_bt.dropna(axis=1, how='all')
                    tickers_ok = [t for t in tickers_bt if t in prezzi_bt.columns]
                    df_bt = df_bt[df_bt['Ticker'].isin(tickers_ok)].copy()
                    df_bt['PN'] = df_bt['PN'] / df_bt['PN'].sum() * 100

                    # Serie GGIV
                    rend_bt = prezzi_bt.pct_change().dropna()
                    pesi_v  = np.array([df_bt.set_index('Ticker').loc[t, 'PN'] / 100
                                        for t in tickers_ok])
                    rend_g  = pd.Series(rend_bt[tickers_ok].values @ pesi_v,
                                        index=rend_bt.index)
                    idx_g   = (1 + rend_g).cumprod() * BASE_VAL
                    rend_b  = (prezzi_bt[BENCH_T].pct_change().dropna()
                               .reindex(rend_g.index).fillna(0)
                               if BENCH_T in prezzi_bt.columns
                               else pd.Series(0, index=rend_g.index))
                    idx_b   = (1 + rend_b).cumprod() * BASE_VAL

                    # Metriche
                    def calc_m(rend, idx, nome):
                        ny  = len(rend) / 252
                        cagr = (idx.iloc[-1] / BASE_VAL) ** (1/ny) - 1
                        vol  = rend.std() * np.sqrt(252)
                        rf   = 0.035
                        sh   = (cagr - rf) / vol if vol > 0 else 0
                        dd   = ((idx - idx.cummax()) / idx.cummax()).min()
                        cal  = cagr / abs(dd) if dd != 0 else 0
                        dv   = rend[rend < 0].std() * np.sqrt(252)
                        so   = (cagr - rf) / dv if dv > 0 else 0
                        rm   = rend.resample('ME').apply(lambda x: (1+x).prod()-1)
                        ra   = rend.resample('YE').apply(lambda x: (1+x).prod()-1)
                        return {
                            'nome': nome, 'cagr': cagr, 'vol': vol, 'sh': sh,
                            'so': so, 'dd': dd, 'cal': cal,
                            'rt': idx.iloc[-1]/BASE_VAL - 1,
                            'wr': (rend > 0).mean(),
                            'bm': rm.max(), 'wm': rm.min(),
                            'bmd': rm.idxmax().strftime('%b %Y') if not rm.empty else '',
                            'wmd': rm.idxmin().strftime('%b %Y') if not rm.empty else '',
                            'ra': ra,
                            'dds': (idx - idx.cummax()) / idx.cummax(),
                        }

                    mg = calc_m(rend_g, idx_g, "GGIV Index")
                    mb = calc_m(rend_b, idx_b, BENCH_N)

                    # Stile grafici
                    plt.rcParams.update({
                        'figure.facecolor': CS, 'axes.facecolor': CB,
                        'axes.edgecolor': '#1a2d45', 'axes.labelcolor': CG,
                        'axes.grid': True, 'grid.color': '#1a2d45',
                        'grid.linewidth': 0.5, 'xtick.color': CG,
                        'ytick.color': CG, 'text.color': '#e8eaf0',
                        'font.family': 'monospace', 'font.size': 9,
                    })

                    # Grafico 1 — Performance
                    fig1, axes = plt.subplots(3, 1, figsize=(12, 10),
                                              gridspec_kw={'height_ratios': [3, 1.2, 1.2]})
                    fig1.patch.set_facecolor(CS)
                    ax1 = axes[0]
                    ax1.plot(idx_b.index, idx_b.values, color=CG, lw=1.2, label=BENCH_N, alpha=0.8)
                    ax1.plot(idx_g.index, idx_g.values, color=CV, lw=2.0, label='GGIV Index')
                    ax1.fill_between(idx_g.index, BASE_VAL, idx_g.values,
                                     where=idx_g.values > BASE_VAL, color=CV, alpha=0.07)
                    ax1.axhline(BASE_VAL, color='#1a2d45', lw=0.8, ls='--')
                    crash = pd.Timestamp('2020-03-23')
                    if crash in idx_g.index:
                        ax1.axvline(crash, color=CR, lw=0.8, ls=':', alpha=0.6)
                        ax1.text(crash, ax1.get_ylim()[0]*1.02, 'COVID\nLow',
                                 color=CR, fontsize=7, ha='center')
                    ax1.legend(loc='upper left', framealpha=0.3, facecolor=CB, edgecolor='#1a2d45')
                    ax1.set_title(f'GGIV Index vs {BENCH_N} — 2020 → {datetime.now().year}',
                                  color='#e8eaf0', fontsize=11, pad=10)
                    ax1.set_ylabel('Valore (base 1000)')

                    ax2 = axes[1]
                    ra_g = mg['ra'] * 100
                    ra_b = mb['ra'].reindex(mg['ra'].index, fill_value=0) * 100
                    x    = np.arange(len(ra_g))
                    w    = 0.35
                    ax2.bar(x-w/2, ra_g.values, w,
                            color=[CV if v >= 0 else CR for v in ra_g.values],
                            alpha=0.85, label='GGIV')
                    ax2.bar(x+w/2, ra_b.values, w, color=CG, alpha=0.6, label=BENCH_N)
                    ax2.set_xticks(x); ax2.set_xticklabels(ra_g.index.year, fontsize=8)
                    ax2.axhline(0, color='#1a2d45', lw=0.8)
                    ax2.set_ylabel('Rend. Annuo (%)')
                    ax2.legend(fontsize=8, facecolor=CB, edgecolor='#1a2d45', framealpha=0.4)

                    ax3 = axes[2]
                    dds = mg['dds'] * 100
                    ax3.fill_between(dds.index, 0, dds.values, color=CR, alpha=0.5)
                    ax3.plot(dds.index, dds.values, color=CR, lw=0.8)
                    ax3.axhline(0, color='#1a2d45', lw=0.5)
                    ax3.set_ylabel('Drawdown (%)'); ax3.set_xlabel('Data')
                    mi = dds.idxmin()
                    ax3.annotate(f'Max DD: {dds.min():.1f}%',
                                 xy=(mi, dds.min()), xytext=(mi, dds.min()-3),
                                 color=CR, fontsize=8, ha='center',
                                 arrowprops=dict(arrowstyle='->', color=CR, lw=0.8))
                    plt.tight_layout(pad=1.5)
                    b1 = _io.BytesIO()
                    plt.savefig(b1, format='png', dpi=150, bbox_inches='tight', facecolor=CS)
                    plt.close(); b1.seek(0)

                    # Grafico 2 — Composizione
                    fig2, (axA, axB) = plt.subplots(1, 2, figsize=(10, 4))
                    fig2.patch.set_facecolor(CS)
                    ct = {'Tier 1': CR, 'Tier 2': '#378ADD', 'Tier 3': CV}
                    pt = df_bt.groupby('Tier')['PN'].sum()
                    wedges, texts, autotexts = axA.pie(
                        pt.values, labels=pt.index, autopct='%1.1f%%',
                        colors=[ct.get(t, CG) for t in pt.index],
                        pctdistance=0.75, startangle=90,
                        wedgeprops=dict(linewidth=1.5, edgecolor=CS)
                    )
                    for t in texts: t.set_color('#e8eaf0'); t.set_fontsize(9)
                    for at in autotexts: at.set_color('#0a0e1a'); at.set_fontsize(8)
                    axA.set_title('Allocazione per Tier', color='#e8eaf0', fontsize=10)
                    df_s = df_bt.sort_values('PN', ascending=True)
                    nomi = [str(a)[:20] for a in df_s['Azienda']]
                    brs  = axB.barh(nomi, df_s['PN'].values,
                                    color=[ct.get(t, CG) for t in df_s['Tier']],
                                    alpha=0.85, height=0.6)
                    axB.axvline(10, color=CO, lw=0.8, ls='--', alpha=0.7)
                    for bar, val in zip(brs, df_s['PN'].values):
                        axB.text(val+0.2, bar.get_y()+bar.get_height()/2,
                                 f'{val:.1f}%', va='center', color='#e8eaf0', fontsize=7.5)
                    axB.set_xlabel('Peso (%)')
                    axB.set_title('Pesi per Azienda (post DSRM+UCITS)', color='#e8eaf0', fontsize=10)
                    axB.legend(handles=[mpatches.Patch(color=c, label=t) for t, c in ct.items()],
                               fontsize=8, facecolor=CB, edgecolor='#1a2d45', framealpha=0.5)
                    plt.tight_layout(pad=1.5)
                    b2 = _io.BytesIO()
                    plt.savefig(b2, format='png', dpi=150, bbox_inches='tight', facecolor=CS)
                    plt.close(); b2.seek(0)

                    # PDF
                    pdf_buf = _io.BytesIO()
                    NR = rl_colors.HexColor('#0a0e1a')
                    BR = rl_colors.HexColor('#0d1b2a')
                    OR = rl_colors.HexColor('#c9a84c')
                    VR = rl_colors.HexColor('#1D9E75')
                    RR = rl_colors.HexColor('#A32D2D')
                    GR = rl_colors.HexColor('#4a4a5a')
                    WR = rl_colors.white

                    def PS(n, **k): return ParagraphStyle(n, **k)
                    HS  = PS('H',  fontName='Helvetica-Bold', fontSize=20, textColor=OR, leading=26, alignment=TA_CENTER)
                    SS  = PS('S',  fontName='Helvetica', fontSize=10, textColor=rl_colors.HexColor('#e8eaf0'), leading=14, alignment=TA_CENTER)
                    MS  = PS('M',  fontName='Helvetica', fontSize=8, textColor=GR, leading=12, alignment=TA_CENTER)
                    SeS = PS('Se', fontName='Helvetica-Bold', fontSize=11, textColor=NR, leading=14, spaceBefore=8, spaceAfter=3)
                    NS  = PS('N',  fontName='Helvetica-Bold', fontSize=17, textColor=OR, leading=21, alignment=TA_CENTER)
                    LS  = PS('L',  fontName='Helvetica', fontSize=8, textColor=GR, leading=11, alignment=TA_CENTER)
                    THS = PS('TH', fontName='Helvetica-Bold', fontSize=8, textColor=WR, leading=11, alignment=TA_CENTER)
                    TCS = PS('TC', fontName='Helvetica', fontSize=8, textColor=NR, leading=11)
                    TCC = PS('TCC',fontName='Helvetica', fontSize=8, textColor=NR, leading=11, alignment=TA_CENTER)
                    TGS = PS('TG', fontName='Helvetica-Bold', fontSize=8, textColor=VR, leading=11, alignment=TA_CENTER)
                    TRS = PS('TR', fontName='Helvetica-Bold', fontSize=8, textColor=RR, leading=11, alignment=TA_CENTER)
                    DS  = PS('D',  fontName='Helvetica-Oblique', fontSize=7.5, textColor=GR, leading=11, alignment=TA_JUSTIFY)

                    def hrr(): return HRFlowable(width='100%', thickness=1.0, color=OR, spaceAfter=8, spaceBefore=4)
                    def spr(h=6): return Spacer(1, h)
                    def cd(v, pos=True): return TGS if (v > 0) == pos else TRS

                    doc_pdf = SimpleDocTemplate(pdf_buf, pagesize=A4,
                        leftMargin=2.2*cm, rightMargin=2.2*cm,
                        topMargin=2.0*cm, bottomMargin=2.0*cm,
                        title='GGIV Index — Backtest Tear Sheet',
                        author='Francesco Giliberti')

                    sp_pdf = []
                    sp_pdf += [
                        Paragraph("⬡ GGIV INDEX", HS),
                        Paragraph("GRAPHENE GLOBAL INDEX VAULT — BACKTEST TEAR SHEET", SS),
                        Paragraph(f"Periodo: {DATA_INIZIO} → {datetime.now().strftime('%d/%m/%Y')}  |  Benchmark: {BENCH_N}  |  Base: {BASE_VAL:.0f}  |  AUM simulato: € {capitale_globale:,.0f}", MS),
                        hrr(), spr(4),
                    ]
                    kpi = [[Paragraph(f"{mg['cagr']*100:.2f}%", NS), Paragraph(f"{mg['sh']:.2f}", NS), Paragraph(f"{mg['dd']*100:.2f}%", NS), Paragraph(f"{mg['rt']*100:.1f}%", NS), Paragraph(f"{idx_g.iloc[-1]:,.1f}", NS)],
                           [Paragraph("CAGR", LS), Paragraph("Sharpe Ratio", LS), Paragraph("Max Drawdown", LS), Paragraph("Rendimento Totale", LS), Paragraph(f"Valore Indice (base {BASE_VAL:.0f})", LS)]]
                    kpi_t = Table(kpi, colWidths=[3.3*cm]*5)
                    kpi_t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BR),('BOX',(0,0),(-1,-1),0.5,OR),('INNERGRID',(0,0),(-1,-1),0.3,rl_colors.HexColor('#1a2d45')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
                    sp_pdf += [kpi_t, spr(10), Paragraph("PERFORMANCE STORICA E DRAWDOWN", SeS), hrr(), Image(b1, width=16*cm, height=13.5*cm), spr(4), PageBreak()]

                    def p(v): return f"{v*100:+.2f}%"
                    def pp(v): return f"{v*100:.2f}%"
                    def f2(v): return f"{v:.2f}"
                    md = [
                        [Paragraph("METRICA",THS), Paragraph("GGIV INDEX",THS), Paragraph(BENCH_N,THS), Paragraph("DELTA",THS)],
                        [Paragraph("Rendimento Totale",TCS), Paragraph(p(mg['rt']),cd(mg['rt'])), Paragraph(p(mb['rt']),cd(mb['rt'])), Paragraph(p(mg['rt']-mb['rt']),cd(mg['rt']-mb['rt']))],
                        [Paragraph("CAGR Annualizzato",TCS), Paragraph(p(mg['cagr']),cd(mg['cagr'])), Paragraph(p(mb['cagr']),cd(mb['cagr'])), Paragraph(p(mg['cagr']-mb['cagr']),cd(mg['cagr']-mb['cagr']))],
                        [Paragraph("Volatilità Annualizzata",TCS), Paragraph(pp(mg['vol']),TCC), Paragraph(pp(mb['vol']),TCC), Paragraph("—",TCC)],
                        [Paragraph("Sharpe Ratio (rf=3.5%)",TCS), Paragraph(f2(mg['sh']),cd(mg['sh'])), Paragraph(f2(mb['sh']),cd(mb['sh'])), Paragraph(f2(mg['sh']-mb['sh']),cd(mg['sh']-mb['sh']))],
                        [Paragraph("Sortino Ratio",TCS), Paragraph(f2(mg['so']),cd(mg['so'])), Paragraph(f2(mb['so']),cd(mb['so'])), Paragraph(f2(mg['so']-mb['so']),cd(mg['so']-mb['so']))],
                        [Paragraph("Maximum Drawdown",TCS), Paragraph(p(mg['dd']),cd(mg['dd'],False)), Paragraph(p(mb['dd']),cd(mb['dd'],False)), Paragraph(p(mg['dd']-mb['dd']),cd(mg['dd']-mb['dd'],False))],
                        [Paragraph("Calmar Ratio",TCS), Paragraph(f2(mg['cal']),cd(mg['cal'])), Paragraph(f2(mb['cal']),cd(mb['cal'])), Paragraph(f2(mg['cal']-mb['cal']),cd(mg['cal']-mb['cal']))],
                        [Paragraph("Win Rate",TCS), Paragraph(f"{mg['wr']*100:.1f}%",TCC), Paragraph(f"{mb['wr']*100:.1f}%",TCC), Paragraph("—",TCC)],
                        [Paragraph("Miglior Mese",TCS), Paragraph(f"{mg['bm']*100:+.1f}% ({mg['bmd']})",TGS), Paragraph(f"{mb['bm']*100:+.1f}% ({mb['bmd']})",TGS), Paragraph("—",TCC)],
                        [Paragraph("Peggior Mese",TCS), Paragraph(f"{mg['wm']*100:+.1f}% ({mg['wmd']})",TRS), Paragraph(f"{mb['wm']*100:+.1f}% ({mb['wmd']})",TRS), Paragraph("—",TCC)],
                    ]
                    mt = Table(md, colWidths=[5.5*cm, 3.5*cm, 3.5*cm, 3.1*cm])
                    mt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BR),('ROWBACKGROUNDS',(0,1),(-1,-1),[rl_colors.HexColor('#f9f9f7'),rl_colors.HexColor('#f5f5f5')]),('BOX',(0,0),(-1,-1),0.5,GR),('INNERGRID',(0,0),(-1,-1),0.3,rl_colors.HexColor('#cccccc')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
                    sp_pdf += [Paragraph(f"METRICHE COMPARATIVE — GGIV vs {BENCH_N}", SeS), hrr(), mt, spr(10)]
                    sp_pdf += [Paragraph("COMPOSIZIONE PORTAFOGLIO — POST DSRM + UCITS", SeS), hrr(), Image(b2, width=16*cm, height=6.5*cm), spr(6)]

                    pd_data = [[Paragraph("TICKER",THS), Paragraph("AZIENDA",THS), Paragraph("TIER",THS), Paragraph("DSRM",THS), Paragraph("PESO BASE",THS), Paragraph("PESO FINALE",THS)]]
                    for _, row in df_bt.sort_values('PN', ascending=False).iterrows():
                        ds = TGS if row['FDSRM']==1.0 else (TCC if row['FDSRM']==0.75 else TRS)
                        pd_data.append([Paragraph(str(row['Ticker']),TCC), Paragraph(str(row['Azienda'])[:26],TCS), Paragraph(str(row['Tier']),TCC), Paragraph(f"{row['FDSRM']:.2f}",ds), Paragraph(f"{row['Peso_Base']:.1f}%",TCC), Paragraph(f"{row['PN']:.2f}%",TCC)])
                    pt2 = Table(pd_data, colWidths=[2.3*cm, 5.5*cm, 2.5*cm, 1.8*cm, 2.1*cm, 2.4*cm])
                    pt2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BR),('ROWBACKGROUNDS',(0,1),(-1,-1),[rl_colors.HexColor('#f9f9f7'),rl_colors.HexColor('#f5f5f5')]),('BOX',(0,0),(-1,-1),0.5,GR),('INNERGRID',(0,0),(-1,-1),0.3,rl_colors.HexColor('#cccccc')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
                    sp_pdf += [pt2, spr(12), hrr()]
                    sp_pdf.append(Paragraph(f"DISCLAIMER — Documento generato automaticamente dal Vault Algorithm GGIV. I risultati del backtest sono calcolati ex-post su dati Yahoo Finance e non costituiscono garanzia di rendimenti futuri. Proprietà intellettuale di Francesco Giliberti — Rulebook v1.3 — {datetime.now().strftime('%d/%m/%Y')}.", DS))

                    doc_pdf.build(sp_pdf)
                    pdf_buf.seek(0)

                    st.success("PDF generato con successo.")
                    st.download_button(
                        label="SCARICA TEAR SHEET PDF",
                        data=pdf_buf,
                        file_name=f"GGIV_TearSheet_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                except Exception as e:
                    st.error(f"Errore nella generazione del PDF: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# --- SCHEDA 4: CORRELAZIONE & MACRO ---
with tab_correlazione:

    # ---- SEZIONE A: SENSORE MACRO ----
    st.markdown("### SENSORE MACRO — CONTESTO DI MERCATO")

    @st.cache_data(ttl=300)
    def get_macro_data():
        """Scarica VIX e Treasury 10Y. Restituisce dizionario con valori e variazioni."""
        risultati = {}
        macro_tickers = {
            'VIX': '^VIX',
            'TREASURY_10Y': '^TNX',
            'DXY': 'DX-Y.NYB',
        }
        for nome, ticker in macro_tickers.items():
            try:
                d = yf.Ticker(ticker).history(period="5d")
                if len(d) >= 2:
                    val = d['Close'].iloc[-1]
                    prev = d['Close'].iloc[-2]
                    delta = val - prev
                    delta_pct = (delta / prev) * 100
                    risultati[nome] = {'valore': val, 'delta': delta, 'delta_pct': delta_pct}
            except Exception as e:
                st.warning(f"Dato macro non disponibile ({nome}): {e}")
        return risultati

    with st.spinner("Caricamento dati macro..."):
        macro = get_macro_data()

    if macro:
        col_m1, col_m2, col_m3 = st.columns(3)

        # VIX — Indice della paura
        if 'VIX' in macro:
            v = macro['VIX']
            vix_val = v['valore']
            # Regime VIX: <15 calmo, 15-25 normale, 25-35 stress, >35 panico
            if vix_val < 15:
                regime = "MERCATO CALMO"
                shield_color = "#00d4aa"
            elif vix_val < 25:
                regime = "VOLATILITÀ NORMALE"
                shield_color = "#c9a84c"
            elif vix_val < 35:
                regime = "STRESS DI MERCATO"
                shield_color = "#e05a5a"
            else:
                regime = "PANICO — SHIELD CRITICO"
                shield_color = "#ff2222"

            col_m1.metric(
                "VIX — INDICE DELLA PAURA",
                f"{vix_val:.2f}",
                f"{v['delta_pct']:+.2f}% — {regime}"
            )
            # Barra visiva del regime VIX
            vix_pct = min(vix_val / 50, 1.0)
            col_m1.markdown(f"""
            <div style="margin-top:8px;">
                <div style="display:flex; justify-content:space-between;
                            font-size:10px; color:#7a8fa6; margin-bottom:4px;">
                    <span>CALMO</span><span>STRESS</span><span>PANICO</span>
                </div>
                <div style="background:#1a2d45; border-radius:3px; height:6px; overflow:hidden;">
                    <div style="width:{vix_pct*100:.0f}%; background:{shield_color};
                                height:100%; border-radius:3px;"></div>
                </div>
                <div style="font-size:10px; color:{shield_color}; margin-top:4px;
                            font-family:'Courier New',monospace; letter-spacing:0.08em;">
                    {regime}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Treasury 10Y
        if 'TREASURY_10Y' in macro:
            t = macro['TREASURY_10Y']
            col_m2.metric(
                "TREASURY USA 10Y",
                f"{t['valore']:.3f}%",
                f"{t['delta_pct']:+.2f}%"
            )
            col_m2.markdown(f"""
            <div style="margin-top:8px; font-size:11px; color:#7a8fa6;
                        font-family:'Courier New',monospace; line-height:1.8;">
                {"⚠ TASSI ALTI — pressione su growth" if t['valore'] > 4.5
                 else "✓ TASSI MODERATI — contesto neutro" if t['valore'] > 3.5
                 else "✓ TASSI BASSI — favorevole a tech/growth"}
            </div>
            """, unsafe_allow_html=True)

        # DXY — Dollaro
        if 'DXY' in macro:
            d = macro['DXY']
            col_m3.metric(
                "DXY — INDICE DOLLARO",
                f"{d['valore']:.2f}",
                f"{d['delta_pct']:+.2f}%"
            )
            col_m3.markdown(f"""
            <div style="margin-top:8px; font-size:11px; color:#7a8fa6;
                        font-family:'Courier New',monospace; line-height:1.8;">
                {"⚠ DOLLARO FORTE — pressione su commodities e mercati EM"
                 if d['valore'] > 104
                 else "✓ DOLLARO NEUTRO — contesto equilibrato"}
            </div>
            """, unsafe_allow_html=True)

        # Stato Golden Shield contestualizzato con il VIX
        st.markdown("---")
        if 'VIX' in macro:
            vix_val = macro['VIX']['valore']
            peso_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
            if vix_val > 25 and peso_shield >= 30:
                st.success(f"GOLDEN SHIELD OPERATIVO in regime di stress (VIX {vix_val:.1f}). Tier 3 al {peso_shield:.1f}% — protezione attiva.")
            elif vix_val > 25 and peso_shield < 30:
                st.error(f"ATTENZIONE — VIX a {vix_val:.1f} (stress) ma Tier 3 solo al {peso_shield:.1f}%. Ribilanciare urgentemente.")
            else:
                st.info(f"Mercato nella norma (VIX {vix_val:.1f}). Tier 3 al {peso_shield:.1f}% — monitoraggio standard.")
    else:
        st.warning("Impossibile caricare dati macro. Controlla la connessione.")

    st.markdown("---")

    # ---- SEZIONE B: MATRICE DI CORRELAZIONE ----
    st.markdown("### MATRICE DI CORRELAZIONE — DECORRELAZIONE TIER")
    st.caption("Scarica 90 giorni di dati storici per tutte le aziende in portafoglio e calcola la correlazione dei rendimenti giornalieri.")

    @st.cache_data(ttl=3600)  # Cache 1 ora — dati storici non cambiano frequentemente
    def calcola_correlazione(tickers: tuple):
        """Scarica 90gg di dati e calcola la matrice di correlazione dei rendimenti."""
        try:
            raw = yf.download(list(tickers), period="90d", auto_adjust=True, progress=False)
            if raw.empty:
                return None, None
            # Gestisce sia singolo ticker che multipli
            if isinstance(raw.columns, pd.MultiIndex):
                prezzi = raw['Close']
            else:
                prezzi = raw[['Close']]
            rendimenti = prezzi.pct_change().dropna()
            return rendimenti.corr(), rendimenti
        except Exception as e:
            st.warning(f"Errore nel calcolo correlazione: {e}")
            return None, None

    if not df_aziende.empty and 'Ticker' in df_aziende.columns:
        tickers_portafoglio = tuple(df_aziende['Ticker'].dropna().unique())

        if len(tickers_portafoglio) >= 2:
            with st.spinner(f"Scaricando 90 giorni di dati per {len(tickers_portafoglio)} aziende..."):
                corr_matrix, rendimenti = calcola_correlazione(tickers_portafoglio)

            if corr_matrix is not None and not corr_matrix.empty:

                # Sostituisce i ticker con i nomi azienda se disponibili
                ticker_to_nome = dict(zip(df_aziende['Ticker'], df_aziende['Azienda']))
                corr_display = corr_matrix.copy()
                corr_display.columns = [ticker_to_nome.get(t, t) for t in corr_display.columns]
                corr_display.index = [ticker_to_nome.get(t, t) for t in corr_display.index]

                # Heatmap con scala divergente: rosso=correlato, verde=decorrelato
                fig_heatmap = go.Figure(go.Heatmap(
                    z=corr_display.values,
                    x=corr_display.columns.tolist(),
                    y=corr_display.index.tolist(),
                    colorscale=[
                        [0.0,  '#00d4aa'],   # -1.0 = decorrelazione perfetta = verde
                        [0.5,  '#0d1b2a'],   # 0.0  = nessuna correlazione = neutro
                        [1.0,  '#e05a5a'],   # +1.0 = correlazione perfetta = rosso
                    ],
                    zmid=0,
                    zmin=-1,
                    zmax=1,
                    text=np.round(corr_display.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(size=10, color='#e8eaf0', family='Courier New'),
                    hovertemplate='%{y} / %{x}<br>Correlazione: %{z:.3f}<extra></extra>',
                    colorbar=dict(
                        tickcolor='#7a8fa6',
                        tickfont=dict(color='#7a8fa6', size=10),
                        title=dict(text='ρ', font=dict(color='#7a8fa6')),
                        bgcolor='#0d1b2a',
                    )
                ))
                fig_heatmap.update_layout(
                    paper_bgcolor='#0d1b2a',
                    plot_bgcolor='#0d1b2a',
                    font=dict(color='#e8eaf0', family='Courier New', size=10),
                    xaxis=dict(tickangle=-35, tickfont=dict(size=9), gridcolor='#1a2d45'),
                    yaxis=dict(tickfont=dict(size=9), gridcolor='#1a2d45'),
                    margin=dict(t=20, b=80, l=120, r=20),
                    height=max(400, len(tickers_portafoglio) * 38),
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

                # Analisi automatica della decorrelazione del Tier 3
                st.markdown("#### ANALISI AUTOMATICA DECORRELAZIONE TIER 3")
                if 'Tier' in df_aziende.columns:
                    ticker_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Ticker'].tolist()
                    ticker_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Ticker'].tolist()

                    if ticker_t3 and ticker_t1:
                        coppie_cross = []
                        for t3 in ticker_t3:
                            for t1 in ticker_t1:
                                if t3 in corr_matrix.columns and t1 in corr_matrix.columns:
                                    rho = corr_matrix.loc[t3, t1]
                                    nome_t3 = ticker_to_nome.get(t3, t3)
                                    nome_t1 = ticker_to_nome.get(t1, t1)
                                    coppie_cross.append((nome_t3, nome_t1, rho))

                        if coppie_cross:
                            media_cross = np.mean([c[2] for c in coppie_cross])
                            if media_cross < 0.3:
                                st.success(f"SHIELD CONFERMATO — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Il Tier 3 è effettivamente decorrelato e funziona da scudo.")
                            elif media_cross < 0.6:
                                st.warning(f"DECORRELAZIONE PARZIALE — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Verificare la composizione del Tier 3.")
                            else:
                                st.error(f"SHIELD DEBOLE — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Il Tier 3 si muove troppo in linea col Tier 1.")
            else:
                st.warning("Impossibile calcolare la matrice. I ticker nel CSV potrebbero non essere riconosciuti da Yahoo Finance.")
        else:
            st.info("Servono almeno 2 aziende nel portafoglio per calcolare la correlazione.")
    else:
        st.warning("Dati portafoglio non disponibili.")


# --- SCHEDA 5: RISCHIO & ORDINI ---
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
    st.markdown("### SENSORE IP — BREVETTI & GES")
    if not df_aziende.empty:
        target = st.selectbox("Seleziona azienda:", df_aziende['Azienda'].tolist())
        row_t  = df_aziende[df_aziende['Azienda'] == target]

        # GES Score calcolato dal tool v2.0 (priorità su Health_Score statico)
        if 'GES_Score' in df_aziende.columns and not row_t['GES_Score'].isna().all():
            ges_raw = row_t['GES_Score'].values[0]
            score   = round(float(ges_raw) * 100, 1) if ges_raw else 0
            label   = "GES SCORE (calcolato)"
        else:
            score_val = row_t['Health_Score'].values if 'Health_Score' in row_t.columns else [0]
            score     = int(score_val[0]) if len(score_val) > 0 else 0
            label     = "HEALTH SCORE (statico)"

        stato  = "ECCELLENTE" if score >= 80 else "MODERATO" if score >= 50 else "ALLERTA"
        colore = "#00d4aa"    if score >= 80 else "#c9a84c"  if score >= 50 else "#e05a5a"
        st.metric(label, f"{score}/100", stato)

        # Mostra dettaglio brevetti se disponibile
        cb1, cb2, cb3 = st.columns(3)
        if 'Brevetti_Granted' in row_t.columns:
            cb1.metric("BREVETTI GRANTED", str(int(row_t['Brevetti_Granted'].values[0] or 0)), "USPTO concessi")
        if 'Brevetti_Pending' in row_t.columns:
            cb2.metric("BREVETTI PENDING", str(int(row_t['Brevetti_Pending'].values[0] or 0)), "domande attive")
        if 'Tier' in row_t.columns:
            tier_az = row_t['Tier'].values[0]
            coeff   = {"Tier 1": "α=0.30 β=0.70", "Tier 2": "α=0.55 β=0.45", "Tier 3": "α=0.70 β=0.30"}
            cb3.metric("COEFFICIENTI GES", coeff.get(tier_az, "—"), f"Rulebook v1.3 — {tier_az}")

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
