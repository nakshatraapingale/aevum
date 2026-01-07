# Aevum - Longevity Health Dashboard
# 🧬 Digital Twin Dashboard - Longevity Medicine Platform

A comprehensive, stateful data-analysis pipeline and Streamlit-based dashboard that integrates longitudinal blood biomarker data with high-frequency WHOOP biometrics for personalized longevity optimization.

## Features

### Phase 1: Deep Data Extraction & Normalization
- **Blood Analytics**: Extract biomarkers from uploaded PDFs with lab reference ranges
- **Longevity Optimal Ranges**: 50+ biomarkers with evidence-based longevity targets
- **WHOOP Integration**: Parse WHOOP CSV exports with 7-day and 30-day rolling averages

### Phase 2: The Longevity Engine
- **Bio-Age Calculation**: Practical biological age estimation based on biomarker deviations
- **DunedinPACE Proxy**: Pace of aging estimation from blood markers
- **Organ System Scoring**: Health scores for 7 organ systems (0-100 scale)

### Phase 3: Cross-Dataset Correlation
- **Lagging Indicator Analysis**: Time-series cross-correlation between blood markers and WHOOP metrics
- **Performance Ceiling Test**: Statistical analysis of nutrient deficiencies vs performance metrics

### Phase 4: Master Dashboard

#### Tab 1: Bio-Age Summary
- Biological age gauge (chronological vs biological)
- Pace of aging speedometer
- Organ system radar chart

#### Tab 2: Optimal Zone
- Traffic light system for all biomarkers
- Lab normal vs longevity optimal comparison
- Category filtering

#### Tab 3: Correlation Matrix
- Blood marker ↔ WHOOP metric heatmaps
- Lag analysis visualization
- Performance ceiling detection

#### Tab 4: Actionable Protocol
- Overall health grade (A-F)
- Top 5 priority interventions
- Evidence-based lifestyle recommendations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## Data Input

### Blood Biomarkers
Upload a CSV with columns matching biomarker names (e.g., Glucose, HbA1c, hs-CRP, etc.)

### WHOOP Data
Export your WHOOP data as CSV from the WHOOP app and upload directly.

## Project Structure

```
digital-twin/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── modules/
│   ├── optimal_ranges.py     # Longevity optimal range definitions
│   ├── longevity_engine.py   # Bio-age and organ scoring
│   ├── data_extraction.py    # PDF and CSV parsing
│   ├── correlation_analysis.py # Cross-correlation engine
│   └── insights_engine.py    # Protocol generation
└── data/                     # Data storage
```

## Longevity Optimal Ranges

Key biomarkers with longevity-optimized targets (different from standard lab ranges):

| Biomarker | Longevity Optimal | Standard Lab Range |
|-----------|-------------------|-------------------|
| hs-CRP | <0.5 mg/L | <3.0 mg/L |
| HbA1c | 4.8-5.2% | 4.0-5.6% |
| Vitamin D | 50-80 ng/mL | 30-100 ng/mL |
| ApoB | 40-70 mg/dL | <130 mg/dL |
| Ferritin | 50-150 ng/mL | 30-400 ng/mL |

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Statistical Analysis**: SciPy, StatsModels
- **Visualization**: Plotly
- **PDF Parsing**: pdfplumber

## References

- Levine ME, et al. "An epigenetic biomarker of aging" (2018) - PhenoAge algorithm
- Belsky DW, et al. "DunedinPACE" (2022) - Pace of aging estimation
- Bryan Johnson's Blueprint Protocol - Biomarker targets
- Peter Attia's "Outlive" - Longevity optimal ranges

## Deployment

### Streamlit Cloud Deployment

1. Push your code to GitHub (see below)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository and `app.py`
5. Add your secrets in "Advanced settings":
   ```toml
   SUPABASE_URL = "your-url-here"
   SUPABASE_KEY = "your-key-here"
   ```
6. Click "Deploy"!

### Environment Variables

For local development, create `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

**Never commit this file to Git** - it's in `.gitignore` for safety.

## Authentication

The app uses Supabase for user authentication:
- Email/password signup and login
- User-specific data storage
- Demo mode for trying without an account
