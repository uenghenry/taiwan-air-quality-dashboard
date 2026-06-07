# Executive Summary — Taiwan City Air Quality Dashboard

**Student:** [YOUR NAME]  
**Application URL:** [PASTE YOUR STREAMLIT URL HERE]  
**GitHub Repository:** [PASTE YOUR GITHUB URL HERE]

## Project Purpose

This project develops a lightweight web dashboard for comparing current air-quality conditions across representative locations in Taiwan. The application helps users identify locations with relatively high air-quality index values and compare particulate-matter levels, including PM2.5 and PM10.

## Data Pipeline and Data Wrangling

The application uses the Open-Meteo Air Quality API. Python sends API requests for twelve representative cities and counties and receives current data in JSON format. The transformation stage converts these records into a pandas DataFrame, selects relevant variables, converts numeric values, removes missing and duplicated records, calculates the PM2.5-to-PM10 ratio, and classifies each location according to its US AQI level. The cleaned dataset is then loaded directly into the Streamlit dashboard and can also be downloaded as a CSV file.

## Dashboard and Refresh Mechanism

The dashboard includes four key performance indicators, a US AQI comparison chart, a PM2.5 and PM10 comparison chart, a location map, a city filter, and a detailed data table. API results are cached for ten minutes to reduce unnecessary requests. The cache expires automatically, and users can also press a refresh button to retrieve the latest available values.

## Tools and Limitations

The application is developed with Python, pandas, requests, and Streamlit, and is publicly deployed through Streamlit Community Cloud and GitHub. A limitation is that Open-Meteo provides modeled data for selected coordinates rather than official measurements from every monitoring station; therefore, this dashboard is designed for general comparison rather than regulatory or health decision-making.
