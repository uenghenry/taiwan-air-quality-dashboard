from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CITIES = [
    {"city": "臺北市", "latitude": 25.0330, "longitude": 121.5654},
    {"city": "新北市", "latitude": 25.0120, "longitude": 121.4657},
    {"city": "桃園市", "latitude": 24.9937, "longitude": 121.3010},
    {"city": "新竹市", "latitude": 24.8138, "longitude": 120.9675},
    {"city": "臺中市", "latitude": 24.1477, "longitude": 120.6736},
    {"city": "彰化縣", "latitude": 24.0756, "longitude": 120.5440},
    {"city": "嘉義市", "latitude": 23.4801, "longitude": 120.4491},
    {"city": "臺南市", "latitude": 22.9999, "longitude": 120.2269},
    {"city": "高雄市", "latitude": 22.6273, "longitude": 120.3014},
    {"city": "屏東縣", "latitude": 22.5519, "longitude": 120.5488},
    {"city": "花蓮縣", "latitude": 23.9911, "longitude": 121.6112},
    {"city": "臺東縣", "latitude": 22.7554, "longitude": 121.1500},
]

st.set_page_config(
    page_title="Taiwan Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide",
)

st.title("🌫️ Taiwan City Air Quality Dashboard")
st.write(
    "This dashboard collects current modeled air-quality data for "
    "representative locations across Taiwan and compares AQI and particulate matter."
)


def classify_us_aqi(aqi):
    if pd.isna(aqi):
        return "No data"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for sensitive groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very unhealthy"
    return "Hazardous"


@st.cache_data(ttl=600)
def load_and_clean_data(refresh_token=0):
    rows = []

    for location in CITIES:
        parameters = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "pm10,pm2_5,us_aqi,european_aqi",
            "timezone": "Asia/Taipei",
        }

        response = requests.get(
            API_URL,
            params=parameters,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        payload = response.json()
        current = payload.get("current", {})

        rows.append(
            {
                "city": location["city"],
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "pm2_5": current.get("pm2_5"),
                "pm10": current.get("pm10"),
                "us_aqi": current.get("us_aqi"),
                "european_aqi": current.get("european_aqi"),
                "source_time": current.get("time"),
            }
        )

    df = pd.DataFrame(rows)

    numeric_columns = [
        "latitude",
        "longitude",
        "pm2_5",
        "pm10",
        "us_aqi",
        "european_aqi",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = (
        df.dropna(subset=["city", "latitude", "longitude", "us_aqi"])
        .drop_duplicates(subset=["city"])
        .reset_index(drop=True)
    )

    df["air_quality_status"] = df["us_aqi"].apply(classify_us_aqi)
    df["pm_ratio"] = (
        df["pm2_5"] / df["pm10"].replace(0, pd.NA)
    ).round(2)

    return df


if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = 0

if "refresh_message" not in st.session_state:
    st.session_state.refresh_message = ""

if st.button("🔄 Refresh latest data"):
    st.session_state.refresh_token += 1
    st.session_state.refresh_message = (
        "Data refreshed at "
        + datetime.now(ZoneInfo("Asia/Taipei")).strftime("%H:%M:%S")
    )

try:
    data = load_and_clean_data(st.session_state.refresh_token)
except Exception as error:
    st.error(
        "The air-quality data source could not be loaded. "
        "Please wait a moment and press the refresh button."
    )
    st.exception(error)
    st.stop()

if st.session_state.refresh_message:
    st.success(st.session_state.refresh_message)

city_options = ["All Taiwan"] + data["city"].tolist()
selected_city = st.selectbox("Choose a city or county", city_options)

if selected_city == "All Taiwan":
    filtered_data = data.copy()
    st.info("Currently showing all 12 locations.")
else:
    filtered_data = data[data["city"] == selected_city].copy()
    st.info(f"Currently showing: {selected_city}")

average_aqi = filtered_data["us_aqi"].mean()
highest_row = filtered_data.loc[filtered_data["us_aqi"].idxmax()]
unhealthy_count = int((filtered_data["us_aqi"] > 100).sum())
average_pm25 = filtered_data["pm2_5"].mean()

column1, column2, column3, column4 = st.columns(4)
column1.metric("Average US AQI", f"{average_aqi:.0f}")
column2.metric("Highest-AQI location", highest_row["city"])
column3.metric("Locations above AQI 100", unhealthy_count)
column4.metric("Average PM2.5", f"{average_pm25:.1f} μg/m³")

st.caption(
    "Dashboard loaded at "
    + datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
    + " (Taipei time). API data are cached for 10 minutes unless refreshed manually."
)

st.subheader("US AQI comparison")
aqi_chart_data = filtered_data[
    ["city", "us_aqi"]
].sort_values("us_aqi", ascending=False)
st.bar_chart(
    aqi_chart_data,
    x="city",
    y="us_aqi",
    height=420,
)

st.subheader("PM2.5 and PM10 comparison")
particle_chart_data = filtered_data[
    ["city", "pm2_5", "pm10"]
].sort_values("pm2_5", ascending=False)
st.bar_chart(
    particle_chart_data,
    x="city",
    y=["pm2_5", "pm10"],
    height=420,
)

st.subheader("Location map")
st.map(
    filtered_data,
    latitude="latitude",
    longitude="longitude",
    size=100,
    zoom=7 if selected_city == "All Taiwan" else 11,
)

st.subheader("Air-quality details")
display_columns = [
    "city",
    "air_quality_status",
    "us_aqi",
    "european_aqi",
    "pm2_5",
    "pm10",
    "pm_ratio",
    "source_time",
]
detail_table = filtered_data[display_columns].sort_values(
    "us_aqi",
    ascending=False,
)
st.dataframe(detail_table, width="stretch", hide_index=True)

csv_data = detail_table.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Download cleaned data as CSV",
    data=csv_data,
    file_name="taiwan_air_quality_cleaned.csv",
    mime="text/csv",
)

with st.expander("Data pipeline"):
    st.markdown(
        """
        1. **Extract:** Send API requests to Open-Meteo for current
           air-quality data at representative locations in Taiwan.
        2. **Transform:** Convert JSON records into a pandas DataFrame,
           convert numeric fields, remove missing or duplicated records,
           calculate the PM2.5-to-PM10 ratio, and classify AQI status.
        3. **Load/Present:** Load the cleaned data into KPI cards,
           comparison charts, a map, a table, and a downloadable CSV.
        4. **Refresh:** The cache expires every 10 minutes. The refresh
           button creates a new request and displays the refresh time.
        """
    )

st.info(
    "Note: This dashboard uses modeled air-quality data for representative "
    "coordinates, rather than official readings from every monitoring station."
)
