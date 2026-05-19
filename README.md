# Did Flash Flooding Events Increase in Frequency Within the State of Kentucky from 2015-2025?

## Project Overview
This project analyzes flash flooding events in the state of Kentucky from 2015–2025 to determine whether there is an observable increase in event frequency over time.

The primary objective is to apply data analytics techniques to identify temporal trends, geographic hotspots, and reporting patterns using real-world weather event data.

This project demonstrates skills in data cleaning, exploratory data analysis (EDA), time-series aggregation, and data visualization using Python.

## Project Structure
```
├── data/
│ ├── raw/
│ ├── processed/
├── notebooks/
├── plots
├── README.md 
└── requirements.txt
```

## How to Run This Project
1. Clone this repository.
### 2. Create a virtual environment
Run the following command to create a virtual environment in a folder named `.venv`:

```bash
python -m venv .venv
```

### 3. Activate the virtual environment
Activate the environment based on your operating system:

#### **Windows (Command Prompt):**
```bash
.venv\Scripts\activate.bat
```

#### **Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

#### **macOS / Linux:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies
Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### Deactivating
When you are done working on the project, you can return to your system's global Python environment by running:

```bash
deactivate
```

## Tools & Technologies
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook

## Key Analytical Questions
- Has the frequency of flash flooding events in Kentucky increased from 2015 to 2025?
- Which years show the highest concentration of events?
- Which counties experience the most flash flooding activity?
- What reporting sources most frequently document these events?
- Are there observable temporal or geographic clustering patterns?

## Methodology
The analysis workflow includes:
- Data cleaning and preprocessing of NOAA Storm Events data
- Standardization of event timestamps and geographic fields
- Aggregation of events by year and county
- Exploratory Data Analysis (EDA) using Python (Pandas, Matplotlib, Seaborn)
- Identification of temporal trends and spatial hotspots
- Visualization of frequency distributions and comparative trends over time

## Key Findings & Insights
- Year-over-year variability in flash flood frequency was observed across the dataset.
- Certain counties show consistently higher event concentrations, suggesting localized vulnerability.
- Emergency services and call center reports are among the most common documentation sources.
- Temporal clustering suggests potential links between seasonal weather patterns and event frequency.

## Data Sources
- National Weather Service (NOAA Storm Events Database)
- Weather API
- Datasets used in this project can be found in the `data/` folder

## Author
Ashley A. Dehart

## License
MIT License