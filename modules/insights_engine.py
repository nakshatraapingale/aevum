"""
Insights Engine - Actionable Protocol Generator
"""
from typing import Dict, List
from modules.optimal_ranges import get_optimal_range, normalize_biomarker_name, classify_value

INTERVENTION_PROTOCOLS = {
    "Glucose_high": {"category": "Metabolic", "interventions": ["Time-restricted eating (16:8)", "Post-meal walks (10-15 min)", "Reduce refined carbs by 50%", "Sleep 7-9 hours consistently"], "mechanism": "Improves insulin sensitivity"},
    "HbA1c_high": {"category": "Metabolic", "interventions": ["Use CGM for 2 weeks", "Replace high-glycemic foods", "Fiber intake 30-40g daily", "Zone 2 cardio 150+ min/week"], "mechanism": "Reduces glycemic variability"},
    "Triglycerides_high": {"category": "Metabolic", "interventions": ["Eliminate added sugars/alcohol 30 days", "Omega-3: 2-4g EPA/DHA daily", "Aerobic exercise 30 min daily"], "mechanism": "Reduces hepatic TG production"},
    "LDL Cholesterol_high": {"category": "Metabolic", "interventions": ["Soluble fiber 10-25g daily", "Plant sterols 2g daily", "Replace saturated with unsaturated fats", "Track ApoB for better risk assessment"], "mechanism": "Reduces cholesterol absorption"},
    "ApoB_high": {"category": "Metabolic", "interventions": ["Saturated fat <10g/day", "EPA/DHA 2-4g daily", "Discuss statin with physician", "Zone 2 cardio 4-5x weekly"], "mechanism": "Reduces atherogenic particles"},
    "hs-CRP_high": {"category": "Inflammatory", "interventions": ["Mediterranean diet protocol", "Omega-3 index target >8%", "Sleep optimization", "Address oral health"], "mechanism": "Reduces systemic inflammation"},
    "Homocysteine_high": {"category": "Inflammatory", "interventions": ["Methylated B-vitamins", "Increase folate-rich foods", "Test MTHFR polymorphism", "Betaine (TMG) 500-1000mg daily"], "mechanism": "Supports methylation cycle"},
    "WBC_high": {"category": "Inflammatory", "interventions": ["Rule out infection/stress", "Reduce processed foods", "HRV training/meditation", "Check for hidden infections"], "mechanism": "Reduces immune activation"},
    "Albumin_low": {"category": "Inflammatory", "interventions": ["Protein 1.2-1.6g/kg body weight", "Address gut issues", "Ensure adequate calories"], "mechanism": "Supports albumin synthesis"},
    "Ferritin_low": {"category": "Hematologic", "interventions": ["Iron-rich foods (red meat, greens)", "Iron bisglycinate 25-50mg + vit C", "Avoid calcium/coffee with iron meals", "Target ferritin 50-150 ng/mL"], "mechanism": "Replenishes iron stores"},
    "Ferritin_high": {"category": "Hematologic", "interventions": ["Test for hemochromatosis", "Blood donation if eligible", "Reduce red meat intake", "Monitor liver function"], "mechanism": "Prevents iron-mediated damage"},
    "RDW_high": {"category": "Hematologic", "interventions": ["Test B12, folate, iron, copper", "Address deficiencies", "Anti-inflammatory protocol"], "mechanism": "Normalizes RBC production"},
    "Vitamin D_low": {"category": "Nutritional", "interventions": ["D3 5,000-10,000 IU daily", "Sun 15-30 min midday", "Take D3 with fat", "Add K2 (MK-7) 100-200mcg", "Target 50-80 ng/mL"], "mechanism": "Essential for immune/hormonal function"},
    "ALT_high": {"category": "Liver", "interventions": ["Eliminate alcohol 30+ days", "Reduce fructose/processed foods", "Milk thistle 200-400mg", "NAC 600-1200mg daily"], "mechanism": "Reduces hepatocyte stress"},
    "GGT_high": {"category": "Liver", "interventions": ["Complete alcohol cessation", "Weight loss 5-10%", "Cruciferous vegetables", "NAC + milk thistle"], "mechanism": "Reduces oxidative stress"},
    "Creatinine_high": {"category": "Kidney", "interventions": ["Hydration 3+ liters daily", "Moderate protein if excessive", "Monitor blood pressure", "Reduce NSAIDs"], "mechanism": "Supports kidney function"},
    "Uric Acid_high": {"category": "Kidney", "interventions": ["Reduce purine-rich foods", "Increase water intake", "Tart cherry extract 500mg 2x", "Reduce fructose"], "mechanism": "Reduces uric acid"},
    "TSH_high": {"category": "Thyroid", "interventions": ["Full thyroid panel test", "Selenium 200mcg daily", "Optimize iodine status", "Discuss medication if hypothyroid"], "mechanism": "Supports thyroid function"},
    "TSH_low": {"category": "Thyroid", "interventions": ["Full thyroid panel + antibodies", "Reduce caffeine/stimulants", "Stress management", "Consult endocrinologist"], "mechanism": "Normalizes thyroid axis"},
}


def generate_protocol(biomarkers: Dict, top_n: int = 5) -> List[Dict]:
    """Generate prioritized intervention protocol based on biomarker deviations."""
    deviations = []
    for marker, data in biomarkers.items():
        value = data.get('value') if isinstance(data, dict) else data
        lab_low = data.get('lab_low') if isinstance(data, dict) else None
        lab_high = data.get('lab_high') if isinstance(data, dict) else None
        if value is None:
            continue
        classification = classify_value(marker, value, lab_low, lab_high)
        if classification['status'] in ['optimal', 'unknown']:
            continue
        optimal = get_optimal_range(marker)
        if optimal:
            opt_low, opt_high = optimal['optimal_low'], optimal['optimal_high']
            opt_range = opt_high - opt_low
            if value < opt_low:
                deviation_pct = (opt_low - value) / opt_range * 100
                direction = 'low'
            else:
                deviation_pct = (value - opt_high) / opt_range * 100
                direction = 'high'
            deviations.append({
                'marker': marker, 'value': value, 'optimal_low': opt_low,
                'optimal_high': opt_high, 'deviation_pct': deviation_pct,
                'direction': direction, 'status': classification['status'],
                'category': optimal.get('category', 'Unknown')
            })
    deviations.sort(key=lambda x: x['deviation_pct'], reverse=True)
    protocols = []
    for dev in deviations[:top_n]:
        marker = normalize_biomarker_name(dev['marker'])
        key = f"{marker}_{dev['direction']}"
        if key in INTERVENTION_PROTOCOLS:
            protocol = INTERVENTION_PROTOCOLS[key].copy()
            protocol['target_marker'] = dev['marker']
            protocol['current_value'] = dev['value']
            protocol['optimal_range'] = f"{dev['optimal_low']}-{dev['optimal_high']}"
            protocol['deviation_severity'] = 'high' if dev['deviation_pct'] > 50 else 'moderate' if dev['deviation_pct'] > 25 else 'mild'
            protocol['priority_score'] = dev['deviation_pct']
            protocols.append(protocol)
        else:
            protocols.append({
                'category': dev['category'], 'target_marker': dev['marker'],
                'current_value': dev['value'], 'optimal_range': f"{dev['optimal_low']}-{dev['optimal_high']}",
                'deviation_severity': 'high' if dev['deviation_pct'] > 50 else 'moderate',
                'priority_score': dev['deviation_pct'],
                'interventions': [f"Optimize {dev['marker']} through diet/lifestyle", "Consult healthcare provider", "Retest in 3 months"],
                'mechanism': "Supports metabolic health"
            })
    return protocols


def summarize_health_status(biomarkers: Dict, organ_scores: Dict) -> Dict:
    """Generate overall health status summary."""
    status_counts = {'optimal': 0, 'suboptimal': 0, 'low': 0, 'high': 0, 'unknown': 0}
    for marker, data in biomarkers.items():
        value = data.get('value') if isinstance(data, dict) else data
        if value is None:
            continue
        classification = classify_value(marker, value)
        status_counts[classification['status']] += 1
    total = sum(status_counts.values())
    optimal_pct = (status_counts['optimal'] / total * 100) if total > 0 else 0
    weak_systems = []
    for system, data in organ_scores.items():
        if data.get('score') and data['score'] < 70:
            weak_systems.append({'system': system, 'score': data['score'], 'interpretation': data.get('interpretation', 'Needs attention')})
    weak_systems.sort(key=lambda x: x['score'])
    if optimal_pct >= 80: overall_grade, overall_message = 'A', 'Excellent - Most markers optimal'
    elif optimal_pct >= 60: overall_grade, overall_message = 'B', 'Good - Majority healthy'
    elif optimal_pct >= 40: overall_grade, overall_message = 'C', 'Fair - Several areas need work'
    elif optimal_pct >= 20: overall_grade, overall_message = 'D', 'Needs Attention'
    else: overall_grade, overall_message = 'F', 'Critical - Intervention needed'
    return {
        'overall_grade': overall_grade, 'overall_message': overall_message,
        'optimal_percentage': round(optimal_pct, 1), 'status_breakdown': status_counts,
        'total_markers': total, 'weakest_systems': weak_systems[:3],
        'priority_focus': weak_systems[0]['system'] if weak_systems else None
    }
