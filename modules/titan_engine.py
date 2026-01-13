"""
Titan Protocol v2 - Longevity Scoring Engine
Implements hierarchical biomarker weighting with gradient scoring.
"""
from typing import Dict, List, Optional, Any
import math

# =============================================================================
# GRADIENT SCORING FUNCTION
# =============================================================================

def calculate_gradient_score(value: float, config: Dict) -> float:
    """
    Calculate score using 3-zone gradient interpolation.
    Zone A (Optimal): Score = 100
    Zone B (Functional): Score interpolates 100 -> 40
    Zone C (Critical): Score interpolates 40 -> 5
    Zone D (Failure): Score = 5
    """
    opt = config.get('opt', 50)
    direction = config.get('dir', 'low')
    
    # For split markers, func_limit may not exist - use defaults
    func_limit = config.get('func_limit', opt)
    crit_limit = config.get('crit_limit', opt)
    
    def lerp(v, start, end, score_start, score_end):
        if abs(end - start) == 0:
            return score_start
        fraction = abs(v - start) / abs(end - start)
        return score_start - (fraction * (score_start - score_end))
    
    # LOWER IS BETTER (e.g., ApoB, CRP, Glucose)
    if direction == 'low':
        if value <= opt:
            return 100
        if value >= crit_limit:
            return 5
        if value <= func_limit:
            return lerp(value, opt, func_limit, 100, 40)
        else:
            return lerp(value, func_limit, crit_limit, 40, 5)
    
    # HIGHER IS BETTER (e.g., HDL, HRV)
    elif direction == 'high':
        if value >= opt:
            return 100
        if value <= crit_limit:
            return 5
        if value >= func_limit:
            return lerp(value, func_limit, opt, 40, 100)
        else:
            return lerp(value, crit_limit, func_limit, 5, 40)
    
    # SPLIT / GOLDILOCKS (e.g., Sodium - both high and low are bad)
    elif direction == 'split':
        opt_low = config.get('opt_low', opt * 0.9)
        opt_high = config.get('opt_high', opt * 1.1)
        if opt_low <= value <= opt_high:
            return 100
        elif value < opt_low:
            return lerp(value, crit_limit, opt_low, 5, 100)
        else:
            return lerp(value, opt_high, crit_limit, 100, 5)
    
    return 50  # Default fallback


# =============================================================================
# DERIVED METRICS CALCULATION
# =============================================================================

def enrich_labs(labs: Dict) -> Dict:
    """Calculate derived/virtual biomarkers from raw inputs."""
    enriched = labs.copy()
    
    # HOMA-IR (Insulin Resistance)
    if 'Fasting_Insulin' in labs and 'Glucose' in labs:
        enriched['HOMA_IR'] = (labs['Fasting_Insulin'] * labs['Glucose']) / 405.0
    
    # Non-HDL Cholesterol
    if 'Total_Cholesterol' in labs and 'HDL' in labs:
        enriched['Non_HDL'] = labs['Total_Cholesterol'] - labs['HDL']
    
    # Remnant Cholesterol
    if all(k in labs for k in ['Total_Cholesterol', 'HDL', 'LDL']):
        enriched['Remnant_Cholesterol'] = labs['Total_Cholesterol'] - labs['HDL'] - labs['LDL']
    
    # Neutrophil-to-Lymphocyte Ratio (NLR)
    if 'Neutrophils' in labs and 'Lymphocytes' in labs and labs['Lymphocytes'] > 0:
        enriched['NLR'] = labs['Neutrophils'] / labs['Lymphocytes']
    
    # A/G Ratio
    if 'Albumin' in labs and 'Globulin' in labs and labs['Globulin'] > 0:
        enriched['AG_Ratio'] = labs['Albumin'] / labs['Globulin']
    
    # Transferrin Saturation (if we have Iron and TIBC)
    if 'Iron' in labs and 'TIBC' in labs and labs['TIBC'] > 0:
        enriched['Transferrin_Sat'] = (labs['Iron'] / labs['TIBC']) * 100
    
    return enriched


# =============================================================================
# SYSTEM CONFIGURATIONS - TITAN PROTOCOL V2
# =============================================================================

TITAN_SYSTEMS = {
    "cardiovascular": {
        "name": "Heart Health",
        "weight": 0.20,
        "buckets": [
            {
                "name": "Atherogenic Load",
                "weight": 0.45,
                "markers": [
                    {"id": "ApoB", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 70, "func_limit": 100, "crit_limit": 130}, "dir": "low"},
                    {"id": "LDL_P", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 1000, "func_limit": 1300, "crit_limit": 1600}, "dir": "low"},
                    {"id": "Lp_a", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 20, "func_limit": 50, "crit_limit": 100}, "dir": "low"},
                    {"id": "sdLDL", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 20, "func_limit": 30, "crit_limit": 50}, "dir": "low"},
                    {"id": "Non_HDL", "status": "Proxy", "proxy_for": "ApoB", "thresholds": {"opt": 100, "func_limit": 130, "crit_limit": 160}, "dir": "low"},
                    {"id": "LDL", "status": "Proxy", "proxy_for": "ApoB", "thresholds": {"opt": 70, "func_limit": 100, "crit_limit": 130}, "dir": "low"},
                ]
            },
            {
                "name": "Inflammation",
                "weight": 0.25,
                "markers": [
                    {"id": "hs_CRP", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 0.5, "func_limit": 2.0, "crit_limit": 5.0}, "dir": "low"},
                    {"id": "Homocysteine", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 7, "func_limit": 10, "crit_limit": 15}, "dir": "low"},
                    {"id": "IL_6", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 1.0, "func_limit": 3.0, "crit_limit": 6.0}, "dir": "low"},
                    {"id": "Fibrinogen", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 250, "func_limit": 350, "crit_limit": 450}, "dir": "low"},
                    {"id": "ESR", "status": "Proxy", "proxy_for": "hs_CRP", "thresholds": {"opt": 5, "func_limit": 15, "crit_limit": 30}, "dir": "low"},
                ]
            },
            {
                "name": "Lipid Clearance",
                "weight": 0.15,
                "markers": [
                    {"id": "Triglycerides", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 70, "func_limit": 120, "crit_limit": 200}, "dir": "low"},
                    {"id": "HDL", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 60, "func_limit": 45, "crit_limit": 35}, "dir": "high"},
                    {"id": "Remnant_Cholesterol", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 15, "func_limit": 25, "crit_limit": 40}, "dir": "low"},
                ]
            },
            {
                "name": "Fatty Acids",
                "weight": 0.10,
                "markers": [
                    {"id": "Omega3_Index", "status": "Primary", "weight": 0.60, "thresholds": {"opt": 8, "func_limit": 5, "crit_limit": 3}, "dir": "high"},
                    {"id": "Omega6_Omega3_Ratio", "status": "Contributor", "weight": 0.40, "thresholds": {"opt": 3, "func_limit": 6, "crit_limit": 10}, "dir": "low"},
                ]
            },
            {
                "name": "Viscosity",
                "weight": 0.05,
                "markers": [
                    {"id": "Hematocrit", "status": "Primary", "weight": 1.0, "thresholds": {"opt": 42, "func_limit": 48, "crit_limit": 54}, "dir": "low"},
                    {"id": "Hemoglobin", "status": "Proxy", "proxy_for": "Hematocrit", "thresholds": {"opt": 14, "func_limit": 16, "crit_limit": 18}, "dir": "low"},
                ]
            }
        ]
    },
    "metabolic": {
        "name": "Metabolic Health",
        "weight": 0.20,
        "buckets": [
            {
                "name": "Glycemic Control",
                "weight": 0.45,
                "markers": [
                    {"id": "Fasting_Insulin", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 4, "func_limit": 8, "crit_limit": 15}, "dir": "low"},
                    {"id": "HbA1c", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 5.0, "func_limit": 5.6, "crit_limit": 6.4}, "dir": "low"},
                    {"id": "HOMA_IR", "status": "Primary", "weight": 0.20, "thresholds": {"opt": 1.0, "func_limit": 2.0, "crit_limit": 3.5}, "dir": "low"},
                    {"id": "Glucose", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 85, "func_limit": 100, "crit_limit": 126}, "dir": "low"},
                    {"id": "C_Peptide", "status": "Secondary", "weight": 0.10, "thresholds": {"opt": 1.5, "func_limit": 3.0, "crit_limit": 5.0}, "dir": "low"},
                ]
            },
            {
                "name": "Mitochondrial",
                "weight": 0.20,
                "markers": [
                    {"id": "Lactate", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 0.8, "func_limit": 1.5, "crit_limit": 2.5}, "dir": "low"},
                    {"id": "CoQ10", "status": "Secondary", "weight": 0.30, "thresholds": {"opt": 1.0, "func_limit": 0.6, "crit_limit": 0.3}, "dir": "high"},
                    {"id": "BHB", "status": "Secondary", "weight": 0.35, "thresholds": {"opt": 0.3, "func_limit": 0.1, "crit_limit": 0.05}, "dir": "high"},
                ]
            },
            {
                "name": "Electrolytes",
                "weight": 0.15,
                "markers": [
                    {"id": "Magnesium", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 2.2, "func_limit": 1.8, "crit_limit": 1.5}, "dir": "high"},
                    {"id": "Potassium", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 4.2, "func_limit": 3.8, "crit_limit": 3.2}, "dir": "high"},
                    {"id": "Sodium", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 140, "opt_low": 136, "opt_high": 144, "crit_limit": 130}, "dir": "split"},
                ]
            },
            {
                "name": "Micronutrients",
                "weight": 0.20,
                "markers": [
                    {"id": "Vitamin_D", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 50, "func_limit": 30, "crit_limit": 20}, "dir": "high"},
                    {"id": "B12", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 600, "func_limit": 400, "crit_limit": 200}, "dir": "high"},
                    {"id": "Folate", "status": "Secondary", "weight": 0.20, "thresholds": {"opt": 15, "func_limit": 8, "crit_limit": 4}, "dir": "high"},
                    {"id": "B6", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 30, "func_limit": 15, "crit_limit": 5}, "dir": "high"},
                ]
            }
        ]
    },
    "immune": {
        "name": "Immune Function",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Inflammatory Load",
                "weight": 0.40,
                "markers": [
                    {"id": "IL_6", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 1.0, "func_limit": 3.0, "crit_limit": 6.0}, "dir": "low"},
                    {"id": "hs_CRP", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 0.5, "func_limit": 2.0, "crit_limit": 5.0}, "dir": "low"},
                    {"id": "TNF_alpha", "status": "Secondary", "weight": 0.15, "thresholds": {"opt": 1.0, "func_limit": 3.0, "crit_limit": 6.0}, "dir": "low"},
                    {"id": "Fibrinogen", "status": "Contributor", "weight": 0.10, "thresholds": {"opt": 250, "func_limit": 350, "crit_limit": 450}, "dir": "low"},
                    {"id": "Ferritin", "status": "Contributor", "weight": 0.10, "thresholds": {"opt": 80, "func_limit": 200, "crit_limit": 400}, "dir": "low"},
                ]
            },
            {
                "name": "Cellular Defense",
                "weight": 0.25,
                "markers": [
                    {"id": "Neutrophils", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 4.0, "opt_low": 2.0, "opt_high": 6.0, "crit_limit": 1.0}, "dir": "split"},
                    {"id": "Lymphocytes", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 2.0, "func_limit": 1.2, "crit_limit": 0.8}, "dir": "high"},
                    {"id": "WBC", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 6.0, "opt_low": 4.0, "opt_high": 8.0, "crit_limit": 3.0}, "dir": "split"},
                    {"id": "Monocytes", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 0.4, "func_limit": 0.8, "crit_limit": 1.2}, "dir": "low"},
                ]
            },
            {
                "name": "Immuno-Endocrine",
                "weight": 0.20,
                "markers": [
                    {"id": "Vitamin_D", "status": "Primary", "weight": 0.50, "thresholds": {"opt": 50, "func_limit": 30, "crit_limit": 20}, "dir": "high"},
                    {"id": "Cortisol", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 12, "opt_low": 6, "opt_high": 18, "crit_limit": 25}, "dir": "split"},
                    {"id": "DHEA_S", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 300, "func_limit": 150, "crit_limit": 80}, "dir": "high"},
                ]
            },
            {
                "name": "Autoimmunity",
                "weight": 0.15,
                "markers": [
                    {"id": "ANA", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 0, "func_limit": 1, "crit_limit": 1}, "dir": "low"},
                    {"id": "TPO_Ab", "status": "Secondary", "weight": 0.30, "thresholds": {"opt": 0, "func_limit": 30, "crit_limit": 100}, "dir": "low"},
                    {"id": "RF", "status": "Secondary", "weight": 0.30, "thresholds": {"opt": 0, "func_limit": 14, "crit_limit": 40}, "dir": "low"},
                ]
            }
        ]
    },
    "blood": {
        "name": "Blood Health",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Oxygen Transport",
                "weight": 0.30,
                "markers": [
                    {"id": "Hemoglobin", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 14.5, "func_limit": 12.5, "crit_limit": 10}, "dir": "high"},
                    {"id": "MCV", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 88, "opt_low": 82, "opt_high": 94, "crit_limit": 75}, "dir": "split"},
                    {"id": "RDW", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 12.5, "func_limit": 14, "crit_limit": 16}, "dir": "low"},
                    {"id": "Platelets", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 250, "opt_low": 150, "opt_high": 350, "crit_limit": 100}, "dir": "split"},
                ]
            },
            {
                "name": "Iron Status",
                "weight": 0.30,
                "markers": [
                    {"id": "Ferritin", "status": "Primary", "weight": 0.45, "thresholds": {"opt": 100, "func_limit": 40, "crit_limit": 20}, "dir": "high"},
                    {"id": "Transferrin_Sat", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 30, "func_limit": 20, "crit_limit": 15}, "dir": "high"},
                    {"id": "Iron", "status": "Proxy", "proxy_for": "Transferrin_Sat", "thresholds": {"opt": 100, "func_limit": 60, "crit_limit": 40}, "dir": "high"},
                    {"id": "TIBC", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 300, "func_limit": 400, "crit_limit": 500}, "dir": "low"},
                ]
            },
            {
                "name": "Hematopoietic Fuel",
                "weight": 0.20,
                "markers": [
                    {"id": "B12", "status": "Primary", "weight": 0.45, "thresholds": {"opt": 600, "func_limit": 400, "crit_limit": 200}, "dir": "high"},
                    {"id": "Folate", "status": "Contributor", "weight": 0.35, "thresholds": {"opt": 15, "func_limit": 8, "crit_limit": 4}, "dir": "high"},
                    {"id": "Copper", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 100, "func_limit": 80, "crit_limit": 60}, "dir": "high"},
                ]
            },
            {
                "name": "Hemolysis",
                "weight": 0.20,
                "markers": [
                    {"id": "Reticulocytes", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 1.0, "opt_low": 0.5, "opt_high": 1.5, "crit_limit": 0.2}, "dir": "split"},
                    {"id": "Haptoglobin", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 100, "func_limit": 50, "crit_limit": 20}, "dir": "high"},
                    {"id": "LDH", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 180, "func_limit": 250, "crit_limit": 400}, "dir": "low"},
                ]
            }
        ]
    },
    "brain": {
        "name": "Brain Health",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Methylation",
                "weight": 0.25,
                "markers": [
                    {"id": "Homocysteine", "status": "Primary", "weight": 0.50, "thresholds": {"opt": 7, "func_limit": 10, "crit_limit": 15}, "dir": "low"},
                    {"id": "B12", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 600, "func_limit": 400, "crit_limit": 200}, "dir": "high"},
                    {"id": "Folate", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 15, "func_limit": 8, "crit_limit": 4}, "dir": "high"},
                ]
            },
            {
                "name": "Neuro-Metabolic",
                "weight": 0.30,
                "markers": [
                    {"id": "Free_T3", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 3.2, "func_limit": 2.5, "crit_limit": 2.0}, "dir": "high"},
                    {"id": "TSH", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 1.5, "func_limit": 3.0, "crit_limit": 5.0}, "dir": "low"},
                    {"id": "Free_T4", "status": "Secondary", "weight": 0.20, "thresholds": {"opt": 1.2, "func_limit": 0.9, "crit_limit": 0.7}, "dir": "high"},
                    {"id": "BHB", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 0.3, "func_limit": 0.1, "crit_limit": 0.05}, "dir": "high"},
                ]
            },
            {
                "name": "Neuro-Inflammation",
                "weight": 0.30,
                "markers": [
                    {"id": "IL_6", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 1.0, "func_limit": 3.0, "crit_limit": 6.0}, "dir": "low"},
                    {"id": "hs_CRP", "status": "Proxy", "proxy_for": "IL_6", "thresholds": {"opt": 0.5, "func_limit": 2.0, "crit_limit": 5.0}, "dir": "low"},
                    {"id": "Omega3_Index", "status": "Contributor", "weight": 0.35, "thresholds": {"opt": 8, "func_limit": 5, "crit_limit": 3}, "dir": "high"},
                    {"id": "CoQ10", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 1.0, "func_limit": 0.6, "crit_limit": 0.3}, "dir": "high"},
                ]
            },
            {
                "name": "Neuro-Trophic",
                "weight": 0.15,
                "markers": [
                    {"id": "Cortisol", "status": "Primary", "weight": 0.40, "thresholds": {"opt": 12, "func_limit": 20, "crit_limit": 28}, "dir": "low"},
                    {"id": "IGF_1", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 180, "func_limit": 120, "crit_limit": 80}, "dir": "high"},
                    {"id": "DHEA_S", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 300, "func_limit": 150, "crit_limit": 80}, "dir": "high"},
                    {"id": "Vitamin_D", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 50, "func_limit": 30, "crit_limit": 20}, "dir": "high"},
                ]
            }
        ]
    },
    "liver": {
        "name": "Liver Health",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Hepatocellular",
                "weight": 0.35,
                "markers": [
                    {"id": "ALT", "status": "Primary", "weight": 0.50, "thresholds": {"opt": 20, "func_limit": 35, "crit_limit": 60}, "dir": "low"},
                    {"id": "AST", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 22, "func_limit": 35, "crit_limit": 55}, "dir": "low"},
                    {"id": "LDH", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 180, "func_limit": 250, "crit_limit": 400}, "dir": "low"},
                ]
            },
            {
                "name": "Biliary & Detox",
                "weight": 0.35,
                "markers": [
                    {"id": "GGT", "status": "Primary", "weight": 0.45, "thresholds": {"opt": 20, "func_limit": 40, "crit_limit": 80}, "dir": "low"},
                    {"id": "ALP", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 60, "func_limit": 100, "crit_limit": 150}, "dir": "low"},
                    {"id": "Bilirubin_Total", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 0.8, "func_limit": 1.2, "crit_limit": 2.0}, "dir": "low"},
                ]
            },
            {
                "name": "Synthetic Function",
                "weight": 0.30,
                "markers": [
                    {"id": "Albumin", "status": "Primary", "weight": 0.55, "thresholds": {"opt": 4.5, "func_limit": 3.8, "crit_limit": 3.2}, "dir": "high"},
                    {"id": "Globulin", "status": "Contributor", "weight": 0.25, "thresholds": {"opt": 2.8, "opt_low": 2.3, "opt_high": 3.3, "crit_limit": 2.0}, "dir": "split"},
                    {"id": "AG_Ratio", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 1.8, "func_limit": 1.2, "crit_limit": 0.9}, "dir": "high"},
                ]
            }
        ]
    },
    "kidney": {
        "name": "Kidney Health",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Filtration",
                "weight": 0.40,
                "markers": [
                    {"id": "Cystatin_C", "status": "Primary", "weight": 0.50, "thresholds": {"opt": 0.8, "func_limit": 1.0, "crit_limit": 1.3}, "dir": "low"},
                    {"id": "Creatinine", "status": "Proxy", "proxy_for": "Cystatin_C", "thresholds": {"opt": 0.9, "func_limit": 1.2, "crit_limit": 1.5}, "dir": "low"},
                    {"id": "BUN", "status": "Contributor", "weight": 0.30, "thresholds": {"opt": 14, "func_limit": 20, "crit_limit": 28}, "dir": "low"},
                    {"id": "eGFR", "status": "Secondary", "weight": 0.20, "thresholds": {"opt": 90, "func_limit": 60, "crit_limit": 45}, "dir": "high"},
                ]
            },
            {
                "name": "Structural Integrity",
                "weight": 0.30,
                "markers": [
                    {"id": "ACR", "status": "Primary", "weight": 0.45, "thresholds": {"opt": 10, "func_limit": 30, "crit_limit": 100}, "dir": "low"},
                    {"id": "Uric_Acid", "status": "Contributor", "weight": 0.35, "thresholds": {"opt": 5.0, "func_limit": 7.0, "crit_limit": 9.0}, "dir": "low"},
                    {"id": "Microalbumin", "status": "Proxy", "proxy_for": "ACR", "thresholds": {"opt": 10, "func_limit": 30, "crit_limit": 100}, "dir": "low"},
                ]
            },
            {
                "name": "Electrolyte Regulation",
                "weight": 0.30,
                "markers": [
                    {"id": "Potassium", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 4.2, "opt_low": 3.8, "opt_high": 4.8, "crit_limit": 3.2}, "dir": "split"},
                    {"id": "CO2", "status": "Secondary", "weight": 0.25, "thresholds": {"opt": 25, "func_limit": 22, "crit_limit": 18}, "dir": "high"},
                    {"id": "Phosphorus", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 3.5, "opt_low": 2.5, "opt_high": 4.5, "crit_limit": 2.0}, "dir": "split"},
                    {"id": "Calcium", "status": "Contributor", "weight": 0.20, "thresholds": {"opt": 9.5, "opt_low": 8.5, "opt_high": 10.2, "crit_limit": 8.0}, "dir": "split"},
                ]
            }
        ]
    },
    "hormonal": {
        "name": "Hormonal Health",
        "weight": 0.10,
        "buckets": [
            {
                "name": "Thyroid",
                "weight": 0.35,
                "markers": [
                    {"id": "Free_T3", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 3.2, "func_limit": 2.5, "crit_limit": 2.0}, "dir": "high"},
                    {"id": "TSH", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 1.5, "func_limit": 3.0, "crit_limit": 5.0}, "dir": "low"},
                    {"id": "Free_T4", "status": "Secondary", "weight": 0.20, "thresholds": {"opt": 1.2, "func_limit": 0.9, "crit_limit": 0.7}, "dir": "high"},
                    {"id": "Reverse_T3", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 15, "func_limit": 22, "crit_limit": 30}, "dir": "low"},
                    {"id": "TPO_Ab", "status": "Contributor", "weight": 0.10, "thresholds": {"opt": 0, "func_limit": 30, "crit_limit": 100}, "dir": "low"},
                ]
            },
            {
                "name": "Sex Steroids",
                "weight": 0.35,
                "markers": [
                    {"id": "Free_Testosterone", "status": "Primary", "weight": 0.35, "thresholds": {"opt": 15, "func_limit": 9, "crit_limit": 5}, "dir": "high"},
                    {"id": "Estradiol", "status": "Primary", "weight": 0.25, "thresholds": {"opt": 25, "func_limit": 15, "crit_limit": 8}, "dir": "high"},
                    {"id": "SHBG", "status": "Secondary", "weight": 0.15, "thresholds": {"opt": 40, "opt_low": 20, "opt_high": 60, "crit_limit": 15}, "dir": "split"},
                    {"id": "Progesterone", "status": "Secondary", "weight": 0.15, "thresholds": {"opt": 1.0, "func_limit": 0.5, "crit_limit": 0.2}, "dir": "high"},
                    {"id": "Testosterone_Total", "status": "Contributor", "weight": 0.10, "thresholds": {"opt": 600, "func_limit": 400, "crit_limit": 250}, "dir": "high"},
                ]
            },
            {
                "name": "Adrenal & Growth",
                "weight": 0.30,
                "markers": [
                    {"id": "IGF_1", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 180, "func_limit": 120, "crit_limit": 80}, "dir": "high"},
                    {"id": "Cortisol", "status": "Primary", "weight": 0.30, "thresholds": {"opt": 12, "opt_low": 6, "opt_high": 18, "crit_limit": 25}, "dir": "split"},
                    {"id": "DHEA_S", "status": "Secondary", "weight": 0.25, "thresholds": {"opt": 300, "func_limit": 150, "crit_limit": 80}, "dir": "high"},
                    {"id": "Pregnenolone", "status": "Contributor", "weight": 0.15, "thresholds": {"opt": 100, "func_limit": 50, "crit_limit": 25}, "dir": "high"},
                ]
            }
        ]
    }
}


# =============================================================================
# BIOMARKER NAME MAPPING
# =============================================================================

BIOMARKER_ALIASES = {
    # Common aliases -> Titan ID
    "apob": "ApoB", "apo b": "ApoB", "apolipoprotein b": "ApoB",
    "ldl": "LDL", "ldl-c": "LDL", "ldl cholesterol": "LDL",
    "hdl": "HDL", "hdl-c": "HDL", "hdl cholesterol": "HDL",
    "triglycerides": "Triglycerides", "tg": "Triglycerides", "trigs": "Triglycerides",
    "total cholesterol": "Total_Cholesterol", "tc": "Total_Cholesterol",
    "hs-crp": "hs_CRP", "hscrp": "hs_CRP", "crp": "hs_CRP", "c-reactive protein": "hs_CRP",
    "hba1c": "HbA1c", "a1c": "HbA1c", "hemoglobin a1c": "HbA1c", "glycated hemoglobin": "HbA1c",
    "glucose": "Glucose", "fasting glucose": "Glucose", "blood sugar": "Glucose",
    "insulin": "Fasting_Insulin", "fasting insulin": "Fasting_Insulin",
    "hemoglobin": "Hemoglobin", "hgb": "Hemoglobin", "hb": "Hemoglobin",
    "hematocrit": "Hematocrit", "hct": "Hematocrit",
    "albumin": "Albumin", "alb": "Albumin",
    "creatinine": "Creatinine", "creat": "Creatinine",
    "bun": "BUN", "blood urea nitrogen": "BUN", "urea": "BUN",
    "alt": "ALT", "sgpt": "ALT", "alanine aminotransferase": "ALT",
    "ast": "AST", "sgot": "AST", "aspartate aminotransferase": "AST",
    "alp": "ALP", "alkaline phosphatase": "ALP",
    "ggt": "GGT", "gamma gt": "GGT", "gamma-glutamyl transferase": "GGT",
    "bilirubin": "Bilirubin_Total", "total bilirubin": "Bilirubin_Total",
    "vitamin d": "Vitamin_D", "25-oh vitamin d": "Vitamin_D", "vit d": "Vitamin_D",
    "b12": "B12", "vitamin b12": "B12", "cobalamin": "B12",
    "folate": "Folate", "folic acid": "Folate",
    "ferritin": "Ferritin",
    "iron": "Iron", "serum iron": "Iron",
    "tibc": "TIBC", "total iron binding capacity": "TIBC",
    "tsh": "TSH", "thyroid stimulating hormone": "TSH",
    "free t3": "Free_T3", "ft3": "Free_T3",
    "free t4": "Free_T4", "ft4": "Free_T4",
    "wbc": "WBC", "white blood cells": "WBC", "leukocytes": "WBC",
    "rbc": "RBC", "red blood cells": "RBC", "erythrocytes": "RBC",
    "platelets": "Platelets", "plt": "Platelets", "thrombocytes": "Platelets",
    "mcv": "MCV", "mean corpuscular volume": "MCV",
    "mch": "MCH", "mean corpuscular hemoglobin": "MCH",
    "mchc": "MCHC",
    "rdw": "RDW", "red cell distribution width": "RDW",
    "neutrophils": "Neutrophils", "neut": "Neutrophils",
    "lymphocytes": "Lymphocytes", "lymph": "Lymphocytes",
    "monocytes": "Monocytes", "mono": "Monocytes",
    "eosinophils": "Eosinophils", "eos": "Eosinophils",
    "basophils": "Basophils", "baso": "Basophils",
    "homocysteine": "Homocysteine", "hcy": "Homocysteine",
    "uric acid": "Uric_Acid", "urate": "Uric_Acid",
    "magnesium": "Magnesium", "mg": "Magnesium",
    "potassium": "Potassium", "k": "Potassium",
    "sodium": "Sodium", "na": "Sodium",
    "calcium": "Calcium", "ca": "Calcium",
    "phosphorus": "Phosphorus", "phosphate": "Phosphorus",
    "chloride": "Chloride", "cl": "Chloride",
    "co2": "CO2", "bicarbonate": "CO2", "hco3": "CO2",
    "egfr": "eGFR", "gfr": "eGFR",
    "cystatin c": "Cystatin_C", "cystatin-c": "Cystatin_C",
    "ldh": "LDH", "lactate dehydrogenase": "LDH",
    "cortisol": "Cortisol",
    "dhea-s": "DHEA_S", "dheas": "DHEA_S", "dhea sulfate": "DHEA_S",
    "igf-1": "IGF_1", "igf1": "IGF_1", "insulin-like growth factor": "IGF_1",
    "testosterone": "Testosterone_Total", "total testosterone": "Testosterone_Total",
    "free testosterone": "Free_Testosterone",
    "estradiol": "Estradiol", "e2": "Estradiol",
    "progesterone": "Progesterone",
    "shbg": "SHBG", "sex hormone binding globulin": "SHBG",
    "omega-3 index": "Omega3_Index", "omega 3 index": "Omega3_Index",
    "esr": "ESR", "sed rate": "ESR", "sedimentation rate": "ESR",
    "fibrinogen": "Fibrinogen",
    "il-6": "IL_6", "interleukin 6": "IL_6", "interleukin-6": "IL_6",
    "tnf-alpha": "TNF_alpha", "tnf alpha": "TNF_alpha",
    "globulin": "Globulin",
    "protein total": "Total_Protein", "total protein": "Total_Protein",
    "reticulocytes": "Reticulocytes", "retic": "Reticulocytes",
    "haptoglobin": "Haptoglobin",
    "lp(a)": "Lp_a", "lipoprotein a": "Lp_a", "lipoprotein(a)": "Lp_a",
}


def normalize_biomarker_name(name: str) -> str:
    """Convert common biomarker names to Titan standard IDs."""
    if not name:
        return name
    key = name.lower().strip()
    return BIOMARKER_ALIASES.get(key, name)


def standardize_labs(raw_labs: Dict) -> Dict:
    """Convert user-provided lab names to Titan standard format."""
    standardized = {}
    for key, value in raw_labs.items():
        if value is None or (isinstance(value, float) and math.isnan(value)):
            continue
        try:
            std_key = normalize_biomarker_name(key)
            standardized[std_key] = float(value)
        except (ValueError, TypeError):
            continue
    return standardized


# =============================================================================
# BUCKET & SYSTEM SCORING
# =============================================================================

def score_bucket(bucket: Dict, labs: Dict) -> Dict:
    """
    Score a single bucket using Primary/Secondary/Proxy logic.
    Returns: {score, confidence, markers_used, markers_missing}
    """
    markers = bucket['markers']
    total_weighted_score = 0
    total_weight_found = 0
    markers_used = []
    markers_missing = []
    
    # Track which primaries were found
    primaries_found = set()
    
    # First pass: score all non-proxy markers
    for marker in markers:
        marker_id = marker['id']
        status = marker['status']
        
        if status == 'Proxy':
            continue  # Handle proxies in second pass
        
        if marker_id in labs:
            value = labs[marker_id]
            score = calculate_gradient_score(value, marker['thresholds'])
            weight = marker.get('weight', 0)
            
            total_weighted_score += score * weight
            total_weight_found += weight
            markers_used.append({
                'id': marker_id,
                'value': value,
                'score': round(score, 1),
                'status': status,
                'weight': weight
            })
            
            if status == 'Primary':
                primaries_found.add(marker_id)
        else:
            markers_missing.append(marker_id)
    
    # Second pass: handle proxies (only if their primary is missing)
    for marker in markers:
        if marker['status'] != 'Proxy':
            continue
        
        marker_id = marker['id']
        proxy_for = marker.get('proxy_for')
        
        # Only use proxy if primary is missing
        if proxy_for and proxy_for not in primaries_found:
            if marker_id in labs:
                value = labs[marker_id]
                score = calculate_gradient_score(value, marker['thresholds'])
                
                # Find the primary's weight to inherit
                primary_weight = 0
                for m in markers:
                    if m['id'] == proxy_for:
                        primary_weight = m.get('weight', 0)
                        break
                
                total_weighted_score += score * primary_weight
                total_weight_found += primary_weight
                markers_used.append({
                    'id': marker_id,
                    'value': value,
                    'score': round(score, 1),
                    'status': 'Proxy (active)',
                    'weight': primary_weight,
                    'proxy_for': proxy_for
                })
    
    # Calculate final bucket score
    if total_weight_found > 0:
        bucket_score = total_weighted_score / total_weight_found
        confidence = total_weight_found  # Proportion of weights found
    else:
        bucket_score = 0
        confidence = 0
    
    return {
        'name': bucket['name'],
        'score': round(bucket_score, 1),
        'confidence': round(confidence, 2),
        'weight': bucket['weight'],
        'markers_used': markers_used,
        'markers_missing': markers_missing
    }


def score_system(system_id: str, labs: Dict) -> Dict:
    """Score an entire health system."""
    if system_id not in TITAN_SYSTEMS:
        return {'error': f'Unknown system: {system_id}'}
    
    system = TITAN_SYSTEMS[system_id]
    bucket_results = []
    total_weighted_score = 0
    total_weight = 0
    all_markers_used = []
    
    for bucket in system['buckets']:
        result = score_bucket(bucket, labs)
        bucket_results.append(result)
        
        if result['confidence'] > 0:
            total_weighted_score += result['score'] * result['weight']
            total_weight += result['weight']
            all_markers_used.extend(result['markers_used'])
    
    # Calculate system score
    if total_weight > 0:
        system_score = total_weighted_score / total_weight
        confidence = total_weight
    else:
        system_score = 0
        confidence = 0
    
    # Determine status
    if system_score >= 80:
        status = "Optimal"
    elif system_score >= 60:
        status = "Good"
    elif system_score >= 40:
        status = "Fair"
    else:
        status = "Risk"
    
    return {
        'system_id': system_id,
        'name': system['name'],
        'score': round(system_score, 1),
        'confidence': round(confidence, 2),
        'status': status,
        'buckets': bucket_results,
        'markers_used': all_markers_used,
        'top_markers': sorted(all_markers_used, key=lambda x: x['weight'], reverse=True)[:3]
    }


def score_all_systems(labs: Dict) -> List[Dict]:
    """Score all health systems."""
    results = []
    for system_id in TITAN_SYSTEMS:
        result = score_system(system_id, labs)
        if 'error' not in result:
            results.append(result)
    return results


# =============================================================================
# BIOLOGICAL AGE CALCULATION (PhenoAge-style)
# =============================================================================

def calculate_biological_age(labs: Dict, chronological_age: int) -> Dict:
    """
    Calculate biological age using PhenoAge algorithm.
    Reference: Levine et al. 2018 - "An epigenetic biomarker of aging..."
    https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002718
    
    Required markers (9 biomarkers + age):
    - Albumin (g/dL)
    - Creatinine (mg/dL)  
    - Glucose (mg/dL)
    - C-reactive protein (mg/L)
    - Lymphocyte percent (%)
    - Mean cell volume (fL)
    - Red cell distribution width (%)
    - Alkaline phosphatase (U/L)
    - White blood cell count (10^3 cells/μL)
    """
    
    # PhenoAge coefficients from Levine 2018 (units: SI)
    PHENOAGE_COEFFICIENTS = {
        'intercept': -19.9067,
        'age': 0.0804,
        'albumin': -0.0336,      # g/L
        'creatinine': 0.0095,    # μmol/L
        'glucose': 0.1953,       # mmol/L
        'ln_crp': 0.0954,        # ln(mg/L)
        'lymphocyte_pct': -0.0120,  # %
        'mcv': 0.0268,           # fL
        'rdw': 0.3306,           # %
        'alp': 0.0019,           # U/L
        'wbc': 0.0554,           # 10^3 cells/μL
    }
    
    # Population means (in SI units) for imputation when markers missing
    # These are approximate healthy adult means
    POPULATION_MEANS = {
        'albumin': 43.0,        # g/L (4.3 g/dL)
        'creatinine': 80.0,     # μmol/L (0.9 mg/dL)
        'glucose': 5.0,         # mmol/L (90 mg/dL)
        'ln_crp': -0.5,         # ln(0.6 mg/L)
        'lymphocyte_pct': 28.0, # %
        'mcv': 89.0,            # fL
        'rdw': 13.0,            # %
        'alp': 65.0,            # U/L
        'wbc': 6.5,             # 10^3/μL
    }
    
    # Gompertz parameters
    GAMMA = 0.0077
    
    # Track markers
    markers_used = []
    missing_markers = []
    marker_values = {}
    
    # Helper to safely get value with bounds checking
    def safe_value(val, min_v, max_v):
        if val is None or math.isnan(val) or math.isinf(val):
            return None
        return max(min_v, min(max_v, val))
    
    # Albumin (g/dL -> g/L) - normal range 3.5-5.5 g/dL
    if 'Albumin' in labs:
        val = safe_value(labs['Albumin'], 2.0, 6.0)
        if val:
            marker_values['albumin'] = val * 10
            markers_used.append({'id': 'Albumin', 'value': val, 'unit': 'g/dL'})
        else:
            missing_markers.append('Albumin')
    else:
        missing_markers.append('Albumin')
    
    # Creatinine (mg/dL -> μmol/L) - normal range 0.5-1.5 mg/dL
    if 'Creatinine' in labs:
        val = safe_value(labs['Creatinine'], 0.3, 3.0)
        if val:
            marker_values['creatinine'] = val * 88.4
            markers_used.append({'id': 'Creatinine', 'value': val, 'unit': 'mg/dL'})
        else:
            missing_markers.append('Creatinine')
    else:
        missing_markers.append('Creatinine')
    
    # Glucose (mg/dL -> mmol/L) - normal range 60-200 mg/dL
    if 'Glucose' in labs:
        val = safe_value(labs['Glucose'], 40, 400)
        if val:
            marker_values['glucose'] = val / 18.0
            markers_used.append({'id': 'Glucose', 'value': val, 'unit': 'mg/dL'})
        else:
            missing_markers.append('Glucose')
    else:
        missing_markers.append('Glucose')
    
    # CRP (mg/L) - normal range 0.1-50 mg/L
    if 'hs_CRP' in labs:
        val = safe_value(labs['hs_CRP'], 0.1, 100)
        if val:
            marker_values['ln_crp'] = math.log(max(val, 0.1))
            markers_used.append({'id': 'hs_CRP', 'value': val, 'unit': 'mg/L'})
        else:
            missing_markers.append('hs_CRP')
    else:
        missing_markers.append('hs_CRP')
    
    # Lymphocyte % - normal range 15-45%
    lymph_key = None
    for key in ['Lymphocytes_pct', 'Lymphocyte_pct', 'Lymphocytes']:
        if key in labs:
            lymph_key = key
            break
    if lymph_key:
        val = safe_value(labs[lymph_key], 5, 60)
        if val:
            marker_values['lymphocyte_pct'] = val
            markers_used.append({'id': 'Lymphocyte%', 'value': val, 'unit': '%'})
        else:
            missing_markers.append('Lymphocyte%')
    else:
        missing_markers.append('Lymphocyte%')
    
    # MCV (fL) - normal range 70-110 fL
    if 'MCV' in labs:
        val = safe_value(labs['MCV'], 60, 120)
        if val:
            marker_values['mcv'] = val
            markers_used.append({'id': 'MCV', 'value': val, 'unit': 'fL'})
        else:
            missing_markers.append('MCV')
    else:
        missing_markers.append('MCV')
    
    # RDW (%) - normal range 10-20%
    if 'RDW' in labs:
        val = safe_value(labs['RDW'], 8, 25)
        if val:
            marker_values['rdw'] = val
            markers_used.append({'id': 'RDW', 'value': val, 'unit': '%'})
        else:
            missing_markers.append('RDW')
    else:
        missing_markers.append('RDW')
    
    # ALP (U/L) - normal range 30-150 U/L
    if 'ALP' in labs:
        val = safe_value(labs['ALP'], 20, 300)
        if val:
            marker_values['alp'] = val
            markers_used.append({'id': 'ALP', 'value': val, 'unit': 'U/L'})
        else:
            missing_markers.append('ALP')
    else:
        missing_markers.append('ALP')
    
    # WBC (10^3/μL) - normal range 3-15
    if 'WBC' in labs:
        val = safe_value(labs['WBC'], 2, 30)
        if val:
            marker_values['wbc'] = val
            markers_used.append({'id': 'WBC', 'value': val, 'unit': '10³/μL'})
        else:
            missing_markers.append('WBC')
    else:
        missing_markers.append('WBC')
    
    # Calculate confidence
    available_count = len(markers_used)
    confidence = available_count / 9.0
    
    # Need at least 4 markers
    if available_count < 4:
        return {
            'biological_age': float(chronological_age),
            'chronological_age': chronological_age,
            'age_delta': 0.0,
            'confidence': round(confidence, 2),
            'markers_used': markers_used,
            'markers_missing': missing_markers,
            'method': 'PhenoAge (insufficient data)'
        }
    
    # Impute missing markers with population means
    for marker_key in POPULATION_MEANS:
        if marker_key not in marker_values:
            marker_values[marker_key] = POPULATION_MEANS[marker_key]
    
    # Calculate xb (linear predictor)
    xb = PHENOAGE_COEFFICIENTS['intercept']
    xb += PHENOAGE_COEFFICIENTS['age'] * chronological_age
    
    for marker_key in ['albumin', 'creatinine', 'glucose', 'ln_crp', 
                       'lymphocyte_pct', 'mcv', 'rdw', 'alp', 'wbc']:
        xb += PHENOAGE_COEFFICIENTS[marker_key] * marker_values[marker_key]
    
    # Calculate PhenoAge using Gompertz mortality model
    try:
        # Clamp xb to prevent overflow
        xb = max(-50, min(50, xb))
        
        hazard = math.exp(xb) * (math.exp(120 * GAMMA) - 1) / GAMMA
        hazard = max(1e-10, min(1e10, hazard))  # Prevent extreme values
        
        mort_score = 1 - math.exp(-hazard)
        mort_score = max(0.0001, min(0.9999, mort_score))
        
        inner = -0.00553 * math.log(1 - mort_score)
        
        if inner > 0 and inner < 1e10:
            phenoage = 141.50225 + math.log(inner) / 0.090165
        else:
            phenoage = float(chronological_age)
            
    except (ValueError, OverflowError, ZeroDivisionError):
        phenoage = float(chronological_age)
    
    # Final sanity check - MUST clamp to reasonable range
    if math.isnan(phenoage) or math.isinf(phenoage):
        phenoage = float(chronological_age)
    phenoage = max(10, min(120, phenoage))
    
    age_delta = phenoage - chronological_age
    
    return {
        'biological_age': round(phenoage, 1),
        'chronological_age': chronological_age,
        'age_delta': round(age_delta, 1),
        'confidence': round(confidence, 2),
        'markers_used': markers_used,
        'markers_missing': missing_markers,
        'method': 'PhenoAge (Levine 2018)'
    }


# =============================================================================
# PACE OF AGING (DunedinPACE-style)
# =============================================================================

def calculate_pace_of_aging(labs: Dict) -> Dict:
    """
    Estimate pace of aging (1.0 = average, <1.0 = slower, >1.0 = faster).
    Based on key biomarkers that reflect physiological decay rate.
    """
    pace_markers = {
        'hs_CRP': {'weight': 0.20, 'opt': 0.5, 'critical': 5.0},
        'Glucose': {'weight': 0.15, 'opt': 85, 'critical': 126},
        'HbA1c': {'weight': 0.15, 'opt': 5.0, 'critical': 6.5},
        'HDL': {'weight': 0.10, 'opt': 60, 'critical': 35, 'dir': 'high'},
        'Triglycerides': {'weight': 0.10, 'opt': 70, 'critical': 200},
        'Albumin': {'weight': 0.10, 'opt': 4.5, 'critical': 3.2, 'dir': 'high'},
        'Creatinine': {'weight': 0.10, 'opt': 0.9, 'critical': 1.5},
        'WBC': {'weight': 0.10, 'opt': 5.5, 'critical': 11},
    }
    
    pace_scores = []
    markers_used = []
    total_weight = 0
    
    for marker_id, config in pace_markers.items():
        if marker_id in labs:
            value = labs[marker_id]
            opt = config['opt']
            critical = config['critical']
            weight = config['weight']
            direction = config.get('dir', 'low')
            
            # Calculate pace contribution
            if direction == 'high':
                # Higher is better
                if value >= opt:
                    pace = 0.8
                elif value <= critical:
                    pace = 1.4
                else:
                    pace = 0.8 + (0.6 * (opt - value) / (opt - critical))
            else:
                # Lower is better
                if value <= opt:
                    pace = 0.8
                elif value >= critical:
                    pace = 1.4
                else:
                    pace = 0.8 + (0.6 * (value - opt) / (critical - opt))
            
            pace_scores.append(pace * weight)
            total_weight += weight
            markers_used.append({
                'id': marker_id,
                'value': value,
                'pace_contribution': round(pace, 2)
            })
    
    if total_weight > 0:
        overall_pace = sum(pace_scores) / total_weight
        confidence = total_weight
    else:
        overall_pace = 1.0
        confidence = 0
    
    # Interpretation
    if overall_pace < 0.9:
        interpretation = "Slower than average aging"
    elif overall_pace <= 1.1:
        interpretation = "Average pace of aging"
    else:
        interpretation = "Faster than average aging"
    
    return {
        'pace': round(overall_pace, 2),
        'confidence': round(confidence, 2),
        'interpretation': interpretation,
        'markers_used': markers_used
    }


# =============================================================================
# MAIN ENGINE FUNCTION
# =============================================================================

def run_titan_engine(raw_labs: Dict, chronological_age: int = 35, sex: str = "male") -> Dict:
    """
    Run the complete Titan Protocol analysis.
    
    Args:
        raw_labs: Dictionary of biomarker name -> value
        chronological_age: User's chronological age
        sex: "male" or "female" (for sex-specific thresholds)
    
    Returns:
        Complete health report in JSON format
    """
    # Step 1: Standardize biomarker names
    labs = standardize_labs(raw_labs)
    
    # Step 2: Enrich with derived metrics
    labs = enrich_labs(labs)
    
    # Step 3: Calculate biological age
    bio_age_result = calculate_biological_age(labs, chronological_age)
    
    # Step 4: Calculate pace of aging
    pace_result = calculate_pace_of_aging(labs)
    
    # Step 5: Score all systems
    systems = score_all_systems(labs)
    
    # Step 6: Calculate overall health score
    if systems:
        valid_systems = [s for s in systems if s['confidence'] > 0]
        if valid_systems:
            overall_score = sum(s['score'] * TITAN_SYSTEMS[s['system_id']]['weight'] 
                              for s in valid_systems) / sum(TITAN_SYSTEMS[s['system_id']]['weight'] 
                              for s in valid_systems)
        else:
            overall_score = 0
    else:
        overall_score = 0
    
    # Step 7: Generate insights
    insights = generate_insights(systems, bio_age_result, pace_result)
    
    return {
        'summary': {
            'bio_age': bio_age_result['biological_age'],
            'chrono_age': chronological_age,
            'age_delta': bio_age_result['age_delta'],
            'pace_of_aging': pace_result['pace'],
            'overall_health_score': round(overall_score, 0)
        },
        'systems': systems,
        'bio_age_detail': bio_age_result,
        'pace_detail': pace_result,
        'insights': insights,
        'labs_processed': len(labs)
    }


def generate_insights(systems: List[Dict], bio_age: Dict, pace: Dict) -> List[str]:
    """Generate actionable insights with specific recommendations."""
    
    # Actionable recommendations for each biomarker
    RECOMMENDATIONS = {
        # Vitamins & Minerals
        'Vitamin_D': "Take Vitamin D3 (2000-4000 IU daily) with fatty meal, or get 15-20 min sunlight",
        'Vitamin_B12': "Take methylcobalamin B12 supplement, or eat eggs, fish, and fortified cereals",
        'Iron': "Eat spinach, lentils, red meat, or pair iron-rich foods with vitamin C for absorption",
        'Ferritin': "Increase iron intake: liver, beans, fortified cereals. Avoid tea/coffee with meals",
        'Folate': "Eat leafy greens (spinach, kale), lentils, asparagus, or take methylfolate supplement",
        
        # Lipids
        'LDL': "Reduce saturated fats, eat oats, nuts, olive oil. Consider plant sterols or fiber supplement",
        'HDL': "Exercise 30 min daily, eat fatty fish, avocados, olive oil. Limit refined carbs",
        'Triglycerides': "Cut sugar and refined carbs, eat fatty fish 2x/week, limit alcohol",
        'ApoB': "Reduce saturated fat, increase soluble fiber (oats, psyllium), consider statins if high",
        'Non_HDL': "Focus on fiber-rich foods, omega-3s from fish, and reduce processed foods",
        'Total_Cholesterol': "Eat more fiber, reduce red meat, add plant sterols from nuts and seeds",
        
        # Blood Sugar
        'Glucose': "Reduce refined carbs, eat more fiber, walk 15 min after meals",
        'HbA1c': "Low glycemic diet, regular exercise, consider berberine or cinnamon supplements",
        'Fasting_Insulin': "Intermittent fasting, reduce carbs, strength training helps insulin sensitivity",
        'HOMA_IR': "Exercise regularly, reduce sugar intake, consider metformin if pre-diabetic",
        
        # Inflammation
        'hs_CRP': "Eat turmeric, ginger, fatty fish. Reduce sugar, processed foods, and stress",
        'ESR': "Anti-inflammatory diet: berries, leafy greens, fatty fish. Check for underlying causes",
        'Homocysteine': "Take B-complex (B6, B12, folate), eat leafy greens, reduce alcohol",
        
        # Liver
        'ALT': "Limit alcohol, avoid acetaminophen overuse, eat cruciferous vegetables, milk thistle",
        'AST': "Reduce alcohol, exercise moderately, eat antioxidant-rich foods (berries, greens)",
        'GGT': "Stop alcohol completely for 30 days, drink coffee, eat sulfur-rich foods (garlic, onions)",
        'ALP': "Get vitamin D and zinc levels checked, eat dairy and leafy greens",
        'Bilirubin': "Stay hydrated, eat beets and carrots, avoid alcohol",
        
        # Kidney
        'Creatinine': "Stay well hydrated, reduce protein if very high intake, avoid NSAIDs",
        'BUN': "Drink more water, moderate protein intake, avoid excessive salt",
        'Uric_Acid': "Avoid beer and organ meats, drink tart cherry juice, stay hydrated",
        'eGFR': "Control blood pressure, stay hydrated, limit salt and protein if low",
        'Cystatin_C': "Maintain healthy weight, control blood pressure, stay hydrated",
        
        # Blood
        'Hemoglobin': "Eat iron-rich foods (red meat, spinach), vitamin C for absorption, B12 if deficient",
        'RBC': "Eat iron and B12 rich foods, check for underlying bleeding if low",
        'WBC': "Get enough sleep, manage stress, eat zinc-rich foods (pumpkin seeds, meat)",
        'Platelets': "Eat folate-rich foods, avoid alcohol if low, check B12 levels",
        'MCV': "If high: check B12/folate. If low: check iron. Eat balanced diet with leafy greens",
        'RDW': "Address underlying deficiencies (iron, B12, folate), eat nutrient-dense foods",
        
        # Thyroid
        'TSH': "If high: check iodine intake, selenium (Brazil nuts). If low: reduce stress, check thyroid",
        'T3': "Eat selenium (Brazil nuts), zinc, avoid excessive soy, manage stress",
        'T4': "Ensure adequate iodine (seaweed, iodized salt), avoid goitrogens if low",
        
        # Hormones
        'Testosterone': "Lift weights, sleep 7-8 hrs, eat zinc (oysters, meat), reduce alcohol",
        'Cortisol': "Practice stress management, sleep hygiene, adaptogenic herbs (ashwagandha)",
        'DHEA': "Manage stress, exercise regularly, consider DHEA supplement if very low",
        
        # Other
        'Albumin': "Eat adequate protein (eggs, fish, meat), stay hydrated",
        'Total_Protein': "Increase protein intake: eggs, fish, legumes, dairy",
        'Magnesium': "Eat nuts, seeds, dark chocolate, leafy greens. Consider magnesium glycinate supplement",
        'Zinc': "Eat oysters, pumpkin seeds, beef, or take zinc picolinate supplement",
        'Calcium': "Dairy products, fortified plant milk, leafy greens, sardines with bones",
    }
    
    insights = []
    
    # Collect all poorly scoring markers across systems
    poor_markers = []
    for system in systems:
        for marker in system.get('markers_used', []):
            if marker.get('score', 100) < 60:
                poor_markers.append({
                    'id': marker['id'],
                    'score': marker['score'],
                    'value': marker['value'],
                    'system': system['name']
                })
    
    # Sort by score (worst first)
    poor_markers.sort(key=lambda x: x['score'])
    
    # Generate actionable insights for poor markers
    for marker in poor_markers[:4]:  # Top 4 worst markers
        marker_id = marker['id']
        if marker_id in RECOMMENDATIONS:
            insights.append(f"{marker_id.replace('_', ' ')}: {RECOMMENDATIONS[marker_id]}")
        else:
            insights.append(f"Improve {marker_id.replace('_', ' ')} (score: {marker['score']:.0f}) - consult your doctor")
    
    # Add positive insight if doing well
    optimal_systems = [s for s in systems if s['score'] >= 80]
    if optimal_systems and len(insights) < 5:
        names = ', '.join(s['name'] for s in optimal_systems[:2])
        insights.append(f"Great job! Your {names} markers are in optimal range - keep it up!")
    
    # Bio age insight
    delta = bio_age['age_delta']
    if delta < -3 and len(insights) < 6:
        insights.append(f"Excellent! Your biological age is {abs(delta):.1f} years younger than actual")
    elif delta > 3 and len(insights) < 6:
        insights.append(f"Focus on the recommendations above to reduce your biological age")
    
    return insights[:6]
