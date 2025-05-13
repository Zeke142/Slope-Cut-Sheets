import streamlit as st
import pandas as pd
import numpy as np

# App Config
st.set_page_config(page_title="Slope Cut Sheet", layout="centered")

st.title("Slope Cut Sheet Generator")

# --- Input Section ---
st.header("Input Parameters")

begin_station = st.number_input("Begin Station", value=0.0)
end_station = st.number_input("End Station", value=100.0)
begin_elev = st.number_input("Elevation at Begin Station", value=100.0)
end_elev = st.number_input("Elevation at End Station", value=110.0)
increment = st.number_input("Station Increment", value=25.0)

custom_stations_input = st.text_input(
    "Optional: Enter custom stations (e.g., 25,45,85)", value="25,45,85"
)

# --- Data Calculation ---
slope = (end_elev - begin_elev) / (end_station - begin_station)
slope_percent = round(slope * 100, 2)

# Round begin station to nearest increment
remainder = begin_station % increment
start_at = begin_station if remainder == 0 else begin_station + (increment - remainder)

standard_stations = np.arange(start_at, end_station + increment, increment)
elevations = begin_elev + slope * (standard_stations - begin_station)

df_main = pd.DataFrame({
    "Station": [f"{int(s//100)}+{int(s%100):02}" for s in standard_stations],
    "Elevation (ft)": np.round(elevations, 3)
})

# --- Custom Stations ---
df_custom = pd.DataFrame()
if custom_stations_input.strip():
    try:
        custom_stations = [float(s.strip()) for s in custom_stations_input.split(',')]
        custom_stations = [s for s in custom_stations if s not in standard_stations]
        custom_elevs = begin_elev + slope * (np.array(custom_stations) - begin_station)

        df_custom = pd.DataFrame({
            "Station": [f"{int(s//100)}+{int(s%100):02}" for s in custom_stations],
            "Elevation (ft)": np.round(custom_elevs, 3)
        })
    except:
        st.error("Invalid format for custom stations. Use comma-separated numbers.")

# --- Combine and Sort ---
df_combined = pd.concat([df_main, df_custom]).drop_duplicates()
df_combined["Sort"] = df_combined["Station"].apply(lambda x: int(x.replace("+", "")))
df_combined = df_combined.sort_values("Sort").drop(columns="Sort").reset_index(drop=True)

# --- Display Output ---
st.subheader(f"Slope: {slope_percent:.2f}%")

def render_html_table(df):
    html = '<style>table, th, td {border: 1px solid black; border-collapse: collapse; padding: 0px; margin: 0px; font-size: 14px;} th, td {text-align: center;}</style>'
    html += '<table>'
    html += '<tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr>'
    for _, row in df.iterrows():
        html += '<tr>' + ''.join(f'<td>{row[col]}</td>' for col in df.columns) + '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

render_html_table(df_combined)

# --- Download Option ---
csv = df_combined.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "slope_cut_sheet.csv", "text/csv")