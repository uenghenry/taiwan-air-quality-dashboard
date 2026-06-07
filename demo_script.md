# 60-Second Demo Script

Hello, my project is the Taiwan City Air Quality Dashboard.

The application extracts current modeled air-quality data from the Open-Meteo API for twelve representative locations in Taiwan. Python converts the JSON responses into a pandas DataFrame, changes variables into numeric formats, removes invalid and duplicated records, calculates a particulate-matter ratio, and classifies each location by its US AQI level.

The dashboard presents average AQI, the location with the highest AQI, the number of locations above AQI 100, and average PM2.5. It also contains AQI and particulate-matter comparison charts, a map, a city filter, a detailed table, and a cleaned CSV download.

The data cache expires every ten minutes, and this refresh button can request the latest data immediately. The application is deployed on Streamlit Community Cloud, so it is available through a public URL instead of localhost.
