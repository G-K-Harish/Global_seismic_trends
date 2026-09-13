# Global_seismic_trends
Earthquake data pipeline and analysis — USGS API → Python/Pandas → MySQL → SQL analysis → Streamlit dashboard, covering 5 years of global seismic activity.

## Overview
I pulled earthquake records from the USGS API, cleaned and engineered features on top of them with Python/Pandas, loaded the result into MySQL, ran SQL analysis, and built a Streamlit dashboard to explore the findings.

## Tech stack
Python, Pandas, NumPy, Requests, Regex, MySQL, SQLAlchemy, PyMySQL, Plotly, Streamlit

## Workflow
USGS API → Python extraction & cleaning → feature engineering → MySQL → SQL analysis → Streamlit dashboard

## Dataset
Earthquake records for five years, pulled month by month from the USGS API. Original API fields are kept, plus a set of engineered columns (see docs/data-dictionary.md).

## Data cleaning
- Timestamp conversion
- Text standardization
- Regex-based location/country extraction from the place field
- Missing value handling
- Numeric field cleanup
- Duplicate checks

## Feature engineering
country, year, month, day, day_of_week, hour, depth_category, mag_category

## Database
MySQL database earthquake_db, table earthquakes, id as primary key.

## SQL analysis
Covers strongest/deepest earthquakes, magnitude patterns, frequency over time, reporting networks, tsunami activity, alert levels, station coverage, geographic clustering, year-over-year change, and deep-focus earthquake patterns (window functions, JSON_TABLE, proximity analysis).

## Dashboard
KPI summary, yearly/monthly trends, magnitude distribution, shallow vs. deep breakdown, global map, alert and tsunami analysis, reporting network breakdown, strongest/deepest event tables, and a raw data explorer.

## Possible applications
Earthquake risk monitoring, disaster planning input, infrastructure risk assessment, insurance risk modeling, general seismic research.

### Author
Harish
