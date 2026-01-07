"""
Data Extraction Module
Parses blood biomarker PDFs and WHOOP CSV exports.
"""
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Try to import pdfplumber, handle if not available
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def extract_biomarkers_from_pdf(pdf_path: str) -> Dict:
    """
    Extract biomarker data from a lab results PDF.
    Returns dict with biomarker name -> {value, unit, lab_low, lab_high, date}
    """
    if not PDF_AVAILABLE:
        return {"error": "pdfplumber not installed"}
    
    biomarkers = {}
    test_date = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
                
                # Also try extracting tables
                tables = page.extract_tables()
                for table in tables:
                    biomarkers.update(parse_table_data(table))
            
            # Parse free text for biomarkers
            text_biomarkers = parse_text_for_biomarkers(full_text)
            biomarkers.update(text_biomarkers)
            
            # Try to find test date
            test_date = extract_test_date(full_text)
    
    except Exception as e:
        return {"error": str(e)}
    
    return {
        "biomarkers": biomarkers,
        "test_date": test_date,
        "source_file": pdf_path
    }


def parse_table_data(table: List[List]) -> Dict:
    """Parse a table from PDF for biomarker data."""
    biomarkers = {}
    
    if not table or len(table) < 2:
        return biomarkers
    
    # Find header row (look for "Test", "Result", "Reference")
    header_idx = None
    for idx, row in enumerate(table):
        row_text = " ".join([str(cell).lower() if cell else "" for cell in row])
        if any(term in row_text for term in ["test", "result", "reference", "value", "range"]):
            header_idx = idx
            break
    
    if header_idx is None:
        header_idx = 0
    
    # Map columns
    headers = [str(h).lower() if h else "" for h in table[header_idx]]
    
    name_col = None
    value_col = None
    ref_col = None
    unit_col = None
    
    for i, h in enumerate(headers):
        if any(term in h for term in ["test", "name", "analyte", "component"]):
            name_col = i
        elif any(term in h for term in ["result", "value"]):
            value_col = i
        elif any(term in h for term in ["reference", "range", "normal"]):
            ref_col = i
        elif "unit" in h:
            unit_col = i
    
    # Parse data rows
    for row in table[header_idx + 1:]:
        if not row or len(row) <= max(filter(None, [name_col, value_col, ref_col, unit_col]), default=0):
            continue
        
        name = str(row[name_col]).strip() if name_col is not None and row[name_col] else None
        if not name:
            continue
        
        value_str = str(row[value_col]).strip() if value_col is not None and row[value_col] else None
        value = parse_numeric_value(value_str)
        
        ref_range = str(row[ref_col]).strip() if ref_col is not None and row[ref_col] else None
        ref_low, ref_high = parse_reference_range(ref_range)
        
        unit = str(row[unit_col]).strip() if unit_col is not None and row[unit_col] else extract_unit(value_str)
        
        if value is not None:
            biomarkers[name] = {
                "value": value,
                "unit": unit,
                "lab_low": ref_low,
                "lab_high": ref_high
            }
    
    return biomarkers


def parse_text_for_biomarkers(text: str) -> Dict:
    """Parse free text for biomarker values using regex patterns."""
    biomarkers = {}
    
    # Common patterns for lab results
    patterns = [
        # Pattern: "Biomarker Name: 5.2 mg/dL (4.0-6.0)"
        r'([A-Za-z][A-Za-z\s\-\(\)]+?)\s*:\s*([\d\.]+)\s*([a-zA-Z/%]+)?\s*\(?(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\)?',
        # Pattern: "Biomarker Name 5.2 Reference: 4.0-6.0"
        r'([A-Za-z][A-Za-z\s\-\(\)]+?)\s+([\d\.]+)\s*([a-zA-Z/%]+)?\s*(?:Reference|Ref|Range)?:?\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)',
        # Simple: "Glucose 95 mg/dL"
        r'([A-Za-z][A-Za-z\s\-\(\)]+?)\s+([\d\.]+)\s*([a-zA-Z/%]+)',
    ]
    
    for pattern in patterns[:2]:  # Use first two more specific patterns
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match[0].strip()
            value = parse_numeric_value(match[1])
            unit = match[2] if len(match) > 2 else None
            ref_low = float(match[3]) if len(match) > 3 and match[3] else None
            ref_high = float(match[4]) if len(match) > 4 and match[4] else None
            
            if value is not None and len(name) > 2:
                biomarkers[name] = {
                    "value": value,
                    "unit": unit,
                    "lab_low": ref_low,
                    "lab_high": ref_high
                }
    
    return biomarkers


def parse_numeric_value(value_str: str) -> Optional[float]:
    """Extract numeric value from string."""
    if not value_str:
        return None
    
    # Remove common non-numeric characters but keep decimal point
    cleaned = re.sub(r'[<>≤≥]', '', str(value_str))
    
    # Find first number
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def parse_reference_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse reference range string into low/high values."""
    if not range_str:
        return None, None
    
    # Pattern: "4.0-6.0" or "4.0 - 6.0" or "<5.0" etc
    match = re.search(r'(\d+\.?\d*)\s*[-–to]\s*(\d+\.?\d*)', range_str)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    # Pattern: "<5.0"
    match = re.search(r'<\s*(\d+\.?\d*)', range_str)
    if match:
        return 0, float(match.group(1))
    
    # Pattern: ">3.0"
    match = re.search(r'>\s*(\d+\.?\d*)', range_str)
    if match:
        return float(match.group(1)), None
    
    return None, None


def extract_unit(value_str: str) -> Optional[str]:
    """Extract unit from value string."""
    if not value_str:
        return None
    
    units = ['mg/dL', 'g/dL', 'ng/mL', 'pg/mL', 'U/L', 'IU/L', 'mIU/L', 
             'K/uL', 'M/uL', 'fL', '%', 'mmol/L', 'umol/L', 'ug/dL', 
             'nmol/L', 'mg/L', 'mm/hr']
    
    for unit in units:
        if unit.lower() in value_str.lower():
            return unit
    
    return None


def extract_test_date(text: str) -> Optional[str]:
    """Extract test date from PDF text."""
    date_patterns = [
        r'(?:Collection|Test|Collected|Date)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\w+\s+\d{1,2},?\s+\d{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


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
        'Total Cholesterol': [195, 190, 185, 182],
        'LDL Cholesterol': [115, 108, 102, 98],
        'HDL Cholesterol': [52, 55, 58, 62],
        'hs-CRP': [1.2, 0.9, 0.6, 0.4],
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
        'Vitamin D': [32, 45, 58, 65],
        'Vitamin B12': [450, 520, 600, 680],
        'TSH': [2.8, 2.4, 2.1, 1.9],
        'ALP': [55, 52, 50, 48],
        'Lymphocyte_pct': [32, 33, 34, 35],
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


def pdf_to_dataframe(pdf_file) -> pd.DataFrame:
    """
    Convert uploaded PDF file to DataFrame format expected by the app.
    Handles file-like objects from Streamlit file_uploader.
    """
    import tempfile
    import os
    
    if not PDF_AVAILABLE:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
    
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
        
        # Convert to DataFrame format
        rows = []
        for name, data in biomarkers.items():
            row = {"date": test_date, name: data["value"]}
            rows.append(row)
        
        # Pivot to wide format (one row with all biomarkers as columns)
        df = pd.DataFrame([{"date": test_date}])
        for name, data in biomarkers.items():
            df[name] = data["value"]
        
        return df
        
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
