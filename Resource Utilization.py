import pandas as pd
import numpy as np
import networkx as nx

# Create activities dataframe first
activities_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
    'Duration': [1, 8, 2, 7, 3, 7, 3, 6, 4, 3, 5, 2, 3, 9, 8, 
                 2, 2, 2, 2, 2, 22, 22, 3, 3, 3, 2, 2, 2, 
                 3, 3, 12, 12, 8, 8, 6, 1]
})

# Add resource data
activities_data['Foremen'] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                             1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1,
                             1, 1, 1, 1, 1, 1, 1, 2]

activities_data['Workers'] = [2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2,
                            2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 2, 2, 2,
                            2, 2, 2, 2, 2, 2, 2, 0]

# Create dependencies dataframe
dependencies_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3',
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
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
    
    late_times = {}
    project_duration = max(t['EF'] for t in early_times.values())
    
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

def analyze_resources(activities_df, cpm_results):
    project_duration = cpm_results['project_duration']
    results_df = cpm_results['results']
    
    # Initialize resource arrays
    foremen_usage = np.zeros(project_duration + 1)
    workers_usage = np.zeros(project_duration + 1)
    
    # Calculate daily resource usage
    for _, activity in results_df.iterrows():
        es = activity['ES']
        ef = activity['EF']
        act_code = activity['Activity']
        
        # Get resource requirements
        foremen = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Foremen'].values[0]
        workers = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Workers'].values[0]
        
        # Add resources for duration of activity
        for day in range(int(es), int(ef)):
            foremen_usage[day] += foremen
            workers_usage[day] += workers
    
    # Calculate resource metrics
    resource_metrics = {
        'Peak_Foremen': max(foremen_usage),
        'Peak_Workers': max(workers_usage),
        'Avg_Foremen': np.mean(foremen_usage),
        'Avg_Workers': np.mean(workers_usage),
        'Daily_Foremen': foremen_usage,
        'Daily_Workers': workers_usage
    }
    
    # Identify resource leveling opportunities
    leveling_opportunities = []
    
    # Check for activities with float that could be shifted
    for _, activity in results_df.iterrows():
        if activity['Total_Float'] > 0:
            act_code = activity['Activity']
            foremen = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Foremen'].values[0]
            workers = activities_df.loc[activities_df['Activity_Code'] == act_code, 'Workers'].values[0]
            
            if foremen > 0 or workers > 0:
                leveling_opportunities.append({
                    'Activity': act_code,
                    'Float': activity['Total_Float'],
                    'Foremen': foremen,
                    'Workers': workers
                })
    
    return resource_metrics, leveling_opportunities

# Run CPM analysis first
results = calculate_cpm(activities_data, dependencies_data)

# Then run resource analysis
resource_metrics, leveling_opportunities = analyze_resources(activities_data, results)

# Print results
print("\nRESOURCE ANALYSIS RESULTS")
print("-" * 50)
print(f"\nPeak Resource Requirements:")
print(f"Maximum Foremen needed: {resource_metrics['Peak_Foremen']}")
print(f"Maximum Workers needed: {resource_metrics['Peak_Workers']}")
print(f"\nAverage Resource Utilization:")
print(f"Average Foremen per day: {resource_metrics['Avg_Foremen']:.2f}")
print(f"Average Workers per day: {resource_metrics['Avg_Workers']:.2f}")

print("\nResource Leveling Opportunities:")
print("-" * 50)
for opp in leveling_opportunities:
    print(f"Activity {opp['Activity']}:")
    print(f"  Float available: {opp['Float']} days")
    print(f"  Resources that could be shifted: {opp['Foremen']} foremen, {opp['Workers']} workers")

# Identify peak resource periods
peak_foremen_days = np.where(resource_metrics['Daily_Foremen'] == resource_metrics['Peak_Foremen'])[0]
peak_workers_days = np.where(resource_metrics['Daily_Workers'] == resource_metrics['Peak_Workers'])[0]

print("\nPeak Resource Periods:")
print("-" * 50)
print(f"Peak Foremen Usage occurs on days: {peak_foremen_days}")
print(f"Peak Workers Usage occurs on days: {peak_workers_days}")