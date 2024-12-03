import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def create_custom_network_diagram(activities_df, dependencies_df, cpm_results):
    G = nx.DiGraph()
    
    # Add nodes
    for _, row in activities_df.iterrows():
        G.add_node(row['Activity_Code'], 
                  duration=row['Duration'],
                  critical=row['Activity_Code'] in cpm_results['critical_path'])
    
    # Add edges
    for _, row in dependencies_df.iterrows():
        if pd.notna(row['Prior_Activities']) and row['Prior_Activities'] != '-':
            predecessors = row['Prior_Activities'].split(',')
            for pred in predecessors:
                G.add_edge(pred.strip(), row['Activity_Code'])
    
    plt.figure(figsize=(20, 8))
    
    # Updated position dictionary for all nodes
    pos = {
        'A': (1, 2),
        'B': (2, 2),
        'C1': (3, 2),
        'C2': (4, 2),
        'D': (5, 2),
        'E': (6, 2),
        'F': (7, 3),
        'G': (7, 1),
        'H': (8, 2),
        'I': (9, 2),
        'J': (10, 3),
        'K': (10, 2),
        'L': (10, 1),
        'M': (11, 2),
        'N': (12, 3),
        'O1': (12, 1.5),
        'O2': (13, 1.5),
        'P1': (12, 0.5),
        'P2': (13, 0.5),
        'P3': (14, 0.5),
        'Q1': (15, 2),
        'Q2': (16, 2),
        'R1': (17, 3),
        'R2': (18, 3),
        'R3': (19, 3),
        'S1': (17, 1),
        'S2': (18, 1),
        'S3': (19, 1),
        'T1': (20, 2),
        'T2': (21, 2),
        'U': (22, 2),
        'V': (23, 2),
        'W1': (24, 2),
        'W2': (25, 2),
        'X': (26, 2),
        'Y': (27, 2)
    }
    
    # Draw non-critical nodes
    non_critical_nodes = [node for node in G.nodes() if node not in cpm_results['critical_path']]
    nx.draw_networkx_nodes(G, pos,
                          nodelist=non_critical_nodes,
                          node_color='lightgray',
                          node_size=1000)
    
    # Draw critical nodes
    critical_nodes = [node for node in G.nodes() if node in cpm_results['critical_path']]
    nx.draw_networkx_nodes(G, pos,
                          nodelist=critical_nodes,
                          node_color='red',
                          node_size=1000)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True, arrowsize=15)
    
    # Add labels with duration
    labels = {node: f"{node}\n{G.nodes[node]['duration']}d" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title("Project Network Diagram\n(Critical Path in Red)", pad=20)
    plt.axis('off')
    return plt

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
        if total_float == 0:
            critical_path.append(node)
    
    return {
        'project_duration': project_duration,
        'critical_path': critical_path
    }

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
    'Activity_Code': activities_data['Activity_Code'],
    'Prior_Activities': ['-', 'A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                        'M', 'O1', 'M', 'P1', 'P2', 'N,O2,P3', 'Q1', 'Q2', 'R1', 'R2', 'Q2', 'S1', 'S2',
                        'R3,S3', 'T1', 'T2', 'U', 'V', 'W1', 'W2', 'X']
})

# Run CPM analysis
cpm_results = calculate_cpm(activities_data, dependencies_data)

# Create and display the network diagram
plt = create_custom_network_diagram(activities_data, dependencies_data, cpm_results)
plt.show()

print("\nProject Duration:", cpm_results['project_duration'], "days")
print("Critical Path:", " -> ".join(cpm_results['critical_path']))