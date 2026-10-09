import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- SIDOKONFIGURATION & STYLING ---
st.set_page_config(
    page_title="GridPulse ⚡ Autonomt Virtuellt Kraftverk",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS för modern tech-look
st.markdown("""
<style>
    .main-title {
        font-size: 3rem !important;
        font-weight: 800;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.4rem;
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .kris-flash {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ef5350;
        color: #c62828;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- APPENS TITEL & INTRO ---
st.markdown('<div class="main-title">GridPulse ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Tjäna pengar när din elbil sover – live-simulering av det digitala megabatteriet</div>', unsafe_allow_html=True)

st.markdown("""
### ⚖️ Gungbrädan (Elnätets balans)
Välkommen till din första fungerande prototyp! Den här appen simulerar hur **GridPulse** spionerar på elnätet varje sekund. 
När nätet hamnar i obalans (frekvensen avviker från **50.00 Hz**) aktiveras vårt virtuella kraftverk helt autonomt.
""")

# --- SIDOMENY / KONTROLLPANEL ---
st.sidebar.header("⚙️ Inställningar för ditt superbatteri")
antal_bilar = st.sidebar.slider("Antal anslutna elbilar i nätverket", min_value=10, max_value=10000, value=1000, step=10)
andel_aktiva = st.sidebar.slider("Andel bilar tillgängliga just nu (%)", min_value=10, max_value=100, value=85)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Affärsmodell (25/75-split):**
* 💸 **Bilägarna får:** 75% av intäkterna
* ⚡ **GridPulse tar:** 25% i plattformsavgift
""")

# --- DATAGENERERING (LIVE-KÄNSLA) ---
np.random.seed(42)
peak_timmar = [7, 8, 9, 17, 18, 19]

# Simulera nätfrekvens (ska ligga runt 50Hz, men dippa vid peak-timmar)
frekvenser = []
peak_timmar = [7, 8, 9, 17, 18, 19] # Fixat: Tider då folk startar apparater och laddar bilar
for hour in range(24):
    if hour in peak_timmar:
        freq = np.random.uniform(49.82, 49.92)
    else:
        freq = np.random.uniform(49.95, 50.05)
    frekvenser.append(freq)

df = pd.DataFrame({'Tid': tidsstämplar, 'Frekvens (Hz)': frekvenser})

# Beräkna kapacitet och ekonomi baserat på användarens slider-val
total_effekt_kw = antal_bilar * (andel_aktiva / 100.0) * 11
total_effekt_mw = total_effekt_kw / 1000.0

# Trygg beredskapsersättning (snitt 60 öre per timme per bil)
beredskap_per_timme = total_effekt_kw * 0.60
total_beredskap_dygn = beredskap_per_timme * 24

# Kris-bonusar (Antal timmar där frekvensen dök under 49.92 Hz)
kris_timmar = df[df['Frekvens (Hz)'] < 49.92].shape[0]
kris_intäkt_dygn = kris_timmar * (total_effekt_kw * 15.0 * (5/60)) # 15 kr/kWh under 5 minuters utryckning

total_intäkt_dygn = total_beredskap_dygn + kris_intäkt_dygn
bilagare_del = total_intäkt_dygn * 0.75
gridpulse_del = total_intäkt_dygn * 0.25

# --- METRICS-SEKTION (DASHBOARD) ---
st.markdown("### 📊 Ekonomisk översikt för detta dygn")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <h4>⚡ Virtuell Kapacitet</h4>
        <p style="font-size: 1.8rem; font-weight: bold; color: #1E88E5;">{total_effekt_mw:.2f} MW</p>
        <p style="color: #666; font-size: 0.9rem;">Motsvarar {int(antal_bilar * (andel_aktiva/100))} aktiva bilar på uppfarten.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <h4>🎉 Totalt utbetalat till bilägare</h4>
        <p style="font-size: 1.8rem; font-weight: bold; color: #2E7D32;">{bilagare_del:,.0f} kr</p>
        <p style="color: #666; font-size: 0.9rem;">Snitt per bil: {bilagare_del/(antal_bilar*(andel_aktiva/100)):,.0f} kr / dygn</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <h4>💸 Vår plattformsavgift (25%)</h4>
        <p style="font-size: 1.8rem; font-weight: bold; color: #EF6C00;">{gridpulse_del:,.0f} kr</p>
        <p style="color: #666; font-size: 0.9rem;">Ren mjukvaruvinst för GridPulse på 24 timmar.</p>
    </div>
    """, unsafe_allow_html=True)

# --- REALTIDSVARNING OM DET ÄR KRIS ---
st.markdown("---")
senaste_frekvens = frekvenser[-1]
if senaste_frekvens < 49.92:
    st.markdown(f'<div class="kris-flash">🚨 AKUT OBALANS DETEKTERAD: {senaste_frekvens:.2f} Hz! Autopiloten aktiverad. Ström matas ut till elnätet från bilarna just nu!</div>', unsafe_allow_html=True)
else:
    st.markdown('✅ **Status för elnätet:** Stabilt (50.01 Hz). Bilarna ligger i viloläge och samlar in timlön i beredskap.')

# --- GRAF ÖVER DYGNETS SVÄNGNINGAR ---
st.markdown("### 📈 Elnätets puls under dygnet (Frekvenskurva)")
st.line_chart(df.set_index('Tid'))

st.markdown("""
ℹ️ *Grafen visar hur nätets stabilitet (Hz) går upp och ner. Varje gång linjen sjunker djupt, skjuter GridPulse-appen automatiskt till ström från dina användares bilar och samlar in chock-ersättningar.*
""")
