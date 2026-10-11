import streamlit as st
import pandas as pd
import random

# 1. Konfigurera instrumentpanelens layout
st.set_page_config(
    page_title="GridPulse - Admin Dashboard V1G",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ GridPulse - Admin Dashboard (V1G MVP)")
st.subheader("Kontrollpanel för det digitala megabatteriet (Virtual Power Plant)")
st.markdown("---")

# 2. Initiera tillstånd (Session State) så att simulatorn minns data mellan klick
if 'simulated_cars' not in st.session_state:
    car_models = ["Tesla Model 3", "Volvo EX90", "VW ID.4", "Polestar 3", "Kia EV6", "BMW i4"]
    cars_data = []
    
    # Skapa 10 unika simulerade testbilar
    for i in range(1, 11):
        model = random.choice(car_models)
        soc = random.randint(25, 85)        # Batteriprocent
        is_plugged = random.choice([True, True, True, False]) # 75% chans att sladden är i
        is_home = random.choice([True, True, True, False])    # 75% chans att bilen är hemma
        limit = 80                           # Ägarens trygghetsgräns
        
        # GridPulse Regleringslogik: Bilen måste ladda, vara hemma, och ha kapacitet kvar till gränsen
        is_charging = is_plugged and soc < limit
        is_eligible = is_plugged and is_home and is_charging
        charge_power = round(random.uniform(3.7, 11.0), 1) if is_charging else 0.0
        
        cars_data.append({
            "Bil-ID": f"GP-{1000 + i}",
            "Modell": model,
            "Batteri (SoC)": f"{soc}%",
            "Trygghetsgräns": f"{limit}%",
            "Inkopplad": "✅" if is_plugged else "❌",
            "Hemma (GPS)": "✅" if is_home else "❌",
            "Laddar nu": "✅" if is_charging else "❌",
            "Reglerbar (V1G)": "Aktiv" if is_eligible else "Ej tillgänglig",
            "Nuvarande Effekt (kW)": charge_power,
            "_eligible_bool": is_eligible
        })
    
    st.session_state['simulated_cars'] = pd.DataFrame(cars_data)
    st.session_state['balance_status'] = "Normal (50.00 Hz)"
    st.session_state['total_profit'] = 0.0
    st.session_state['user_payout'] = 0.0

# Hämta data från sessionen
df = st.session_state['simulated_cars'].copy()
eligible_mask = df["_eligible_bool"] == True
total_cars = len(df)
active_vpp_cars = df[eligible_mask].shape[0]
total_kw_available = round(df[eligible_mask]["Nuvarande Effekt (kW)"].sum(), 1)

# 3. Översiktskort (KPI-metrics)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Totalt anslutna bilar", f"{total_cars} st")
with col2:
    st.metric("Aktiva V1G-reserver just nu", f"{active_vpp_cars} st")
with col3:
    st.metric("Tillgänglig Flex-effekt", f"{total_kw_available} kW")
with col4:
    status_emoji = "🟢" if st.session_state['balance_status'] == "Normal (50.00 Hz)" else "🔴"
    st.metric("Elnätets Status", f"{status_emoji} {st.session_state['balance_status']}")

st.markdown("---")

# 4. Sidomeny (Sidebar) med interaktiva simulatorknappar
st.sidebar.header("🕹️ Simulator-kontroller")
st.sidebar.write("Använd knapparna för att testa hur systemets AI och ekonomi reagerar vid en nätkrasch.")

if st.sidebar.button("🚨 Simulera Nätkrasch (Aktivera mFRR/aFRR)", type="primary"):
    st.session_state['balance_status'] = "OBALANS (49.85 Hz)"
    
    # Priskalkylator vid kris (t.ex. 15 kr per kWh under en simulerad 15-minutersperiod)
    kris_pris_per_kwh = 15.0
    genererad_intakt = round(total_kw_available * 0.25 * kris_pris_per_kwh, 2)
    
    # Utför 25/75 vinstdelning
    st.session_state['total_profit'] += round(genererad_intakt * 0.25, 2)
    st.session_state['user_payout'] += round(genererad_intakt * 0.75, 2)
    st.rerun()

if st.sidebar.button("🔄 Återställ Elnätet till Normalläge"):
    st.session_state['balance_status'] = "Normal (50.00 Hz)"
    st.rerun()

# 5. Finansiell översikt (Visar ackumulerade pengar live)
st.subheader("💰 Realiserad Ekonomi (25/75 Split från Stödtjänster)")
col_fin1, col_fin2 = st.columns(2)
with col_fin1:
    st.info(f"**GridPulse Intäkt (25%):** {st.session_state['total_profit']:.2f} SEK")
with col_fin2:
    st.success(f"**Utbetalning till dina Bilägare (75%):** {st.session_state['user_payout']:.2f} SEK")

st.markdown("---")

# 6. Flottans status och visualisering av API-anrop
st.subheader("🚗 Fordonsflottans Live-status (Realtidsdata)")

display_df = df.drop(columns=["_eligible_bool"])

if st.session_state['balance_status'] != "Normal (50.00 Hz)":
    # Om nätet har kraschat: Visa visuellt att laddningen har stängts av (V1G i praktiken)
    df.loc[eligible_mask, "Nuvarande Effekt (kW)"] = 0.0
    df.loc[eligible_mask, "Laddar nu"] = "⏸️ Pausad"
    
    st.warning("⚠️ **GridPulse AI har upptäckt obalans! Smart-paussignaler har skickats via molnet till alla aktiva fordon.**")
    st.dataframe(df.drop(columns=["_eligible_bool"]), use_container_width=True)
    
    # Tekniskt underlag till IQX för att visa hur backend-anropen förväntas loggas
    st.subheader("💻 API-Logg (Underlag för IQX backend-arkitektur)")
    st.code(f"""
[LOGG] Frekvensavvikelse upptäckt på elnätet. Aktiverar mFRR-reglering.
[LOGG] Anropar Enode/Smartcar API: POST /v1/vehicles/bulk/charge-control -> {{"action": "PAUSE"}}
[LOGG] API-Svar: 200 OK. {active_vpp_cars} fordon svarade och har tillfälligt pausat laddningen.
[LOGG] Totalt avlastad effekt: {total_kw_available} kW levererat till aggregatorn.
    """, language="bash")
else:
    st.dataframe(display_df, use_container_width=True)
