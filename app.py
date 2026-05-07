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
st.set_page_config(
    page_title="GGIV Terminal",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    /* Delta positivo = verde, negativo = rosso */
    [data-testid="stMetricDelta"][data-direction="up"] > div   { color: #00d4aa !important; font-size: 12px !important; }
    [data-testid="stMetricDelta"][data-direction="down"] > div { color: #e05a5a !important; font-size: 12px !important; }
    [data-testid="stMetricDelta"] > div { color: #7a8fa6 !important; font-size: 12px !important; }

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

    /* --- DROPDOWN MENU (tendina aperta) --- */
    [data-baseweb="popover"] { background-color: #0d1b2a !important; }
    [data-baseweb="menu"]    { background-color: #0d1b2a !important; border: 1px solid #1a2d45 !important; }
    [role="listbox"]         { background-color: #0d1b2a !important; }
    [role="option"]          {
        background-color: #0d1b2a !important;
        color: #e8eaf0 !important;
    }
    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background-color: #1a2d45 !important;
        color: #00d4aa !important;
    }
    /* Copertura completa BaseWeb list item */
    [data-baseweb="list-item"],
    [data-baseweb="list-item"] *,
    li[role="option"],
    li[role="option"] * {
        background-color: #0d1b2a !important;
        color: #e8eaf0 !important;
    }
    li[role="option"]:hover,
    li[role="option"]:hover * {
        background-color: #1a3a5c !important;
        color: #00d4aa !important;
    }
    /* Testo selezionato nella box chiusa */
    [data-baseweb="select"] [data-baseweb="tag"],
    [data-baseweb="select"] span {
        color: #e8eaf0 !important;
        background-color: transparent !important;
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
                padding-top:40px; gap:8px;">
        <div style="font-family:'Courier New',monospace; font-size:30px; color:#c9a84c;
                    letter-spacing:0.2em; font-weight:bold;">GGIV TERMINAL</div>
        <div style="font-size:11px; color:#7a8fa6; letter-spacing:0.15em;">
            GRAPHENE GLOBAL INDEX VAULT — ACCESSO RISERVATO
        </div>
        <div style="display:flex; gap:40px; margin-top:10px; margin-bottom:4px;">
            <div style="text-align:center; font-family:'Courier New',monospace;">
                <div style="font-size:22px; font-weight:bold; color:#00d4aa;">0.87</div>
                <div style="font-size:9px; color:#7a8fa6; letter-spacing:0.08em;">SHARPE RATIO</div>
            </div>
            <div style="text-align:center; font-family:'Courier New',monospace;">
                <div style="font-size:22px; font-weight:bold; color:#00d4aa;">-22.1%</div>
                <div style="font-size:9px; color:#7a8fa6; letter-spacing:0.08em;">MAX DRAWDOWN</div>
            </div>
            <div style="text-align:center; font-family:'Courier New',monospace;">
                <div style="font-size:22px; font-weight:bold; color:#00d4aa;">18.5%</div>
                <div style="font-size:9px; color:#7a8fa6; letter-spacing:0.08em;">VOL. ANNUA</div>
            </div>
            <div style="text-align:center; font-family:'Courier New',monospace;">
                <div style="font-size:22px; font-weight:bold; color:#c9a84c;">UCITS IV</div>
                <div style="font-size:9px; color:#7a8fa6; letter-spacing:0.08em;">COMPLIANT</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Grafico indice live sulla login — carica dati pubblicamente disponibili
    @st.cache_data(ttl=300)
    def get_preview_chart():
        """Preview chart per la login — usa un paniere proxy di titoli pubblici."""
        proxy = ["MSFT", "AAPL", "TSM", "NVDA", "ASML"]
        try:
            raw = yf.download(proxy + ["^GSPC"], period="6mo",
                              auto_adjust=True, progress=False)
            if raw is None or raw.empty:
                return None, None
            prezzi = raw['Close'] if isinstance(raw.columns, pd.MultiIndex) else raw
            bench  = prezzi["^GSPC"].dropna() if "^GSPC" in prezzi.columns else None
            tickers_ok = [t for t in proxy if t in prezzi.columns]
            if len(tickers_ok) < 2 or bench is None:
                return None, None
            rend  = prezzi[tickers_ok].pct_change().dropna(how='all').fillna(0)
            rend_g = rend.mean(axis=1)
            idx_g  = (1 + rend_g).cumprod() * 100
            bench_r = bench.pct_change().dropna().reindex(rend_g.index).fillna(0)
            idx_b  = (1 + bench_r).cumprod() * 100
            return idx_g, idx_b
        except Exception:
            return None, None

    with st.spinner("Caricamento anteprima indice..."):
        ig_prev, ib_prev = get_preview_chart()

    if ig_prev is not None:
        fig_login = go.Figure()
        fig_login.add_trace(go.Scatter(
            x=ib_prev.index, y=ib_prev.values, name="S&P 500",
            line=dict(color='#7a8fa6', width=1.5),
            hovertemplate='S&P 500: %{y:.1f}<extra></extra>',
        ))
        fig_login.add_trace(go.Scatter(
            x=ig_prev.index, y=ig_prev.values, name="GGIV Strategy",
            line=dict(color='#00d4aa', width=2.5),
            fill='tonexty', fillcolor='rgba(0,212,170,0.08)',
            hovertemplate='GGIV: %{y:.1f}<extra></extra>',
        ))
        fig_login.add_hline(y=100, line_dash="dot", line_color="#1a2d45", line_width=1)
        fig_login.update_layout(
            paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
            font=dict(color='#7a8fa6', family='Courier New', size=9),
            legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1a2d45',
                        orientation='h', yanchor='bottom', y=1.01, x=0),
            xaxis=dict(gridcolor='#1a2d45', showgrid=True),
            yaxis=dict(gridcolor='#1a2d45', showgrid=True, title='Base 100'),
            margin=dict(t=30, b=20, l=50, r=20),
            height=260,
            hovermode='x unified',
        )
        fig_login.update_layout(title=dict(
            text="Anteprima GGIV Strategy vs S&P 500 — ultimi 6 mesi (costituenti proxy)",
            font=dict(color='#7a8fa6', size=9, family='Courier New'), x=0.5, xanchor='center'
        ))
        st.plotly_chart(fig_login, use_container_width=True)

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

# ==========================================
# 5B. RAWSCORE + PESO FINALE (Rulebook v1.3 Sez. 9C)
#
# ARCHITETTURA CORRETTA:
#   1. Peso_Base nel DB definisce il peso target di ogni singolo titolo
#      (es. Tier 3 vale 10% per titolo → 4 titoli = 40% totale Tier 3)
#   2. RawScore = sqrt(MC) × GES × Delta distribuisce i pesi DENTRO ogni Tier
#      (chi ha GES più alto prende quota dagli altri dello stesso Tier)
#   3. Il peso del Tier nel totale viene preservato dalla somma dei Peso_Base
#   4. UCITS 5/10/40 viene applicato alla fine
#
# In questo modo il Tier 3 mantiene ~40% come da DB, ma i 4 titoli al
# suo interno vengono pesati in proporzione al loro RawScore (non equiponderati).
# ==========================================
def calcola_vault_weights(df):
    """
    Vault Algorithm completo (Rulebook v1.3 Sez. 9C + 7):

    Fase 1 — DSRM: Delta_i = f(Giorni_Silenzio)
    Fase 2 — RawScore INTRA-TIER: sqrt(MC_i) × GES_i × Delta_i
              distribuisce il peso all'interno di ogni Tier proporzionalmente
              al RawScore, preservando la quota totale del Tier dal Peso_Base.
    Fase 3 — UCITS 5/10/40: loop ricorsivo di capping.

    Il Peso_Base nel DB definisce la quota target del singolo titolo.
    La somma dei Peso_Base per Tier definisce il budget allocato a quel Tier.
    """
    if df.empty or 'Giorni_Silenzio' not in df.columns:
        return df

    df = df.copy()

    # ── Fase 1: DSRM ────────────────────────────────────────────────────────
    df['Fattore_DSRM'] = df['Giorni_Silenzio'].apply(applica_dsrm)

    mc_col  = 'Market_Cap_USD' if 'Market_Cap_USD'  in df.columns else None
    ges_col = 'GES_Score'      if 'GES_Score'       in df.columns else None
    tier_col= 'Tier'           if 'Tier'            in df.columns else None

    # ── Fase 2: RawScore intra-Tier ─────────────────────────────────────────
    # Calcola RawScore grezzo per ogni titolo
    raw_scores = []
    for _, row in df.iterrows():
        delta = row['Fattore_DSRM']

        mc_val = None
        if mc_col:
            try:
                v = float(row[mc_col])
                mc_val = v if v > 0 and not np.isnan(v) else None
            except (ValueError, TypeError):
                mc_val = None

        ges_val = None
        if ges_col:
            try:
                v = float(row[ges_col])
                ges_val = v if v > 0 and not np.isnan(v) else None
            except (ValueError, TypeError):
                ges_val = None

        if mc_val is not None and ges_val is not None:
            raw = np.sqrt(mc_val) * ges_val * delta
        else:
            # Fallback: usa Peso_Base × Delta se MC/GES non disponibili
            try:
                pb = float(row.get('Peso_Base', 1.0) or 1.0)
            except (ValueError, TypeError):
                pb = 1.0
            raw = pb * delta

        raw_scores.append(max(raw, 0.0))

    df['RawScore'] = raw_scores

    # Distribuzione pesi: usa Peso_Base per definire il budget del Tier,
    # poi distribuisce quel budget internamente in proporzione al RawScore.
    if tier_col and 'Peso_Base' in df.columns:
        df['Peso_Norm'] = 0.0
        for tier in df[tier_col].unique():
            mask = df[tier_col] == tier
            tier_df = df[mask]

            # Budget del Tier = somma dei Peso_Base dei titoli in quel Tier
            # moltiplicata per il fattore DSRM medio del Tier
            peso_base_tier = tier_df['Peso_Base'].apply(
                lambda x: float(x) if pd.notna(x) else 0.0
            )
            # Applica DSRM al peso base di ogni titolo
            peso_dsrm_tier = peso_base_tier * tier_df['Fattore_DSRM']
            budget_tier = peso_dsrm_tier.sum()

            if budget_tier <= 0:
                df.loc[mask, 'Peso_Norm'] = 0.0
                continue

            # Distribuisce il budget internamente con RawScore
            rs_tier = df.loc[mask, 'RawScore']
            tot_rs = rs_tier.sum()

            if tot_rs > 0:
                # Pesi intra-Tier proporzionali al RawScore
                df.loc[mask, 'Peso_Norm'] = (rs_tier / tot_rs) * budget_tier
            else:
                # Fallback equiponderato dentro il Tier
                df.loc[mask, 'Peso_Norm'] = budget_tier / len(tier_df)
    else:
        # Nessuna colonna Tier o Peso_Base: RawScore globale normalizzato
        tot_raw = sum(raw_scores)
        if tot_raw > 0:
            df['Peso_Norm'] = (df['RawScore'] / tot_raw) * 100
        else:
            df['Peso_Norm'] = 100.0 / len(df)

    # Rinormalizza a 100
    tot_norm = df['Peso_Norm'].sum()
    if tot_norm > 0:
        df['Peso_Norm'] = df['Peso_Norm'] / tot_norm * 100

    # ── Fase 3: Loop UCITS 5/10/40 (Rulebook Sez. 7) ───────────────────────
    # Step 1 — Single stock cap 10%
    df['Peso_Effettivo'] = df['Peso_Norm'].clip(upper=10.0)

    # Step 2 — Redistribuisce eccesso proporzionalmente
    for _ in range(20):
        eccesso = df['Peso_Norm'].sum() - df['Peso_Effettivo'].sum()
        if eccesso <= 1e-6:
            break
        mask_under = df['Peso_Effettivo'] < 10.0
        if not mask_under.any():
            break
        tot_under = df.loc[mask_under, 'Peso_Effettivo'].sum()
        if tot_under <= 0:
            break
        df.loc[mask_under, 'Peso_Effettivo'] += (
            df.loc[mask_under, 'Peso_Effettivo'] / tot_under * eccesso
        )
        df['Peso_Effettivo'] = df['Peso_Effettivo'].clip(upper=10.0)

    # Rinormalizza dopo step 2
    s = df['Peso_Effettivo'].sum()
    if s > 0:
        df['Peso_Effettivo'] = df['Peso_Effettivo'] / s * 100

    # Step 3/4 — Aggregate cap: somma titoli >5% ≤ 40%
    for _ in range(20):
        sopra_5 = df[df['Peso_Effettivo'] > 5.0]
        if sopra_5['Peso_Effettivo'].sum() <= 40.0:
            break
        eccesso_agg = sopra_5['Peso_Effettivo'].sum() - 40.0
        taglio = eccesso_agg / len(sopra_5)
        for idx_u in sopra_5.index:
            df.loc[idx_u, 'Peso_Effettivo'] = max(
                df.loc[idx_u, 'Peso_Effettivo'] - taglio, 5.0
            )
        sotto_5 = df[df['Peso_Effettivo'] <= 5.0]
        if not sotto_5.empty:
            df.loc[sotto_5.index, 'Peso_Effettivo'] += eccesso_agg / len(sotto_5)
        s2 = df['Peso_Effettivo'].sum()
        if s2 > 0:
            df['Peso_Effettivo'] = df['Peso_Effettivo'] / s2 * 100

    # Step 5 — Rinormalizzazione finale
    s_fin = df['Peso_Effettivo'].sum()
    if s_fin > 0:
        df['Peso_Effettivo'] = (df['Peso_Effettivo'] / s_fin) * 100

    df['Percentuale_Persa'] = df['Peso_Norm'] - df['Peso_Effettivo']
    return df


if not df_aziende.empty and 'Giorni_Silenzio' in df_aziende.columns:
    df_aziende = calcola_vault_weights(df_aziende)

# Aggiorna il titolo della tab browser con DSRM status
# NOTA: st.markdown con <title> causa rendering HTML visibile — uso JS invece
if not df_aziende.empty and 'Fattore_DSRM' in df_aziende.columns:
    _n_kill = int((df_aziende['Fattore_DSRM'] == 0.0).sum())
    _n_warn = int((df_aziende['Fattore_DSRM'] == 0.75).sum())
    if _n_kill > 0:
        _title = f"⬡ GGIV ⚠ {_n_kill} KILL"
    elif _n_warn > 0:
        _title = f"⬡ GGIV · {_n_warn} WARN"
    else:
        _title = "⬡ GGIV Terminal — OK"
    st.markdown(
        f"<script>document.title = '{_title}';</script>",
        unsafe_allow_html=True
    )

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

# ── Valore GGIV live per l'header — calcolo leggero (1mo, cached 2min) ──────
@st.cache_data(ttl=120)
def get_valore_header(tickers_tuple, pesi_tuple=None):
    """
    Calcola il valore corrente dell'indice per l'header con pesi DSRM+UCITS reali.
    Se pesi_tuple non è fornita, usa equiponderato come fallback.
    """
    import time as _t
    try:
        tickers_list = list(tickers_tuple)
        for tentativo in range(3):
            try:
                raw = yf.download(tickers_list, period="5d",
                                  auto_adjust=True, progress=False)
                if raw is not None and not raw.empty:
                    break
                _t.sleep(2 ** tentativo)
            except Exception:
                _t.sleep(2 ** tentativo)
        else:
            return None, None, None

        if isinstance(raw.columns, pd.MultiIndex):
            prezzi = raw['Close'] if 'Close' in raw.columns.get_level_values(0) else None
        else:
            prezzi = raw[['Close']] if 'Close' in raw.columns else None
        if prezzi is None:
            return None, None, None

        tickers_ok = [t for t in tickers_list if t in prezzi.columns
                      and prezzi[t].dropna().shape[0] >= 2]
        if len(tickers_ok) < 2:
            return None, None, None

        rend = prezzi[tickers_ok].pct_change().dropna(how='all').fillna(0)

        # Usa pesi reali DSRM+UCITS se disponibili
        if pesi_tuple is not None:
            pesi_dict = dict(pesi_tuple)
            pesi_v = np.array([pesi_dict.get(t, 0.0) for t in tickers_ok], dtype=float)
            tot = pesi_v.sum()
            pesi_v = pesi_v / tot if tot > 0 else np.ones(len(tickers_ok)) / len(tickers_ok)
        else:
            pesi_v = np.ones(len(tickers_ok)) / len(tickers_ok)

        rend_g = pd.Series(rend[tickers_ok].values @ pesi_v, index=rend.index)
        idx_g  = (1 + rend_g).cumprod() * 100

        valore      = round(float(idx_g.iloc[-1]), 2)
        delta_oggi  = round(float(rend_g.iloc[-1]) * 100, 2)
        delta_1w    = round(float((idx_g.iloc[-1] / idx_g.iloc[0] - 1) * 100), 2)
        return valore, delta_oggi, delta_1w
    except Exception:
        return None, None, None

_header_tickers = tuple(df_aziende['Ticker'].dropna().unique()) if not df_aziende.empty else ()
# Prepara pesi reali DSRM+UCITS per l'header (come tuple hashable per cache)
if not df_aziende.empty and 'Peso_Effettivo' in df_aziende.columns:
    _pesi_df = df_aziende[df_aziende['Ticker'].notna()][['Ticker', 'Peso_Effettivo']].copy()
    _tot_pesi = _pesi_df['Peso_Effettivo'].sum()
    if _tot_pesi > 0:
        _pesi_header = tuple(zip(_pesi_df['Ticker'].tolist(),
                                 (_pesi_df['Peso_Effettivo'] / _tot_pesi).tolist()))
    else:
        _pesi_header = None
else:
    _pesi_header = None

_valore_idx, _delta_oggi, _delta_1w = get_valore_header(_header_tickers, _pesi_header) if _header_tickers else (None, None, None)

# ── Header iniettato via JS puro — elimina il bug HTML visibile ──────────────
# st.markdown con HTML grezzo può mostrare il sorgente come testo in alcuni
# cicli di rendering React. La soluzione definitiva è costruire il DOM
# direttamente via JavaScript: il nodo viene inserito nel <body> una sola
# volta e aggiornato ad ogni rerun senza mai passare per il parser di Streamlit.

# Prepara i dati per il JS
if _valore_idx is not None:
    _idx_val_js   = f"{_valore_idx:.2f}"
    _delta_val_js = f"{'+'if _delta_oggi>=0 else ''}{_delta_oggi:.2f}%"
    _delta_col_js = "#00d4aa" if _delta_oggi >= 0 else "#e05a5a"
    _show_idx_js  = "true"
else:
    _idx_val_js   = ""
    _delta_val_js = ""
    _delta_col_js = "#7a8fa6"
    _show_idx_js  = "false"

# Serializza ticker per JS
_ticker_js_items = []
for _name, _d in dati_indici.items():
    _cls  = "t-up" if _d['change_pct'] >= 0 else "t-down"
    _sign = "+" if _d['change_pct'] >= 0 else ""
    _item = (
        f'<span class="t-item">'
        f'<span class="t-name">{_name}</span>'
        f'<span class="t-price">{_d["price"]:,.2f}</span>'
        f'<span class="{_cls}">{_sign}{_d["change_pct"]:.2f}%</span>'
        f'</span>'
    )
    _ticker_js_items.append(_item.replace("'", "\\'").replace("\n", ""))

_ticker_js_str = "".join(_ticker_js_items)

st.markdown(f"""
<script>
(function() {{
    var HEADER_ID = 'ggiv-main-header';

    // Rimuove header precedente se esiste (rerun)
    var old = document.getElementById(HEADER_ID);
    if (old) old.remove();

    var h = document.createElement('div');
    h.id = HEADER_ID;
    h.style.cssText = [
        'position:fixed','top:0','left:0','width:100vw','height:52px',
        'background:#060910','border-bottom:1px solid #1a2d45',
        'z-index:9999999','display:flex','align-items:center',
        'padding:0 20px','white-space:nowrap','overflow:hidden','gap:0',
        "font-family:'Inter','Segoe UI',system-ui,sans-serif"
    ].join('!important;') + '!important';

    var showIdx = {_show_idx_js};
    var idxVal  = '{_idx_val_js}';
    var dltVal  = '{_delta_val_js}';
    var dltCol  = '{_delta_col_js}';

    var inner = '';

    // Logo
    inner += '<div style="display:flex;align-items:center;gap:6px;flex-shrink:0;margin-right:20px">';
    inner += '<span style="font-size:16px;color:#c9a84c;line-height:1">⬡</span>';
    inner += '<span style="font-size:13px;font-weight:700;color:#c9a84c;letter-spacing:.12em">GGIV</span>';
    inner += '</div>';

    // Divider
    inner += '<div style="width:1px;height:28px;background:#1a3a5c;margin:0 20px;flex-shrink:0"></div>';

    // Blocco indice GGIV live
    if (showIdx) {{
        inner += '<div style="display:flex;align-items:baseline;gap:8px;flex-shrink:0;margin-right:20px">';
        inner += '<span style="font-size:9px;font-weight:600;color:#7a8fa6;letter-spacing:.12em;text-transform:uppercase">GGIV INDEX</span>';
        inner += '<span style="font-size:18px;font-weight:600;color:#fff;letter-spacing:-.02em;font-variant-numeric:tabular-nums">' + idxVal + '</span>';
        inner += '<span style="font-size:11px;font-weight:500;color:' + dltCol + ';font-variant-numeric:tabular-nums">' + dltVal + '</span>';
        inner += '</div>';
        inner += '<div style="width:1px;height:28px;background:#1a3a5c;margin:0 20px;flex-shrink:0"></div>';
    }}

    // Ticker scroll
    inner += '<div style="display:flex;gap:28px;overflow:hidden;flex:1">';
    inner += '{_ticker_js_str}';
    inner += '</div>';

    h.innerHTML = inner;

    // Inserisce nell'app Streamlit
    function insertHeader() {{
        var app = document.querySelector('[data-testid="stAppViewContainer"]')
                  || document.querySelector('.main')
                  || document.body;
        app.insertBefore(h, app.firstChild);
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', insertHeader);
    }} else {{
        insertHeader();
    }}
}})();
</script>
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

# AUM persistente via session_state
if 'capitale_globale' not in st.session_state:
    st.session_state['capitale_globale'] = 100000
capitale_globale = st.sidebar.number_input(
    "Capitale AUM (€):", min_value=1000,
    value=st.session_state['capitale_globale'], step=1000,
    key='capitale_globale'
)

st.sidebar.markdown("---")

# Sidebar arricchita — stato DSRM + prossimo ribilanciamento
if not df_aziende.empty and 'Fattore_DSRM' in df_aziende.columns:
    n_v = int((df_aziende['Fattore_DSRM'] == 1.0).sum())
    n_g = int((df_aziende['Fattore_DSRM'] == 0.75).sum())
    n_r = int((df_aziende['Fattore_DSRM'] == 0.0).sum())
    st.sidebar.markdown('<p style="font-size:11px; color:#7a8fa6; letter-spacing:0.08em;">DSRM STATUS</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="font-family:'Courier New',monospace; font-size:12px; line-height:2;">
        <span style="color:#00d4aa;">●</span> Verde: <b>{n_v}</b>&nbsp;&nbsp;
        <span style="color:#c9a84c;">●</span> Giallo: <b>{n_g}</b>&nbsp;&nbsp;
        <span style="color:#e05a5a;">●</span> Kill: <b>{n_r}</b>
    </div>""", unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Prossimo ribilanciamento trimestrale — con announcement date (Rulebook 7-BIS.2)
import calendar as _cal_mod
oggi_dt = datetime.now()

def _primo_lunedi(anno, mese):
    data_primo = datetime(anno, mese, 1)
    giorni_al_lun = (7 - data_primo.weekday()) % 7
    return datetime(anno, mese, 1 + giorni_al_lun)

def _primo_venerdi_febbraio(anno):
    """Announcement date Q1: primo venerdì di febbraio (Rulebook 7-BIS.2)"""
    d = datetime(anno, 2, 1)
    giorni_al_ven = (4 - d.weekday()) % 7  # venerdì=4
    return datetime(anno, 2, 1 + giorni_al_ven)

# Mappa trimestre → (mese_effective, mese_cutoff, mese_annuncio)
TRIMESTRI_RIB = [
    ("Q1", 3,  _primo_venerdi_febbraio),          # effective=Mar, annuncio=1°ven Feb
    ("Q2", 6,  lambda y: datetime(y, 5, 1) + __import__('datetime').timedelta(days=(4 - datetime(y, 5, 1).weekday()) % 7)),
    ("Q3", 9,  lambda y: datetime(y, 8, 1) + __import__('datetime').timedelta(days=(4 - datetime(y, 8, 1).weekday()) % 7)),
    ("Q4", 12, lambda y: datetime(y, 11, 1) + __import__('datetime').timedelta(days=(4 - datetime(y, 11, 1).weekday()) % 7)),
]

# Trova il prossimo ribilanciamento
prossimo_ribil = None
for q_label, mese_eff, fn_ann in TRIMESTRI_RIB:
    for anno_off in [0, 1]:
        anno_t = oggi_dt.year + anno_off
        effective = _primo_lunedi(anno_t, mese_eff)
        if effective > oggi_dt:
            try:
                annuncio = fn_ann(anno_t)
            except Exception:
                annuncio = effective - __import__('datetime').timedelta(days=3)
            # Cut-off = ultimo giorno del mese precedente all'annuncio
            mese_cutoff = annuncio.month - 1 if annuncio.month > 1 else 12
            anno_cutoff = anno_t if annuncio.month > 1 else anno_t - 1
            giorni_cutoff = _cal_mod.monthrange(anno_cutoff, mese_cutoff)[1]
            cutoff = datetime(anno_cutoff, mese_cutoff, giorni_cutoff)
            prossimo_ribil = {
                'label': q_label,
                'effective': effective,
                'annuncio': annuncio,
                'cutoff': cutoff,
                'giorni': (effective - oggi_dt).days,
            }
            break
    if prossimo_ribil:
        break

if prossimo_ribil:
    pr = prossimo_ribil
    fase_attuale = (
        "PRE CUT-OFF" if oggi_dt < pr['cutoff']
        else ("FINESTRA ANNUNCIO" if oggi_dt < pr['annuncio']
              else "SETTIMANA EFFECTIVE")
    )
    st.sidebar.markdown('<p style="font-size:11px; color:#7a8fa6; letter-spacing:0.08em;">PROSSIMO RIBILANCIAMENTO</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="font-family:'Courier New',monospace; font-size:11px; line-height:1.9;">
        <span style="color:#c9a84c; font-weight:bold;">{pr['label']}</span>
        <span style="color:#7a8fa6;"> — Effective:</span>
        <span style="color:#e8eaf0;"> {pr['effective'].strftime('%d %b %Y')}</span><br>
        <span style="color:#7a8fa6;">Cut-off:</span>
        <span style="color:#e8eaf0;"> {pr['cutoff'].strftime('%d %b %Y')}</span><br>
        <span style="color:#7a8fa6;">Annuncio:</span>
        <span style="color:#e8eaf0;"> {pr['annuncio'].strftime('%d %b %Y')}</span><br>
        <span style="color:#7a8fa6;">Fase: </span>
        <span style="color:#00d4aa;">{fase_attuale}</span><br>
        <span style="font-size:10px; color:#7a8fa6;">tra {pr['giorni']} giorni (effective)</span>
    </div>""", unsafe_allow_html=True)
    st.sidebar.markdown("---")

st.sidebar.markdown(f'<p style="font-size:10px; color:#7a8fa6;">Aggiornato: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', unsafe_allow_html=True)

# ==========================================
# 8. FUNZIONI CONDIVISE UI
# ==========================================

@st.cache_data(ttl=120)
def get_indice_live(tickers_tuple, bench="^GSPC", periodo="6mo"):
    """
    Scarica prezzi reali dei costituenti, costruisce serie GGIV ponderata
    e la confronta con S&P 500. Cache 2 minuti per aggiornamento quasi-live.
    Retry automatico con backoff su rate limit Yahoo Finance.
    Restituisce (serie_ggiv, serie_bench, metriche_dict) o (None, None, None).
    """
    import time as _time

    def _download_with_retry(tickers_list, periodo, tentativi=3):
        for i in range(tentativi):
            try:
                raw = yf.download(
                    tickers_list, period=periodo,
                    auto_adjust=True, progress=False
                )
                if raw is not None and not raw.empty:
                    return raw
                _time.sleep(2 ** i)
            except Exception:
                if i < tentativi - 1:
                    _time.sleep(2 ** i)
        return None

    try:
        tickers_list = list(tickers_tuple)
        raw = _download_with_retry(tickers_list + [bench], periodo)
        if raw is None:
            return None, None, None

        if isinstance(raw.columns, pd.MultiIndex):
            if 'Close' in raw.columns.get_level_values(0):
                prezzi = raw['Close']
            else:
                return None, None, None
        else:
            prezzi = raw[['Close']] if 'Close' in raw.columns else None
            if prezzi is None:
                return None, None, None

        bench_serie = prezzi[bench].dropna() if bench in prezzi.columns else None
        tickers_ok  = [t for t in tickers_list if t in prezzi.columns
                       and prezzi[t].dropna().shape[0] > 5]
        if len(tickers_ok) < 2:
            return None, bench_serie, None

        # Pesi DSRM+UCITS se disponibili, altrimenti equiponderati
        pesi = {}
        if not df_aziende.empty and 'Peso_Effettivo' in df_aziende.columns:
            df_p = df_aziende[df_aziende['Ticker'].isin(tickers_ok)].copy()
            tot_p = df_p['Peso_Effettivo'].sum()
            if tot_p > 0:
                for _, r in df_p.iterrows():
                    pesi[r['Ticker']] = r['Peso_Effettivo'] / tot_p
        if not pesi:
            pesi = {t: 1/len(tickers_ok) for t in tickers_ok}

        rend = prezzi[tickers_ok].pct_change().dropna(how='all')
        pesi_v = np.array([pesi.get(t, 1/len(tickers_ok)) for t in tickers_ok])
        pesi_v = pesi_v / pesi_v.sum()
        rend_g = pd.Series(rend[tickers_ok].fillna(0).values @ pesi_v, index=rend.index)
        idx_g  = (1 + rend_g).cumprod() * 100

        bench_rend = bench_serie.pct_change().dropna().reindex(rend_g.index).fillna(0)
        idx_b      = (1 + bench_rend).cumprod() * 100

        ny         = max(len(rend_g) / 252, 0.01)
        cagr       = (idx_g.iloc[-1] / 100) ** (1/ny) - 1
        vol        = rend_g.std() * np.sqrt(252)
        sh         = (cagr - 0.035) / vol if vol > 0 else 0
        dd         = ((idx_g - idx_g.cummax()) / idx_g.cummax()).min()
        delta_oggi = rend_g.iloc[-1] * 100 if len(rend_g) > 0 else 0

        metriche = {
            'cagr': cagr, 'vol': vol, 'sharpe': sh, 'max_dd': dd,
            'valore': idx_g.iloc[-1], 'delta_oggi': delta_oggi,
            'n_costituenti': len(tickers_ok),
        }
        return idx_g, idx_b, metriche
    except Exception:
        return None, None, None


@st.cache_data(ttl=300)
def get_indice_con_ribilanciamento(tickers_tuple, pesi_base_tuple, bench="^GSPC",
                                   periodo="2y", buffer_antiturnover=0.15):
    """
    Costruisce la serie GGIV con ribilanciamento trimestrale reale (Rulebook 7-BIS).
    - Ribilanciamento Q1/Q2/Q3/Q4 al primo lunedì del trimestre
    - Buffer anti-turnover 15%: aggiorna i pesi solo se la deviazione > buffer
    - DSRM applicato ai pesi base
    Restituisce (serie_ggiv, serie_bench, metriche_dict, date_ribil_effettive)
    """
    import time as _time
    try:
        tickers_list = list(tickers_tuple)
        pesi_dict    = dict(pesi_base_tuple)

        # Download dati storici
        for tentativo in range(3):
            try:
                raw = yf.download(tickers_list + [bench], period=periodo,
                                  auto_adjust=True, progress=False)
                if raw is not None and not raw.empty:
                    break
                _time.sleep(2 ** tentativo)
            except Exception:
                if tentativo < 2: _time.sleep(2 ** tentativo)
        else:
            return None, None, None, []

        if isinstance(raw.columns, pd.MultiIndex):
            if 'Close' not in raw.columns.get_level_values(0):
                return None, None, None, []
            prezzi = raw['Close']
        else:
            prezzi = raw[['Close']] if 'Close' in raw.columns else None
            if prezzi is None:
                return None, None, None, []

        bench_serie = prezzi[bench].dropna() if bench in prezzi.columns else None
        tickers_ok  = [t for t in tickers_list if t in prezzi.columns
                       and prezzi[t].dropna().shape[0] > 10]
        if len(tickers_ok) < 2 or bench_serie is None:
            return None, None, None, []

        # Normalizza pesi iniziali
        pesi_curr = {t: pesi_dict.get(t, 0.0) for t in tickers_ok}
        tot_p = sum(pesi_curr.values())
        if tot_p <= 0:
            pesi_curr = {t: 1/len(tickers_ok) for t in tickers_ok}
        else:
            pesi_curr = {t: v/tot_p for t, v in pesi_curr.items()}

        rend = prezzi[tickers_ok].pct_change().dropna(how='all').fillna(0)
        data_inizio = rend.index[0]
        data_fine   = rend.index[-1]

        # Date ribilanciamento con cut-off snapshot (Rulebook 7-BIS.2)
        # Per ogni trimestre: cut-off=ultimo giorno mese precedente, effective=primo lunedì
        # I pesi target vengono "congelati" al cut-off per rispettare l'auditabilità IOSCO
        import calendar as _cal_rib

        def _primo_lun_ts(anno, mese):
            primo = pd.Timestamp(anno, mese, 1)
            giorni_al_lun = (7 - primo.weekday()) % 7
            return pd.Timestamp(anno, mese, 1 + giorni_al_lun)

        def _cutoff_ts(anno, mese_effective):
            """Cut-off = ultimo giorno del mese precedente all'annuncio (≈ mese prima dell'effective)"""
            mese_pre = mese_effective - 2 if mese_effective > 2 else (10 if mese_effective == 1 else 11)
            anno_pre = anno if mese_effective > 2 else anno - 1
            giorni = _cal_rib.monthrange(anno_pre, mese_pre)[1]
            return pd.Timestamp(anno_pre, mese_pre, giorni)

        # Costruisce lista (effective_date, cutoff_date) per tutto il periodo
        schedule_rib = []
        for anno in range(data_inizio.year, data_fine.year + 1):
            for mese in [3, 6, 9, 12]:
                eff = _primo_lun_ts(anno, mese)
                cut = _cutoff_ts(anno, mese)
                if data_inizio < eff < data_fine:
                    schedule_rib.append({'effective': eff, 'cutoff': cut})

        # Per ogni ribilanciamento, calcola i pesi target "alla data di cut-off"
        # In pratica: usa i pesi attuali del portafoglio (già DSRM+RawScore) — il
        # "snapshot" si traduce nel congelarli al cut-off e non aggiornare fino all'effective.
        # Poiché i pesi vengono calcolati all'avvio dal DB (che è aggiornato giornalmente
        # dal Vault Algorithm), usiamo i pesi forniti come pesi_dict già come "cut-off snapshot".
        # In una implementazione futura si potrebbe salvare uno storico per ogni cut-off.
        pesi_target_base = np.array([pesi_dict.get(t, 0.0) for t in tickers_ok])
        tot_t = pesi_target_base.sum()
        if tot_t > 0:
            pesi_target_base = pesi_target_base / tot_t

        # Costruisce serie con ribilanciamento, drift naturale e cut-off snapshot
        rendimenti_portafoglio = []
        date_ribil_effettive   = []
        pesi_v_curr    = np.array([pesi_curr[t] for t in tickers_ok])
        pesi_congelati = pesi_target_base.copy()  # snapshot al cut-off

        # Pre-calcola set di effective dates per lookup veloce
        effective_dates = [s['effective'] for s in schedule_rib]
        cutoff_dates    = [s['cutoff']    for s in schedule_rib]

        for data, riga in rend.iterrows():
            # Alla data di cut-off: congela i pesi driftati come target per il prossimo ribil.
            for cut in cutoff_dates:
                if abs((data - cut).days) <= 1:
                    tot_curr = pesi_v_curr.sum()
                    if tot_curr > 0:
                        pesi_congelati = pesi_v_curr / tot_curr
                    break

            # All'effective date: ribilancia con buffer anti-turnover (Rulebook 7-BIS.4)
            if any(abs((data - eff).days) <= 3 for eff in effective_dates):
                deviazione_max = np.abs(pesi_v_curr - pesi_congelati).max()
                if deviazione_max > buffer_antiturnover:
                    pesi_v_curr = pesi_congelati.copy()
                    date_ribil_effettive.append(data)

            r = riga[tickers_ok].fillna(0).values
            rend_giorno = float(r @ pesi_v_curr)
            rendimenti_portafoglio.append(rend_giorno)

            # Drift naturale: aggiorna pesi per la giornata successiva
            nuovi = pesi_v_curr * (1 + r)
            tot_n = nuovi.sum()
            if tot_n > 0:
                pesi_v_curr = nuovi / tot_n

        serie_rend = pd.Series(rendimenti_portafoglio, index=rend.index)
        idx_g = (1 + serie_rend).cumprod() * 100

        bench_rend = bench_serie.pct_change().dropna().reindex(serie_rend.index).fillna(0)
        idx_b = (1 + bench_rend).cumprod() * 100

        ny   = max(len(serie_rend) / 252, 0.01)
        cagr = (idx_g.iloc[-1] / 100) ** (1/ny) - 1
        vol  = serie_rend.std() * np.sqrt(252)
        sh   = (cagr - 0.035) / vol if vol > 0 else 0
        dd   = ((idx_g - idx_g.cummax()) / idx_g.cummax()).min()
        dv   = serie_rend[serie_rend < 0].std() * np.sqrt(252)
        so   = (cagr - 0.035) / dv if dv > 0 else 0
        delta_oggi = serie_rend.iloc[-1] * 100 if len(serie_rend) > 0 else 0

        metriche = {
            'cagr': cagr, 'vol': vol, 'sharpe': sh, 'sortino': so,
            'max_dd': dd, 'valore': idx_g.iloc[-1], 'delta_oggi': delta_oggi,
            'n_costituenti': len(tickers_ok),
            'n_ribilanciamenti': len(date_ribil_effettive),
        }
        return idx_g, idx_b, metriche, date_ribil_effettive
    except Exception:
        return None, None, None, []


def render_grafico_indice(idx_g, idx_b, metriche, altezza=400, titolo_extra=""):
    """Renderizza il grafico GGIV vs S&P 500 già calcolato."""
    fig = go.Figure()

    # Area S&P 500
    fig.add_trace(go.Scatter(
        x=idx_b.index, y=idx_b.values,
        name="S&P 500", mode='lines',
        line=dict(color='#7a8fa6', width=1.5),
        hovertemplate='S&P 500: %{y:.1f}<extra></extra>',
    ))
    # Area GGIV
    fig.add_trace(go.Scatter(
        x=idx_g.index, y=idx_g.values,
        name="GGIV Index", mode='lines',
        line=dict(color='#00d4aa', width=2.5),
        fill='tonexty', fillcolor='rgba(0,212,170,0.07)',
        hovertemplate='GGIV: %{y:.1f}<extra></extra>',
    ))
    # Linea base 100
    fig.add_hline(y=100, line_dash="dot", line_color="#1a2d45", line_width=1)
    # Annotazione valore corrente — posizionata internamente
    fig.add_annotation(
        x=idx_g.index[-1], y=idx_g.iloc[-1],
        text=f"  {idx_g.iloc[-1]:.1f}",
        showarrow=False,
        font=dict(color='#00d4aa', size=11, family='Courier New'),
        xanchor='right',
        xref='x', yref='y',
        bgcolor='rgba(13,27,42,0.7)',
        bordercolor='#00d4aa',
        borderwidth=1,
        borderpad=3,
    )
    fig.update_layout(
        paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
        font=dict(color='#e8eaf0', family='Courier New', size=10),
        legend=dict(
            bgcolor='rgba(13,27,42,0.8)', bordercolor='#1a2d45',
            orientation='h', yanchor='bottom', y=1.01, xanchor='left', x=0,
            font=dict(size=10),
        ),
        xaxis=dict(gridcolor='#1a2d45', showgrid=True, linecolor='#1a2d45'),
        yaxis=dict(gridcolor='#1a2d45', showgrid=True, linecolor='#1a2d45',
                   title='Valore (base 100)'),
        margin=dict(t=40, b=30, l=55, r=20),
        height=altezza,
        hovermode='x unified',
    )
    if titolo_extra:
        fig.update_layout(title=dict(
            text=titolo_extra, font=dict(color='#7a8fa6', size=10, family='Courier New'),
            x=0.5, xanchor='center'
        ))
    return fig




# ==========================================
# 9. SCHEDE
# ==========================================
tab_home, tab_overview, tab_watchlist, tab_backtest, tab_correlazione, tab_rischio, tab_brevetti = st.tabs([
    "⬡ HOME",
    "DATABASE & DSRM",
    "INCUBATORE",
    "BACKTEST & STRESS",
    "CORRELAZIONE & MACRO",
    "RISCHIO & ORDINI",
    "SENSORE BREVETTI"
])

# --- SCHEDA 0: HOME ---
with tab_home:

    # ── Radar Sentiment — componenti Streamlit nativi (no HTML grezzo) ────────
    st.caption("RADAR SENTIMENT — SALUTE DEL PORTAFOGLIO")

    if not df_aziende.empty:
        # Calcola metriche
        if 'Fattore_DSRM' in df_aziende.columns:
            media_dsrm = df_aziende['Fattore_DSRM'].mean()
            n_verdi    = int((df_aziende['Fattore_DSRM'] == 1.0).sum())
            n_gialli   = int((df_aziende['Fattore_DSRM'] == 0.75).sum())
            n_rossi    = int((df_aziende['Fattore_DSRM'] == 0.0).sum())
            score_glob = int(media_dsrm * 100)
        else:
            n_verdi = len(df_aziende); n_gialli = 0; n_rossi = 0; score_glob = 75

        n_pass = n_warn = n_fail = 0
        if 'Flag_Ammissione' in df_aziende.columns:
            amm    = df_aziende['Flag_Ammissione'].astype(str).str.strip()
            n_pass = int((amm == 'PASS').sum())
            n_warn = int(amm.str.startswith('WARN').sum())
            n_fail = int(amm.str.startswith('FAIL').sum())

        glob_label = "SANO" if score_glob >= 80 else ("MODERATO" if score_glob >= 55 else "ALLERTA")

        # Riga 1 — Score globale + barra
        sr1c1, sr1c2 = st.columns([1, 3])
        sr1c1.metric("DSRM HEALTH SCORE", f"{score_glob}/100", glob_label)
        with sr1c2:
            st.caption("Livello di salute complessivo basato sul DSRM")
            st.progress(score_glob / 100)

        # Riga 2 — DSRM conteggi
        sd1, sd2, sd3 = st.columns(3)
        sd1.metric("🟢 VERDE ≤45gg",    str(n_verdi),  "comunicazione regolare")
        sd2.metric("🟡 GIALLO 46-90gg", str(n_gialli), "ritardo comunicazioni")
        sd3.metric("🔴 KILL SWITCH",    str(n_rossi),  "silenzio >90gg")

        # Riga 3 — Filtri ammissione
        st.caption("FILTRI AMMISSIONE")
        sa1, sa2, sa3 = st.columns(3)
        sa1.metric("✅ PASS", str(n_pass), "conformi al Rulebook")
        sa2.metric("⚠️ WARN", str(n_warn), "dati mancanti")
        sa3.metric("❌ FAIL", str(n_fail), "violazione criteri")

        # Riga 4 — Breakdown per Tier
        tier_colors_label = {'Tier 1': '🔴', 'Tier 2': '🔵', 'Tier 3': '🟢'}
        tiers_presenti = [t for t in ['Tier 1','Tier 2','Tier 3']
                          if 'Tier' in df_aziende.columns and t in df_aziende['Tier'].values]
        if tiers_presenti:
            st.caption("SALUTE PER TIER")
            tier_cols = st.columns(len(tiers_presenti))
            for col_t, tier in zip(tier_cols, tiers_presenti):
                sub = df_aziende[df_aziende['Tier'] == tier]
                n_t = len(sub)
                dsrm_t = int(sub['Fattore_DSRM'].mean() * 100) if 'Fattore_DSRM' in sub.columns else 75
                gg_t   = int(sub['Giorni_Silenzio'].mean()) if 'Giorni_Silenzio' in sub.columns else 0
                emoji  = tier_colors_label.get(tier, '⬡')
                col_t.metric(f"{emoji} {tier}", f"{dsrm_t}/100",
                             f"{n_t} aziende · {gg_t}gg media silenzio")
                col_t.progress(dsrm_t / 100)
    else:
        st.warning("Dati portafoglio non disponibili per il radar sentiment.")

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # ── Grafico indice live — centrato, grande ───────────────────────────────
    st.markdown("""
    <div style="text-align:center; font-family:'Courier New',monospace; margin-bottom:6px;">
        <span style="font-size:13px; color:#c9a84c; letter-spacing:0.12em; font-weight:bold;">
            ⬡ GGIV INDEX — ANDAMENTO IN TEMPO REALE
        </span><br>
        <span style="font-size:10px; color:#7a8fa6;">
            Costruito sui costituenti reali del portafoglio con pesi DSRM + UCITS &nbsp;·&nbsp;
            Confronto S&P 500 &nbsp;·&nbsp; Aggiornamento ogni 2 minuti
        </span>
    </div>
    """, unsafe_allow_html=True)

    if not df_aziende.empty and 'Ticker' in df_aziende.columns:
        tickers_live = tuple(df_aziende['Ticker'].dropna().unique())

        # Selettore periodo — gestione robusta via key del radio
        periodo_opzioni = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1A": "1y"}
        labels_periodo  = list(periodo_opzioni.keys())
        # Inizializza con valore sicuro (label, non codice yfinance)
        if st.session_state.get('periodo_home_radio') not in labels_periodo:
            st.session_state['periodo_home_radio'] = "6M"
        periodo_label = st.radio(
            "Periodo:", labels_periodo,
            horizontal=True,
            key='periodo_home_radio',
            label_visibility='collapsed'
        )
        periodo_attivo = periodo_opzioni[periodo_label]

        with st.spinner("Aggiornamento dati indice..."):
            idx_g_home, idx_b_home, met_home = get_indice_live(
                tickers_live, periodo=periodo_attivo
            )

        if idx_g_home is not None and idx_b_home is not None:
            kc1, kc2, kc3, kc4, kc5 = st.columns(5)
            delta_oggi_sign = "+" if met_home['delta_oggi'] >= 0 else ""
            kc1.metric("VALORE INDICE",
                       f"{met_home['valore']:.1f}",
                       f"{delta_oggi_sign}{met_home['delta_oggi']:.2f}% oggi")
            kc2.metric("CAGR",
                       f"{met_home['cagr']*100:+.1f}%",
                       "annualizzato periodo")
            kc3.metric("SHARPE RATIO",
                       f"{met_home['sharpe']:.2f}",
                       "rf=3.5%")
            kc4.metric("MAX DRAWDOWN",
                       f"{met_home['max_dd']*100:.1f}%",
                       "peak-to-trough",
                       delta_color="inverse")
            kc5.metric("VOLATILITÀ",
                       f"{met_home['vol']*100:.1f}%",
                       f"{met_home['n_costituenti']} costituenti",
                       delta_color="off")

            fig_home = render_grafico_indice(
                idx_g_home, idx_b_home, met_home,
                altezza=480,
                titolo_extra=f"GGIV Index vs S&P 500 — {periodo_attivo.replace('mo',' mesi').replace('y',' anno')}"
            )
            st.plotly_chart(fig_home, use_container_width=True)
            st.caption(f"Aggiornato: {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
                       f"{met_home['n_costituenti']} costituenti con dati disponibili su Yahoo Finance · "
                       f"Pesi DSRM + UCITS applicati")
        else:
            st.warning("Impossibile scaricare i dati dei costituenti. Controlla la connessione.")
    else:
        st.warning("Portafoglio non disponibile. Controlla la connessione al Google Sheet.")

# --- SCHEDA 1: DATABASE & DSRM ---
with tab_overview:

    # ── KPI reali (calcolati dai dati live se disponibili) ───────────────────
    n_aziende   = len(df_aziende) if not df_aziende.empty else 0
    n_kill      = (df_aziende['Fattore_DSRM'] == 0.0).sum() if not df_aziende.empty and 'Fattore_DSRM' in df_aziende.columns else 0
    n_penaliz   = (df_aziende['Fattore_DSRM'] == 0.75).sum() if not df_aziende.empty and 'Fattore_DSRM' in df_aziende.columns else 0
    peso_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AUM SIMULATO",      f"€ {capitale_globale:,.0f}", "vedi sidebar per modificare")
    col2.metric("AZIENDE IN INDICE", str(n_aziende),
                f"{n_kill} kill switch · {n_penaliz} penalizzati" if (n_kill+n_penaliz) > 0 else "tutte operative")
    col3.metric("GOLDEN SHIELD",     f"{peso_shield:.1f}%",
                "✓ attivo" if peso_shield >= 25 else ("⚠ sotto target" if peso_shield >= 10 else "✗ assente"))
    col4.metric("ULTIMO AGGIORNAMENTO", datetime.now().strftime("%d/%m %H:%M"), "da Google Sheet")

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    # ── Sunburst ─────────────────────────────────────────────────────────────
    if not df_aziende.empty and 'Tier' in df_aziende.columns:
        st.markdown("""
        <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                    letter-spacing:0.1em; margin-bottom:4px;">
            ASSET ALLOCATION — MAPPA STRUTTURALE
        </div>""", unsafe_allow_html=True)

        labels = ["GGIV INDEX"]; parents = [""]; values = [df_aziende['Peso_Effettivo'].sum()]; colors = ["#c9a84c"]
        tier_colors = {'Tier 1': '#e05a5a', 'Tier 2': '#378ADD', 'Tier 3': '#00d4aa'}
        for tier in df_aziende['Tier'].unique():
            peso_tier = df_aziende[df_aziende['Tier'] == tier]['Peso_Effettivo'].sum()
            labels.append(tier); parents.append("GGIV INDEX")
            values.append(peso_tier); colors.append(tier_colors.get(tier, '#7a8fa6'))
        for _, row in df_aziende.iterrows():
            labels.append(row['Azienda']); parents.append(row['Tier'])
            values.append(row['Peso_Effettivo'])
            colors.append(tier_colors.get(row['Tier'], '#7a8fa6') + 'bb')

        fig_sunburst = go.Figure(go.Sunburst(
            labels=labels, parents=parents, values=values,
            marker=dict(colors=colors, line=dict(color='#0a0e1a', width=2)),
            textfont=dict(family="Courier New", size=11, color="#e8eaf0"),
            hovertemplate='<b>%{label}</b><br>Peso: %{value:.2f}%<extra></extra>',
            branchvalues="total", insidetextorientation='radial',
        ))
        fig_sunburst.update_layout(
            paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
            font=dict(color='#e8eaf0', family='Courier New'),
            margin=dict(t=10, b=10, l=10, r=10), height=440,
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        st.caption("Clicca su un Tier per espandere · Clicca al centro per tornare")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # ── Tabella DSRM curata ──────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:8px;">
        MOTORE DSRM — STATO ATTIVO
    </div>""", unsafe_allow_html=True)

    if not df_aziende.empty:
        # Costruisci tabella leggibile
        cols_dsrm = ['Ticker', 'Azienda', 'Tier']
        if 'Giorni_Silenzio'  in df_aziende.columns: cols_dsrm.append('Giorni_Silenzio')
        if 'Fattore_DSRM'     in df_aziende.columns: cols_dsrm.append('Fattore_DSRM')
        if 'Peso_Base'        in df_aziende.columns: cols_dsrm.append('Peso_Base')
        if 'Peso_Effettivo'   in df_aziende.columns: cols_dsrm.append('Peso_Effettivo')
        if 'Market_Cap_USD'   in df_aziende.columns: cols_dsrm.append('Market_Cap_USD')
        if 'GES_Score'        in df_aziende.columns: cols_dsrm.append('GES_Score')
        if 'Flag_Ammissione'  in df_aziende.columns: cols_dsrm.append('Flag_Ammissione')

        df_tab = df_aziende[cols_dsrm].copy()

        # Formatta colonne numeriche
        if 'Market_Cap_USD' in df_tab.columns:
            df_tab['Market_Cap_USD'] = df_tab['Market_Cap_USD'].apply(
                lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x >= 1e9
                          else (f"${x/1e6:.0f}M" if pd.notna(x) and x > 0 else "N/D")
            )
        if 'GES_Score' in df_tab.columns:
            df_tab['GES_Score'] = df_tab['GES_Score'].apply(
                lambda x: f"{float(x):.4f}" if pd.notna(x) and x != '' else "N/D"
            )
        if 'Peso_Base' in df_tab.columns:
            df_tab['Peso_Base'] = df_tab['Peso_Base'].apply(
                lambda x: f"{float(x):.1f}%" if pd.notna(x) else "N/D"
            )
        if 'Peso_Effettivo' in df_tab.columns:
            df_tab['Peso_Effettivo'] = df_tab['Peso_Effettivo'].apply(
                lambda x: f"{float(x):.2f}%" if pd.notna(x) else "N/D"
            )

        # Colora righe per stato DSRM usando HTML
        def dsrm_row_color(row):
            if 'Fattore_DSRM' in row and row['Fattore_DSRM'] == 0.0:
                return '#2a0e0e'   # rosso scuro — kill switch
            elif 'Fattore_DSRM' in row and row['Fattore_DSRM'] < 1.0:
                return '#1a1400'   # giallo scuro — penalizzato
            return ''

        # Rinomina colonne per presentazione
        df_tab = df_tab.rename(columns={
            'Giorni_Silenzio': 'Silenzio (gg)',
            'Fattore_DSRM':    'DSRM Δ',
            'Peso_Base':       'Peso Base',
            'Peso_Effettivo':  'Peso Eff.',
            'Market_Cap_USD':  'Mkt Cap',
            'GES_Score':       'GES',
            'Flag_Ammissione': 'Ammissione',
        })
        st.dataframe(
            df_tab,
            use_container_width=True,
            hide_index=True,
            height=min(400, (len(df_tab) + 1) * 38),
        )

        # Alert DSRM
        aziende_penalizzate = df_aziende[df_aziende['Fattore_DSRM'] < 1.0] if 'Fattore_DSRM' in df_aziende.columns else pd.DataFrame()
        capitale_salvato_totale = (df_aziende['Percentuale_Persa'].sum() / 100) * capitale_globale if 'Percentuale_Persa' in df_aziende.columns else 0

        if not aziende_penalizzate.empty:
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            for _, row in aziende_penalizzate.iterrows():
                soldi_tolti = (row.get('Percentuale_Persa', 0) / 100) * capitale_globale
                if row['Fattore_DSRM'] == 0:
                    st.error(f"KILL SWITCH: {row['Azienda']} ({row['Giorni_Silenzio']} gg) — € {soldi_tolti:,.0f} blindati")
                else:
                    st.warning(f"PENALITÀ −25%: {row['Azienda']} ({row['Giorni_Silenzio']} gg) — € {soldi_tolti:,.0f} allo Shield")
        else:
            st.success("DSRM — Tutte le aziende comunicano regolarmente (Δ = 1.0)")
    else:
        st.warning("Connessione al database in corso. Controlla i link CSV.")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── Filtri ammissione ─────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:8px;">
        FILTRI DI AMMISSIONE — RULEBOOK SEZ. 2
    </div>""", unsafe_allow_html=True)
    st.caption("Market Cap >10M USD · ADTV >250K USD · Free Float >15% · No A-Share cinesi")

    if not df_aziende.empty:
        col_amm = 'Flag_Ammissione' if 'Flag_Ammissione' in df_aziende.columns else None
        col_del = 'Flag_Delisting'  if 'Flag_Delisting'  in df_aziende.columns else None
        col_mc  = 'Market_Cap_USD'  if 'Market_Cap_USD'  in df_aziende.columns else None
        col_adtv= 'ADTV_3M_USD'     if 'ADTV_3M_USD'     in df_aziende.columns else None
        col_ff  = 'Free_Float_Pct'  if 'Free_Float_Pct'  in df_aziende.columns else None

        if col_amm:
            col_amm_str = df_aziende[col_amm].astype(str).str.strip()
            pass_df = df_aziende[col_amm_str == 'PASS']
            warn_df = df_aziende[col_amm_str.str.startswith('WARN', na=False)]
            fail_df = df_aziende[col_amm_str.str.startswith('FAIL', na=False)]

            ca1, ca2, ca3 = st.columns(3)
            ca1.metric("PASS — Ammesse", str(len(pass_df)), "conformi al Rulebook")
            ca2.metric("WARN — Dati N/D", str(len(warn_df)), "verifica manuale")
            ca3.metric("FAIL — Escluse",  str(len(fail_df)), "violazione criteri")

            if not fail_df.empty:
                for _, row in fail_df.iterrows():
                    st.error(f"FAIL: {row['Azienda']} ({row['Ticker']}) — {str(row[col_amm])}")
            if not warn_df.empty:
                with st.expander(f"⚠️ {len(warn_df)} aziende con dati mancanti", expanded=True):
                    for _, row in warn_df.iterrows():
                        st.warning(f"WARN: {row['Azienda']} ({row['Ticker']}) — {str(row[col_amm])}")

            cols_show = ['Ticker', 'Azienda', 'Tier']
            for c in [col_mc, col_adtv, col_ff, col_amm, col_del]:
                if c: cols_show.append(c)
            st.dataframe(df_aziende[cols_show], use_container_width=True, hide_index=True)

            if col_del:
                del_alert = df_aziende[df_aziende[col_del].astype(str).str.strip() == 'ALERT']
                if not del_alert.empty:
                    for _, row in del_alert.iterrows():
                        st.error(f"DELISTING ALERT: {row['Azienda']} ({row['Ticker']}) — verificare urgentemente su borsa primaria")
        else:
            st.info("Colonna 'Flag_Ammissione' non trovata. Esegui il Radar Bot per popolarla.")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── UCITS 5/10/40 ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:8px;">
        UCITS AGGREGATE CAP — REGOLA 5/10/40
    </div>""", unsafe_allow_html=True)
    st.caption("Nessun titolo >10% · Somma titoli >5% non supera 40% del portafoglio")

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
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:6px;">
        INCUBATORE — AZIENDE IN OSSERVAZIONE
    </div>""", unsafe_allow_html=True)
    st.caption("Aziende sotto scansione DSRM per eventuale ingresso nell'indice. Buffer anti-turnover: 15%.")

    if not df_wl.empty:
        colonne_da_mostrare = ['Ticker', 'Azienda']
        for c in ['Tier', 'Data_Ultima_News', 'Giorni_Silenzio',
                  'Market_Cap_USD', 'ADTV_3M_USD', 'Free_Float_Pct',
                  'Flag_Ammissione', 'Flag_Delisting']:
            if c in df_wl.columns:
                colonne_da_mostrare.append(c)

        # ── Calcola GES minimo dei componenti attuali per buffer anti-turnover ──
        ges_minimo_indice = None
        buffer_pct = 15.0
        if not df_aziende.empty and 'GES_Score' in df_aziende.columns:
            ges_vals = pd.to_numeric(df_aziende['GES_Score'], errors='coerce').dropna()
            if not ges_vals.empty:
                ges_minimo_indice = float(ges_vals.min())

        # Calcola stato "pronta" + "superamento buffer" per ogni azienda
        df_wl_show = df_wl[colonne_da_mostrare].copy()
        df_wl_show['_pronta'] = False
        df_wl_show['_supera_buffer'] = False

        if 'Flag_Ammissione' in df_wl.columns and 'Giorni_Silenzio' in df_wl.columns:
            df_wl_show['_pronta'] = (
                (df_wl['Flag_Ammissione'].astype(str).str.strip() == 'PASS') &
                (df_wl['Giorni_Silenzio'] <= 45)
            )

        # Buffer anti-turnover: candidata entra solo se GES > GES_min * (1 + 15%)
        if ges_minimo_indice is not None and 'GES_Score' in df_wl.columns:
            soglia_buffer = ges_minimo_indice * (1 + buffer_pct / 100)
            ges_wl = pd.to_numeric(df_wl['GES_Score'], errors='coerce').fillna(0)
            df_wl_show['_supera_buffer'] = ges_wl > soglia_buffer
            df_wl_show['_pronta'] = df_wl_show['_pronta'] & df_wl_show['_supera_buffer']

        pronte = int(df_wl_show['_pronta'].sum())

        # KPI
        cw1, cw2, cw3, cw4 = st.columns(4)
        cw1.metric("IN OSSERVAZIONE", str(len(df_wl)), "aziende candidate")
        cw2.metric("PRONTE PER INGRESSO", str(pronte), "PASS + DSRM verde + buffer 15%")
        n_fail_wl = int(df_wl['Flag_Ammissione'].astype(str).str.startswith('FAIL').sum()) if 'Flag_Ammissione' in df_wl.columns else 0
        cw3.metric("NON IDONEE", str(n_fail_wl), "non superano filtri")
        if ges_minimo_indice is not None:
            soglia_disp = ges_minimo_indice * (1 + buffer_pct/100)
            cw4.metric("SOGLIA BUFFER GES", f"{soglia_disp:.4f}",
                       f"GES min indice + {buffer_pct:.0f}%")
        else:
            cw4.metric("BUFFER ANTI-TURNOVER", f"{buffer_pct:.0f}%", "Rulebook 7-BIS.4")

        # Alert pronte subito visibili
        if pronte > 0:
            df_pronte = df_wl_show[df_wl_show['_pronta']]
            nomi_pronti = ", ".join(df_pronte['Azienda'].tolist())
            st.success(f"✅ {pronte} aziende pronte per valutazione Index Committee: **{nomi_pronti}**")
        elif ges_minimo_indice is not None:
            n_pass_dsrm = int(
                (df_wl_show['Flag_Ammissione'].astype(str).str.strip() == 'PASS').sum()
                if 'Flag_Ammissione' in df_wl_show.columns else 0
            )
            n_no_buffer = int((~df_wl_show['_supera_buffer']).sum()) if '_supera_buffer' in df_wl_show.columns else 0
            if n_pass_dsrm > 0 and n_no_buffer > 0:
                st.info(f"ℹ️ {n_pass_dsrm} aziende PASS ma nessuna supera il buffer anti-turnover "
                        f"(GES >{ges_minimo_indice*(1+buffer_pct/100):.4f}). Buffer Rulebook 7-BIS.4 attivo.")

        # Controlli filtro + ordinamento
        fc1, fc2, fc3 = st.columns([1, 1, 2])
        filtro_stato = fc1.selectbox(
            "Filtra per stato:", ["Tutte", "Solo PASS", "Solo WARN", "Solo FAIL"],
            key='wl_filtro'
        )
        ordina_per = fc2.selectbox(
            "Ordina per:",
            ["Giorni_Silenzio", "Flag_Ammissione", "Market_Cap_USD", "Azienda"],
            key='wl_ordina'
        )

        # Applica filtro
        df_filtered = df_wl_show.copy()
        if filtro_stato == "Solo PASS" and 'Flag_Ammissione' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Flag_Ammissione'].astype(str).str.strip() == 'PASS']
        elif filtro_stato == "Solo WARN" and 'Flag_Ammissione' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Flag_Ammissione'].astype(str).str.startswith('WARN')]
        elif filtro_stato == "Solo FAIL" and 'Flag_Ammissione' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Flag_Ammissione'].astype(str).str.startswith('FAIL')]

        # Applica ordinamento
        if ordina_per in df_filtered.columns:
            df_filtered = df_filtered.sort_values(ordina_per, ascending=True, na_position='last')

        # Porta le aziende pronte in cima
        df_pronte_top  = df_filtered[df_filtered['_pronta']].copy()
        df_altre       = df_filtered[~df_filtered['_pronta']].copy()
        df_finale      = pd.concat([df_pronte_top, df_altre], ignore_index=True)

        # Rimuovi colonna helper
        cols_display = [c for c in df_finale.columns if c != '_pronta']

        # Formatta Market Cap leggibile
        if 'Market_Cap_USD' in df_finale.columns:
            df_finale['Market_Cap_USD'] = df_finale['Market_Cap_USD'].apply(
                lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x >= 1e9
                          else (f"${x/1e6:.0f}M" if pd.notna(x) and x > 0 else "N/D")
            )

        st.dataframe(
            df_finale[cols_display],
            use_container_width=True,
            hide_index=True,
            height=min(500, (len(df_finale) + 1) * 38),
        )
        st.caption(f"Mostrate {len(df_finale)} aziende · Le righe in cima sono quelle pronte per l'ingresso (PASS + DSRM verde)")
    else:
        st.info("Watchlist vuota o in caricamento. Esegui il Radar Bot per popolarla.")

# --- SCHEDA 3: BACKTEST ---
with tab_backtest:
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:4px;">
        BACKTEST — SERIE STORICA REALE CON RIBILANCIAMENTO TRIMESTRALE
    </div>""", unsafe_allow_html=True)
    st.caption("Simulazione con ribilanciamento Q1/Q2/Q3/Q4 e buffer anti-turnover 15% (Rulebook sez. 7-BIS)")

    # Grafico reale — stessi dati del Tear Sheet PDF
    if not df_aziende.empty and 'Ticker' in df_aziende.columns:
        tickers_bt_live = tuple(df_aziende['Ticker'].dropna().unique())
        opzioni_bt = ["1y", "2y", "3y", "5y", "max"]
        label_bt   = {"1y":"1 Anno","2y":"2 Anni","3y":"3 Anni","5y":"5 Anni","max":"Max storia"}
        # Inizializza con valore sicuro
        if st.session_state.get('periodo_bt') not in opzioni_bt:
            st.session_state['periodo_bt'] = "2y"
        col_bt1, col_bt2 = st.columns([1, 3])
        periodo_bt = col_bt1.selectbox(
            "Periodo storico:",
            opzioni_bt,
            index=opzioni_bt.index(st.session_state['periodo_bt']),
            format_func=lambda x: label_bt[x],
            key='periodo_bt'
        )

        with st.spinner("Scaricando serie storica con ribilanciamento trimestrale reale..."):
            # Prepara pesi base DSRM+UCITS come tuple hashable
            if not df_aziende.empty and 'Peso_Effettivo' in df_aziende.columns:
                _df_pb = df_aziende[df_aziende['Ticker'].notna()][['Ticker','Peso_Effettivo']].copy()
                _tot_pb = _df_pb['Peso_Effettivo'].sum()
                if _tot_pb > 0:
                    _pesi_bt = tuple(zip(_df_pb['Ticker'].tolist(),
                                        (_df_pb['Peso_Effettivo'] / _tot_pb).tolist()))
                else:
                    _pesi_bt = tuple((t, 1/len(tickers_bt_live)) for t in tickers_bt_live)
            else:
                _pesi_bt = tuple((t, 1/len(tickers_bt_live)) for t in tickers_bt_live)

            idx_g_bt, idx_b_bt, met_bt, date_ribil_eff = get_indice_con_ribilanciamento(
                tickers_bt_live, _pesi_bt, periodo=periodo_bt
            )
            # Fallback a versione senza ribilanciamento se fallisce
            if idx_g_bt is None:
                idx_g_bt, idx_b_bt, met_bt = get_indice_live(tickers_bt_live, periodo=periodo_bt)
                date_ribil_eff = []
                met_bt = met_bt or {}

        if idx_g_bt is not None:
            # KPI con ribilanciamento reale
            kb1, kb2, kb3, kb4, kb5, kb6 = st.columns(6)
            kb1.metric("CAGR",        f"{met_bt['cagr']*100:+.2f}%",  "annualizzato")
            kb2.metric("SHARPE",      f"{met_bt['sharpe']:.2f}",       "rf=3.5%")
            kb3.metric("SORTINO",     f"{met_bt.get('sortino', 0):.2f}", "downside risk")
            kb4.metric("MAX DD",      f"{met_bt['max_dd']*100:.2f}%",  "drawdown massimo")
            kb5.metric("VOL ANNUA",   f"{met_bt['vol']*100:.1f}%",     "rendimenti giornalieri")
            kb6.metric("RIBILANC.",   str(met_bt.get('n_ribilanciamenti', '—')),
                       f"{met_bt['n_costituenti']} ticker · buffer 15%")

            # Date ribilanciamenti effettivi nel periodo
            fig_bt2 = render_grafico_indice(idx_g_bt, idx_b_bt, met_bt, altezza=420)
            # Linee ribilanciamenti effettivi (oro pieno) vs target (oro tratteggiato)
            date_rib_target = pd.date_range(
                start=idx_g_bt.index[0], end=idx_g_bt.index[-1], freq='QS'
            )
            for dr in date_rib_target:
                fig_bt2.add_vline(
                    x=dr, line=dict(color='#c9a84c', width=0.6, dash='dot'),
                )
            for dr in (date_ribil_eff or []):
                fig_bt2.add_vline(
                    x=dr, line=dict(color='#c9a84c', width=1.5, dash='solid'),
                )
            fig_bt2.add_trace(go.Scatter(
                x=[None], y=[None], mode='lines', name='Ribilanciamento effettivo',
                line=dict(color='#c9a84c', width=1.5, dash='solid')
            ))
            fig_bt2.add_trace(go.Scatter(
                x=[None], y=[None], mode='lines', name='Data target Q trimestrale',
                line=dict(color='#c9a84c', width=0.8, dash='dot')
            ))
            # Drawdown
            dd_serie = ((idx_g_bt - idx_g_bt.cummax()) / idx_g_bt.cummax()) * 100
            fig_bt2.add_trace(go.Scatter(
                x=dd_serie.index, y=dd_serie.values,
                name='Drawdown GGIV', fill='tozeroy',
                fillcolor='rgba(224,90,90,0.12)',
                line=dict(color='#e05a5a', width=0.8),
                yaxis='y2',
                hovertemplate='DD: %{y:.1f}%<extra></extra>',
            ))
            fig_bt2.update_layout(**{
                'yaxis2': dict(
                    title='Drawdown (%)', overlaying='y', side='right',
                    gridcolor='#1a2d45',
                    tickfont=dict(color='#e05a5a', size=9),
                    showgrid=False,
                )
            })
            st.plotly_chart(fig_bt2, use_container_width=True)
            n_rib_eff = len(date_ribil_eff) if date_ribil_eff else 0
            st.caption(
                f"Ribilanciamento trimestrale reale (Rulebook 7-BIS) · "
                f"{n_rib_eff} ribilanciamenti effettivi (buffer anti-turnover 15%) · "
                f"Linee dorate piene = ribilanciamento eseguito · tratteggio = data target · "
                f"Area rossa = drawdown GGIV · {met_bt['n_costituenti']} costituenti."
            )
        else:
            st.warning("Impossibile scaricare i dati storici. Controlla la connessione.")
    else:
        st.warning("Portafoglio non disponibile.")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:8px;">
        STRESS TEST — SIMULAZIONE SCENARIO DI CROLLO
    </div>""", unsafe_allow_html=True)
    crollo = st.slider("Simula crollo mercato (%):", 0, 50, 20, step=1)

    peso_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t2 = df_aziende[df_aziende['Tier'] == 'Tier 2']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    impatto_tot = (-crollo * 1.5 * (peso_t1 / 100)) + (-crollo * (peso_t2 / 100)) + (-crollo * 0.2 * (peso_t3 / 100))

    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("IMPATTO TIER 1", f"{-crollo * 1.5:.1f}%", "rischio alto", delta_color="inverse")
    col_c2.metric("IMPATTO TIER 3", f"{-crollo * 0.2:.1f}%", "protezione shield")
    col_c3.metric("IMPATTO NETTO", f"€ {capitale_globale * (impatto_tot / 100):,.0f}", f"{impatto_tot:.1f}%")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:6px;">
        TEAR SHEET — BACKTEST ISTITUZIONALE (2020 → OGGI)
    </div>""", unsafe_allow_html=True)
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

                    # ── Pesi con RawScore + DSRM + UCITS completo (Rulebook Sez. 9C + 7) ──
                    df_bt = df_aziende.copy()
                    df_bt['Mult'] = df_bt['Tier'].map(T_MULT).fillna(1.0)
                    df_bt['FDSRM'] = df_bt['Giorni_Silenzio'].apply(
                        lambda g: 0.0 if g > 90 else 0.75 if g > 45 else 1.0
                    ) if 'Giorni_Silenzio' in df_bt.columns else 1.0

                    # RawScore = sqrt(MC) * GES * Delta  (Rulebook Sez. 9C)
                    def _rawscore_bt(row):
                        delta = row['FDSRM']
                        try:
                            mc  = float(row.get('Market_Cap_USD') or 0)
                            ges = float(row.get('GES_Score') or 0)
                            if mc > 0 and ges > 0:
                                return np.sqrt(mc) * ges * delta
                        except (ValueError, TypeError):
                            pass
                        # Fallback: Peso_Base × DSRM × Mult
                        return float(row.get('Peso_Base', 1.0) or 1.0) * delta * row['Mult']

                    df_bt['RS'] = df_bt.apply(_rawscore_bt, axis=1).clip(lower=0)
                    tot_rs = df_bt['RS'].sum()
                    df_bt['PG'] = (df_bt['RS'] / tot_rs * 100) if tot_rs > 0 else (100.0 / len(df_bt))

                    # Loop UCITS 5/10/40 completo (Rulebook Sez. 7, 5 passi)
                    df_bt['PN'] = df_bt['PG'].clip(upper=10.0)
                    for _ucits_iter in range(20):
                        exc = df_bt['PG'].sum() - df_bt['PN'].sum()
                        if exc <= 1e-6:
                            break
                        mask_u = df_bt['PN'] < 10.0
                        if not mask_u.any():
                            break
                        tot_u = df_bt.loc[mask_u, 'PN'].sum()
                        if tot_u > 0:
                            df_bt.loc[mask_u, 'PN'] += df_bt.loc[mask_u, 'PN'] / tot_u * exc
                        df_bt['PN'] = df_bt['PN'].clip(upper=10.0)
                    # Rinormalizza
                    s_u = df_bt['PN'].sum()
                    if s_u > 0:
                        df_bt['PN'] = df_bt['PN'] / s_u * 100
                    # Aggregate cap 40%
                    for _agg_iter in range(20):
                        s5 = df_bt[df_bt['PN'] > 5.0]['PN'].sum()
                        if s5 <= 40.0:
                            break
                        exc_a = s5 - 40.0
                        n5 = (df_bt['PN'] > 5.0).sum()
                        if n5 == 0:
                            break
                        taglio = exc_a / n5
                        df_bt.loc[df_bt['PN'] > 5.0, 'PN'] = \
                            df_bt.loc[df_bt['PN'] > 5.0, 'PN'].apply(lambda x: max(x - taglio, 5.0))
                        sotto = df_bt[df_bt['PN'] <= 5.0]
                        if not sotto.empty:
                            df_bt.loc[sotto.index, 'PN'] += exc_a / len(sotto)
                        s_a2 = df_bt['PN'].sum()
                        if s_a2 > 0:
                            df_bt['PN'] = df_bt['PN'] / s_a2 * 100
                    # Rinormalizzazione finale
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

                    # Serie GGIV — con gestione Divisore D_t (Rulebook Sez. 9D)
                    # Il Divisore formale (D_t = Σ P×S×FF×W / I_t) richiede dati
                    # su azioni in circolazione (S) e free float (FF) giornalieri
                    # non disponibili su Yahoo Finance gratuitamente.
                    # Implementazione: (1+r).cumprod() × BASE_VAL equivale a
                    # mantenere D_t costante (nessuna corporate action), che è
                    # l'approssimazione corretta per backtest su un periodo fisso
                    # senza eventi societari noti. Il divisore viene ricalcolato
                    # al momento di ogni Kill Switch DSRM tramite la funzione
                    # di ribilanciamento (Rulebook Sez. 9D: D_t+1 = D_t × MC_post/MC_pre).
                    rend_bt = prezzi_bt.pct_change().dropna()
                    pesi_v  = np.array([df_bt.set_index('Ticker').loc[t, 'PN'] / 100
                                        for t in tickers_ok])
                    rend_g  = pd.Series(rend_bt[tickers_ok].values @ pesi_v,
                                        index=rend_bt.index)
                    idx_g   = (1 + rend_g).cumprod() * BASE_VAL
                    # Ricalcolo divisore per Kill Switch attivi (Sez. 9D)
                    # I titoli con FDSRM=0 hanno peso=0: il capitale
                    # redistribuito agli altri titoli è equivalente a
                    # D_t+1 = D_t × (1 - peso_eliminato/100)
                    kill_pesi = df_bt.loc[df_bt['FDSRM'] == 0.0, 'PN'].sum() / 100
                    if kill_pesi > 0:
                        # Il divisore è già incorporato nella rinormalizzazione dei pesi
                        # (i pesi degli altri titoli vengono scalati su di loro)
                        # Non è necessario correggere la serie — la ridistribuzione
                        # proporzionale del peso dei Kill Switch sugli altri titoli
                        # implementa implicitamente il ricalcolo del divisore.
                        pass
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
                    # La serie parte dalla data in cui tutti i ticker hanno dati disponibili
                    data_inizio_reale = idx_g.index[0].strftime('%b %Y')
                    ax1.set_title(
                        f'GGIV Index vs {BENCH_N} — {data_inizio_reale} → {datetime.now().strftime("%b %Y")} '
                        f'(dati disponibili per tutti i costituenti)',
                        color='#e8eaf0', fontsize=10, pad=10
                    )
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
                    data_serie_inizio = idx_g.index[0].strftime('%d/%m/%Y')
                    n_costi = len(tickers_ok)
                    sp_pdf.append(Paragraph(
                        f"NOTA METODOLOGICA — Il periodo visualizzato ({data_serie_inizio} → "
                        f"{datetime.now().strftime('%d/%m/%Y')}) riflette la data di inizio comune "
                        f"a tutti i {n_costi} costituenti con dati disponibili su Yahoo Finance. "
                        f"Ticker illiquidi o di quotazione recente possono ridurre l'orizzonte storico. "
                        f"Le metriche del presente Tear Sheet si riferiscono alla composizione reale "
                        f"del portafoglio GGIV con pesi DSRM + UCITS aggiornati, e differiscono dalla "
                        f"simulazione del White Paper v1.3 (portafoglio ipotetico 20 costituenti, "
                        f"periodo 2020-2024). Entrambe le analisi sono backtest ex-post e non "
                        f"costituiscono garanzia di rendimenti futuri. "
                        f"Proprietà intellettuale Francesco Giliberti — Rulebook v1.3 — "
                        f"{datetime.now().strftime('%d/%m/%Y')}.", DS))

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
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:8px;">
        SENSORE MACRO — CONTESTO DI MERCATO
    </div>""", unsafe_allow_html=True)

    @st.cache_data(ttl=300)
    def get_macro_data():
        """Scarica VIX, Treasury 10Y, DXY. Restituisce dizionario con valori e variazioni."""
        risultati = {}
        macro_tickers = {
            'VIX':          '^VIX',
            'TREASURY_10Y': '^TNX',
            'DXY':          'DX-Y.NYB',
        }
        for nome, ticker in macro_tickers.items():
            try:
                d = yf.Ticker(ticker).history(period="5d")
                if len(d) >= 2:
                    val  = float(d['Close'].iloc[-1])
                    prev = float(d['Close'].iloc[-2])
                    delta = val - prev
                    risultati[nome] = {
                        'valore':    val,
                        'delta':     delta,
                        'delta_pct': (delta / prev) * 100 if prev else 0,
                    }
            except Exception:
                pass
        return risultati

    @st.cache_data(ttl=300)
    def get_storico_vix(giorni=90):
        """Scarica storico VIX per il grafico di regime."""
        try:
            d = yf.Ticker('^VIX').history(period=f"{giorni}d")
            return d['Close'].dropna()
        except Exception:
            return None

    with st.spinner("Caricamento dati macro..."):
        macro = get_macro_data()

    # ── Calcola pesi portafoglio per Tier (usati nell'analisi sotto) ────────
    peso_t1 = df_aziende[df_aziende['Tier'] == 'Tier 1']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t2 = df_aziende[df_aziende['Tier'] == 'Tier 2']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_t3 = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    peso_tot = peso_t1 + peso_t2 + peso_t3
    # Normalizza se necessario (porta a 100)
    if peso_tot > 0:
        peso_t1_n = peso_t1 / peso_tot * 100
        peso_t2_n = peso_t2 / peso_tot * 100
        peso_t3_n = peso_t3 / peso_tot * 100
    else:
        peso_t1_n = peso_t2_n = peso_t3_n = 0

    if macro:
        # ── Riga metriche ───────────────────────────────────────────────────
        col_m1, col_m2, col_m3 = st.columns(3)

        # VIX
        if 'VIX' in macro:
            v = macro['VIX']
            vix_val = v['valore']
            if vix_val < 15:
                regime_vix = "MERCATO CALMO";        vix_color = "#00d4aa"
            elif vix_val < 25:
                regime_vix = "VOLATILITÀ NORMALE";   vix_color = "#c9a84c"
            elif vix_val < 35:
                regime_vix = "STRESS DI MERCATO";    vix_color = "#e05a5a"
            else:
                regime_vix = "PANICO — SHIELD CRITICO"; vix_color = "#ff2222"

            col_m1.metric("VIX — INDICE DELLA PAURA", f"{vix_val:.2f}",
                          f"{v['delta_pct']:+.2f}%")
            vix_pct = min(vix_val / 50, 1.0)
            col_m1.markdown(f"""
            <div style="margin-top:8px;">
                <div style="display:flex; justify-content:space-between;
                            font-size:10px; color:#7a8fa6; margin-bottom:4px;">
                    <span>CALMO&lt;15</span><span>NORMALE</span><span>STRESS&gt;25</span><span>PANICO&gt;35</span>
                </div>
                <div style="background:#1a2d45; border-radius:3px; height:8px; overflow:hidden;">
                    <div style="width:{vix_pct*100:.0f}%; background:{vix_color};
                                height:100%; border-radius:3px; transition:width 0.4s;"></div>
                </div>
                <div style="font-size:11px; color:{vix_color}; margin-top:5px;
                            font-family:'Courier New',monospace; font-weight:bold; letter-spacing:0.1em;">
                    {regime_vix}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            vix_val = 20.0; regime_vix = "N/D"; vix_color = "#7a8fa6"

        # Treasury 10Y
        if 'TREASURY_10Y' in macro:
            t = macro['TREASURY_10Y']
            tnx = t['valore']
            if tnx > 4.5:
                tnx_label = "⚠ TASSI ALTI — pressione su growth/Tier 1"; tnx_color = "#e05a5a"
            elif tnx > 3.5:
                tnx_label = "◆ TASSI MODERATI — contesto neutro";          tnx_color = "#c9a84c"
            else:
                tnx_label = "✓ TASSI BASSI — favorevole a tech/growth";    tnx_color = "#00d4aa"

            col_m2.metric("TREASURY USA 10Y", f"{tnx:.3f}%",
                          f"{t['delta_pct']:+.2f}%")
            col_m2.markdown(f"""
            <div style="margin-top:8px;">
                <div style="background:#1a2d45; border-radius:3px; height:8px; overflow:hidden;">
                    <div style="width:{min(tnx/6*100,100):.0f}%; background:{tnx_color};
                                height:100%; border-radius:3px;"></div>
                </div>
                <div style="font-size:11px; color:{tnx_color}; margin-top:5px;
                            font-family:'Courier New',monospace; letter-spacing:0.06em;">
                    {tnx_label}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            tnx = 4.0; tnx_color = "#c9a84c"; tnx_label = "N/D"

        # DXY
        if 'DXY' in macro:
            d = macro['DXY']
            dxy = d['valore']
            if dxy > 106:
                dxy_label = "⚠ DOLLARO FORTE — pressione su EM e commodities"; dxy_color = "#e05a5a"
            elif dxy > 100:
                dxy_label = "◆ DOLLARO NEUTRO — contesto equilibrato";           dxy_color = "#c9a84c"
            else:
                dxy_label = "✓ DOLLARO DEBOLE — favorevole a mercati internaz."; dxy_color = "#00d4aa"

            col_m3.metric("DXY — INDICE DOLLARO", f"{dxy:.2f}",
                          f"{d['delta_pct']:+.2f}%")
            col_m3.markdown(f"""
            <div style="margin-top:8px;">
                <div style="background:#1a2d45; border-radius:3px; height:8px; overflow:hidden;">
                    <div style="width:{min((dxy-85)/40*100,100):.0f}%; background:{dxy_color};
                                height:100%; border-radius:3px;"></div>
                </div>
                <div style="font-size:11px; color:{dxy_color}; margin-top:5px;
                            font-family:'Courier New',monospace; letter-spacing:0.06em;">
                    {dxy_label}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            dxy = 102.0; dxy_color = "#c9a84c"

        st.markdown("---")

        # ── BLOCCO CENTRALE: regime + portafoglio contestualizzato ──────────
        st.markdown("#### REGIME DI MERCATO — IMPATTO SUL PORTAFOGLIO GGIV")

        # Determina regime complessivo (combina VIX + tassi)
        if vix_val >= 35 or (vix_val >= 25 and tnx > 4.5):
            regime_label = "CRISI"
            regime_color = "#ff2222"
            regime_desc  = "Condizioni di mercato severe. Shield Tier 3 critico. Priorità: protezione capitale."
            azioni_richieste = [
                f"Verifica peso Tier 3 — attualmente {peso_t3_n:.1f}% (target ≥30%)",
                "Controlla DSRM: ticker in giallo/rosso vanno espulsi con priorità",
                "Evita nuovi ingressi in Tier 1 finché VIX > 35",
            ]
        elif vix_val >= 25 or tnx > 4.5:
            regime_label = "STRESS"
            regime_color = "#e05a5a"
            regime_desc  = "Volatilità elevata. Shield operativo ma da monitorare. Tassi alti penalizzano Tier 1."
            azioni_richieste = [
                f"Tier 3 a {peso_t3_n:.1f}% — {'✓ sufficiente' if peso_t3_n >= 25 else '⚠ sotto soglia, considera ribilanciamento'}",
                f"Tier 1 a {peso_t1_n:.1f}% — aziende pre-revenue più esposte al risk-off",
                "Monitora ADTV dei Tier 1 OTC/ASX — liquidità può ridursi in stress",
            ]
        elif vix_val < 15 and tnx < 3.5:
            regime_label = "OPPORTUNITÀ"
            regime_color = "#00d4aa"
            regime_desc  = "Condizioni ottimali per growth e Tier 1. Bassa volatilità, tassi contenuti."
            azioni_richieste = [
                "Valuta nuovi candidati Watchlist — finestra favorevole per ingressi",
                f"Tier 1 a {peso_t1_n:.1f}% — considera incremento se candidati con GES alto",
                "Aggiorna Rev_Grafene_Pct — in bull market i report sono più completi",
            ]
        else:
            regime_label = "NORMALE"
            regime_color = "#c9a84c"
            regime_desc  = "Volatilità nella norma. Monitoraggio standard. Nessuna azione urgente."
            azioni_richieste = [
                "Esegui il run settimanale del Radar Bot il lunedì",
                f"Distribuzione Tier: T1 {peso_t1_n:.1f}% / T2 {peso_t2_n:.1f}% / T3 {peso_t3_n:.1f}%",
                "Verifica scadenza prossimo ribilanciamento trimestrale",
            ]

        # Card regime
        st.markdown(f"""
        <div style="background:#0d1b2a; border:1px solid {regime_color}; border-radius:6px;
                    padding:16px 20px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
                <div style="font-size:22px; font-weight:bold; color:{regime_color};
                            font-family:'Courier New',monospace; letter-spacing:0.15em;">
                    ◉ REGIME: {regime_label}
                </div>
            </div>
            <div style="font-size:12px; color:#b0bec5; font-family:'Courier New',monospace;
                        line-height:1.7; margin-bottom:12px;">
                {regime_desc}
            </div>
            <div style="font-size:11px; color:#7a8fa6; font-family:'Courier New',monospace;">
                AZIONI SUGGERITE:
            </div>
            {''.join(f'<div style="font-size:11px; color:#e8eaf0; font-family:\'Courier New\',monospace; margin-top:4px; padding-left:10px;">→ {a}</div>' for a in azioni_richieste)}
        </div>
        """, unsafe_allow_html=True)

        # ── Gauge pesi Tier contestualizzati ────────────────────────────────
        col_g1, col_g2, col_g3 = st.columns(3)

        def render_gauge_tier(col, label, peso_n, color, soglia_min, soglia_ok, regime_color):
            """Barra peso Tier con semaforo contestuale al regime."""
            if peso_n >= soglia_ok:
                stato = "✓ OK"; stato_c = "#00d4aa"
            elif peso_n >= soglia_min:
                stato = "◆ WATCH"; stato_c = "#c9a84c"
            else:
                stato = "⚠ BASSO"; stato_c = "#e05a5a"
            col.markdown(f"""
            <div style="background:#0d1b2a; border:1px solid #1a2d45; border-radius:5px;
                        padding:12px 14px; margin-bottom:8px;">
                <div style="font-size:10px; color:#7a8fa6; font-family:'Courier New',monospace;
                            letter-spacing:0.08em; margin-bottom:6px;">{label}</div>
                <div style="font-size:24px; font-weight:bold; color:{color};
                            font-family:'Courier New',monospace;">{peso_n:.1f}%</div>
                <div style="background:#1a2d45; border-radius:3px; height:6px; margin:6px 0; overflow:hidden;">
                    <div style="width:{min(peso_n,100):.0f}%; background:{color};
                                height:100%; border-radius:3px;"></div>
                </div>
                <div style="font-size:10px; color:{stato_c}; font-family:'Courier New',monospace;">
                    {stato} (soglia: {soglia_ok:.0f}%)
                </div>
            </div>""", unsafe_allow_html=True)

        # Tier 3: con architettura intra-Tier, il Peso_Base DB viene rispettato (~40%)
        render_gauge_tier(col_g1, "TIER 1 — PURE PLAYERS (alpha)",          peso_t1_n, "#00d4aa", 20, 30, regime_color)
        render_gauge_tier(col_g2, "TIER 2 — SUPPLY CHAIN (infrastruttura)", peso_t2_n, "#c9a84c", 30, 35, regime_color)
        render_gauge_tier(col_g3, "TIER 3 — SHIELD (protezione)",
                          peso_t3_n,
                          "#e05a5a" if peso_t3_n < 25 else "#00d4aa",
                          25, 30, regime_color)

        # ── Grafico storico VIX 90 giorni ───────────────────────────────────
        st.markdown("---")
        st.markdown("#### STORICO VIX 90 GIORNI — REGIME DI VOLATILITÀ")
        with st.spinner("Caricamento storico VIX..."):
            storico_vix = get_storico_vix(90)

        if storico_vix is not None and len(storico_vix) > 5:
            fig_vix = go.Figure()
            # Aree di regime colorate
            date_vix = storico_vix.index
            x0, x1 = date_vix[0], date_vix[-1]
            fig_vix.add_hrect(y0=0,  y1=15, fillcolor="#00d4aa", opacity=0.06, line_width=0)
            fig_vix.add_hrect(y0=15, y1=25, fillcolor="#c9a84c", opacity=0.06, line_width=0)
            fig_vix.add_hrect(y0=25, y1=35, fillcolor="#e05a5a", opacity=0.08, line_width=0)
            fig_vix.add_hrect(y0=35, y1=80, fillcolor="#ff2222", opacity=0.08, line_width=0)
            # Linee soglia
            for y, label, col in [(15, "CALMO", "#00d4aa"), (25, "STRESS", "#e05a5a"), (35, "PANICO", "#ff2222")]:
                fig_vix.add_hline(y=y, line_dash="dot", line_color=col, line_width=1,
                                  annotation_text=label, annotation_position="left",
                                  annotation_font=dict(color=col, size=9, family="Courier New"))
            # Linea VIX
            fig_vix.add_trace(go.Scatter(
                x=date_vix, y=storico_vix.values,
                mode='lines', name='VIX',
                line=dict(color='#e8eaf0', width=1.5),
                fill='tozeroy', fillcolor='rgba(232,234,240,0.05)',
            ))
            # Punto corrente
            fig_vix.add_trace(go.Scatter(
                x=[date_vix[-1]], y=[storico_vix.iloc[-1]],
                mode='markers', name=f'Oggi: {storico_vix.iloc[-1]:.2f}',
                marker=dict(color=vix_color, size=10, symbol='circle'),
            ))
            fig_vix.update_layout(
                paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
                font=dict(color='#7a8fa6', family='Courier New', size=10),
                xaxis=dict(gridcolor='#1a2d45', showgrid=True),
                yaxis=dict(gridcolor='#1a2d45', showgrid=True, title='VIX'),
                height=220, margin=dict(t=10, b=30, l=50, r=10),
                showlegend=True,
                legend=dict(bgcolor='#0d1b2a', bordercolor='#1a2d45', font=dict(size=9)),
            )
            st.plotly_chart(fig_vix, use_container_width=True)
        else:
            st.caption("Storico VIX non disponibile — controlla la connessione.")

    else:
        st.warning("Impossibile caricare dati macro. Controlla la connessione.")

    st.markdown("---")

    # ---- SEZIONE B: MATRICE DI CORRELAZIONE ----
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:6px;">
        MATRICE DI CORRELAZIONE — DECORRELAZIONE TIER
    </div>""", unsafe_allow_html=True)
    st.caption("Rendimenti giornalieri su 90 giorni. I ticker OTC/ASX con storia insufficiente su Yahoo Finance vengono esclusi automaticamente con spiegazione.")

    @st.cache_data(ttl=3600)
    def calcola_correlazione(tickers: tuple):
        """
        Scarica 90gg di dati e calcola la matrice di correlazione dei rendimenti.
        Restituisce: (corr_matrix, rendimenti, dict_status_per_ticker)
        dict_status: { ticker: {'ok': bool, 'motivo': str, 'giorni': int} }
        """
        status = {t: {'ok': False, 'motivo': 'Non scaricato', 'giorni': 0} for t in tickers}
        try:
            raw = yf.download(
                list(tickers), period="90d",
                auto_adjust=True, progress=False,
                group_by="ticker",
            )
            if raw is None or raw.empty:
                return None, None, status

            # Estrae Close gestendo tutte le strutture di yfinance
            if isinstance(raw.columns, pd.MultiIndex):
                if 'Close' in raw.columns.get_level_values(0):
                    prezzi = raw['Close']
                elif 'Close' in raw.columns.get_level_values(1):
                    prezzi = raw.xs('Close', axis=1, level=1)
                else:
                    return None, None, status
            else:
                if 'Close' in raw.columns:
                    prezzi = raw[['Close']]
                    prezzi.columns = list(tickers)[:1]
                else:
                    return None, None, status

            # Analizza ogni ticker individualmente per il report di status
            for t in tickers:
                if t not in prezzi.columns:
                    status[t] = {'ok': False, 'motivo': 'Ticker non trovato su Yahoo Finance', 'giorni': 0}
                    continue
                col = prezzi[t].dropna()
                giorni = len(col)
                if giorni == 0:
                    status[t] = {'ok': False, 'motivo': 'Nessun dato disponibile (possibile delisting)', 'giorni': 0}
                elif giorni < 10:
                    status[t] = {'ok': False, 'motivo': f'Solo {giorni} giorni di storia (min 10)', 'giorni': giorni}
                elif giorni < 30:
                    status[t] = {'ok': True, 'motivo': f'Dati limitati ({giorni}gg) — correlazione meno affidabile', 'giorni': giorni}
                else:
                    status[t] = {'ok': True, 'motivo': f'{giorni} giorni disponibili', 'giorni': giorni}

            # Rimuovi ticker senza dati sufficienti (meno di 10 giorni)
            ticker_validi = [t for t in tickers if status[t]['giorni'] >= 10 and t in prezzi.columns]
            if len(ticker_validi) < 2:
                return None, None, status

            prezzi_clean = prezzi[ticker_validi].dropna(axis=1, how='all')
            rendimenti = prezzi_clean.pct_change().dropna(how='all')
            rendimenti = rendimenti.dropna(thresh=max(2, int(rendimenti.shape[1] * 0.5)))

            if rendimenti.shape[0] < 10:
                return None, None, status

            return rendimenti.corr(), rendimenti, status

        except Exception as e:
            return None, None, status

    if not df_aziende.empty and 'Ticker' in df_aziende.columns:
        tickers_portafoglio = tuple(df_aziende['Ticker'].dropna().unique())

        if len(tickers_portafoglio) >= 2:
            with st.spinner(f"Scaricando 90 giorni per {len(tickers_portafoglio)} ticker..."):
                corr_matrix, rendimenti, ticker_status = calcola_correlazione(tickers_portafoglio)

            # ── Report status per ticker ────────────────────────────────────
            ticker_ok    = [t for t in tickers_portafoglio if ticker_status[t]['ok']]
            ticker_fail  = [t for t in tickers_portafoglio if not ticker_status[t]['ok']]
            ticker_warn  = [t for t in ticker_ok if ticker_status[t]['giorni'] < 30]

            if ticker_fail or ticker_warn:
                with st.expander(f"ℹ️ Report dati — {len(ticker_ok)} ticker in matrice, {len(ticker_fail)} esclusi", expanded=len(ticker_fail) > 0):
                    ticker_to_nome_rep = dict(zip(df_aziende['Ticker'], df_aziende['Azienda']))
                    # Esclusi
                    if ticker_fail:
                        st.markdown("**❌ Esclusi dalla matrice — dati insufficienti:**")
                        for t in ticker_fail:
                            nome = ticker_to_nome_rep.get(t, t)
                            motivo = ticker_status[t]['motivo']
                            tier_t = df_aziende[df_aziende['Ticker'] == t]['Tier'].values
                            tier_str = tier_t[0] if len(tier_t) else "?"
                            st.markdown(f"""
                            <div style="background:#1a0a0a; border-left:3px solid #e05a5a;
                                        padding:6px 10px; margin:4px 0; border-radius:3px;
                                        font-family:'Courier New',monospace; font-size:11px;">
                                <span style="color:#e05a5a; font-weight:bold;">{t}</span>
                                <span style="color:#7a8fa6;"> ({nome} — {tier_str})</span><br>
                                <span style="color:#b0bec5;">→ {motivo}</span>
                            </div>""", unsafe_allow_html=True)
                    # Avvertimenti
                    if ticker_warn:
                        st.markdown("**⚠️ In matrice ma con storia limitata (&lt;30 giorni):**")
                        for t in ticker_warn:
                            nome = ticker_to_nome_rep.get(t, t)
                            st.markdown(f"""
                            <div style="background:#1a1400; border-left:3px solid #c9a84c;
                                        padding:6px 10px; margin:4px 0; border-radius:3px;
                                        font-family:'Courier New',monospace; font-size:11px;">
                                <span style="color:#c9a84c; font-weight:bold;">{t}</span>
                                <span style="color:#7a8fa6;"> — {nome}</span><br>
                                <span style="color:#b0bec5;">→ {ticker_status[t]['motivo']}</span>
                            </div>""", unsafe_allow_html=True)

            if corr_matrix is not None and not corr_matrix.empty:

                # Pulizia finale della matrice
                corr_clean = corr_matrix.dropna(how='all', axis=0).dropna(how='all', axis=1)
                corr_matrix = corr_clean

                # Sostituisce ticker con nomi azienda
                ticker_to_nome = dict(zip(df_aziende['Ticker'], df_aziende['Azienda']))
                corr_display = corr_matrix.copy()
                corr_display.columns = [ticker_to_nome.get(t, t) for t in corr_display.columns]
                corr_display.index   = [ticker_to_nome.get(t, t) for t in corr_display.index]

                # Etichette brevi (max 15 char) per leggibilità
                def short(s): return s[:14] + '…' if len(s) > 15 else s
                corr_display.columns = [short(c) for c in corr_display.columns]
                corr_display.index   = [short(c) for c in corr_display.index]

                fig_heatmap = go.Figure(go.Heatmap(
                    z=corr_display.values,
                    x=corr_display.columns.tolist(),
                    y=corr_display.index.tolist(),
                    colorscale=[
                        [0.0,  '#00d4aa'],
                        [0.5,  '#0d1b2a'],
                        [1.0,  '#e05a5a'],
                    ],
                    zmid=0, zmin=-1, zmax=1,
                    text=np.round(corr_display.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(size=9, color='#e8eaf0', family='Courier New'),
                    hovertemplate='%{y} / %{x}<br>Correlazione: %{z:.3f}<extra></extra>',
                    colorbar=dict(
                        tickcolor='#7a8fa6',
                        tickfont=dict(color='#7a8fa6', size=10),
                        title=dict(text='ρ', font=dict(color='#7a8fa6')),
                        bgcolor='#0d1b2a',
                    )
                ))
                n = len(corr_display)
                fig_heatmap.update_layout(
                    paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
                    font=dict(color='#e8eaf0', family='Courier New', size=9),
                    xaxis=dict(tickangle=-40, tickfont=dict(size=8), gridcolor='#1a2d45'),
                    yaxis=dict(tickfont=dict(size=8), gridcolor='#1a2d45'),
                    margin=dict(t=20, b=100, l=130, r=20),
                    height=max(380, n * 36),
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

                # ── Analisi decorrelazione Tier 3 ──────────────────────────
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
                                    if not np.isnan(rho):
                                        coppie_cross.append((
                                            ticker_to_nome.get(t3, t3),
                                            ticker_to_nome.get(t1, t1),
                                            rho
                                        ))

                        if coppie_cross:
                            valori_cross = [c[2] for c in coppie_cross]
                            media_cross  = np.mean(valori_cross)
                            if media_cross < 0.3:
                                st.success(f"SHIELD CONFERMATO — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Il Tier 3 è decorrelato e funziona da scudo.")
                            elif media_cross < 0.6:
                                st.warning(f"DECORRELAZIONE PARZIALE — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Verificare composizione Tier 3.")
                            else:
                                st.error(f"SHIELD DEBOLE — Correlazione media Tier 3 / Tier 1: {media_cross:.2f}. Tier 3 troppo correlato a Tier 1.")

                            # Tabella coppie peggiori (più correlate)
                            coppie_sorted = sorted(coppie_cross, key=lambda x: x[2], reverse=True)[:5]
                            st.caption("Top 5 coppie più correlate (T3/T1):")
                            for t3n, t1n, rho in coppie_sorted:
                                col_rho = "#e05a5a" if rho > 0.6 else "#c9a84c" if rho > 0.3 else "#00d4aa"
                                st.markdown(f"""
                                <div style="font-family:'Courier New',monospace; font-size:11px;
                                            padding:3px 0; color:#b0bec5;">
                                    <span style="color:{col_rho}; font-weight:bold;">{rho:+.2f}</span>
                                    &nbsp; {short(t3n)} ↔ {short(t1n)}
                                </div>""", unsafe_allow_html=True)
                        else:
                            st.info("DATI INSUFFICIENTI — Servono almeno 30 giorni di storia comune tra Tier 1 e Tier 3.")
            else:
                st.warning("Impossibile calcolare la matrice — nessun ticker ha dati sufficienti su Yahoo Finance.")
        else:
            st.info("Servono almeno 2 aziende nel portafoglio per calcolare la correlazione.")
    else:
        st.warning("Dati portafoglio non disponibili.")


# --- SCHEDA 5: RISCHIO & ORDINI ---
with tab_rischio:
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:12px;">
        GESTIONE RISCHIO & ORDINI
    </div>""", unsafe_allow_html=True)
    limite_rischio = st.slider("Soglia massima per posizione (%):", 5, 40, 15, step=1)

    peso_totale_shield = df_aziende[df_aziende['Tier'] == 'Tier 3']['Peso_Effettivo'].sum() if not df_aziende.empty else 0
    n_shield = int((df_aziende['Tier'] == 'Tier 3').sum()) if not df_aziende.empty else 0

    # Soglie Golden Shield:
    # - BLOCCO (<10%): emergenza reale, Shield quasi assente
    # - WARNING (10–25%): sotto target, probabile DB non aggiornato o DSRM attivi
    # - OK (≥25%): Shield operativo (il target DB è ~40%, ma UCITS e DSRM possono ridurlo)
    SHIELD_BLOCCO = 10.0   # blocco operatività — Shield assente (emergenza)
    SHIELD_WARN   = 25.0   # avviso — sotto target, verifica DB/DSRM
    SHIELD_OK     = 25.0

    shield_strutturale = n_shield > 0 and peso_totale_shield >= SHIELD_BLOCCO
    blocco_scudo = peso_totale_shield < SHIELD_BLOCCO

    if blocco_scudo:
        st.error(
            f"BLOCCO OPERATIVITÀ — Tier 3 al {peso_totale_shield:.1f}% "
            f"(minimo assoluto: {SHIELD_BLOCCO:.0f}%). Shield assente — operazioni sospese."
        )
    elif peso_totale_shield < SHIELD_WARN:
        st.warning(
            f"⚠ SHIELD SOTTO TARGET — Tier 3 al {peso_totale_shield:.1f}% "
            f"(target: ~30–40%). Possibile causa: MC o GES mancanti nel DB "
            f"(fallback Peso_Base attivo) oppure Kill Switch DSRM attivi. "
            f"Esegui il Vault Algorithm Update Tool per aggiornare i dati."
        )
    else:
        st.success(f"GOLDEN SHIELD ATTIVO — Tier 3 al {peso_totale_shield:.1f}% · {n_shield} costituenti")

    if not df_aziende.empty:
        for _, row in df_aziende[df_aziende['Peso_Effettivo'] > limite_rischio].iterrows():
            st.warning(f"PROFIT TAKER — {row['Azienda']}: {row['Peso_Effettivo']:.1f}% — Ridurre di {row['Peso_Effettivo'] - limite_rischio:.1f}%")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

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
            st.dataframe(ordini, use_container_width=True, hide_index=True)

# --- SCHEDA 6: BREVETTI & GES ---
with tab_brevetti:
    st.markdown("""
    <div style="font-family:'Courier New',monospace; font-size:11px; color:#7a8fa6;
                letter-spacing:0.1em; margin-bottom:12px;">
        SENSORE IP — BREVETTI & GES SCORE
    </div>""", unsafe_allow_html=True)
    if not df_aziende.empty:
        col_sel, col_rank = st.columns([1, 1])

        with col_sel:
            target = st.selectbox("Seleziona azienda:", df_aziende['Azienda'].tolist())
            row_t  = df_aziende[df_aziende['Azienda'] == target]

            if 'GES_Score' in df_aziende.columns and not row_t['GES_Score'].isna().all():
                ges_raw = row_t['GES_Score'].values[0]
                try:
                    ges_float = float(ges_raw) if ges_raw else 0.0
                except (ValueError, TypeError):
                    ges_float = 0.0
                # GES è in [0,1] — scala ×100 solo per display
                score = round(ges_float * 100, 1)
                label = "GES SCORE (calcolato)"
                # Soglie calibrate sul range GES reale:
                # Tier 1 max: (0.30×1.0 + 0.70×1.0)×1.5 = 1.50 → ×100 = 150 (teorico)
                # Tier 3 max: (0.70×1.0 + 0.30×1.0)×0.5 = 0.50 → ×100 = 50 (teorico)
                # Soglie pratiche basate su distribuzione reale portafoglio:
                stato  = "ECCELLENTE" if score >= 60 else "MODERATO" if score >= 25 else "BASSO"
                colore = "#00d4aa"    if score >= 60 else "#c9a84c"  if score >= 25 else "#e05a5a"
            else:
                score_val = row_t['Health_Score'].values if 'Health_Score' in row_t.columns else [0]
                score     = int(score_val[0]) if len(score_val) > 0 else 0
                ges_float = 0.0
                label     = "HEALTH SCORE (statico)"
                stato  = "ECCELLENTE" if score >= 80 else "MODERATO" if score >= 50 else "ALLERTA"
                colore = "#00d4aa"    if score >= 80 else "#c9a84c"  if score >= 50 else "#e05a5a"
            st.metric(label, f"{score}/100", stato)

            cb1, cb2, cb3 = st.columns(3)
            if 'Brevetti_Granted' in row_t.columns:
                try:
                    val_g = row_t['Brevetti_Granted'].values[0]
                    val_g = int(float(val_g)) if val_g not in (None, '', 'nan') and str(val_g) != 'nan' else 0
                except (ValueError, TypeError): val_g = 0
                cb1.metric("GRANTED", str(val_g), "USPTO")
            if 'Brevetti_Pending' in row_t.columns:
                try:
                    val_p = row_t['Brevetti_Pending'].values[0]
                    val_p = int(float(val_p)) if val_p not in (None, '', 'nan') and str(val_p) != 'nan' else 0
                except (ValueError, TypeError): val_p = 0
                cb2.metric("PENDING", str(val_p), "domande")
            if 'Tier' in row_t.columns:
                tier_az = row_t['Tier'].values[0]
                coeff   = {"Tier 1": "α=0.30 β=0.70", "Tier 2": "α=0.55 β=0.45", "Tier 3": "α=0.70 β=0.30"}
                cb3.metric("COEFF.", coeff.get(tier_az, "—"), tier_az)

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                gauge=dict(
                    axis=dict(range=[0, 150], tickcolor="#7a8fa6",
                              tickfont=dict(color="#7a8fa6", size=10),
                              tickvals=[0, 25, 60, 100, 150],
                              ticktext=["0","25","60","100","150"]),
                    bar=dict(color=colore), bgcolor="#0d1b2a", bordercolor="#1a2d45",
                    steps=[
                        dict(range=[0,   25], color="#1a0e0e"),  # BASSO
                        dict(range=[25,  60], color="#1a1a0e"),  # MODERATO
                        dict(range=[60, 150], color="#0e1a16"),  # ECCELLENTE
                    ],
                    threshold=dict(line=dict(color=colore, width=2), thickness=0.75, value=score)
                ),
                number=dict(font=dict(color="#e8eaf0", family="Courier New"), suffix=""),
                title=dict(text=f"GES ×100 · raw={ges_float:.4f}",
                           font=dict(color="#7a8fa6", size=9, family="Courier New"))
            ))
            fig_gauge.update_layout(
                paper_bgcolor='#0d1b2a', font=dict(color='#e8eaf0', family='Courier New'),
                height=260, margin=dict(t=20, b=10, l=30, r=30),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_rank:
            st.markdown("""
            <div style="font-family:'Courier New',monospace; font-size:10px; color:#7a8fa6;
                        letter-spacing:0.08em; margin-bottom:10px;">
                RANKING GES — TOP AZIENDE PER ESPOSIZIONE
            </div>""", unsafe_allow_html=True)

            if 'GES_Score' in df_aziende.columns:
                df_ges = df_aziende[['Azienda', 'Ticker', 'Tier', 'GES_Score']].copy()
                df_ges['GES_Score'] = pd.to_numeric(df_ges['GES_Score'], errors='coerce').fillna(0)
                df_ges['GES_100'] = (df_ges['GES_Score'] * 100).round(1)
                df_ges = df_ges.sort_values('GES_100', ascending=False).head(10)

                tier_colors_r = {'Tier 1': '#e05a5a', 'Tier 2': '#378ADD', 'Tier 3': '#00d4aa'}
                for rank, (_, row_r) in enumerate(df_ges.iterrows(), 1):
                    col_t = tier_colors_r.get(row_r['Tier'], '#7a8fa6')
                    bar_w = min(int(row_r['GES_100']), 100)
                    is_target = row_r['Azienda'] == target
                    bg = "#1a2d45" if is_target else "#0a1628"
                    st.markdown(f"""
                    <div style="background:{bg}; border-radius:4px; padding:7px 10px;
                                margin-bottom:5px; border:1px solid {'#c9a84c' if is_target else '#1a2d45'};">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:center; margin-bottom:4px;">
                            <div style="font-family:'Courier New',monospace; font-size:10px;">
                                <span style="color:#7a8fa6;">{rank:02d}.</span>
                                <span style="color:#e8eaf0; margin-left:4px;">{row_r['Ticker']}</span>
                                <span style="color:#7a8fa6; margin-left:6px; font-size:9px;">{row_r['Azienda'][:18]}</span>
                            </div>
                            <div style="font-size:11px; font-weight:bold; color:{col_t};
                                        font-family:'Courier New',monospace;">
                                {row_r['GES_100']:.1f}
                            </div>
                        </div>
                        <div style="background:#1a2d45; border-radius:2px; height:3px; overflow:hidden;">
                            <div style="width:{bar_w}%; background:{col_t}; height:100%; border-radius:2px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("GES Score non disponibile. Esegui il Radar Bot per calcolarlo.")
    else:
        st.info("Dati non disponibili.")
