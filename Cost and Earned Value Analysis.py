import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create activities dataframe with cost data
activities_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
    'Duration': [1, 8, 2, 7, 3, 7, 3, 6, 4, 3, 5, 2, 3, 9, 8, 
                 2, 2, 2, 2, 2, 22, 22, 3, 3, 3, 2, 2, 2, 
                 3, 3, 12, 12, 8, 8, 6, 1],
    'Budget_Cost': [1000, 8000, 2000, 7000, 3000, 7000, 3000, 6000, 4000, 3000, 5000, 2000, 3000, 
                    9000, 8000, 2000, 2000, 2000, 2000, 2000, 22000, 22000, 3000, 3000, 3000, 
                    2000, 2000, 2000, 3000, 3000, 12000, 12000, 8000, 8000, 6000, 1000],
    'Actual_Cost': [1200, 7800, 2200, 7500, 2800, 7200, 3100, 6200, 4200, 2900, 5100, 1900, 3200, 
                    9500, 8200, 1900, 2100, 2100, 1900, 2200, 23000, 21500, 3200, 2900, 3100, 
                    1900, 2100, 2000, 3200, 2900, 12500, 12200, 8300, 7800, 6200, 900],
    'Percent_Complete': [100, 100, 100, 100, 100, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45,
                        40, 35, 30, 25, 20, 15, 10, 5, 5, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0]
})

def perform_earned_value_analysis(activities_df, current_date):
    # Calculate basic metrics
    BAC = activities_df['Budget_Cost'].sum()  # Budget at Completion
    
    # Calculate PV, EV, and AC
    PV = 0  # Planned Value
    EV = 0  # Earned Value
    AC = 0  # Actual Cost
    
    for _, activity in activities_df.iterrows():
        # Planned Value calculation
        if activity['Duration'] > 0:
            planned_percent = 100
            PV += (planned_percent/100) * activity['Budget_Cost']
        
        # Earned Value calculation
        EV += (activity['Percent_Complete']/100) * activity['Budget_Cost']
        
        # Actual Cost calculation
        if activity['Percent_Complete'] > 0:
            AC += activity['Actual_Cost'] * (activity['Percent_Complete']/100)
    
    # Calculate performance indices
    SV = EV - PV  # Schedule Variance
    CV = EV - AC  # Cost Variance
    
    SPI = EV/PV if PV != 0 else 0  # Schedule Performance Index
    CPI = EV/AC if AC != 0 else 0  # Cost Performance Index
    
    # Estimate at Completion (EAC)
    EAC = BAC/CPI if CPI != 0 else 0
    
    # Variance at Completion (VAC)
    VAC = BAC - EAC
    
    # To Complete Performance Index (TCPI)
    work_remaining = BAC - EV
    cost_remaining = EAC - AC
    TCPI = work_remaining/cost_remaining if cost_remaining != 0 else 0
    
    return {
        'BAC': BAC,
        'PV': PV,
        'EV': EV,
        'AC': AC,
        'SV': SV,
        'CV': CV,
        'SPI': SPI,
        'CPI': CPI,
        'EAC': EAC,
        'VAC': VAC,
        'TCPI': TCPI
    }

def analyze_cost_variance(activities_df):
    cost_analysis = []
    
    for _, activity in activities_df.iterrows():
        budget = activity['Budget_Cost']
        actual = activity['Actual_Cost']
        variance = budget - actual
        variance_pct = (variance/budget)*100 if budget != 0 else 0
        
        status = 'On Budget'
        if variance_pct < -5:
            status = 'Over Budget'
        elif variance_pct > 5:
            status = 'Under Budget'
            
        cost_analysis.append({
            'Activity': activity['Activity_Code'],
            'Budget': budget,
            'Actual': actual,
            'Variance': variance,
            'Variance_Pct': variance_pct,
            'Status': status
        })
    
    return pd.DataFrame(cost_analysis)

# Set current date for analysis
current_date = datetime(2024, 1, 1) + timedelta(days=30)  # 30 days into project

# Perform analyses
eva_results = perform_earned_value_analysis(activities_data, current_date)
cost_variance_results = analyze_cost_variance(activities_data)

# Print Results
print("\nEARNED VALUE ANALYSIS RESULTS")
print("=" * 80)
print(f"Budget at Completion (BAC): ${eva_results['BAC']:,.2f}")
print(f"Planned Value (PV): ${eva_results['PV']:,.2f}")
print(f"Earned Value (EV): ${eva_results['EV']:,.2f}")
print(f"Actual Cost (AC): ${eva_results['AC']:,.2f}")
print("\nPERFORMANCE METRICS")
print("-" * 50)
print(f"Schedule Variance (SV): ${eva_results['SV']:,.2f}")
print(f"Cost Variance (CV): ${eva_results['CV']:,.2f}")
print(f"Schedule Performance Index (SPI): {eva_results['SPI']:.2f}")
print(f"Cost Performance Index (CPI): {eva_results['CPI']:.2f}")
print("\nFORECASTS")
print("-" * 50)
print(f"Estimate at Completion (EAC): ${eva_results['EAC']:,.2f}")
print(f"Variance at Completion (VAC): ${eva_results['VAC']:,.2f}")
print(f"To Complete Performance Index (TCPI): {eva_results['TCPI']:.2f}")

print("\nCOST VARIANCE ANALYSIS")
print("=" * 80)
print("\nActivities with Significant Variances (>5%):")
significant_variances = cost_variance_results[
    (cost_variance_results['Variance_Pct'].abs() > 5)
].sort_values('Variance_Pct', ascending=False)
print(significant_variances.to_string(index=False))

# Performance Assessment
print("\nPROJECT PERFORMANCE ASSESSMENT")
print("=" * 80)
if eva_results['SPI'] < 0.95:
    print("Schedule Performance: Behind Schedule")
elif eva_results['SPI'] > 1.05:
    print("Schedule Performance: Ahead of Schedule")
else:
    print("Schedule Performance: On Schedule")

if eva_results['CPI'] < 0.95:
    print("Cost Performance: Over Budget")
elif eva_results['CPI'] > 1.05:
    print("Cost Performance: Under Budget")
else:
    print("Cost Performance: On Budget")

# Recommendations
print("\nRECOMMENDATIONS")
print("=" * 80)
if eva_results['CPI'] < 1:
    print("- Implement cost control measures")
    print("- Review cost overrun activities for optimization")
if eva_results['SPI'] < 1:
    print("- Accelerate critical activities")
    print("- Review resource allocation")
if eva_results['TCPI'] > 1.1:
    print("- Significant performance improvement needed to meet budget")
    print("- Consider scope reduction or budget revision")