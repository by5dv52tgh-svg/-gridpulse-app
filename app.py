import streamlit as st
import pandas as pd
import random
import datetime

# 1. Konfigurera instrumentpanelen
st.set_page_config(
    page_title="GridPulse - Global VPP Control Center",
    page_icon="⚡",
    layout="wide"
)

# Initiera ackumulerad ekonomi i bakgrunden så att den minns klick
if 'total_profit' not in st.session_state:
    st.session_state['total_profit'] = 0.0
    st.session_state['user_payout'] = 0.0
    st.session_state['aggregator_payout'] = 0.0
    st.session_state['co2_saved'] = 0.0
    st.session_state['balance_status'] = "Normal (50.00 Hz)"

st.title("⚡ GridPulse - Global VPP Control Center")
st.subheader("Fas 1 (2026): V1G Smart-Pausning via Aggregator")
st.markdown("---")

# 2. Skapa flikar: En för affärsdemo och en för IQX-utvecklarna
tab1, tab2 = st.tabs(["📊 Live VPP Simulator", "💻 IQX Technical Blueprint"])

with tab1:
    st.subheader("Simulera och skala ditt virtuella megabatteri")
    
    # Sidomeny för kontroller och skalbarhet
    st.sidebar.header("🕹️ Skalbarhetskontroller")
    st.sidebar.write("Justera storleken på ditt nätverk för att se hur ekonomin och miljönyttan skalar live.")
    
    # Skjutreglage för att simulera upp till 50 000 bilar
    simulated_fleet_size = st.sidebar.slider("Välj antal registrerade elbilar i appen:", 10, 50000, 1000, step=10)
    
    # --- REALISTISK FILTRERINGSLOGIK (DIN ANALYS) ---
    # 1. Hur många är inkopplade hemma just nu en vanlig kväll? (Ca 55%)
    plugged_in_cars = int(simulated_fleet_size * 0.55)
    
    # 2. Hur många av dessa är under sin trygghetsgräns (t.ex. 60%) och laddar akut? 
    # Dessa blockeras av systemet och kan EJ pausas. (Ca 30% av de inkopplade)
    akut_laddande_cars = int(plugged_in_cars * 0.30)
    
    # 3. Hur många är redan fulladdade (100%)? De drar ingen el och kan EJ pausas. (Ca 40% av de inkopplade)
    fulladdade_cars = int(plugged_in_cars * 0.40)
    
    # 4. Det perfekta reglerbara fönstret: Bilar som är MELLAN sin trygghetsgräns (t.ex. 60%) och 100%.
    # Endast dessa bilar är aktiva V1G-reserver som kan pausas! (Resterande 30% av de inkopplade)
    active_vpp_cars = int(plugged_in_cars * 0.30)
    
    # Genomsnittlig laddeffekt per bil i det reglerbara fönstret (Blandat 3.7kW och 11kW ger ca 7.4 kW snitt)
    avg_kw_per_car = 7.4
    total_kw_available = round(active_vpp_cars * avg_kw_per_car, 1)
    total_mw_available = round(total_kw_available / 1000, 2)
    
    # Knappar för elnätskrasch
    st.sidebar.markdown("---")
    st.sidebar.subheader("Elnätshändelse (mFRR/aFRR)")
    
    if st.sidebar.button("🚨 Aktivera Smart-Pausning (Nätkrasch)", type="primary"):
        st.session_state['balance_status'] = "OBALANS (49.85 Hz)"
        
        # Ersättning 2026: Snittpris på 300 kr per MW/timme under en simulerad 15-minutersperiod (0.25 timmar)
        mw_price_per_hour = 300.0
        total_payout_from_state = round(total_mw_available * 0.25 * mw_price_per_hour, 2)
        
        # Sätt ett minsta golv för demovisning om man bara testar med 10 bilar
        if total_payout_from_state < 50.0:
            total_payout_from_state = 100.0
            
        # 1. Mellanhanden (Aggregatorn) tar 10%
        agg_share = round(total_payout_from_state * 0.10, 2)
        remaining_pool = total_payout_from_state - agg_share
        
        # 2. GridPulse tar 25% av det som är kvar, Användarna får 75%
        st.session_state['aggregator_payout'] += agg_share
        st.session_state['total_profit'] += round(remaining_pool * 0.25, 2)
        st.session_state['user_payout'] += round(remaining_pool * 0.75, 2)
        
        # Miljöberäkning: Ett oljekraftverk släpper ut ca 0.8 kg CO2 per kWh.
        st.session_state['co2_saved'] += round((total_kw_available * 0.25) * 0.8 / 1000, 2)
        st.rerun()

    if st.sidebar.button("🔄 Återställ Elnätet till Normalläge"):
        st.session_state['balance_status'] = "Normal (50.00 Hz)"
        st.rerun()

    # KPI-Rutor överst på sidan (Här syns din exakta logik live)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registrerade bilar i appen", f"{simulated_fleet_size:,} st".replace(",", " "))
    with col2:
        st.metric("Reglerbara V1G-bilar (Mellan gräns & 100%)", f"{active_vpp_cars:,} st".replace(",", " "))
    with col3:
        st.metric("Faktisk tillgänglig Flex-effekt", f"{total_mw_available} MW")
    with col4:
        status_emoji = "🟢" if st.session_state['balance_status'] == "Normal (50.00 Hz)" else "🔴"
        st.metric("Elnätets Frekvens", f"{status_emoji} {st.session_state['balance_status']}")

    # En visuell förklaring för investerare baserad på din analys
    st.info(f"📊 **Statistisk nedbrytning av din flotta just nu:** Av {simulated_fleet_size:,} bilar är {plugged_in_cars:,} st inkopplade på uppfarten. **{akut_laddande_cars:,} st** blockeras eftersom de är under sin trygghetsgräns, och **{fulladdade_cars:,} st** är redan fulladdade. Det ger oss **{active_vpp_cars:,} st aktiva bilar** som kan pausas live!".replace(",", " "))

    st.markdown("---")

    # Finansiell översikt och Miljönytta
    st.subheader("💰 Realiserad Ekonomi & Miljönytta (Ackumulerat)")
    col_fin1, col_fin2, col_fin3 = st.columns(3)
    with col_fin1:
        st.info(f"💼 **GridPulse Plattformsavgift (25%):** {st.session_state['total_profit']:,.2f} SEK".replace(",", " "))
    with col_fin2:
        st.success(f"👥 **Utbetalt till Bilägare (75%):** {st.session_state['user_payout']:,.2f} SEK".replace(",", " "))
    with col_fin3:
        st.warning(f"🌱 **Inbesparade CO2-utsläpp:** {st.session_state['co2_saved']:,} ton".replace(",", " "))
        
    st.caption(f"Notera: Aggregatorns (mellanhandens) 10% andel har dragits av från kalkylen ({st.session_state['aggregator_payout']:,.2f} SEK totalt).".replace(",", " "))

    st.markdown("---")

    # Live-utsnitt från databasen som visar de olika unika scenarierna
    st.subheader("🚗 Live-scenarier från databasen (Exempelvy)")
    
    sample_cars = [
        {"vehicle_id": "GP-1001", "brand": "Tesla Model 3", "current_soc": "45%", "safety_limit_soc": "60%", "Status": "⚡ Laddar akut", "Reglerbar (V1G)": "❌ Låst (Under trygghetsgräns)"},
        {"vehicle_id": "GP-1002", "brand": "Volvo EX90", "current_soc": "75%", "safety_limit_soc": "60%", "Status": "⏸️ Pausad via API" if st.session_state['balance_status'] != "Normal (50.00 Hz)" else "⚡ Laddar flexibelt", "Reglerbar (V1G)": "✅ Aktiv"},
        {"vehicle_id": "GP-1003", "brand": "VW ID.4", "current_soc": "100%", "safety_limit_soc": "60%", "Status": "🔋 Fulladdad", "Reglerbar (V1G)": "❌ Ej tillgänglig (Klar)"},
        {"vehicle_id": "GP-1004", "brand": "Polestar 3", "current_soc": "85%", "safety_limit_soc": "70%", "Status": "⏸️ Pausad via API" if st.session_state['balance_status'] != "Normal (50.00 Hz)" else "⚡ Laddar flexibelt", "Reglerbar (V1G)": "✅ Aktiv"},
        {"vehicle_id": "GP-1005", "brand": "BMW i4", "current_soc": "30%", "safety_limit_soc": "80%", "Status": "⚡ Laddar akut", "Reglerbar (V1G)": "❌ Låst (Under trygghetsgräns)"}
    ]
    st.dataframe(pd.DataFrame(sample_cars), use_container_width=True)

with tab2:
    st.subheader("💻 IQX Technical Blueprint & Database Schema")
    st.markdown("Detta underlag visar arkitekturen för backend-teamet på IQX.")
    
    st.info("💡 **Arkitektonisk strategi:** Vi använder mFRR/aFRR-marknaderna där svarstiden tillåts vara upp till 5-15 minuter. Detta eliminerar problemen med biltillverkarnas moln-latens (som ofta ligger på 10-30 sekunder).")
    
    st.subheader("Databas-tabeller (PostgreSQL / Relationell struktur)")
    
    st.markdown("**1. Tabell: `users` (Kundregister)**")
    st.code("""
    user_id       UUID PRIMARY KEY          # Unikt ID för bilägaren
    first_name    VARCHAR(50) NOT NULL
    last_name     VARCHAR(50) NOT NULL
    email         VARCHAR(100) UNIQUE       # Autentisering
    iban_account  VARCHAR(34) NOT NULL      # För 75%-utbetalningen
    """, language="sql")

    st.markdown("**2. Tabell: `vehicles` (Live IoT-status via Enode/Smartcar)**")
    st.code("""
    vehicle_id          UUID PRIMARY KEY
    user_id             UUID REFERENCES users(user_id)
    brand               VARCHAR(30) NOT NULL
    api_access_token    TEXT NOT NULL            # Krypterad OAuth-nyckel till bilens moln
    current_soc         INT NOT NULL             # Aktuell batteriprocent (0-100)
    safety_limit_soc    INT DEFAULT 60           # Användarens trygghetsgräns
    is_plugged_in       BOOLEAN DEFAULT FALSE    # Är laddsladden i?
    is_at_home_gps      BOOLEAN DEFAULT FALSE    # GPS-verifiering (fuskspärr)
    el_area             VARCHAR(5) NOT NULL      # SE1, SE2, SE3 eller SE4
    """, language="sql")

    st.markdown("**3. Tabell: `flex_transactions` (Avräkningslogg för 25/75 split)**")
    st.code("""
    transaction_id        UUID PRIMARY KEY
    vehicle_id            UUID REFERENCES vehicles(vehicle_id)
    shedded_power_kw      NUMERIC(4,1)             # Strypt effekt under kraschen
    total_grid_payout     NUMERIC(8,2)             # Pengar erhållna från staten/aggregatorn
    aggregator_share_sek  NUMERIC(8,2)             # Beräknas: total * 0.10
    gridpulse_share_sek   NUMERIC(8,2)             # Beräknas: (total - aggregator_share) * 0.25
    user_share_sek        NUMERIC(8,2)             # Beräknas: (total - aggregator_share) * 0.75
    timestamp             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """, language="sql")
