import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Slope Cut Sheet", layout="centered")
st.title("Slope Cut Sheet Generator")

# --- Styling ---
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Station Formatter ---
def format_station(station):
    station = int(round(station))
    left = station // 100
    right = station % 100
    return f"{left}+{right:02d}"

# --- User Inputs ---
st.header("Input Parameters")

begin_station = st.number_input("Begin Station", value=0.0)
end_station = st.number_input("End Station", value=100.0)
begin_elev = st.number_input("Elevation at Begin Station (ft)", value=100.0)
end_elev = st.number_input("Elevation at End Station (ft)", value=110.0)
increment = st.number_input("Station Increment", value=25.0, min_value=1.0)

custom_stations_input = st.text_input(
    "Optional: Enter specific stations separated by commas (e.g. 25, 45, 85)",
    value=""
)

# --- Slope Calculation ---
slope = (end_elev - begin_elev) / (end_station - begin_station)
slope_percent = round(slope * 100, 2)

# --- Build Station Range (aligned with increment) ---
def generate_station_range(begin, end, inc):
    start = begin
    while start % inc != 0:
        start += 1
    return np.arange(begin, end + 0.1, inc)

station_range = generate_station_range(begin_station, end_station, increment)
station_range = np.unique(np.append(station_range, [begin_station, end_station]))  # Ensure begin/end included

elevations = begin_elev + slope * (station_range - begin_station)

df_main = pd.DataFrame({
    "Station": station_range,
    "Elevation (ft)": np.round(elevations, 3)
})

df_main["Station"] = df_main["Station"].apply(format_station)
df_main = df_main.sort_values(by="Station")

# --- Handle Custom Stations ---
df_custom = pd.DataFrame()
if custom_stations_input.strip():
    try:
        custom_stations = [float(s.strip()) for s in custom_stations_input.split(',')]
        valid_customs = [s for s in custom_stations if s not in station_range]
        custom_elevs = begin_elev + slope * (np.array(valid_customs) - begin_station)

        df_custom = pd.DataFrame({
            "Station": [format_station(s) for s in valid_customs],
            "Elevation (ft)": np.round(custom_elevs, 3)
        })
    except:
        st.error("Please ensure custom stations are valid numbers separated by commas.")

# --- Merge and Display ---
df_all = pd.concat([df_main, df_custom]).drop_duplicates(subset="Station")
df_all = df_all.sort_values(by="Station").reset_index(drop=True)

st.subheader(f"Slope: {slope_percent:.2f}%")
st.dataframe(df_all, use_container_width=True)

# --- Export CSV ---
csv = df_all.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "slope_cut_sheet.csv", "text/csv")