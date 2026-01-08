"""
Cross-Dataset Correlation Analysis Module
Time-series correlation between blood biomarkers and WHOOP metrics.
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import correlate
from typing import Dict, List, Tuple, Optional


def calculate_correlation_matrix(df: pd.DataFrame, 
                                  blood_markers: List[str], 
                                  whoop_metrics: List[str]) -> pd.DataFrame:
    """
    Calculate correlation matrix between blood markers and WHOOP metrics.
    Returns DataFrame with correlations and p-values.
    """
    correlations = []
    
    for blood in blood_markers:
        if blood not in df.columns:
            continue
        for whoop in whoop_metrics:
            if whoop not in df.columns:
                continue
            
            # Get non-null pairs
            mask = df[blood].notna() & df[whoop].notna()
            if mask.sum() < 10:
                continue
            
            x = df.loc[mask, blood]
            y = df.loc[mask, whoop]
            
            # Pearson correlation
            r, p = stats.pearsonr(x, y)
            
            # Spearman (rank) correlation
            rho, p_spear = stats.spearmanr(x, y)
            
            correlations.append({
                'blood_marker': blood,
                'whoop_metric': whoop,
                'pearson_r': r,
                'pearson_p': p,
                'spearman_rho': rho,
                'spearman_p': p_spear,
                'n_samples': mask.sum(),
                'significant': p < 0.05
            })
    
    return pd.DataFrame(correlations)


def lagging_indicator_analysis(df: pd.DataFrame,
                                blood_marker: str,
                                whoop_metric: str,
                                max_lag_days: int = 7) -> Dict:
    """
    Analyze time-lagged correlations between a blood marker event 
    and WHOOP metric response.
    
    For example: Does elevated hs-CRP correlate with decreased HRV 48 hours later?
    """
    if blood_marker not in df.columns or whoop_metric not in df.columns:
        return {"error": "Columns not found"}
    
    results = []
    
    for lag in range(-max_lag_days, max_lag_days + 1):
        # Shift blood marker relative to WHOOP
        # Positive lag = blood marker leads (e.g., CRP spike before HRV drop)
        shifted_blood = df[blood_marker].shift(-lag)
        
        # Get valid pairs
        mask = shifted_blood.notna() & df[whoop_metric].notna()
        if mask.sum() < 10:
            continue
        
        x = shifted_blood[mask]
        y = df.loc[mask, whoop_metric]
        
        r, p = stats.pearsonr(x, y)
        
        results.append({
            'lag_days': lag,
            'correlation': r,
            'p_value': p,
            'direction': 'blood_leads' if lag > 0 else 'blood_lags' if lag < 0 else 'same_day'
        })
    
    results_df = pd.DataFrame(results)
    
    # Find optimal lag
    if len(results_df) > 0:
        best_idx = results_df['correlation'].abs().idxmax()
        optimal_lag = results_df.loc[best_idx]
    else:
        optimal_lag = None
    
    return {
        'analysis': results_df.to_dict('records'),
        'optimal_lag': optimal_lag.to_dict() if optimal_lag is not None else None,
        'interpretation': interpret_lag(optimal_lag) if optimal_lag is not None else "Insufficient data"
    }


def interpret_lag(lag_result: pd.Series) -> str:
    """Interpret the lagging indicator result."""
    if lag_result is None:
        return "Insufficient data for analysis"
    
    lag = lag_result['lag_days']
    r = lag_result['correlation']
    p = lag_result['p_value']
    
    if p > 0.05:
        return "No statistically significant relationship found"
    
    strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.6 else "strong"
    direction = "positive" if r > 0 else "negative"
    
    if lag > 0:
        return f"{strength.capitalize()} {direction} correlation: Blood marker changes precede WHOOP metric changes by ~{lag} days"
    elif lag < 0:
        return f"{strength.capitalize()} {direction} correlation: WHOOP metric changes precede blood marker changes by ~{abs(lag)} days"
    else:
        return f"{strength.capitalize()} {direction} correlation: Changes occur simultaneously"


def performance_ceiling_analysis(df: pd.DataFrame,
                                  nutrient_markers: List[str],
                                  performance_metrics: List[str]) -> Dict:
    """
    Analyze if nutrient deficiencies correlate with performance ceilings.
    
    Tests if low Ferritin, Vitamin D, etc. correlate with lower max strain,
    lower peak HRV, etc.
    """
    results = []
    
    for nutrient in nutrient_markers:
        if nutrient not in df.columns:
            continue
        
        # Define "deficiency" as bottom quartile
        nutrient_threshold = df[nutrient].quantile(0.25)
        
        for perf in performance_metrics:
            if perf not in df.columns:
                continue
            
            # Split into deficient vs adequate groups
            deficient = df[df[nutrient] <= nutrient_threshold][perf].dropna()
            adequate = df[df[nutrient] > nutrient_threshold][perf].dropna()
            
            if len(deficient) < 5 or len(adequate) < 5:
                continue
            
            # Statistical tests
            t_stat, t_p = stats.ttest_ind(deficient, adequate)
            mannwhit_u, mannwhit_p = stats.mannwhitneyu(deficient, adequate, alternative='less')
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt((deficient.std()**2 + adequate.std()**2) / 2)
            cohens_d = (adequate.mean() - deficient.mean()) / pooled_std if pooled_std > 0 else 0
            
            results.append({
                'nutrient': nutrient,
                'nutrient_threshold': nutrient_threshold,
                'performance_metric': perf,
                'deficient_mean': deficient.mean(),
                'adequate_mean': adequate.mean(),
                'deficient_max': deficient.max(),
                'adequate_max': adequate.max(),
                't_statistic': t_stat,
                't_p_value': t_p,
                'mann_whitney_p': mannwhit_p,
                'cohens_d': cohens_d,
                'significant': mannwhit_p < 0.05,
                'ceiling_effect': deficient.max() < adequate.mean()
            })
    
    results_df = pd.DataFrame(results)
    
    # Handle empty results
    if results_df.empty:
        return {
            'analysis': [],
            'significant_ceilings': [],
            'summary': "Insufficient data for performance ceiling analysis."
        }
    
    # Identify significant ceiling effects
    significant_effects = results_df[results_df['significant'] & results_df['ceiling_effect']]
    
    return {
        'analysis': results_df.to_dict('records'),
        'significant_ceilings': significant_effects.to_dict('records') if len(significant_effects) > 0 else [],
        'summary': generate_ceiling_summary(significant_effects)
    }


def generate_ceiling_summary(effects_df: pd.DataFrame) -> str:
    """Generate human-readable summary of performance ceiling findings."""
    if len(effects_df) == 0:
        return "No significant performance ceiling effects detected from nutrient status."
    
    summaries = []
    for _, row in effects_df.iterrows():
        nutrient = row['nutrient']
        metric = row['performance_metric']
        diff = row['adequate_mean'] - row['deficient_mean']
        
        summaries.append(
            f"• Low {nutrient} associated with {metric} being {diff:.1f} units lower on average"
        )
    
    return "Performance Ceiling Effects Detected:\n" + "\n".join(summaries)


def cross_correlation_heatmap_data(df: pd.DataFrame,
                                    blood_cols: List[str],
                                    whoop_cols: List[str]) -> Dict:
    """
    Generate data for correlation heatmap visualization.
    """
    # Filter to available columns
    blood_available = [c for c in blood_cols if c in df.columns]
    whoop_available = [c for c in whoop_cols if c in df.columns]
    
    if not blood_available or not whoop_available:
        return {"error": "Insufficient columns for heatmap"}
    
    # Create correlation matrix
    corr_matrix = np.zeros((len(blood_available), len(whoop_available)))
    p_matrix = np.zeros((len(blood_available), len(whoop_available)))
    
    for i, blood in enumerate(blood_available):
        for j, whoop in enumerate(whoop_available):
            mask = df[blood].notna() & df[whoop].notna()
            if mask.sum() >= 10:
                r, p = stats.pearsonr(df.loc[mask, blood], df.loc[mask, whoop])
                corr_matrix[i, j] = r
                p_matrix[i, j] = p
            else:
                corr_matrix[i, j] = np.nan
                p_matrix[i, j] = 1.0
    
    return {
        'correlations': corr_matrix.tolist(),
        'p_values': p_matrix.tolist(),
        'blood_markers': blood_available,
        'whoop_metrics': whoop_available
    }


def generate_insights(correlation_df: pd.DataFrame,
                       lag_results: Dict,
                       ceiling_results: Dict) -> List[Dict]:
    """
    Generate actionable insights from all correlation analyses.
    """
    insights = []
    
    # Strong correlations
    if len(correlation_df) > 0:
        strong_corrs = correlation_df[
            (correlation_df['pearson_r'].abs() > 0.5) & 
            (correlation_df['significant'])
        ]
        
        for _, row in strong_corrs.iterrows():
            r = row['pearson_r']
            direction = "positively" if r > 0 else "negatively"
            
            insights.append({
                'type': 'correlation',
                'priority': 'high' if abs(r) > 0.7 else 'medium',
                'finding': f"{row['blood_marker']} is strongly {direction} correlated with {row['whoop_metric']}",
                'correlation': r,
                'actionable': True
            })
    
    # Lagging indicators
    if lag_results and lag_results.get('optimal_lag'):
        lag = lag_results['optimal_lag']
        if lag['p_value'] < 0.05 and abs(lag['correlation']) > 0.3:
            insights.append({
                'type': 'predictive',
                'priority': 'high',
                'finding': lag_results['interpretation'],
                'lag_days': lag['lag_days'],
                'actionable': True
            })
    
    # Performance ceilings
    if ceiling_results and ceiling_results.get('significant_ceilings'):
        for effect in ceiling_results['significant_ceilings']:
            insights.append({
                'type': 'ceiling',
                'priority': 'high',
                'finding': f"Low {effect['nutrient']} limits {effect['performance_metric']} potential",
                'effect_size': effect['cohens_d'],
                'actionable': True
            })
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    insights.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
    
    return insights
