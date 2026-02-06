# PensionBridge - Specifiche Tecniche

## Formule e Algoritmi Implementati

### 1. Calcolo Data Pensione

#### Pensione di Vecchiaia
```
Età Richiesta = 67 anni
Data Pensione = Data Attuale + (67 - Età Attuale) anni
```

#### Pensione Anticipata Ordinaria
```
Requisiti Uomini: 42 anni e 10 mesi di contributi
Requisiti Donne: 41 anni e 10 mesi di contributi
```

#### Lavoratori Precoci (Legge 232/2016)
```
Requisiti: 41 anni di contributi
Condizione: Almeno 12 mesi di contributi versati prima dei 19 anni di età
```

#### Lavoratori Usuranti (D.Lgs 67/2011)
```
Formula Quota: Età + Anni Contributi ≥ 97.6
Età Minima: 61 anni e 7 mesi
Categorie: Notturni, catena montaggio, conducenti, lavori ad alta temperatura
```

### 2. Stima Pensione Netta

#### Formula Base
```python
Netto_Mensile_Stimato = (RAL × 0.65) / 13  # Tassazione + 13 mensilità
Fattore_Anni = min(Anni_Contributi / 40.0, 1.1)
Pensione = Netto_Mensile_Stimato × Tasso_Sostituzione × Fattore_Anni
```

#### Tassi di Sostituzione per Tipo Contribuzione
- **Dipendente Privato**: 75%
- **Artigiani/Commercianti**: 65% (aliquota contributiva più bassa)
- **Autonomi**: 60%
- **Coltivatori Diretti**: 55%

### 3. Calcolo NASPI

#### Importo Mensile
```python
Retribuzione_Mensile = RAL / 13
Soglia_NASPI = €1,352.19  # Valore 2024

if Retribuzione_Mensile ≤ Soglia_NASPI:
    NASPI = Retribuzione_Mensile × 0.75
else:
    NASPI = (Soglia_NASPI × 0.75) + ((Retribuzione_Mensile - Soglia_NASPI) × 0.25)
```

#### Durata
```python
Durata_Mesi = min(Mesi_Contributi_Ultimi_4_Anni / 2, 24)
```

#### Riduzione Progressiva
- Dal 4° mese: riduzione del 3% mensile

### 4. APE Sociale

#### Requisiti
```
Età Minima: 63 anni
Anni Contributi: 30 anni (standard) o 36 anni (usuranti)

Categorie Ammesse:
- Disoccupati
- Caregiver (assistenza familiare disabile grave)
- Invalidi ≥ 74%
- Lavoratori usuranti/gravosi
```

#### Importo
```python
Pensione_Teorica = stima_pensione_netta(RAL, Anni_Contributi)
APE_Sociale = min(Pensione_Teorica, €1,500)  # Massimale mensile
```

### 5. R.I.T.A. (Rendita Integrativa Temporanea Anticipata)

#### Requisiti
```
Condizioni:
- Cessazione attività lavorativa
- Entro 5 anni dalla pensione (10 anni per inoccupati >24 mesi)
- Almeno 20 anni nel fondo pensione
```

#### Calcolo Rendita
```python
RITA_Mensile_Lorda = Montante_Complementare / (Anni_a_Pensione × 12)

# Tassazione agevolata
Anni_Nel_Fondo = 20  # Esempio
Tassazione = max(0.09, 0.15 - 0.003 × max(0, Anni_Nel_Fondo - 15))

RITA_Mensile_Netta = RITA_Mensile_Lorda × (1 - Tassazione)
```

**Beneficio Fiscale**: Dal 15% si riduce dello 0.3% per ogni anno oltre il 15°, fino al minimo del 9%

### 6. Calcolo Incentivo Esodo Regionale

#### Formula Completa
```python
# Step 1: Calcolo Gap Mensile
Stipendio_Netto_Mensile = (RAL × 0.65) / 13
Copertura_Mensile = NASPI + APE_Sociale + RITA
Gap_Mensile = Stipendio_Netto_Mensile - Copertura_Mensile

# Step 2: Applicazione Fattore Regionale
Gap_Mensile_Corretto = Gap_Mensile × Fattore_Regionale

# Step 3: Incentivo Base
Incentivo_Base = Gap_Mensile_Corretto × Mesi_Mancanti

# Step 4: Valore Tempo Libero
Valore_Tempo_Mensile = 1000 × (1.5 - Fattore_Regionale)
Valore_Tempo_Totale = Valore_Tempo_Mensile × Mesi_Mancanti

# Step 5: Incentivo Totale
Incentivo_Totale = Incentivo_Base + Valore_Tempo_Totale
```

#### Fattori Regionali (Costo Vita)
```
Regioni Alto Costo:           Regioni Medio Costo:         Regioni Basso Costo:
- Lazio: 1.15                 - Emilia-Romagna: 1.05       - Calabria: 0.82
- Lombardia: 1.12             - Toscana: 1.06              - Molise: 0.83
- Trentino-Alto Adige: 1.10   - Veneto: 1.03               - Basilicata: 0.85
- Liguria: 1.08               - Piemonte: 1.02             - Sicilia: 0.86
```

#### Logica del Valore Tempo Libero
Il valore del tempo libero è **inversamente proporzionale** al costo della vita:
- Regioni con **alto costo vita** → **Basso valore tempo** (serve più denaro per vivere)
- Regioni con **basso costo vita** → **Alto valore tempo** (maggiore potere d'acquisto)

### 7. Analisi Costi/Benefici Aziendali

#### Costo Mantenimento Dipendente
```python
Costo_Azienda_Annuo = RAL × 1.35  # INPS + TFR + altri oneri
Costo_Totale = Costo_Azienda_Annuo × (Mesi_Mancanti / 12)
```

#### Risparmio Aziendale
```python
Risparmio = Costo_Totale_Mantenimento - Incentivo_Esodo
ROI = (Risparmio / Incentivo_Esodo) × 100
```

### 8. Ottimizzazione Temporale

#### Proiezione Pensione Futura
```python
for Anni_Extra in range(0, 6):
    RAL_Futura = RAL × (1.01 ** Anni_Extra)  # Incremento 1% annuo
    Anni_Contributi_Futuri = Anni_Contributi + Anni_Extra
    Pensione_Futura = stima_pensione_netta(RAL_Futura, Anni_Contributi_Futuri)
```

#### Break-Even Analysis
```python
Aspettativa_Vita = 85 anni
Anni_Pensione = Aspettativa_Vita - Età_Uscita
Totale_Lifetime = Pensione_Mensile × 12 × Anni_Pensione
```

## Esempi di Calcolo

### Esempio 1: Dipendente Privato Standard
```
Input:
- Età: 62 anni
- Sesso: Uomo
- Anni Contributi: 38
- RAL: €45,000
- Regione: Lombardia (fattore 1.12)
- Mesi contributivi ultimi 4 anni: 48

Calcoli:
- Pensione stimata: €1,603/mese
- NASPI: €1,541/mese per 24 mesi
- Mesi a pensione: 58 mesi (4.8 anni)
- Gap mensile: €711/mese (€2,253 - €1,541)
- Gap corretto: €796/mese (×1.12)
- Incentivo base: €46,168
- Valore tempo: €17,400
- INCENTIVO TOTALE: €63,568
```

### Esempio 2: Lavoratore Precoce in Calabria
```
Input:
- Età: 58 anni
- Sesso: Donna
- Anni Contributi: 41 (precoce)
- RAL: €35,000
- Regione: Calabria (fattore 0.82)
- Previdenza complementare: €50,000

Calcoli:
- Pensione stimata: €1,246/mese
- NASPI: €1,229/mese
- R.I.T.A.: €1,201/mese
- Mesi a pensione: 0 (già idoneo!)
- Può uscire immediatamente
- Copertura R.I.T.A. disponibile
```

### Esempio 3: Lavoratore Usurante APE Sociale
```
Input:
- Età: 63 anni
- Sesso: Uomo
- Anni Contributi: 36 (usurante)
- RAL: €40,000
- Regione: Campania (fattore 0.88)
- Usurante: Sì

Calcoli:
- Pensione stimata: €1,354/mese
- APE Sociale: €1,354/mese (ammissibile)
- NASPI: €1,433/mese per 24 mesi
- Mesi a pensione: 48 mesi (4 anni)
- Copertura totale: €2,787/mese
- Gap: -€554/mese (POSITIVO!)
- Può uscire con copertura superiore allo stipendio
```

## Note Implementative

### Semplificazioni Adottate
1. **Tassazione**: Aliquota media del 35% (0.65 netto su lordo)
2. **Costo Azienda**: Moltiplicatore 1.35 su RAL
3. **Indicizzazione**: Non considerata per semplicità
4. **Finestre Uscita**: Non implementate (uscita immediata al raggiungimento requisiti)
5. **Penalizzazioni**: Non applicate (es. penalizzazione anticipata)

### Dati da Verificare con INPS
- Estratto conto contributivo completo
- Periodi scoperti o figurativi
- Contribuzione estera (totalizzazione)
- Opzione donna (se applicabile)
- Quota 103/104 (se disponibile)

### Aggiornamenti Normativi Necessari
- Soglia NASPI annuale
- Massimale APE Sociale
- Età pensione vecchiaia (speranza vita)
- Requisiti contributivi (aumenti periodici)
