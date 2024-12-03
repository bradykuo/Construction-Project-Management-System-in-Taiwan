# Construction Project Management System in Taiwan 🏗️

## Overview
A comprehensive construction project management system that implements CPM (Critical Path Method) and PERT (Program Evaluation and Review Technique) analysis for a 174-day construction project. The system helps optimize scheduling, resource allocation, and risk management.

## Features
- **Critical Path Analysis (CPM)**
  - Calculates project duration and critical activities
  - Identifies float times and scheduling flexibility
  - Generates network diagrams and Gantt charts

- **PERT Analysis**
  - Probabilistic duration estimates
  - Confidence intervals for project completion
  - Risk assessment for activities

- **Resource Management**
  - Workforce allocation tracking
  - Resource utilization optimization
  - Peak resource requirement analysis

- **Risk Analysis**
  - Activity-level risk assessment
  - Schedule risk evaluation
  - Mitigation strategy recommendations

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/construction-project-management.git

# Navigate to the project directory
cd construction-project-management

# Install required packages
pip install -r requirements.txt
```

## Dependencies
- Python 3.8+
- pandas
- networkx
- numpy
- scipy
- plotly
- matplotlib

## Usage

1. **Run CPM Analysis**
```python
python cpm_method.py
```

2. **Generate Gantt Chart**
```python
python gantt_chart.py
```

3. **Perform PERT Analysis**
```python
python pert_method.py
```

## Project Structure
```
construction-project-management/
│
├── src/
│   ├── cpm_method.py        # Critical Path Method implementation
│   ├── gantt_chart.py       # Gantt chart visualization
│   ├── network_diagram.py   # Network diagram generator
│   └── pert_method.py       # PERT analysis implementation
│
├── data/
│   └── taiwan-construction-data-92days.txt  # Sample project data
│
├── requirements.txt
└── README.md
```

## Sample Output

### Critical Path Analysis
- Project Duration: 174 days
- Critical Path: A → B → C1 → C2 → D → E → F → H → I → J → M → N → Q1 → Q2
- Key Milestones:
  - Site Preparation (8 days)
  - Foundation Work (7 days)
  - Steel Roof Installation (22 days)

### PERT Analysis Results
- Expected Duration: 171.5 days
- 95% Confidence Interval: 155.1 - 187.9 days
- Completion Probabilities:
  - 170 days: 89%
  - 175 days: 94%
  - 180 days: 97%

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is available for academic and educational purposes.

## Acknowledgments
- Data source: Taiwan Construction Industry Database
- NetworkX library for graph calculations
- Plotly for interactive visualizations
