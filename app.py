import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="PensionBridge Win-Win", layout="wide")

# --- DATI REGIONALI COSTO DELLA VITA ---
COSTO_VITA_REGIONALE = {
    "Abruzzo": 0.90,
    "Basilicata": 0.85,
    "Calabria": 0.82,
    "Campania": 0.88,
    "Emilia-Romagna": 1.05,
    "Friuli-Venezia Giulia": 1.00,
    "Lazio": 1.15,
    "Liguria": 1.08,
    "Lombardia": 1.12,
    "Marche": 0.92,
    "Molise": 0.83,
    "Piemonte": 1.02,
    "Puglia": 0.87,
    "Sardegna": 0.89,
    "Sicilia": 0.86,
    "Toscana": 1.06,
    "Trentino-Alto Adige": 1.10,
    "Umbria": 0.91,
    "Valle d'Aosta": 1.05,
    "Veneto": 1.03
}

# --- FUNZIONI DI UTILITÀ (SIMULAZIONE SEMPLIFICATA) ---
def calcola_data_pensione(eta_attuale, anni_contributi, sesso, is_lavoratore_precoce=False, 
                         is_lavoratore_usurante=False, tipo_contribuzione="Dipendente Privato"):
    """
    Stima data pensione basata su regole attuali semplificate (2025).
    Include lavoratori precoci, usuranti e diverse tipologie contributive.
    """
    oggi = date.today()
    # Regola Vecchiaia: 67 anni
    anni_mancanti_vecchiaia = 67 - eta_attuale
    data_vecchiaia = oggi.replace(year=oggi.year + int(anni_mancanti_vecchiaia))
    
    # Regola Anticipata (42y 10m Uomini, 41y 10m Donne)
    soglia_anni = 42 if sesso == 'Uomo' else 41
    mesi_extra = 10
    
    # Lavoratori Precoci: possono andare in pensione con 41 anni di contributi 
    # se hanno almeno 12 mesi di contributi prima dei 19 anni
    if is_lavoratore_precoce:
        soglia_anni = 41
        mesi_extra = 0
    
    # Lavoratori Usuranti: possibilità di uscita anticipata
    # (notturni, catena di montaggio, conducenti, etc.)
    if is_lavoratore_usurante:
        # Quota 97.6 (somma età + contributi) con almeno 61 anni e 7 mesi di età
        eta_minima_usuranti = 61.58  # 61 anni e 7 mesi
        if eta_attuale >= eta_minima_usuranti and (eta_attuale + anni_contributi) >= 97.6:
            return oggi, data_vecchiaia, oggi
        # Altrimenti calcola quando si raggiunge la quota
        anni_per_quota = max(0, 97.6 - (eta_attuale + anni_contributi))
        data_usuranti = today_plus_months(oggi, int(anni_per_quota * 12))
        if eta_attuale + anni_per_quota >= eta_minima_usuranti:
            return data_usuranti, data_vecchiaia, data_usuranti
    
    # Contribuzione autonomi/artigiani: potrebbero avere requisiti leggermente diversi
    if tipo_contribuzione in ["Artigiani", "Commercianti", "Autonomi"]:
        # Stesse regole ma con aliquote contributive diverse (considerate nel calcolo pensione)
        pass
    
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

def stima_pensione_netta(ral, anni_contributi, tipo_contribuzione="Dipendente Privato"):
    """
    Stima MOLTO semplificata del tasso di sostituzione.
    In un'app reale, qui andrebbe il calcolo contributivo/retributivo.
    Ipotesi: ~70% dell'ultimo netto per carriere lunghe.
    Considera tipo di contribuzione (dipendente, artigiano, autonomo, agricolo).
    """
    netto_mensile_stimato = (ral * 0.65) / 13 # Stima tassazione e 13 mensilità
    
    # Fattore correttivo basato sugli anni (più anni = più pensione)
    fattore_anni = min(anni_contributi / 40.0, 1.1)
    
    # Aliquote contributive diverse per tipologie
    if tipo_contribuzione == "Dipendente Privato":
        tasso_sostituzione_base = 0.75
    elif tipo_contribuzione in ["Artigiani", "Commercianti"]:
        # Aliquota contributiva più bassa = pensione più bassa
        tasso_sostituzione_base = 0.65
    elif tipo_contribuzione == "Autonomi":
        tasso_sostituzione_base = 0.60
    elif tipo_contribuzione == "Coltivatori Diretti":
        tasso_sostituzione_base = 0.55
    else:
        tasso_sostituzione_base = 0.70
    
    pensione = netto_mensile_stimato * tasso_sostituzione_base * fattore_anni
    return pensione

def calcola_naspi(ral, mesi_contributi_ultimi_4_anni):
    """
    Calcola l'importo della NASPI (indennità di disoccupazione).
    La NASPI copre anche figurativamente i contributi previdenziali.
    Importo: 75% della retribuzione media mensile fino a €1,352.19 (2024)
            + 25% dell'eccedenza
    Durata: metà delle settimane contributive degli ultimi 4 anni
    """
    retribuzione_mensile = ral / 13
    soglia_naspi = 1352.19  # Valore 2024, va indicizzato annualmente
    
    if retribuzione_mensile <= soglia_naspi:
        naspi_mensile = retribuzione_mensile * 0.75
    else:
        naspi_mensile = soglia_naspi * 0.75 + (retribuzione_mensile - soglia_naspi) * 0.25
    
    # La NASPI si riduce del 3% ogni mese dal 4° mese
    # Durata massima basata sui mesi contributivi
    durata_mesi = min(mesi_contributi_ultimi_4_anni / 2, 24)
    
    return naspi_mensile, durata_mesi

def calcola_ape_sociale(eta, anni_contributi, ral, is_disoccupato=False, 
                        is_caregiver=False, is_invalido=False, is_lavoratore_usurante=False):
    """
    Calcola l'APE Sociale (Anticipo Pensionistico Sociale).
    Requisiti:
    - Almeno 63 anni di età
    - 30 o 36 anni di contributi (a seconda della categoria)
    - Condizione: disoccupato, caregiver, invalido ≥74%, lavoro usurante/gravoso
    """
    if eta < 63:
        return 0, False, "Età minima 63 anni non raggiunta"
    
    anni_contributi_richiesti = 30
    if is_lavoratore_usurante:
        anni_contributi_richiesti = 36
    
    if anni_contributi < anni_contributi_richiesti:
        return 0, False, f"Servono almeno {anni_contributi_richiesti} anni di contributi"
    
    # Verifica condizioni
    ha_diritto = is_disoccupato or is_caregiver or is_invalido or is_lavoratore_usurante
    
    if not ha_diritto:
        return 0, False, "Non si rientra nelle categorie previste per l'APE Sociale"
    
    # L'APE sociale è pari all'importo della pensione calcolata al momento della domanda
    # ma con un massimale di €1,500 mensili (circa)
    pensione_teorica = stima_pensione_netta(ral, anni_contributi)
    ape_importo = min(pensione_teorica, 1500)
    
    return ape_importo, True, "APE Sociale concedibile"

def calcola_rita(montante_complementare, eta, anni_a_pensione):
    """
    Calcola la R.I.T.A. (Rendita Integrativa Temporanea Anticipata).
    Permette di anticipare l'erogazione della previdenza complementare
    in forma di rendita fino al raggiungimento della pensione obbligatoria.
    
    Requisiti:
    - Cessazione attività lavorativa
    - Maturazione diritto pensione vecchiaia/anticipata entro 5 anni (10 per inoccupati >24 mesi)
    - Almeno 20 anni di contributi al fondo pensione o 5 anni + 5 anni a pensione
    """
    if anni_a_pensione > 5:
        return 0, False, "Troppo lontano dalla pensione (max 5 anni)"
    
    if montante_complementare <= 0:
        return 0, False, "Nessun montante previdenza complementare"
    
    # Calcolo rendita: il montante viene erogato come rendita temporanea
    # Coefficiente di conversione dipende da età e anni di rendita
    # Semplificazione: montante / (anni_a_pensione * 12)
    if anni_a_pensione < 1:
        anni_a_pensione = 1
    
    rita_mensile = montante_complementare / (anni_a_pensione * 12)
    
    # Tassazione agevolata al 15% (ridotta dello 0.3% per ogni anno oltre il 15°)
    tassazione = max(0.09, 0.15 - 0.003 * max(0, 20 - 15))  # Ipotesi 20 anni nel fondo
    rita_netta = rita_mensile * (1 - tassazione)
    
    return rita_netta, True, "R.I.T.A. disponibile"

def calcola_incentivo_esodo_regionale(ral, mesi_mancanti, regione, naspi_mensile=0, 
                                     pensione_anticipata_effettiva=0):
    """
    Calcola l'incentivo all'esodo considerando:
    1. Il delta tra retribuzione e quello che percepirebbe (NASPI + eventuali altre forme)
    2. Il costo della vita regionale
    3. Il valore del tempo libero corretto per regione
    
    Formula: Incentivo = (Stipendio_Netto - Coperture) * Mesi * Fattore_Regionale
    """
    stipendio_netto_mensile = (ral * 0.65) / 13
    
    # Calcolo del gap mensile da coprire
    copertura_mensile = naspi_mensile + pensione_anticipata_effettiva
    gap_mensile = stipendio_netto_mensile - copertura_mensile
    
    # Applicazione del fattore regionale sul gap
    fattore_regionale = COSTO_VITA_REGIONALE.get(regione, 1.0)
    gap_mensile_corretto = gap_mensile * fattore_regionale
    
    # Incentivo base per coprire il periodo
    incentivo_base = gap_mensile_corretto * mesi_mancanti
    
    # Valore del tempo libero (funzione decrescente con l'età e variabile per regione)
    # Più alto nelle regioni con costo vita basso (più potere d'acquisto)
    valore_tempo_mensile = 1000 * (1.5 - fattore_regionale)  # Inversamente proporzionale
    valore_tempo_totale = valore_tempo_mensile * mesi_mancanti
    
    # Incentivo totale suggerito
    incentivo_totale = incentivo_base + valore_tempo_totale
    
    return {
        'incentivo_base': incentivo_base,
        'valore_tempo': valore_tempo_totale,
        'incentivo_totale': incentivo_totale,
        'gap_mensile': gap_mensile,
        'fattore_regionale': fattore_regionale,
        'stipendio_netto': stipendio_netto_mensile,
        'copertura_mensile': copertura_mensile
    }

# --- INTERFACCIA UTENTE ---

st.title("🤝 PensionBridge: Analisi e Negoziazione Uscita")
st.markdown("""
Questo strumento aiuta a trovare il punto di equilibrio tra **l'interesse del lavoratore** (pensione + tempo libero) 
e **l'interesse dell'azienda** (rinnovamento forza lavoro + incentivi).
Include tutte le variabili della legge italiana: lavoratori precoci, usuranti, contributi diversificati, 
NASPI, APE Sociale, R.I.T.A., previdenza complementare e costo vita regionale.
""")

# --- SIDEBAR: INPUT DATI ---
st.sidebar.header("1. Dati Anagrafici")

sesso = st.sidebar.selectbox("Sesso", ["Uomo", "Donna"])
eta = st.sidebar.number_input("Età Anagrafica", 50, 70, 62)
regione = st.sidebar.selectbox("Regione di Residenza", sorted(COSTO_VITA_REGIONALE.keys()))

st.sidebar.markdown("---")
st.sidebar.header("2. Dati Contributivi")

tipo_contribuzione = st.sidebar.selectbox(
    "Tipo Contribuzione Principale",
    ["Dipendente Privato", "Artigiani", "Commercianti", "Autonomi", "Coltivatori Diretti"]
)
anni_contributi = st.sidebar.number_input("Anni di Contributi maturati", 20, 50, 38)

# Categorie speciali
is_lavoratore_precoce = st.sidebar.checkbox(
    "Lavoratore Precoce (almeno 12 mesi prima dei 19 anni)", 
    value=False
)
is_lavoratore_usurante = st.sidebar.checkbox(
    "Lavoratore Usurante/Gravoso (notturni, catena montaggio, etc.)", 
    value=False
)

st.sidebar.markdown("---")
st.sidebar.header("3. Dati Economici")

ral = st.sidebar.number_input("RAL Attuale (€)", 20000, 200000, 45000, step=1000)
costo_azienda_annuo = ral * 1.35 # Stima costo azienda (INPS + TFR)

st.sidebar.markdown("---")
st.sidebar.header("4. Previdenza Complementare")

ha_previdenza_complementare = st.sidebar.checkbox("Ha Previdenza Complementare", value=False)
montante_complementare = 0
if ha_previdenza_complementare:
    montante_complementare = st.sidebar.number_input(
        "Montante Fondo Pensione (€)", 
        0, 500000, 50000, step=5000
    )

st.sidebar.markdown("---")
st.sidebar.header("5. Situazione Lavorativa")

is_disoccupato = st.sidebar.checkbox("Disoccupato/Rischio disoccupazione", value=False)
mesi_contributi_ultimi_4_anni = st.sidebar.number_input(
    "Mesi contributi ultimi 4 anni (per NASPI)", 
    0, 48, 48
)
is_caregiver = st.sidebar.checkbox("Caregiver (assiste familiare disabile)", value=False)
is_invalido = st.sidebar.checkbox("Invalido ≥74%", value=False)

st.sidebar.markdown("---")
st.sidebar.header("6. Incentivo Proposto")

usa_calcolo_automatico = st.sidebar.checkbox("Usa calcolo automatico incentivo", value=True)
if not usa_calcolo_automatico:
    incentivo_proposto = st.sidebar.number_input(
        "Incentivo all'esodo proposto (Lordo)", 
        0, 500000, 30000, step=5000
    )

# --- CALCOLI CORE ---
data_target, data_vecchiaia, data_anticipata = calcola_data_pensione(
    eta, anni_contributi, sesso, is_lavoratore_precoce, is_lavoratore_usurante, tipo_contribuzione
)
pensione_stimata = stima_pensione_netta(ral, anni_contributi, tipo_contribuzione)
stipendio_netto_mensile = (ral * 0.65) / 13

# Calcolo NASPI
naspi_mensile, durata_naspi = calcola_naspi(ral, mesi_contributi_ultimi_4_anni)

# Calcolo APE Sociale
ape_importo, ape_ammissibile, ape_messaggio = calcola_ape_sociale(
    eta, anni_contributi, ral, is_disoccupato, is_caregiver, is_invalido, is_lavoratore_usurante
)

# Calcolo R.I.T.A.
anni_a_pensione = (data_target.year - date.today().year) + \
                  (data_target.month - date.today().month) / 12
rita_mensile, rita_disponibile, rita_messaggio = calcola_rita(
    montante_complementare, eta, anni_a_pensione
)

# Calcolo mesi mancanti alla pensione
mesi_mancanti = (data_target.year - date.today().year) * 12 + \
                (data_target.month - date.today().month)
if mesi_mancanti < 1: 
    mesi_mancanti = 1

# Calcolo incentivo esodo regionale
risultato_incentivo = calcola_incentivo_esodo_regionale(
    ral, mesi_mancanti, regione, naspi_mensile, 
    ape_importo if ape_ammissibile else 0
)

# Imposta incentivo proposto
if usa_calcolo_automatico:
    incentivo_proposto = risultato_incentivo['incentivo_totale']

# --- TABELLONE PRINCIPALE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analisi Pensionistica", 
    "💰 Strumenti di Sostegno",
    "⚖️ Incentivo Esodo", 
    "🏢 Analisi Aziendale",
    "⚙️ Strategia Temporale"
])

with tab1:
    st.header("Quando puoi andare in pensione?")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Data Prima Uscita Utile", data_target.strftime("%d/%m/%Y"))
    col2.metric("Pensione Netta Stimata", f"€ {pensione_stimata:,.2f} / mese")
    col3.metric("Ultimo Stipendio Netto", f"€ {stipendio_netto_mensile:,.2f} / mese")
    
    # Mostra dettagli specifici per categoria
    categoria_info = []
    if is_lavoratore_precoce:
        categoria_info.append("✓ **Lavoratore Precoce**: Requisiti ridotti (41 anni contributi)")
    if is_lavoratore_usurante:
        categoria_info.append("✓ **Lavoratore Usurante**: Accesso anticipato con Quota 97.6")
    if tipo_contribuzione != "Dipendente Privato":
        categoria_info.append(f"✓ **Contribuzione {tipo_contribuzione}**: Aliquote specifiche applicate")
    
    if categoria_info:
        st.success("\n\n".join(categoria_info))
    
    st.info(f"""
    **Dettaglio Normativo:**
    - Per la **Pensione di Vecchiaia** (67 anni) ti mancano ancora {max(0, (data_vecchiaia - date.today()).days // 365)} anni.
    - Per la **Pensione Anticipata** ti mancano ancora {max(0, (data_anticipata - date.today()).days // 365)} anni.
    - Mesi totali alla pensione: **{mesi_mancanti} mesi**
    - Tipo contribuzione: **{tipo_contribuzione}**
    
    *Nota: Questa è una simulazione. I calcoli reali richiedono l'estratto conto contributivo INPS.*
    """)

with tab2:
    st.header("🛡️ Strumenti di Sostegno al Reddito")
    st.markdown("Analisi degli strumenti disponibili per il periodo di transizione alla pensione.")
    
    col_naspi, col_ape, col_rita = st.columns(3)
    
    with col_naspi:
        st.subheader("NASPI")
        st.metric("Importo Mensile", f"€ {naspi_mensile:,.2f}")
        st.metric("Durata (mesi)", f"{durata_naspi:.0f}")
        st.caption(f"""
        La NASPI copre figurativamente i contributi previdenziali.
        Totale erogabile: €{naspi_mensile * durata_naspi:,.2f}
        """)
    
    with col_ape:
        st.subheader("APE Sociale")
        if ape_ammissibile:
            st.success("✅ Ammissibile")
            st.metric("Importo Mensile", f"€ {ape_importo:,.2f}")
        else:
            st.warning("❌ Non ammissibile")
        st.caption(ape_messaggio)
    
    with col_rita:
        st.subheader("R.I.T.A.")
        if rita_disponibile and montante_complementare > 0:
            st.success("✅ Disponibile")
            st.metric("Rendita Mensile Netta", f"€ {rita_mensile:,.2f}")
            st.caption(f"Montante: €{montante_complementare:,.0f}")
        else:
            st.info("ℹ️ Non configurata")
        st.caption(rita_messaggio)
    
    # Riepilogo copertura totale
    st.markdown("---")
    st.subheader("📊 Copertura Totale Durante il Periodo di Transizione")
    
    copertura_totale_mensile = naspi_mensile + (ape_importo if ape_ammissibile else 0) + \
                                (rita_mensile if rita_disponibile else 0)
    gap_vs_stipendio = stipendio_netto_mensile - copertura_totale_mensile
    percentuale_copertura = (copertura_totale_mensile / stipendio_netto_mensile * 100) if stipendio_netto_mensile > 0 else 0
    
    col_cov1, col_cov2, col_cov3 = st.columns(3)
    col_cov1.metric("Copertura Mensile Totale", f"€ {copertura_totale_mensile:,.2f}")
    col_cov2.metric("% vs Stipendio", f"{percentuale_copertura:.1f}%")
    col_cov3.metric("Gap da Coprire", f"€ {gap_vs_stipendio:,.2f}")

with tab3:
    st.header("💼 Calcolo Incentivo all'Esodo")
    st.markdown(f"""
    Calcolo dell'incentivo ottimale considerando:
    - **Regione**: {regione} (fattore costo vita: {risultato_incentivo['fattore_regionale']:.2f})
    - **Delta salariale** rispetto alle coperture disponibili
    - **Valore del tempo libero** regionale
    """)
    
    # Visualizzazione dettagliata del calcolo
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("📊 Breakdown Calcolo")
        st.write(f"**Stipendio Netto Mensile:** €{risultato_incentivo['stipendio_netto']:,.2f}")
        st.write(f"**Copertura Mensile Totale:** €{risultato_incentivo['copertura_mensile']:,.2f}")
        st.write(f"**Gap Mensile:** €{risultato_incentivo['gap_mensile']:,.2f}")
        st.write(f"**Mesi da Coprire:** {mesi_mancanti}")
        st.write(f"**Fattore Regionale ({regione}):** {risultato_incentivo['fattore_regionale']:.2f}x")
        
        st.markdown("---")
        st.metric("Incentivo Base (copertura gap)", 
                 f"€ {risultato_incentivo['incentivo_base']:,.2f}")
        st.metric("Valore Tempo Libero", 
                 f"€ {risultato_incentivo['valore_tempo']:,.2f}")
    
    with col_calc2:
        st.subheader("💰 Incentivo Totale Suggerito")
        st.metric(
            "INCENTIVO ESODO REGIONALE",
            f"€ {risultato_incentivo['incentivo_totale']:,.2f}",
            delta=f"+{risultato_incentivo['valore_tempo']:,.0f} (tempo libero)"
        )
        
        # Grafico a torta composizione incentivo
        fig_comp = go.Figure(data=[go.Pie(
            labels=['Copertura Gap Salariale', 'Valore Tempo Libero'],
            values=[risultato_incentivo['incentivo_base'], risultato_incentivo['valore_tempo']],
            hole=.3
        )])
        fig_comp.update_layout(title="Composizione Incentivo")
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # Comparazione regionale
    st.markdown("---")
    st.subheader("🗺️ Impatto Regionale")
    st.markdown("""
    L'incentivo varia in base al costo della vita regionale. Nelle regioni con costo vita più basso,
    il valore del tempo libero è più alto (maggiore potere d'acquisto).
    """)
    
    # Calcolo incentivi per tutte le regioni (campione)
    regioni_campione = ["Lombardia", "Lazio", "Campania", "Calabria", "Toscana"]
    dati_regionali = []
    for reg in regioni_campione:
        ris = calcola_incentivo_esodo_regionale(ral, mesi_mancanti, reg, naspi_mensile, 
                                                ape_importo if ape_ammissibile else 0)
        dati_regionali.append({
            'Regione': reg,
            'Fattore Costo Vita': COSTO_VITA_REGIONALE[reg],
            'Incentivo': ris['incentivo_totale']
        })
    
    df_regioni = pd.DataFrame(dati_regionali)
    st.bar_chart(df_regioni.set_index('Regione')['Incentivo'])

with tab4:
    st.header("🏢 Analisi Costi/Benefici Aziendali")
    st.markdown("Valutazione della convenienza per l'azienda.")
    
    # Scenario: Uscita ORA con Incentivo vs Lavoro fino alla pensione
    
    # Calcolo Finanziario Aziendale
    col_az1, col_az2 = st.columns(2)
    
    with col_az1:
        st.subheader("💸 Scenario: Mantenimento Dipendente")
        costo_totale_mantenimento = costo_azienda_annuo * (mesi_mancanti / 12)
        
        st.write(f"**Costo azienda mensile:** €{costo_azienda_annuo/12:,.2f}")
        st.write(f"**Mesi fino a pensione:** {mesi_mancanti}")
        st.metric("Costo Totale Mantenimento", f"€ {costo_totale_mantenimento:,.2f}")
    
    with col_az2:
        st.subheader("🎯 Scenario: Incentivo all'Esodo")
        st.metric("Incentivo da Erogare", f"€ {incentivo_proposto:,.2f}")
        
        risparmio_aziendale = costo_totale_mantenimento - incentivo_proposto
        
        if risparmio_aziendale > 0:
            st.success(f"✅ **Risparmio Aziendale: €{risparmio_aziendale:,.2f}**")
            st.write(f"ROI: {(risparmio_aziendale/incentivo_proposto*100):.1f}%")
        else:
            st.error(f"❌ **Costo Extra: €{abs(risparmio_aziendale):,.2f}**")
    
    # Analisi benefici intangibili
    st.markdown("---")
    st.subheader("📈 Benefici Intangibili per l'Azienda")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Rinnovamento Forza Lavoro", "✓", delta="Competenze aggiornate")
    col_b2.metric("Clima Aziendale", "✓", delta="Gestione proattiva")
    col_b3.metric("Riduzione Conflitti", "✓", delta="Soluzione win-win")

with tab5:
    st.header("⏰ Ottimizzazione Data Uscita")
    st.write("Analizziamo come cambia l'importo della pensione lavorando 1, 2 o 3 anni in più.")
    
    anni_extra = [0, 1, 2, 3, 4, 5]
    pensioni_future = []
    
    for a in anni_extra:
        p = stima_pensione_netta(ral * (1.01**a), anni_contributi + a, tipo_contribuzione)
        pensioni_future.append(p)
        
    df_proiezione = pd.DataFrame({
        "Anni Extra Lavoro": anni_extra,
        "Pensione Stimata (€)": pensioni_future,
        "Incremento Mensile (€)": [p - pensioni_future[0] for p in pensioni_future]
    })
    
    st.table(df_proiezione)
    
    st.line_chart(df_proiezione, x="Anni Extra Lavoro", y="Pensione Stimata (€)")
    st.caption("Nota: Lavorare di più aumenta il montante contributivo e il coefficiente di trasformazione (età più alta).")
    
    # Analisi break-even
    st.markdown("---")
    st.subheader("📊 Analisi Break-Even")
    st.markdown("""
    Considera che ogni anno di lavoro in più aumenta la pensione ma riduce gli anni di godimento.
    L'analisi break-even considera l'aspettativa di vita e il valore attuale dei flussi pensionistici.
    """)
    
    # Semplice calcolo break-even
    aspettativa_vita = 85  # Ipotesi
    anni_pensione_se_esci_ora = aspettativa_vita - eta
    
    st.info(f"""
    **Scenario attuale:**
    - Uscita tra {mesi_mancanti} mesi → Pensione €{pensione_stimata:,.2f}/mese per circa {anni_pensione_se_esci_ora:.0f} anni
    - Totale lifetime: €{pensione_stimata * 12 * anni_pensione_se_esci_ora:,.0f}
    
    **Se lavori 2 anni in più:**
    - Pensione €{pensioni_future[2]:,.2f}/mese per circa {anni_pensione_se_esci_ora - 2:.0f} anni
    - Totale lifetime: €{pensioni_future[2] * 12 * (anni_pensione_se_esci_ora - 2):,.0f}
    """)


# --- FOOTER ---
st.markdown("---")
st.caption("""
**PensionBridge Win-Win v2.0** - Developed with Streamlit
    
**Disclaimer**: I valori sono stime a scopo illustrativo basate su normativa italiana vigente (2025).
Per calcoli precisi consultare l'estratto conto INPS e un consulente previdenziale.

**Normativa considerata**:
- Pensione di vecchiaia (67 anni)
- Pensione anticipata ordinaria (42a 10m uomini, 41a 10m donne)
- Lavoratori precoci (Legge 232/2016)
- Lavoratori usuranti (D.Lgs 67/2011)
- NASPI con copertura figurativa
- APE Sociale (Legge di Bilancio)
- R.I.T.A. (Rendita Integrativa Temporanea Anticipata)
- Contribuzioni diversificate (artigiani, commercianti, autonomi, agricoli)
- Costo della vita regionale
""")
