import streamlit as st
import pandas as pd
import numpy as np

# --- App Styling ---
st.set_page_config(page_title="Slope Cut Sheet", layout="centered")
st.markdown(
    "<style>body {background-color: #f0f2f6;} .stApp {color: #1e1e1e;}</style>",
    unsafe_allow_html=True
)

st.title("Slope Cut Sheet Generator")

# --- User Inputs ---
st.header("Enter Basic Parameters")

begin_station = st.number_input("Begin Station", value=0.0)
end_station = st.number_input("End Station", value=100.0)
begin_elev = st.number_input("Elevation at Begin Station", value=100.0)
end_elev = st.number_input("Elevation at End Station", value=110.0)
increment = st.number_input("Station Increment", value=25.0)

custom_stations_input = st.text_input(
    "Optional: Enter custom (odd or specific) stations separated by commas",
    value="25,45,85"
)

# --- Slope Calculation ---
slope = (end_elev - begin_elev) / (end_station - begin_station)
slope_pct = slope * 100

# --- Increment Station Generation (aligned to next multiple of increment) ---
first_increment_station = begin_station
if begin_station % increment != 0:
    first_increment_station = begin_station + (increment - (begin_station % increment))

station_range = np.arange(first_increment_station, end_station, increment)

# --- Build Full List of Stations ---
stations = list({begin_station, end_station} | set(station_range))

# --- Custom Stations ---
custom_stations = []
if custom_stations_input.strip():
    try:
        custom_stations = [float(s.strip()) for s in custom_stations_input.split(',')]
        stations.extend(custom_stations)
    except:
        st.error("Check your custom station input format.")

# --- Calculate Elevations ---
stations = sorted(set(stations))
elevations = [round(begin_elev + slope * (s - begin_station), 3) for s in stations]

df = pd.DataFrame({
    "Station": stations,
    "Elevation (ft)": elevations
})

# --- Display Results ---
st.subheader(f"Slope: {slope_pct:.2f}%")
st.dataframe(df, use_container_width=True)

# --- Export Option ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Results as CSV", csv, "slope_cut_sheet.csv", "text/csv")
