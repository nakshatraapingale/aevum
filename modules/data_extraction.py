"""
Data Extraction Module
Parses blood biomarker PDFs and WHOOP CSV exports.
Uses PyMuPDF (fitz) for fast PDF parsing.
"""
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Try to import fitz (PyMuPDF) - faster than pdfplumber
try:
    import fitz
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# =============================================================================
# BIOMARKER EXTRACTION PATTERNS
# =============================================================================

# Patterns for extracting biomarkers from Orange Health style reports
BIOMARKER_PATTERNS = [
    # Metabolic
    ("Glucose", r"(?:Fasting\s+)?(?:Blood\s+)?Glucose.*?(\d+\.?\d*)\s*mg/dL"),
    ("HbA1c", r"HbA1c.*?(\d+\.?\d*)\s*%"),
    ("Fasting_Insulin", r"(?:Fasting\s+)?Insulin.*?(\d+\.?\d*)\s*(?:uIU|µIU)/mL"),
    
    # Lipids
    ("Total_Cholesterol", r"Cholesterol,?\s*Total.*?(\d+\.?\d*)\s*mg/dL"),
    ("Triglycerides", r"Triglycerides.*?(\d+\.?\d*)\s*mg/dL"),
    ("HDL", r"High-Density Lipoprotein.*?HDL.*?Cholesterol.*?(\d+\.?\d*)\s*mg/dL"),
    ("LDL", r"Low-Density Lipoprotein.*?LDL.*?Cholesterol.*?(?:Calculated\s+)?(\d+\.?\d*)\s*mg/dL"),
    ("VLDL", r"Very Low-Density.*?VLDL.*?(\d+\.?\d*)\s*mg/dL"),
    ("Non_HDL", r"Non-High Density.*?Non-HDL.*?(\d+\.?\d*)\s*mg/dL"),
    
    # Liver
    ("AST", r"Aspartate Aminotransferase.*?AST.*?(\d+\.?\d*)\s*U/L"),
    ("ALT", r"Alanine Transaminase.*?ALT.*?(\d+\.?\d*)\s*U/L"),
    ("ALP", r"Alkaline Phosphatase.*?ALP.*?(\d+\.?\d*)\s*U/L"),
    ("GGT", r"Gamma-Glutamyl.*?GGT.*?(\d+\.?\d*)\s*U/L"),
    ("Bilirubin_Total", r"Bilirubin,?\s*Total.*?(\d+\.?\d*)\s*mg/dL"),
    ("Bilirubin_Direct", r"Bilirubin,?\s*Direct.*?(\d+\.?\d*)\s*mg/dL"),
    
    # Proteins
    ("Albumin", r"Albumin\s+(?:Bromo|BCG).*?(\d+\.?\d*)\s*g/dL"),
    ("Protein_Total", r"(?:Total\s+)?Protein\s+(?:Biuret|Refractometry)?\s*(\d+\.?\d*)\s*g/dL"),
    ("Globulin", r"Globulin\s+(?:Calculated\s+)?(\d+\.?\d*)\s*g/dL"),
    
    # Kidney
    ("Creatinine", r"Creatinine.*?(\d+\.?\d*)\s*mg/dL"),
    ("Urea", r"(?:Blood\s+)?Urea(?:\s+Nitrogen)?.*?(\d+\.?\d*)\s*mg/dL"),
    ("BUN", r"BUN.*?(\d+\.?\d*)\s*mg/dL"),
    ("Uric_Acid", r"Uric Acid.*?(\d+\.?\d*)\s*mg/dL"),
    ("eGFR", r"eGFR.*?(\d+\.?\d*)\s*mL/min"),
    
    # Inflammation
    ("hs_CRP", r"C-Reactive Protein.*?CRP.*?<?(\d+\.?\d*)\s*mg/L"),
    ("ESR", r"(?:Erythrocyte\s+)?Sedimentation Rate.*?ESR.*?(\d+\.?\d*)\s*mm"),
    
    # CBC - Blood Cells
    ("WBC", r"(?:Total\s+)?(?:WBC|Leucocyte|White Blood Cell).*?Count.*?(\d+\.?\d*)\s*(?:x\s*10|cells|thou)"),
    ("RBC", r"(?:Total\s+)?(?:RBC|Red Blood Cell).*?Count.*?(\d+\.?\d*)\s*(?:x\s*10|mill)"),
    ("Hemoglobin", r"(?:Haemoglobin|Hemoglobin)\s*(?:\(Hb\))?\s*(?:Photometry|Cyanmethemoglobin)?.*?(\d+\.?\d*)\s*g/dL"),
    ("Hematocrit", r"(?:Hematocrit|Haematocrit|PCV).*?(\d+\.?\d*)\s*%"),
    ("MCV", r"MCV\s*(?:Mean Corpuscular Volume)?.*?(\d+\.?\d*)\s*fL"),
    ("MCH", r"MCH\s+(?:Mean Corpuscular|Calculated)?.*?(\d+\.?\d*)\s*pg"),
    ("MCHC", r"MCHC.*?(\d+\.?\d*)\s*g/dL"),
    ("RDW", r"RDW.*?(\d+\.?\d*)\s*%"),
    ("Platelet", r"Platelet.*?Count.*?(\d+\.?\d*)\s*(?:x\s*10|Lac|thou)"),
    ("MPV", r"MPV.*?(\d+\.?\d*)\s*fL"),
    
    # WBC Differential
    ("Neutrophils_pct", r"Neutrophils?.*?(\d+\.?\d*)\s*%"),
    ("Lymphocytes_pct", r"Lymphocytes?.*?(\d+\.?\d*)\s*%"),
    ("Monocytes_pct", r"Monocytes?.*?(\d+\.?\d*)\s*%"),
    ("Eosinophils_pct", r"Eosinophils?.*?(\d+\.?\d*)\s*%"),
    ("Basophils_pct", r"Basophils?.*?(\d+\.?\d*)\s*%"),
    
    # Thyroid
    ("TSH", r"TSH.*?(\d+\.?\d*)\s*(?:mIU|uIU|µIU)/(?:mL|L)"),
    ("T3_Total", r"(?:Total\s+)?T3\s+(?!Uptake).*?(\d+\.?\d*)\s*ng/dL"),
    ("T4_Total", r"(?:Total\s+)?T4\s+(?!Free).*?(\d+\.?\d*)\s*(?:ug|µg)/dL"),
    ("FT3", r"(?:Free\s+)?T3.*?FT3.*?(\d+\.?\d*)\s*pg/mL"),
    ("FT4", r"(?:Free\s+)?T4.*?FT4.*?(\d+\.?\d*)\s*ng/dL"),
    
    # Vitamins & Minerals
    ("Vitamin_D", r"Vitamin\s*D.*?25.*?(\d+\.?\d*)\s*ng/mL"),
    ("Vitamin_B12", r"Vitamin\s*B12.*?(\d+\.?\d*)\s*pg/mL"),
    ("Folate", r"Fol(?:ate|ic\s+Acid).*?(\d+\.?\d*)\s*ng/mL"),
    ("Iron", r"(?:Serum\s+)?Iron\s+(?!Binding).*?(\d+\.?\d*)\s*(?:ug|µg)/dL"),
    ("Ferritin", r"Ferritin.*?(\d+\.?\d*)\s*ng/mL"),
    ("TIBC", r"(?:Total\s+)?Iron Binding.*?TIBC.*?(\d+\.?\d*)\s*(?:ug|µg)/dL"),
    ("Transferrin_Sat", r"Transferrin\s*Saturation.*?(\d+\.?\d*)\s*%"),
    
    # Electrolytes
    ("Calcium", r"Calcium\s+(?!Ionized).*?(\d+\.?\d*)\s*mg/dL"),
    ("Phosphorus", r"Phosphorus.*?(\d+\.?\d*)\s*mg/dL"),
    ("Magnesium", r"Magnesium.*?(\d+\.?\d*)\s*(?:mg/dL|mEq/L)"),
    ("Sodium", r"Sodium.*?(\d+\.?\d*)\s*(?:mEq|mmol)/L"),
    ("Potassium", r"Potassium.*?(\d+\.?\d*)\s*(?:mEq|mmol)/L"),
    ("Chloride", r"Chloride.*?(\d+\.?\d*)\s*(?:mEq|mmol)/L"),
    
    # Hormones
    ("Testosterone_Total", r"Testosterone.*?Total.*?(\d+\.?\d*)\s*ng/dL"),
    ("Testosterone_Free", r"(?:Free\s+)?Testosterone.*?Free.*?(\d+\.?\d*)\s*pg/mL"),
    ("Cortisol", r"Cortisol.*?(\d+\.?\d*)\s*(?:ug|µg)/dL"),
    ("DHEA_S", r"DHEA.*?(\d+\.?\d*)\s*(?:ug|µg)/dL"),
    
    # Cardiac
    ("Homocysteine", r"Homocysteine.*?(\d+\.?\d*)\s*(?:umol|µmol)/L"),
    ("Lp_a", r"Lp\s*\(?a\)?.*?(\d+\.?\d*)\s*(?:mg/dL|nmol/L)"),
    ("ApoB", r"Apo(?:lipoprotein)?\s*B.*?(\d+\.?\d*)\s*mg/dL"),
    ("ApoA1", r"Apo(?:lipoprotein)?\s*A.*?(\d+\.?\d*)\s*mg/dL"),
]


def extract_biomarkers_from_text(text: str) -> Dict[str, float]:
    """
    Extract biomarkers from PDF text using regex patterns.
    Returns dict of biomarker_name -> value.
    """
    biomarkers = {}
    
    for name, pattern in BIOMARKER_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                val = float(match.group(1))
                # Sanity check - skip obviously wrong values
                if val > 0 and val < 100000:
                    biomarkers[name] = val
            except (ValueError, IndexError):
                pass
    
    return biomarkers


def extract_biomarkers_from_pdf(pdf_path: str) -> Dict:
    """
    Extract biomarker data from a lab results PDF using PyMuPDF.
    Returns dict with biomarker name -> value.
    """
    if not PDF_AVAILABLE:
        return {"error": "PyMuPDF (fitz) not installed. Run: pip install pymupdf"}
    
    try:
        doc = fitz.open(pdf_path)
        all_text = ""
        for page in doc:
            all_text += page.get_text() + "\n"
        doc.close()
        
        # Extract biomarkers
        biomarkers = extract_biomarkers_from_text(all_text)
        
        # Try to find test date
        test_date = extract_test_date(all_text)
        
        return {
            "biomarkers": biomarkers,
            "test_date": test_date,
            "source_file": pdf_path,
            "text_length": len(all_text)
        }
    
    except Exception as e:
        return {"error": str(e)}


def extract_test_date(text: str) -> Optional[str]:
    """Extract test date from PDF text."""
    date_patterns = [
        r'(?:Collection|Collected|Test\s+Date|Date)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
        r'(\w+\s+\d{1,2},?\s+\d{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def pdf_to_dataframe(pdf_file) -> pd.DataFrame:
    """
    Convert uploaded PDF file to DataFrame format expected by the app.
    Handles file-like objects from Streamlit file_uploader.
    """
    import tempfile
    import os
    
    if not PDF_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) not installed. Run: pip install pymupdf")
    
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name
    
    try:
        # Extract biomarkers
        result = extract_biomarkers_from_pdf(tmp_path)
        
        if "error" in result:
            raise ValueError(f"PDF parsing error: {result['error']}")
        
        biomarkers = result.get("biomarkers", {})
        test_date = result.get("test_date", datetime.now().strftime("%Y-%m-%d"))
        
        if not biomarkers:
            raise ValueError("No biomarkers found in PDF. Try uploading a CSV instead.")
        
        # Convert to DataFrame format (one row with all biomarkers as columns)
        df = pd.DataFrame([{"date": test_date, **biomarkers}])
        
        return df
        
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


def parse_whoop_csv(csv_path: str) -> pd.DataFrame:
    """
    Parse WHOOP export CSV file.
    Returns DataFrame with date index and metrics.
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})
    
    # Standardize column names
    df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
    
    # Find date column
    date_col = None
    for col in df.columns:
        if any(term in col for term in ['date', 'day', 'timestamp']):
            date_col = col
            break
    
    if date_col:
        df['date'] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.set_index('date').sort_index()
    
    return df


def calculate_whoop_rolling_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 7-day and 30-day rolling averages for WHOOP metrics.
    """
    metrics = ['hrv', 'rhr', 'sleep_efficiency', 'respiratory_rate', 
               'recovery_score', 'strain', 'sleep_performance']
    
    # Find available metrics (with flexible column matching)
    metric_cols = {}
    for metric in metrics:
        for col in df.columns:
            if metric.replace('_', '') in col.replace('_', '').replace(' ', '').lower():
                metric_cols[metric] = col
                break
    
    result_df = df.copy()
    
    for metric, col in metric_cols.items():
        if col in df.columns:
            # 7-day rolling average
            result_df[f'{metric}_7d_avg'] = df[col].rolling(window=7, min_periods=3).mean()
            # 30-day rolling average
            result_df[f'{metric}_30d_avg'] = df[col].rolling(window=30, min_periods=7).mean()
    
    return result_df


def create_sample_blood_data() -> pd.DataFrame:
    """Create sample blood biomarker data for testing."""
    dates = pd.date_range(start='2023-01-15', periods=4, freq='3ME')
    
    data = {
        'date': dates,
        'Glucose': [95, 92, 88, 91],
        'HbA1c': [5.4, 5.3, 5.1, 5.2],
        'Triglycerides': [120, 110, 95, 100],
        'Total_Cholesterol': [195, 190, 185, 182],
        'LDL': [115, 108, 102, 98],
        'HDL': [52, 55, 58, 62],
        'hs_CRP': [1.2, 0.9, 0.6, 0.4],
        'Albumin': [4.3, 4.4, 4.5, 4.6],
        'Creatinine': [0.95, 0.92, 0.90, 0.88],
        'ALT': [28, 25, 22, 20],
        'AST': [24, 22, 21, 19],
        'WBC': [6.5, 6.2, 5.8, 5.5],
        'RBC': [4.8, 4.9, 5.0, 5.0],
        'Hemoglobin': [14.5, 14.8, 15.0, 15.1],
        'MCV': [88, 87, 86, 87],
        'RDW': [13.5, 13.2, 12.8, 12.6],
        'Ferritin': [85, 95, 110, 120],
        'Vitamin_D': [32, 45, 58, 65],
        'Vitamin_B12': [450, 520, 600, 680],
        'TSH': [2.8, 2.4, 2.1, 1.9],
        'ALP': [55, 52, 50, 48],
        'Lymphocytes_pct': [32, 33, 34, 35],
    }
    
    return pd.DataFrame(data)


def create_sample_whoop_data(days: int = 90) -> pd.DataFrame:
    """Create sample WHOOP data for testing."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Simulate realistic WHOOP metrics with some autocorrelation
    hrv_base = 45
    rhr_base = 58
    
    hrv = np.cumsum(np.random.normal(0, 3, days)) + hrv_base + np.random.normal(0, 5, days)
    hrv = np.clip(hrv, 20, 120)
    
    rhr = np.cumsum(np.random.normal(0, 0.5, days)) + rhr_base + np.random.normal(0, 2, days)
    rhr = np.clip(rhr, 45, 75)
    
    data = {
        'date': dates,
        'hrv': hrv.astype(int),
        'rhr': rhr.astype(int),
        'sleep_efficiency': np.clip(np.random.normal(82, 8, days), 50, 100),
        'respiratory_rate': np.clip(np.random.normal(15.5, 1.2, days), 12, 20),
        'recovery_score': np.clip(np.random.normal(65, 15, days), 0, 100),
        'strain': np.clip(np.random.normal(12, 4, days), 0, 21),
        'sleep_hours': np.clip(np.random.normal(7.2, 1.0, days), 4, 10),
    }
    
    df = pd.DataFrame(data).set_index('date')
    return calculate_whoop_rolling_averages(df)


def merge_blood_whoop_data(blood_df: pd.DataFrame, whoop_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge blood biomarker data with WHOOP metrics for correlation analysis.
    Uses forward-fill to propagate blood values to daily WHOOP records.
    """
    # Ensure both have datetime index
    if 'date' in blood_df.columns:
        blood_df = blood_df.set_index('date')
    blood_df.index = pd.to_datetime(blood_df.index)
    
    if 'date' in whoop_df.columns:
        whoop_df = whoop_df.set_index('date')
    whoop_df.index = pd.to_datetime(whoop_df.index)
    
    # Merge and forward-fill blood values
    merged = whoop_df.join(blood_df, how='left')
    
    # Forward-fill blood biomarkers (they don't change daily)
    blood_cols = [col for col in blood_df.columns if col not in whoop_df.columns]
    merged[blood_cols] = merged[blood_cols].fillna(method='ffill')
    
    return merged
