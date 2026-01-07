"""
Longevity Engine - Bio-Age Calculations
Implements practical biological age estimation and organ system scoring.
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional

# Simplified PhenoAge-inspired calculation
# Based on deviation from optimal biomarker values
BIOAGE_WEIGHTS = {
    "albumin": {"optimal": 4.5, "weight": -2.0, "per_unit": 0.1},  # g/dL, lower = older
    "creatinine": {"optimal": 0.9, "weight": 1.5, "per_unit": 0.1},  # mg/dL, higher = older
    "glucose": {"optimal": 85, "weight": 0.15, "per_unit": 10},  # mg/dL
    "crp": {"optimal": 0.3, "weight": 2.0, "per_unit": 0.5},  # mg/L, higher = older
    "lymphocyte_pct": {"optimal": 35, "weight": -0.1, "per_unit": 5},  # %, lower = older
    "mcv": {"optimal": 88, "weight": 0.1, "per_unit": 5},  # fL
    "rdw": {"optimal": 12.5, "weight": 2.0, "per_unit": 0.5},  # %, higher = older
    "alp": {"optimal": 55, "weight": 0.05, "per_unit": 10},  # U/L
    "wbc": {"optimal": 5.5, "weight": 0.3, "per_unit": 1},  # K/uL
    "hba1c": {"optimal": 5.0, "weight": 3.0, "per_unit": 0.2},  # %, higher = older
    "triglycerides": {"optimal": 80, "weight": 0.05, "per_unit": 20},  # mg/dL
    "hdl": {"optimal": 65, "weight": -0.1, "per_unit": 10},  # mg/dL, lower = older
}


def calculate_phenoage(
    chronological_age: float,
    albumin: float = None,
    creatinine: float = None,
    glucose: float = None,
    crp: float = None,
    lymphocyte_pct: float = None,
    mcv: float = None,
    rdw: float = None,
    alp: float = None,
    wbc: float = None,
    hba1c: float = None,
    triglycerides: float = None,
    hdl: float = None
) -> Dict:
    """Calculate biological age estimate based on biomarker deviations."""
    
    # Collect provided values
    values = {
        "albumin": albumin, "creatinine": creatinine, "glucose": glucose,
        "crp": crp, "lymphocyte_pct": lymphocyte_pct, "mcv": mcv,
        "rdw": rdw, "alp": alp, "wbc": wbc, "hba1c": hba1c,
        "triglycerides": triglycerides, "hdl": hdl
    }
    
    # Calculate age adjustment based on deviations
    age_adjustments = []
    
    for marker, value in values.items():
        if value is None or marker not in BIOAGE_WEIGHTS:
            continue
        
        params = BIOAGE_WEIGHTS[marker]
        deviation = (value - params["optimal"]) / params["per_unit"]
        adjustment = deviation * params["weight"]
        age_adjustments.append(adjustment)
    
    if not age_adjustments:
        return {
            "phenoage": chronological_age,
            "age_acceleration": 0,
            "pace": 1.0,
            "interpretation": "Insufficient data for bio-age calculation"
        }
    
    # Calculate biological age
    total_adjustment = np.sum(age_adjustments)
    phenoage = chronological_age + total_adjustment
    
    # Clamp to reasonable range
    phenoage = np.clip(phenoage, chronological_age - 15, chronological_age + 15)
    
    age_acceleration = phenoage - chronological_age
    pace = 1.0 + (age_acceleration / max(chronological_age, 1)) * 0.5
    pace = np.clip(pace, 0.7, 1.3)
    
    return {
        "phenoage": round(phenoage, 1),
        "age_acceleration": round(age_acceleration, 1),
        "pace": round(pace, 3),
        "interpretation": interpret_phenoage(age_acceleration),
        "markers_used": len(age_adjustments)
    }


def interpret_phenoage(acceleration: float) -> str:
    if acceleration <= -5:
        return "Significantly younger than chronological age - excellent biological health"
    elif acceleration <= -2:
        return "Moderately younger - good biological markers"
    elif acceleration <= 2:
        return "Aging at expected rate - average biological health"
    elif acceleration <= 5:
        return "Moderately accelerated aging - consider interventions"
    else:
        return "Significantly accelerated aging - recommend comprehensive lifestyle changes"


def estimate_dunedin_pace(biomarkers: Dict) -> Optional[Dict]:
    """Estimate pace of aging from available biomarkers."""
    optimal_ranges = {
        "crp": (0, 0.5), "glucose": (70, 90), "hba1c": (4.8, 5.2),
        "hdl": (60, 100), "triglycerides": (50, 100), "albumin": (4.2, 5.0),
        "creatinine": (0.7, 1.1)
    }
    
    pace_scores = []
    for marker, (low, high) in optimal_ranges.items():
        value = biomarkers.get(marker)
        if value is None:
            continue
        mid = (low + high) / 2
        if value < low:
            deviation = (low - value) / mid * 0.5
        elif value > high:
            deviation = (value - high) / mid * 0.5
        else:
            deviation = 0
        pace_scores.append(deviation)
    
    if len(pace_scores) < 3:
        return None
    
    pace = 1.0 + np.mean(pace_scores)
    pace = np.clip(pace, 0.7, 1.3)
    
    return {
        "pace_estimate": round(pace, 2),
        "confidence": "low" if len(pace_scores) < 5 else "moderate",
        "interpretation": interpret_pace(pace)
    }


def interpret_pace(pace: float) -> str:
    if pace < 0.85: return "Aging slower than normal - excellent"
    elif pace < 0.95: return "Aging slightly slower - very good"
    elif pace < 1.05: return "Aging at normal pace"
    elif pace < 1.15: return "Aging slightly faster - monitor"
    else: return "Aging faster than normal - interventions recommended"


def calculate_organ_system_scores(biomarkers: Dict) -> Dict:
    """Calculate health scores for each organ system (0-100 scale)."""
    from modules.optimal_ranges import get_optimal_range, normalize_biomarker_name
    
    systems = {
        "Metabolic": ["Glucose", "HbA1c", "Triglycerides", "Insulin"],
        "Inflammatory": ["hs-CRP", "WBC", "Albumin", "Homocysteine"],
        "Hematologic": ["Ferritin", "MCV", "RDW", "Hemoglobin", "Iron"],
        "Liver": ["ALT", "AST", "ALP", "GGT", "Bilirubin"],
        "Kidney": ["Creatinine", "BUN", "eGFR", "Uric Acid"],
        "Thyroid": ["TSH", "Free T4", "Free T3"],
        "Nutritional": ["Vitamin D", "Vitamin B12", "Folate", "Magnesium"],
    }
    
    scores = {}
    for system, markers in systems.items():
        marker_scores = []
        for marker in markers:
            normalized = normalize_biomarker_name(marker)
            value = None
            for key in biomarkers:
                if normalize_biomarker_name(key) == normalized:
                    value = biomarkers[key]
                    break
            if value is None:
                continue
            
            optimal = get_optimal_range(marker)
            if optimal is None:
                continue
            
            opt_low, opt_high = optimal["optimal_low"], optimal["optimal_high"]
            opt_mid = (opt_low + opt_high) / 2
            opt_range = max(opt_high - opt_low, 0.01)
            
            if opt_low <= value <= opt_high:
                distance = abs(value - opt_mid)
                score = 100 - (distance / opt_range * 20)
            else:
                if value < opt_low:
                    deviation = (opt_low - value) / opt_range
                else:
                    deviation = (value - opt_high) / opt_range
                score = max(0, 80 - deviation * 30)
            
            marker_scores.append(score)
        
        if marker_scores:
            scores[system] = {
                "score": round(np.mean(marker_scores), 1),
                "markers_evaluated": len(marker_scores),
                "interpretation": interpret_score(np.mean(marker_scores))
            }
        else:
            scores[system] = {"score": None, "markers_evaluated": 0, "interpretation": "Insufficient data"}
    
    return scores


def interpret_score(score: float) -> str:
    if score >= 90: return "Excellent"
    elif score >= 75: return "Good"
    elif score >= 60: return "Fair"
    elif score >= 40: return "Needs attention"
    else: return "Requires intervention"


def get_phenoage_requirements() -> Dict:
    return {
        "required": ["Albumin", "Creatinine", "Glucose", "CRP", "WBC"],
        "optional": ["MCV", "RDW", "ALP", "Lymphocyte%", "HbA1c", "HDL", "Triglycerides"]
    }
