# Pension_Bridge

## 🎯 Descrizione

PensionBridge è un'applicazione Streamlit completa per l'analisi e la negoziazione degli accordi di uscita anticipata dal mondo del lavoro, considerando tutte le variabili della normativa pensionistica italiana.

## ✨ Caratteristiche Principali

### 📊 Calcoli Pensionistici Avanzati
- **Pensione di Vecchiaia** (67 anni)
- **Pensione Anticipata Ordinaria** (42 anni e 10 mesi uomini, 41 anni e 10 mesi donne)
- **Lavoratori Precoci** (Legge 232/2016) - Uscita con 41 anni di contributi
- **Lavoratori Usuranti** (D.Lgs 67/2011) - Quota 97.6 con requisiti specifici

### 💼 Tipologie di Contribuzione
- Dipendenti Privati
- Artigiani e Commercianti
- Autonomi
- Coltivatori Diretti e settore agricolo

### 🛡️ Strumenti di Sostegno al Reddito

#### NASPI (Nuova Assicurazione Sociale per l'Impiego)
- Calcolo importo mensile con regole INPS
- Durata basata sui contributi degli ultimi 4 anni
- Copertura figurativa dei contributi previdenziali

#### APE Sociale (Anticipo Pensionistico Sociale)
- Requisiti: 63 anni di età + 30-36 anni di contributi
- Categorie ammesse:
  - Disoccupati
  - Caregiver di familiari disabili
  - Invalidi ≥74%
  - Lavoratori usuranti/gravosi

#### R.I.T.A. (Rendita Integrativa Temporanea Anticipata)
- Anticipo previdenza complementare
- Rendita temporanea fino alla pensione obbligatoria
- Tassazione agevolata (15% riducibile al 9%)
- Requisiti: entro 5 anni dalla pensione (10 per inoccupati)

### 🗺️ Analisi Regionale

**Costo della Vita per Regione**
- Fattori di correzione per tutte le 20 regioni italiane
- Range da 0.82 (Calabria) a 1.15 (Lazio)
- Impatto sul calcolo dell'incentivo all'esodo

### 💰 Calcolo Incentivo all'Esodo

Il sistema calcola automaticamente l'incentivo ottimale considerando:

1. **Delta Salariale**: Differenza tra stipendio netto e coperture disponibili (NASPI + APE + R.I.T.A.)
2. **Fattore Regionale**: Adeguamento al costo della vita della regione di residenza
3. **Valore del Tempo Libero**: Valutazione del tempo libero inversamente proporzionale al costo vita

**Formula**:
```
Incentivo Totale = (Gap Mensile × Mesi × Fattore Regionale) + Valore Tempo Libero
```

Dove:
- **Gap Mensile** = Stipendio Netto - (NASPI + APE + R.I.T.A.)
- **Fattore Regionale** = Indice costo vita regione (0.82 - 1.15)
- **Valore Tempo** = Funzione decrescente del costo vita (più potere d'acquisto = più valore)

### 🏢 Analisi Aziendale

Confronto costi/benefici per l'azienda:
- Costo mantenimento dipendente vs incentivo esodo
- Calcolo ROI dell'operazione
- Valutazione benefici intangibili (rinnovamento, clima aziendale)

### ⏰ Ottimizzazione Temporale

- Proiezione pensione futura lavorando anni extra (1-5 anni)
- Analisi break-even considerando aspettativa di vita
- Valutazione lifetime dei flussi pensionistici

## 🚀 Installazione e Uso

### Requisiti
```bash
pip install -r requirements.txt
```

### Avvio dell'applicazione
```bash
streamlit run app.py
```

L'applicazione sarà disponibile su `http://localhost:8501`

## 📋 Schermata di Input

### Dati Anagrafici
- Sesso
- Età anagrafica
- Regione di residenza

### Dati Contributivi
- Tipo di contribuzione (Dipendente, Artigiano, Autonomo, Agricolo)
- Anni di contributi maturati
- ☑️ Lavoratore Precoce
- ☑️ Lavoratore Usurante

### Dati Economici
- RAL (Reddito Annuo Lordo)
- Montante previdenza complementare (opzionale)

### Situazione Lavorativa
- Stato occupazionale
- Mesi contributivi ultimi 4 anni (per NASPI)
- Status caregiver o invalido

## 📊 Output e Analisi

### Tab 1: Analisi Pensionistica
- Data prima uscita utile
- Pensione netta stimata
- Dettaglio requisiti normativi per categoria

### Tab 2: Strumenti di Sostegno
- Importi NASPI, APE Sociale, R.I.T.A.
- Copertura totale mensile durante transizione
- Percentuale copertura vs stipendio attuale

### Tab 3: Incentivo Esodo
- Calcolo dettagliato incentivo regionale
- Breakdown: gap salariale + valore tempo libero
- Comparazione tra regioni campione

### Tab 4: Analisi Aziendale
- Confronto scenari (mantenimento vs esodo)
- Risparmio aziendale o costo extra
- ROI e benefici intangibili

### Tab 5: Strategia Temporale
- Proiezione pensione futura
- Analisi break-even lifetime
- Ottimizzazione data uscita

## ⚠️ Disclaimer

I valori forniti sono **stime a scopo illustrativo** basate sulla normativa italiana vigente (2025).

Per calcoli precisi e personalizzati:
- Consultare l'estratto conto contributivo INPS
- Rivolgersi a un consulente previdenziale qualificato
- Verificare i requisiti specifici con CAF o patronati

## 📚 Normativa di Riferimento

- Legge 232/2016 (Lavoratori Precoci)
- D.Lgs 67/2011 (Lavoratori Usuranti)
- Legge di Bilancio annuale (APE Sociale)
- D.Lgs 252/2005 (Previdenza Complementare)
- D.Lgs 22/2015 (NASPI)

## 🛠️ Tecnologie Utilizzate

- **Streamlit**: Framework per interfaccia web
- **Pandas**: Manipolazione dati
- **Plotly**: Visualizzazioni interattive
- **NumPy**: Calcoli numerici

## 📝 Licenza

Questo progetto è fornito "as-is" senza garanzie di alcun tipo.

## 👥 Contributi

Sviluppato per supportare la pianificazione pensionistica e la negoziazione win-win tra lavoratori e aziende.
