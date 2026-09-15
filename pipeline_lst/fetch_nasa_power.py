"""
NASA POWER Ingestion Pipeline: Kanpur Land Surface Temperature (LST) & Meteorology
Fetches multi-year continuous daily satellite skin temperature (LST) and surface meteorology
for the Kanpur metropolitan airshed (26.4499° N, 80.3319° E) across 2017 to 2023.
"""

import os
import sys
import json
import time
import urllib.request
import pandas as pd
import numpy as np

KANPUR_LAT = 26.4499
KANPUR_LON = 80.3319
START_DATE = "20170101"
END_DATE = "20231231"

PARAMETERS = [
    "TS",                 # Earth Skin Temperature (Land Surface Temperature, °C)
    "T2M",                # Air Temperature at 2 Meters (°C)
    "T2M_MAX",            # Maximum Air Temperature at 2 Meters (°C)
    "T2M_MIN",            # Minimum Air Temperature at 2 Meters (°C)
    "ALLSKY_SFC_SW_DWN",  # All-Sky Surface Downward Shortwave Irradiance (MJ/m²/day)
    "RH2M",               # Relative Humidity at 2 Meters (%)
    "WS2M"                # Wind Speed at 2 Meters (m/s)
]

def fetch_kanpur_nasa_power(output_csv):
    """Retrieves continuous daily records from the NASA POWER API and computes thermal metrics."""
    param_str = ",".join(PARAMETERS)
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={param_str}&"
        f"community=AG&"
        f"longitude={KANPUR_LON}&"
        f"latitude={KANPUR_LAT}&"
        f"start={START_DATE}&"
        f"end={END_DATE}&"
        f"format=JSON"
    )
    
    print(f"Fetching NASA POWER satellite telemetry for Kanpur ({KANPUR_LAT}°N, {KANPUR_LON}°E)...")
    print(f"Time Horizon: {START_DATE} to {END_DATE}")
    
    req = urllib.request.Request(url, headers={"User-Agent": "SignalEarth-Research/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        
    properties = data["properties"]["parameter"]
    dates = sorted(list(properties["TS"].keys()))
    
    records = []
    for d_str in dates:
        dt = pd.to_datetime(d_str, format="%Y%m%d")
        
        ts_val = properties["TS"].get(d_str)
        t2m_val = properties["T2M"].get(d_str)
        tmax_val = properties["T2M_MAX"].get(d_str)
        tmin_val = properties["T2M_MIN"].get(d_str)
        sw_val = properties["ALLSKY_SFC_SW_DWN"].get(d_str)
        rh_val = properties["RH2M"].get(d_str)
        ws_val = properties["WS2M"].get(d_str)
        
        # NASA POWER fill value is -999.0
        ts = ts_val if ts_val is not None and ts_val != -999.0 else np.nan
        t2m = t2m_val if t2m_val is not None and t2m_val != -999.0 else np.nan
        tmax = tmax_val if tmax_val is not None and tmax_val != -999.0 else np.nan
        tmin = tmin_val if tmin_val is not None and tmin_val != -999.0 else np.nan
        sw = sw_val if sw_val is not None and sw_val != -999.0 else np.nan
        rh = rh_val if rh_val is not None and rh_val != -999.0 else np.nan
        ws = ws_val if ws_val is not None and ws_val != -999.0 else np.nan
        
        # Thermal diagnostics
        # Delta T = LST (Skin) - Air Temperature (Positive indicates solar superheating; negative indicates radiational cooling)
        delta_t = ts - t2m if pd.notna(ts) and pd.notna(t2m) else np.nan
        dtr = tmax - tmin if pd.notna(tmax) and pd.notna(tmin) else np.nan
        
        # Season definition consistent with CPCB convention
        month = dt.month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Summer"
        elif month in [6, 7, 8, 9]:
            season = "Monsoon"
        else:
            season = "Post-Monsoon"
            
        records.append({
            "Date": dt.strftime("%Y-%m-%d"),
            "Year": dt.year,
            "Month": month,
            "Day": dt.day,
            "Season": season,
            "LST_Skin_C": ts,
            "Air_Temp_2M_C": t2m,
            "Temp_Max_2M_C": tmax,
            "Temp_Min_2M_C": tmin,
            "Delta_T_Skin_Air_C": delta_t,
            "Diurnal_Thermal_Range_C": dtr,
            "Solar_Radiation_MJ_m2": sw,
            "Relative_Humidity_Pct": rh,
            "Wind_Speed_2M_mps": ws
        })
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Successfully saved {len(df)} daily NASA POWER records to {output_csv}.")
    print(f"Summary: Mean LST={df['LST_Skin_C'].mean():.2f}°C, Mean Air Temp={df['Air_Temp_2M_C'].mean():.2f}°C, Max LST={df['LST_Skin_C'].max():.2f}°C")
    return df

if __name__ == "__main__":
    out = os.path.join("data", "lst", "kanpur_nasa_power_daily.csv")
    fetch_kanpur_nasa_power(out)
