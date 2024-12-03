import pandas as pd
import numpy as np
from scipy import stats

# Create PERT dataframe with time estimates
pert_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
    'Optimistic': [1, 6, 1, 5, 2, 5, 2, 4, 3, 2, 4, 1, 2, 7, 6,
                   1, 1, 1, 1, 1, 18, 18, 2, 2, 2, 1, 1, 1,
                   2, 2, 9, 9, 6, 6, 4, 1],
    'Most_Likely': [1, 8, 2, 7, 3, 7, 3, 6, 4, 3, 5, 2, 3, 9, 8,
                    2, 2, 2, 2, 2, 22, 22, 3, 3, 3, 2, 2, 2,
                    3, 3, 12, 12, 8, 8, 6, 1],
    'Pessimistic': [2, 12, 4, 10, 5, 10, 5, 9, 6, 5, 7, 4, 5, 12, 11,
                    4, 4, 4, 4, 4, 28, 28, 5, 5, 5, 4, 4, 4,
                    5, 5, 16, 16, 11, 11, 9, 2]
})

def calculate_pert_estimates(data):
    # Calculate PERT expected time and variance
    data['Expected_Time'] = (data['Optimistic'] + 4*data['Most_Likely'] + data['Pessimistic'])/6
    data['Variance'] = ((data['Pessimistic'] - data['Optimistic'])/6)**2
    data['Std_Dev'] = np.sqrt(data['Variance'])
    
    return data

def calculate_completion_probability(pert_results, target_duration, critical_path_activities):
    # Sum expected times and variances for critical path activities
    critical_path_data = pert_results[pert_results['Activity_Code'].isin(critical_path_activities)]
    
    project_expected_time = critical_path_data['Expected_Time'].sum()
    project_variance = critical_path_data['Variance'].sum()
    project_std_dev = np.sqrt(project_variance)
    
    # Calculate Z-score for target duration
    z_score = (target_duration - project_expected_time) / project_std_dev
    
    # Calculate probability using normal distribution
    probability = stats.norm.cdf(z_score)
    
    return {
        'Expected_Duration': project_expected_time,
        'Standard_Deviation': project_std_dev,
        'Z_Score': z_score,
        'Completion_Probability': probability
    }

def analyze_activity_risks(pert_results):
    # Calculate coefficient of variation (CV) to assess relative risk
    pert_results['CV'] = pert_results['Std_Dev'] / pert_results['Expected_Time']
    
    # Classify risk levels
    pert_results['Risk_Level'] = pd.cut(pert_results['CV'],
                                      bins=[-np.inf, 0.1, 0.2, np.inf],
                                      labels=['Low', 'Medium', 'High'])
    
    return pert_results

# Calculate PERT estimates
pert_results = calculate_pert_estimates(pert_data)

# Critical path from previous CPM analysis (example)
critical_path = ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'H', 'I', 'J', 'M', 'N', 'Q1', 'Q2', 
                'R1', 'R2', 'R3', 'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y']

# Calculate probabilities for different target durations
target_durations = [165, 170, 175, 180, 185]
probability_results = {}
for target in target_durations:
    probability_results[target] = calculate_completion_probability(pert_results, 
                                                                target, 
                                                                critical_path)

# Analyze activity risks
risk_analysis = analyze_activity_risks(pert_results)

# Print Results
print("\nPERT ANALYSIS RESULTS")
print("=" * 80)

print("\nActivity Time Estimates:")
print("-" * 50)
print(pert_results[['Activity_Code', 'Expected_Time', 'Std_Dev', 'CV']].to_string(index=False))

print("\nProject Completion Probabilities:")
print("-" * 50)
for target, result in probability_results.items():
    print(f"\nTarget Duration: {target} days")
    print(f"Expected Project Duration: {result['Expected_Duration']:.1f} days")
    print(f"Project Standard Deviation: {result['Standard_Deviation']:.1f} days")
    print(f"Completion Probability: {result['Completion_Probability']*100:.1f}%")

print("\nHigh Risk Activities (CV > 0.2):")
print("-" * 50)
high_risk = risk_analysis[risk_analysis['Risk_Level'] == 'High']
if not high_risk.empty:
    print(high_risk[['Activity_Code', 'Expected_Time', 'CV', 'Risk_Level']].to_string(index=False))
else:
    print("No high-risk activities identified")

print("\nPERT Analysis Summary:")
print("-" * 50)
base_result = probability_results[170]  # Using 170 days as base since it's close to expected duration
print(f"Most Likely Project Duration: {base_result['Expected_Duration']:.1f} days")
print(f"Project Standard Deviation: {base_result['Standard_Deviation']:.1f} days")
print(f"68% Confidence Interval: {base_result['Expected_Duration']-base_result['Standard_Deviation']:.1f} to "
      f"{base_result['Expected_Duration']+base_result['Standard_Deviation']:.1f} days")
print(f"95% Confidence Interval: {base_result['Expected_Duration']-2*base_result['Standard_Deviation']:.1f} to "
      f"{base_result['Expected_Duration']+2*base_result['Standard_Deviation']:.1f} days")