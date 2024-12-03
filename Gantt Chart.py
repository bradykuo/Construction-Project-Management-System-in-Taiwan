import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime, timedelta
import networkx as nx

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
    
    # Create results DataFrame
    results_df = pd.DataFrame({
        'Activity': list(G.nodes()),
        'Duration': [G.nodes[n]['duration'] for n in G.nodes()],
        'ES': [early_times[n]['ES'] for n in G.nodes()],
        'EF': [early_times[n]['EF'] for n in G.nodes()],
        'LS': [late_times[n]['LS'] for n in G.nodes()],
        'LF': [late_times[n]['LF'] for n in G.nodes()],
        'Total_Float': [late_times[n]['LS'] - early_times[n]['ES'] for n in G.nodes()],
        'Critical': [n in critical_path for n in G.nodes()]
    })
    
    return {
        'project_duration': project_duration,
        'critical_path': critical_path,
        'results': results_df
    }

def create_gantt_chart(cpm_results, activities_data):
    # Create start date
    start_date = datetime(2024, 1, 1)  # You can change this to your project start date
    
    # Prepare data for Gantt chart
    gantt_data = []
    
    for _, activity in cpm_results['results'].iterrows():
        # Calculate start and finish dates
        start = start_date + timedelta(days=int(activity['ES']))
        finish = start_date + timedelta(days=int(activity['EF']))
        
        # Get duration and float
        duration = activity['Duration']
        total_float = activity['Total_Float']
        
        # Color coding based on critical path
        color = 'rgb(255, 100, 100)' if activity['Critical'] else 'rgb(100, 149, 237)'
        
        # Create task dictionary
        task = dict(
            Task=f"{activity['Activity']} ({duration}d)",
            Start=start,
            Finish=finish,
            Resource='Critical' if activity['Critical'] else 'Non-Critical',
            Float=total_float
        )
        gantt_data.append(task)
    
    # Convert to DataFrame
    df = pd.DataFrame(gantt_data)
    
    # Create Gantt chart
    fig = ff.create_gantt(df,
                         colors={'Critical': 'rgb(255, 100, 100)',
                                'Non-Critical': 'rgb(100, 149, 237)'},
                         index_col='Resource',
                         show_colorbar=True,
                         group_tasks=True,
                         showgrid_x=True,
                         showgrid_y=True)
    
    # Update layout
    fig.update_layout(
        title='Project Gantt Chart (Critical Path in Red)',
        xaxis_title='Date',
        height=800,
        font=dict(size=10)
    )
    
    return fig

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

# Run CPM analysis first
cpm_results = calculate_cpm(activities_data, dependencies_data)

# Create Gantt chart
gantt_fig = create_gantt_chart(cpm_results, activities_data)

# Show the chart
gantt_fig.show()