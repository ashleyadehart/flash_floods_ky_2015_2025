# Did Flash Flooding Events Increase in Frequency Within the State of Kentucky from 2015-2025?

## Project Overview
This project analyzes flash flooding events in the state of Kentucky from 2015–2025 to determine whether there is an observable increase in event frequency over time.

This project demonstrates skills in data cleaning, exploratory data analysis (EDA), time-series aggregation, and data visualization using Python.

## Project Structure
```
├── data/
│ ├── raw/
│ ├── processed/
├── notebooks/
├── plots/
├── scripts/
├── README.md 
└── requirements.txt
```

## How to Run This Project
### 1. Clone this repository
```
git clone <https://github.com/ashleyadehart/flash_floods_ky_2015_2025>
```

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
- Visualization of frequency distributions and comparative trends over time

## Key Findings & Insights
- Year-over-year variability in flash flood frequency was observed across the dataset.
- Certain counties show consistently higher event concentrations, suggesting localized vulnerability.
- Emergency services and call center reports are among the most common documentation sources.
- Temporal clustering suggests potential links between seasonal weather patterns and event frequency.

## Data Sources
- [NOAA Storm Events Database](https://www.ncei.noaa.gov/stormevents/choosedates.jsp?statefips=21%2CKENTUCKY)
- [Weather API](https://www.weatherapi.com/)
- [Visual Crossing API](https://www.visualcrossing.com/)
- Datasets used in this project can be found in the `data/` folder

## AI Usage
Generative AI was implemented in the following way(s):
- Creation of a sample README.md file that could be edited throughout the duration of the project.  

## Future Enhancements
Planned future enhancements for this project include expanding the analytical depth and integrating geospatial analysis techniques to better understand flash flooding patterns across Kentucky.

### Planned Extensions
- Integrate historical weather condition data for counties impacted during the top five highest flash flooding event dates to analyze relationships between precipitation intensity, storm conditions, and event frequency.
- Develop predictive analytics and forecasting models to identify potential flash flooding risk trends using historical event and weather datasets.
- Incorporate GIS and geospatial analysis tools to create yearly county-level flash flooding maps for Kentucky from 2015–2025, enabling hotspot identification and spatial trend analysis.
- Perform spatial visualization and clustering analysis to examine regional patterns and areas of recurring vulnerability.
- Explore potential relationships between emergency response infrastructure and flash flooding impacts by analyzing 911 call center funding data, staffing levels, or resource allocation.

## Author
Ashley A. Dehart

## License
MIT License