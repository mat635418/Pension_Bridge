import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="PensionBridge Win-Win", layout="wide")

# --- FUNZIONI DI UTILITÀ (SIMULAZIONE SEMPLIFICATA) ---
def calcola_data_pensione(eta_attuale, anni_contributi, sesso):
    """
    Stima data pensione basata su regole attuali semplificate (2025).
    """
    oggi = date.today()
    # Regola Vecchiaia: 67 anni
    anni_mancanti_vecchiaia = 67 - eta_attuale
    data_vecchiaia = oggi.replace(year=oggi.year + int(anni_mancanti_vecchiaia))
    
    # Regola Anticipata (42y 10m Uomini, 41y 10m Donne)
    soglia_anni = 42 if sesso == 'Uomo' else 41
    mesi_extra = 10
    
    anni_contributivi_mancanti = soglia_anni - anni_contributi
    # Convertiamo tutto in mesi per semplicità
    mesi_totali_mancanti = (anni_contributivi_mancanti * 12) + mesi_extra
    
    if mesi_totali_mancanti < 0:
        mesi_totali_mancanti = 0
        
    data_anticipata = today_plus_months(oggi, int(mesi_totali_mancanti))
    
    # Ritorna la data più vicina tra le due opzioni
    return min(data_vecchiaia, data_anticipata), data_vecchiaia, data_anticipata

def today_plus_months(current_date, months_to_add):
    new_month = current_date.month - 1 + months_to_add
    year = current_date.year + new_month // 12
    month = new_month % 12 + 1
    day = min(current_date.day, [31,
        29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28,
        31,30,31,30,31,31,30,31,30,31][month-1])
    return date(year, month, day)

def stima_pensione_netta(ral, anni_contributi):
    """
    Stima MOLTO semplificata del tasso di sostituzione.
    In un'app reale, qui andrebbe il calcolo contributivo/retributivo.
    Ipotesi: ~70% dell'ultimo netto per carriere lunghe.
    """
    netto_mensile_stimato = (ral * 0.65) / 13 # Stima tassazione e 13 mensilità
    # Fattore correttivo basato sugli anni (più anni = più pensione)
    fattore_anni = min(anni_contributi / 40.0, 1.1) 
    pensione = netto_mensile_stimato * 0.75 * fattore_anni # Tasso sostituzione 75% base
    return pensione

# --- INTERFACCIA UTENTE ---

st.title("🤝 PensionBridge: Analisi e Negoziazione Uscita")
st.markdown("""
Questo strumento aiuta a trovare il punto di equilibrio tra **l'interesse del lavoratore** (pensione + tempo libero) 
e **l'interesse dell'azienda** (rinnovamento forza lavoro + incentivi).
""")

# --- SIDEBAR: INPUT DATI ---
st.sidebar.header("1. Dati Lavoratore")

sesso = st.sidebar.selectbox("Sesso", ["Uomo", "Donna"])
eta = st.sidebar.number_input("Età Anagrafica", 50, 70, 62)
anni_contributi = st.sidebar.number_input("Anni di Contributi maturati", 20, 50, 38)
ral = st.sidebar.number_input("RAL Attuale (€)", 20000, 200000, 45000, step=1000)
costo_azienda_annuo = ral * 1.35 # Stima costo azienda (INPS + TFR)

st.sidebar.markdown("---")
st.sidebar.header("2. Dati Aziendali")
incentivo_proposto = st.sidebar.number_input("Incentivo all'esodo proposto (Lordo)", 0, 200000, 30000, step=5000)

# --- CALCOLI CORE ---
data_target, data_vecchiaia, data_anticipata = calcola_data_pensione(eta, anni_contributi, sesso)
pensione_stimata = stima_pensione_netta(ral, anni_contributi)
stipendio_netto_mensile = (ral * 0.65) / 13

# --- TABELLONE PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["📊 Analisi Pensionistica", "⚖️ Negoziazione (Win-Win)", "⚙️ Strategia Temporale"])

with tab1:
    st.header("Quando puoi andare in pensione?")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Data Prima Uscita Utile", data_target.strftime("%d/%m/%Y"))
    col2.metric("Pensione Netta Stimata", f"€ {pensione_stimata:,.2f} / mese")
    col3.metric("Ultimo Stipendio Netto", f"€ {stipendio_netto_mensile:,.2f} / mese")
    
    st.info(f"""
    **Dettaglio Normativo:**
    - Per la **Pensione di Vecchiaia** (67 anni) ti mancano ancora {(data_vecchiaia - date.today()).days // 365} anni.
    - Per la **Pensione Anticipata** ti mancano ancora {(data_anticipata - date.today()).days // 365} anni.
    
    *Nota: Questa è una simulazione. I calcoli reali richiedono l'estratto conto contributivo INPS.*
    """)

with tab2:
    st.header("L'Accordo Win-Win")
    st.markdown("Analizziamo se l'incentivo proposto dall'azienda rende conveniente l'uscita anticipata rispetto alla pensione naturale.")

    # Scenario: Uscita ORA con Incentivo vs Lavoro fino alla pensione
    mesi_mancanti = (data_target.year - date.today().year) * 12 + (data_target.month - date.today().month)
    if mesi_mancanti < 1: mesi_mancanti = 1
    
    # Calcolo Finanziario
    stipendi_persi = stipendio_netto_mensile * mesi_mancanti
    pensione_guadagnata_anticipo = pensione_stimata * mesi_mancanti # Se esco ora, prendo la pensione per quei mesi che avrei lavorato? 
    # (Attenzione: in realtà se esco e non ho i requisiti devo aspettare la finestra, qui assumiamo 'scivolo' o Naspi ponte, semplifichiamo per MVP)
    
    # Semplifichiamo lo scenario: L'azienda paga per farti uscire X mesi prima della pensione (Isopensione/Scivolo)
    # Gap da coprire = (Stipendio Netto - Eventuale NASPI/Pensione ridotta) * Mesi
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🏢 Per l'Azienda")
        risparmio_stipendi = costo_azienda_annuo * (mesi_mancanti / 12)
        risparmio_netto = risparmio_stipendi - incentivo_proposto
        
        st.write(f"Costo mantenimento dipendente fino alla pensione: **€ {risparmio_stipendi:,.2f}**")
        st.write(f"Incentivo da pagare: **€ {incentivo_proposto:,.2f}**")
        if risparmio_netto > 0:
            st.success(f"✅ Risparmio Aziendale Totale: **€ {risparmio_netto:,.2f}**")
        else:
            st.error(f"❌ Costo extra per l'azienda: € {abs(risparmio_netto):,.2f}")

    with col_b:
        st.subheader("👷 Per il Lavoratore")
        # Il lavoratore perde lo stipendio pieno, ma guadagna: Incentivo netto (tassazione separata ~23% media per TFR) + Tempo libero
        incentivo_netto = incentivo_proposto * 0.77 
        
        # Gap retributivo (Stipendio che non prendo - Pensione che prenderei subito se avessi i requisiti o NASPI)
        # Assumiamo scenario peggiore: niente pensione fino alla data target, si vive di incentivo
        copertura_mensile_incentivo = incentivo_netto / mesi_mancanti
        
        st.metric("Incentivo Netto (Stima)", f"€ {incentivo_netto:,.2f}")
        st.metric("Copertura Mensile (Ponte)", f"€ {copertura_mensile_incentivo:,.2f} / mese")
        
        gap = stipendio_netto_mensile - copertura_mensile_incentivo
        if gap > 0:
            st.warning(f"Differenza rispetto allo stipendio attuale: -€ {gap:,.2f}/mese")
        else:
            st.success(f"Guadagno rispetto allo stipendio: +€ {abs(gap):,.2f}/mese")

    st.markdown("---")
    st.markdown("### 🧬 Il valore del Tempo")
    valore_tempo = st.slider("Quanto vale per te 1 anno di vita 'libera' in €?", 0, 50000, 15000)
    
    bilancio_personale = incentivo_netto + (valore_tempo * (mesi_mancanti/12)) - stipendi_persi
    
    # Grafico a cascata (Waterfall) per decision making
    fig = go.Figure(go.Waterfall(
        name = "Decisione", orientation = "v",
        measure = ["relative", "relative", "relative", "total"],
        x = ["Perdita Stipendi Futuri", "Incasso Incentivo", "Valore Tempo Libero", "Bilancio Totale"],
        textposition = "outside",
        text = [f"-{stipendi_persi/1000:.1f}k", f"+{incentivo_netto/1000:.1f}k", f"+{(valore_tempo * (mesi_mancanti/12))/1000:.1f}k", None],
        y = [-stipendi_persi, incentivo_netto, (valore_tempo * (mesi_mancanti/12)), 0],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(title = "Bilancio Decisionale (Esco Ora vs Resto)", showlegend = False)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Ottimizzazione Data Uscita")
    st.write("Analizziamo come cambia l'importo della pensione lavorando 1, 2 o 3 anni in più.")
    
    anni_extra = [0, 1, 2, 3, 4, 5]
    pensioni_future = []
    
    for a in anni_extra:
        p = stima_pensione_netta(ral * (1.01**a), anni_contributi + a) # Assumiamo aumento RAL 1% annuo
        pensioni_future.append(p)
        
    df_proiezione = pd.DataFrame({
        "Anni Extra Lavoro": anni_extra,
        "Pensione Stimata (€)": pensioni_future,
        "Incremento Mensile (€)": [p - pensioni_future[0] for p in pensioni_future]
    })
    
    st.table(df_proiezione)
    
    st.line_chart(df_proiezione, x="Anni Extra Lavoro", y="Pensione Stimata (€)")
    st.caption("Nota: Lavorare di più aumenta il montante contributivo e il coefficiente di trasformazione (età più alta).")

# --- FOOTER ---
st.markdown("---")
st.caption("Developed with Streamlit. Disclaimer: I valori sono stime a scopo illustrativo.")
