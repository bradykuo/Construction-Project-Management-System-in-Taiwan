import pandas as pd
import networkx as nx

# Create activities dataframe
activities_data = pd.DataFrame({
    'Activity_Code': ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                     'O1', 'O2', 'P1', 'P2', 'P3', 'Q1', 'Q2', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 
                     'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X', 'Y'],
    'Duration': [1, 8, 2, 7, 3, 7, 3, 6, 4, 3, 5, 2, 3, 9, 8, 
                 2, 2, 2, 2, 2, 22, 22, 3, 3, 3, 2, 2, 2, 
                 3, 3, 12, 12, 8, 8, 6, 1]
})

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

# Run CPM analysis
results = calculate_cpm(activities_data, dependencies_data)

print(f"\nProject Duration: {results['project_duration']} days")
print(f"\nCritical Path: {' -> '.join(results['critical_path'])}")
print("\nDetailed Activity Analysis:")
print(results['results'].to_string())