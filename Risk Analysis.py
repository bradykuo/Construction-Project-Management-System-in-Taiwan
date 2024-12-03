import pandas as pd
import numpy as np
import networkx as nx

# Create activities dataframe
activities_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
    'Duration': [1, 8, 2, 7, 3, 7, 3, 6, 4, 3, 5, 2, 3, 9, 8, 
                 2, 2, 2, 2, 2, 22, 22, 3, 3, 3, 2, 2, 2, 
                 3, 3, 12, 12, 8, 8, 6, 1],
    'Foremen': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 2],
    'Workers': [2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2,
                2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 2, 2, 2,
                2, 2, 2, 2, 2, 2, 2, 0]
})

# Create dependencies dataframe
dependencies_data = pd.DataFrame({
    'Activity_Code': activities_data['Activity_Code'],
    'Prior_Activities': ['-', 'A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                        'M', 'O1', 'M', 'P1', 'P2', 'N,O2,P3', 'Q1', 'Q2', 'R1', 'R2', 'Q2', 'S1', 'S2',
                        'R3,S3', 'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X']
})

def calculate_cpm(activities_df, dependencies_df):
    G = nx.DiGraph()
    
    for _, row in activities_df.iterrows():
        G.add_node(row['Activity_Code'], duration=row['Duration'])
    
    for _, row in dependencies_df.iterrows():
        if pd.notna(row['Prior_Activities']) and row['Prior_Activities'] != '-':
            predecessors = row['Prior_Activities'].split(',')
            for pred in predecessors:
                G.add_edge(pred.strip(), row['Activity_Code'])
    
    early_times = {}
    for node in nx.topological_sort(G):
        predecessors = list(G.predecessors(node))
        if not predecessors:
            early_times[node] = {'ES': 0, 'EF': G.nodes[node]['duration']}
        else:
            es = max(early_times[p]['EF'] for p in predecessors)
            early_times[node] = {
                'ES': es,
                'EF': es + G.nodes[node]['duration']
            }
    
    project_duration = max(t['EF'] for t in early_times.values())
    
    late_times = {}
    for node in reversed(list(nx.topological_sort(G))):
        successors = list(G.successors(node))
        if not successors:
            late_times[node] = {
                'LF': project_duration,
                'LS': project_duration - G.nodes[node]['duration']
            }
        else:
            lf = min(late_times[s]['LS'] for s in successors)
            late_times[node] = {
                'LF': lf,
                'LS': lf - G.nodes[node]['duration']
            }
    
    float_times = {}
    critical_path = []
    
    for node in G.nodes():
        total_float = late_times[node]['LS'] - early_times[node]['ES']
        float_times[node] = total_float
        if total_float == 0:
            critical_path.append(node)
    
    results_df = pd.DataFrame({
        'Activity': list(G.nodes()),
        'Duration': [G.nodes[n]['duration'] for n in G.nodes()],
        'ES': [early_times[n]['ES'] for n in G.nodes()],
        'EF': [early_times[n]['EF'] for n in G.nodes()],
        'LS': [late_times[n]['LS'] for n in G.nodes()],
        'LF': [late_times[n]['LF'] for n in G.nodes()],
        'Total_Float': [float_times[n] for n in G.nodes()],
        'Critical': [n in critical_path for n in G.nodes()]
    })
    
    return {
        'project_duration': project_duration,
        'critical_path': critical_path,
        'results': results_df
    }

def calculate_resource_metrics(activities_df, cpm_results):
    project_duration = cpm_results['project_duration']
    results_df = cpm_results['results']
    
    daily_foremen = np.zeros(project_duration + 1)
    daily_workers = np.zeros(project_duration + 1)
    
    for _, activity in results_df.iterrows():
        es = int(activity['ES'])
        ef = int(activity['EF'])
        act_code = activity['Activity']
        
        foremen = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Foremen'].values[0]
        workers = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Workers'].values[0]
        
        for day in range(es, ef):
            daily_foremen[day] += foremen
            daily_workers[day] += workers
    
    return {
        'Daily_Foremen': daily_foremen,
        'Daily_Workers': daily_workers,
        'Peak_Foremen': max(daily_foremen),
        'Peak_Workers': max(daily_workers),
        'Avg_Foremen': np.mean(daily_foremen),
        'Avg_Workers': np.mean(daily_workers)
    }

def analyze_risks(activities_df, cpm_results, resource_metrics):
    risk_analysis = {
        'critical_activities': [],
        'resource_bottlenecks': [],
        'schedule_constraints': []
    }
    
    # 1. Analyze Critical Activities (Zero Float)
    critical_activities = cpm_results['results'][cpm_results['results']['Critical'] == True]
    for _, activity in critical_activities.iterrows():
        duration = activity['Duration']
        impact_level = 'High' if duration > 10 else 'Medium' if duration > 5 else 'Low'
        risk_analysis['critical_activities'].append({
            'Activity': activity['Activity'],
            'Duration': duration,
            'Impact_Level': impact_level,
            'ES': activity['ES'],
            'EF': activity['EF']
        })
    
    # 2. Analyze Resource Bottlenecks
    daily_resource_usage = resource_metrics['Daily_Foremen']
    peak_days = np.where(daily_resource_usage >= np.percentile(daily_resource_usage, 75))[0]
    
    for day in peak_days:
        concurrent_activities = []
        for _, activity in cpm_results['results'].iterrows():
            if activity['ES'] <= day <= activity['EF']:
                concurrent_activities.append(activity['Activity'])
        
        if len(concurrent_activities) > 2:
            risk_analysis['resource_bottlenecks'].append({
                'Day': day,
                'Resource_Level': daily_resource_usage[day],
                'Concurrent_Activities': concurrent_activities
            })
    
    # 3. Analyze Schedule Constraints
    results_df = cpm_results['results']
    for _, activity in results_df.iterrows():
        if activity['Duration'] > 15:
            risk_analysis['schedule_constraints'].append({
                'Type': 'Long Duration',
                'Activity': activity['Activity'],
                'Duration': activity['Duration'],
                'Risk_Level': 'High'
            })
        
        if 0 < activity['Total_Float'] <= 3:
            risk_analysis['schedule_constraints'].append({
                'Type': 'Tight Sequence',
                'Activity': activity['Activity'],
                'Float': activity['Total_Float'],
                'Risk_Level': 'Medium'
            })

    return risk_analysis

# Run CPM analysis
cpm_results = calculate_cpm(activities_data, dependencies_data)

# Calculate resource metrics
resource_metrics = calculate_resource_metrics(activities_data, cpm_results)

# Run risk analysis
risk_results = analyze_risks(activities_data, cpm_results, resource_metrics)

# Print Results
print("\nRISK ANALYSIS RESULTS")
print("=" * 80)

print("\n1. CRITICAL ACTIVITIES ANALYSIS")
print("-" * 50)
critical_df = pd.DataFrame(risk_results['critical_activities'])
if not critical_df.empty:
    print(critical_df.to_string(index=False))
else:
    print("No critical activities found.")

print("\n2. RESOURCE BOTTLENECK ANALYSIS")
print("-" * 50)
if risk_results['resource_bottlenecks']:
    for bottleneck in risk_results['resource_bottlenecks']:
        print(f"Day {bottleneck['Day']}: {len(bottleneck['Concurrent_Activities'])} concurrent activities")
        print(f"Resource Level: {bottleneck['Resource_Level']}")
        print(f"Activities: {', '.join(bottleneck['Concurrent_Activities'])}")
        print()
else:
    print("No significant resource bottlenecks found.")

print("\n3. SCHEDULE CONSTRAINTS ANALYSIS")
print("-" * 50)
constraints_df = pd.DataFrame(risk_results['schedule_constraints'])
if not constraints_df.empty:
    print(constraints_df.to_string(index=False))
else:
    print("No significant schedule constraints found.")

print("\nRECOMMENDATIONS:")
print("-" * 50)
print("1. Critical Activities:")
critical_count = 0
for act in risk_results['critical_activities']:
    if act['Impact_Level'] == 'High':
        print(f"- Implement contingency plans for {act['Activity']} (Duration: {act['Duration']} days)")
        critical_count += 1
if critical_count == 0:
    print("- No high-impact critical activities identified")

print("\n2. Resource Management:")
if risk_results['resource_bottlenecks']:
    print("- Consider resource leveling for peak periods")
    print("- Plan for additional resource availability during peak days")
else:
    print("- Current resource allocation appears adequate")

print("\n3. Schedule Management:")
constraint_count = 0
for constraint in risk_results['schedule_constraints']:
    if constraint['Risk_Level'] == 'High':
        print(f"- Consider breaking down {constraint['Activity']} into smaller activities")
        constraint_count += 1
if constraint_count == 0:
    print("- No high-risk schedule constraints identified")