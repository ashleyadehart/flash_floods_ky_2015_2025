# Kentucky Flash Flooding Events, Frequency, & Severity Data Analysis

## Project Overview
This project analyzes flash flooding events in the state of Kentucky from 2015–2025 to determine whether there has been an observable increase in event frequency over time, along with examining other variables that may impact severity of these flash flooding events.

This project demonstrates skills in data cleaning, exploratory data analysis (EDA), time-series aggregation, data visualization using Python, and SQL querying.

## Project Structure
```
├── data/
│ ├── raw/
│ ├── processed/
├── notebooks/
├── plots/
│ ├── ky_yearly_flash_floods_maps/
├── scripts/
├── sql/
├── .gitignore
├── README.md 
└── requirements.txt
```

## How to Run This Project
### 1. Clone This Repository

```bash
git clone <https://github.com/ashleyadehart/flash_floods_ky_2015_2025>
```

### 2. Create a Virtual Environment
Run the following command to create a virtual environment in a folder named `.venv`:

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment
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

### 4. Install Dependencies
Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 5. Launch Jupyter Notebook
Start the notebook server from your terminal:
\`\`\`bash
jupyter notebook
\`\`\`
*Alternatively, if you prefer the newer interface, you can run:*
\`\`\`bash
jupyter lab
\`\`\`

### 6. Open and Run the Notebook
1. A browser window should automatically open at `http://localhost:8888`.
2. In the file browser interface, click on your notebook file (e.g., `your_notebook.ipynb`).
3. To run individual code cells, select the cell and press **Shift + Enter**.
4. To run the entire notebook at once, click **Cell > Run All** from the top menu.

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
- QGIS
- Canva

## Key Analytical Questions
- Has the frequency of flash flooding events in Kentucky increased from 2015 - 2025?
- Which years show the highest concentration of events?
- Which counties have experienced the most flash flooding activity between 2015 - 2025?
- What reporting sources most frequently document these events?
- Are there observable temporal or geographic clustering patterns?
- Does climate patterns, moon and sun position, and weather conditions increase the severity of flash flooding events?

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
- Kentucky flash-flood events were significantly unevenly distributed across moon-illumination levels, with substantially more events occurring during very low (0–10%) and very high (90–100%) illumination than expected. 
- Annual flash flooding damage had a 200% percentage change between 2024 and 2025.

## Data Sources
- [NOAA Storm Events Database](https://www.ncei.noaa.gov/stormevents/choosedates.jsp?statefips=21%2CKENTUCKY)
- [Weather API](https://www.weatherapi.com/)
- [NCEP Climate Prediction Center]( https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt)
- [ArcGIS Online](https://www.arcgis.com/index.html)
- Datasets used in this project can be found in the `data/` folder

## AI Usage
Generative AI was implemented in the following way(s):
- Creation of a sample README.md file that could be edited throughout the duration of the project.
- Generation of Python scripts that call for daily weather conditions, NLCD data, moon and sun data, and ONI data.
- Troubleshooting errors that occurred throughout the project.

## Future Enhancements
Planned future enhancements for this project include expanding the analytical depth and integrating geospatial analysis techniques to better understand flash flooding patterns across Kentucky.

### Planned Extensions
- Develop predictive analytics and forecasting models to identify potential flash flooding risk trends using historical event and weather datasets.
- Incorporate GIS and geospatial analysis tools to create yearly county-level flash flooding maps for Kentucky from 2015–2025, enabling hotspot identification and spatial trend analysis.
- Perform spatial visualization and clustering analysis to examine regional patterns and areas of recurring vulnerability.
- Explore potential relationships between emergency response infrastructure and flash flooding impacts by analyzing 911 call center funding data, staffing levels, or resource allocation.

## Author
Ashley A. Dehart

## License
MIT License