import streamlit as st
import pandas as pd
import numpy as np

# --- App Title ---
st.title("Slope Cut Sheet Generator")

# --- Input Section ---
st.header("Enter Slope Parameters")

begin_station = st.number_input("Begin Station", value=0.0)
end_station = st.number_input("End Station", value=100.0)
begin_elev = st.number_input("Elevation at Begin Station", value=100.0)
end_elev = st.number_input("Elevation at End Station", value=110.0)
increment = st.number_input("Station Increment", value=25.0, min_value=1.0)

custom_stations_input = st.text_input(
    "Optional: Enter custom stations (e.g., 25,45,85)",
    value="25,45,85"
)

# --- Slope Calculation ---
slope = (end_elev - begin_elev) / (end_station - begin_station)
slope_pct = slope * 100

# --- Adjusted Range ---
start_aligned = begin_station
if begin_station % increment != 0:
    start_aligned = begin_station + (increment - (begin_station % increment))

incremental_stations = np.arange(start_aligned, end_station, increment)
stations_all = np.concatenate(([begin_station], incremental_stations, [end_station]))
stations_all = np.unique(np.round(stations_all, 3))

# --- Elevation Calculation ---
elevations = begin_elev + slope * (stations_all - begin_station)

# --- Format Station Labels ---
def format_station(val):
    return f"{int(val)//100}+{int(val)%100:02}"

formatted_stations = [format_station(s) for s in stations_all]

df_main = pd.DataFrame({
    "Elevation (ft)": np.round(elevations, 3),
    "Station": formatted_stations
})

# --- Custom Stations ---
df_custom = pd.DataFrame()
if custom_stations_input.strip():
    try:
        custom_raw = [float(s.strip()) for s in custom_stations_input.split(',')]
        custom_clean = [s for s in custom_raw if s not in stations_all]

        if custom_clean:
            custom_elevs = begin_elev + slope * (np.array(custom_clean) - begin_station)
            formatted_custom = [format_station(s) for s in custom_clean]

            df_custom = pd.DataFrame({
                "Elevation (ft)": np.round(custom_elevs, 3),
                "Station": formatted_custom
            })
    except Exception as e:
        st.error(f"Invalid input for custom stations: {e}")

# --- Combine and Sort ---
df_combined = pd.concat([df_main, df_custom], ignore_index=True)
df_combined = df_combined.sort_values("Station").reset_index(drop=True)

# --- Display ---
st.markdown(f"**Slope:** {slope_pct:.2f}%")
st.dataframe(df_combined)

# --- Export ---
csv = df_combined.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "slope_cut_sheet.csv", "text/csv")