"""
Longevity Optimal Ranges Database
Based on peer-reviewed longevity research and functional medicine standards.
"""

LONGEVITY_OPTIMAL_RANGES = {
    "Glucose": {"optimal_low": 70, "optimal_high": 90, "unit": "mg/dL", "category": "Metabolic"},
    "Fasting Glucose": {"optimal_low": 70, "optimal_high": 90, "unit": "mg/dL", "category": "Metabolic"},
    "HbA1c": {"optimal_low": 4.8, "optimal_high": 5.2, "unit": "%", "category": "Metabolic"},
    "Hemoglobin A1c": {"optimal_low": 4.8, "optimal_high": 5.2, "unit": "%", "category": "Metabolic"},
    "Fasting Insulin": {"optimal_low": 2, "optimal_high": 6, "unit": "uIU/mL", "category": "Metabolic"},
    "Insulin": {"optimal_low": 2, "optimal_high": 6, "unit": "uIU/mL", "category": "Metabolic"},
    "HOMA-IR": {"optimal_low": 0.5, "optimal_high": 1.5, "unit": "", "category": "Metabolic"},
    "Triglycerides": {"optimal_low": 50, "optimal_high": 100, "unit": "mg/dL", "category": "Metabolic"},
    "Total Cholesterol": {"optimal_low": 150, "optimal_high": 200, "unit": "mg/dL", "category": "Metabolic"},
    "LDL Cholesterol": {"optimal_low": 50, "optimal_high": 100, "unit": "mg/dL", "category": "Metabolic"},
    "LDL-C": {"optimal_low": 50, "optimal_high": 100, "unit": "mg/dL", "category": "Metabolic"},
    "HDL Cholesterol": {"optimal_low": 60, "optimal_high": 100, "unit": "mg/dL", "category": "Metabolic"},
    "HDL-C": {"optimal_low": 60, "optimal_high": 100, "unit": "mg/dL", "category": "Metabolic"},
    "ApoB": {"optimal_low": 40, "optimal_high": 70, "unit": "mg/dL", "category": "Metabolic"},
    "Apolipoprotein B": {"optimal_low": 40, "optimal_high": 70, "unit": "mg/dL", "category": "Metabolic"},
    "Lp(a)": {"optimal_low": 0, "optimal_high": 30, "unit": "nmol/L", "category": "Metabolic"},
    "Lipoprotein(a)": {"optimal_low": 0, "optimal_high": 30, "unit": "nmol/L", "category": "Metabolic"},
    "hs-CRP": {"optimal_low": 0, "optimal_high": 0.5, "unit": "mg/L", "category": "Inflammatory"},
    "CRP": {"optimal_low": 0, "optimal_high": 0.5, "unit": "mg/L", "category": "Inflammatory"},
    "C-Reactive Protein": {"optimal_low": 0, "optimal_high": 0.5, "unit": "mg/L", "category": "Inflammatory"},
    "Homocysteine": {"optimal_low": 5, "optimal_high": 8, "unit": "umol/L", "category": "Inflammatory"},
    "Fibrinogen": {"optimal_low": 200, "optimal_high": 300, "unit": "mg/dL", "category": "Inflammatory"},
    "ESR": {"optimal_low": 0, "optimal_high": 10, "unit": "mm/hr", "category": "Inflammatory"},
    "WBC": {"optimal_low": 4.0, "optimal_high": 6.0, "unit": "K/uL", "category": "Inflammatory"},
    "Albumin": {"optimal_low": 4.2, "optimal_high": 5.0, "unit": "g/dL", "category": "Inflammatory"},
    "Ferritin": {"optimal_low": 50, "optimal_high": 150, "unit": "ng/mL", "category": "Hematologic"},
    "Iron": {"optimal_low": 60, "optimal_high": 120, "unit": "ug/dL", "category": "Hematologic"},
    "Hemoglobin": {"optimal_low": 13.5, "optimal_high": 15.5, "unit": "g/dL", "category": "Hematologic"},
    "Hematocrit": {"optimal_low": 40, "optimal_high": 45, "unit": "%", "category": "Hematologic"},
    "MCV": {"optimal_low": 82, "optimal_high": 92, "unit": "fL", "category": "Hematologic"},
    "RDW": {"optimal_low": 11.5, "optimal_high": 13.0, "unit": "%", "category": "Hematologic"},
    "RBC": {"optimal_low": 4.5, "optimal_high": 5.5, "unit": "M/uL", "category": "Hematologic"},
    "Platelets": {"optimal_low": 175, "optimal_high": 250, "unit": "K/uL", "category": "Hematologic"},
    "ALT": {"optimal_low": 10, "optimal_high": 25, "unit": "U/L", "category": "Liver"},
    "AST": {"optimal_low": 10, "optimal_high": 25, "unit": "U/L", "category": "Liver"},
    "ALP": {"optimal_low": 35, "optimal_high": 70, "unit": "U/L", "category": "Liver"},
    "GGT": {"optimal_low": 10, "optimal_high": 25, "unit": "U/L", "category": "Liver"},
    "Bilirubin": {"optimal_low": 0.3, "optimal_high": 1.0, "unit": "mg/dL", "category": "Liver"},
    "Creatinine": {"optimal_low": 0.7, "optimal_high": 1.1, "unit": "mg/dL", "category": "Kidney"},
    "BUN": {"optimal_low": 10, "optimal_high": 18, "unit": "mg/dL", "category": "Kidney"},
    "eGFR": {"optimal_low": 90, "optimal_high": 120, "unit": "mL/min/1.73m2", "category": "Kidney"},
    "Uric Acid": {"optimal_low": 3.5, "optimal_high": 5.5, "unit": "mg/dL", "category": "Kidney"},
    "Cystatin C": {"optimal_low": 0.5, "optimal_high": 0.9, "unit": "mg/L", "category": "Kidney"},
    "TSH": {"optimal_low": 1.0, "optimal_high": 2.5, "unit": "mIU/L", "category": "Thyroid"},
    "Free T4": {"optimal_low": 1.1, "optimal_high": 1.5, "unit": "ng/dL", "category": "Thyroid"},
    "Free T3": {"optimal_low": 3.0, "optimal_high": 3.5, "unit": "pg/mL", "category": "Thyroid"},
    "Vitamin D": {"optimal_low": 50, "optimal_high": 80, "unit": "ng/mL", "category": "Nutritional"},
    "Vitamin B12": {"optimal_low": 500, "optimal_high": 1000, "unit": "pg/mL", "category": "Nutritional"},
    "Folate": {"optimal_low": 10, "optimal_high": 25, "unit": "ng/mL", "category": "Nutritional"},
    "Magnesium": {"optimal_low": 2.0, "optimal_high": 2.5, "unit": "mg/dL", "category": "Nutritional"},
    "Testosterone": {"optimal_low": 500, "optimal_high": 900, "unit": "ng/dL", "category": "Hormonal"},
    "DHEA-S": {"optimal_low": 250, "optimal_high": 450, "unit": "ug/dL", "category": "Hormonal"},
    "Cortisol": {"optimal_low": 10, "optimal_high": 18, "unit": "ug/dL", "category": "Hormonal"},
    "IGF-1": {"optimal_low": 120, "optimal_high": 200, "unit": "ng/mL", "category": "Hormonal"},
}

BIOMARKER_ALIASES = {
    "glucose, serum": "Glucose", "glucose": "Glucose", "fasting glucose": "Fasting Glucose",
    "hemoglobin a1c": "HbA1c", "hba1c": "HbA1c", "a1c": "HbA1c", "triglycerides": "Triglycerides",
    "total cholesterol": "Total Cholesterol", "ldl cholesterol": "LDL Cholesterol", "ldl": "LDL Cholesterol",
    "hdl cholesterol": "HDL Cholesterol", "hdl": "HDL Cholesterol", "apolipoprotein b": "ApoB", "apob": "ApoB",
    "c-reactive protein": "hs-CRP", "crp": "CRP", "hs-crp": "hs-CRP", "wbc": "WBC", "hemoglobin": "Hemoglobin",
    "hematocrit": "Hematocrit", "mcv": "MCV", "rdw": "RDW", "ferritin": "Ferritin", "iron": "Iron",
    "alt": "ALT", "ast": "AST", "bun": "BUN", "creatinine": "Creatinine", "egfr": "eGFR",
    "tsh": "TSH", "vitamin d": "Vitamin D", "vitamin b12": "Vitamin B12", "folate": "Folate",
    "magnesium": "Magnesium", "testosterone": "Testosterone", "albumin": "Albumin", "platelets": "Platelets",
}


def normalize_biomarker_name(name: str) -> str:
    name_lower = name.lower().strip()
    if name_lower in BIOMARKER_ALIASES:
        return BIOMARKER_ALIASES[name_lower]
    for key in LONGEVITY_OPTIMAL_RANGES:
        if key.lower() == name_lower:
            return key
    return name.strip()


def get_optimal_range(biomarker: str) -> dict:
    normalized = normalize_biomarker_name(biomarker)
    return LONGEVITY_OPTIMAL_RANGES.get(normalized, None)


def classify_value(biomarker: str, value: float, lab_low: float = None, lab_high: float = None) -> dict:
    optimal = get_optimal_range(biomarker)
    if optimal is None:
        return {"status": "unknown", "color": "gray", "message": "No optimal range defined"}
    opt_low, opt_high = optimal["optimal_low"], optimal["optimal_high"]
    if opt_low <= value <= opt_high:
        return {"status": "optimal", "color": "green", "message": "Within longevity optimal range"}
    is_lab_normal = True
    if lab_low is not None and value < lab_low: is_lab_normal = False
    if lab_high is not None and value > lab_high: is_lab_normal = False
    if is_lab_normal and (value < opt_low or value > opt_high):
        direction = "low" if value < opt_low else "high"
        return {"status": "suboptimal", "color": "yellow", "message": f"Lab normal but longevity sub-optimal ({direction})"}
    if value < opt_low:
        return {"status": "low", "color": "red", "message": "Below optimal range"}
    return {"status": "high", "color": "red", "message": "Above optimal range"}


def get_organ_systems() -> dict:
    systems = {}
    for biomarker, data in LONGEVITY_OPTIMAL_RANGES.items():
        category = data["category"]
        if category not in systems: systems[category] = []
        systems[category].append(biomarker)
    return systems
