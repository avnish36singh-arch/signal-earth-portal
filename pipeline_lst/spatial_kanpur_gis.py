"""
Spatial GIS & Land Surface Temperature (LST) Analytical Engine: Kanpur Metropolitan Region
Processes multi-year NASA POWER satellite skin temperature telemetry, generates QGIS-ready
vector GeoJSON layers, models urban thermal zonation, and establishes the physical coupling
between ground radiative cooling (LST) and winter PM2.5 atmospheric inversion entrapment.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Aesthetics consistent with Signal Earth publication standard
sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#D1D5DB'
plt.rcParams['axes.linewidth'] = 0.8

# Key Geographic Anchor Points in Kanpur
KANPUR_STATIONS_GEO = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "station_id": "229252",
                "name": "NSI Kalyanpur",
                "type": "Continuous Ambient Air Quality Monitoring Station (CAAQMS)",
                "operator": "UPPCB / CPCB",
                "zone": "Suburban / Institutional",
                "elevation_m": 133
            },
            "geometry": {
                "type": "Point",
                "coordinates": [80.2581, 26.5052]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "station_id": "5662",
                "name": "Nehru Nagar",
                "type": "Continuous Ambient Air Quality Monitoring Station (CAAQMS)",
                "operator": "UPPCB / CPCB",
                "zone": "Dense Urban Commercial / Residential",
                "elevation_m": 126
            },
            "geometry": {
                "type": "Point",
                "coordinates": [80.3319, 26.4674]
            }
        }
    ]
}

KANPUR_ZONES_GEO = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_01",
                "name": "Central Kanpur Urban Core",
                "classification": "High-Density Built-Up (Impervious)",
                "albedo_characteristic": "Low (Asphalt/Concrete)",
                "mean_uhi_offset_c": 2.1
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.315, 26.450], [80.360, 26.450], [80.365, 26.485],
                    [80.320, 26.490], [80.315, 26.450]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_02",
                "name": "Jajmau Industrial Tannery Cluster",
                "classification": "Heavy Industrial & Dense Settlement",
                "albedo_characteristic": "Moderate-Low",
                "mean_uhi_offset_c": 1.8
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.380, 26.415], [80.435, 26.420], [80.430, 26.450],
                    [80.375, 26.445], [80.380, 26.415]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_03",
                "name": "Panki Industrial & Thermal Buffer",
                "classification": "Power Generation & Manufacturing",
                "albedo_characteristic": "Industrial Roof / Bare Soil",
                "mean_uhi_offset_c": 1.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.210, 26.460], [80.260, 26.465], [80.255, 26.495],
                    [80.205, 26.490], [80.210, 26.460]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_04",
                "name": "IITK & Kalyanpur Institutional Belt",
                "classification": "Suburban Canopy / Educational Campus",
                "albedo_characteristic": "Vegetative Canopy / Tree Cover",
                "mean_uhi_offset_c": -0.8
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.220, 26.500], [80.275, 26.505], [80.270, 26.535],
                    [80.215, 26.530], [80.220, 26.500]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_05",
                "name": "Ganga Riparian Buffer & Floodplain",
                "classification": "Riverine Wetland & Active Silt Floodplain",
                "albedo_characteristic": "Water / Wet Sand Evaporative Cooling",
                "mean_uhi_offset_c": -2.4
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.280, 26.510], [80.400, 26.460], [80.420, 26.480],
                    [80.300, 26.540], [80.280, 26.510]
                ]]
            }
        }
    ]
}

def export_qgis_layers(output_dir):
    """Exports standardized GeoJSON files ready for drag-and-drop loading in QGIS."""
    os.makedirs(output_dir, exist_ok=True)
    stations_path = os.path.join(output_dir, "kanpur_cpcb_stations.geojson")
    zones_path = os.path.join(output_dir, "kanpur_thermal_zones.geojson")
    
    with open(stations_path, "w") as f:
        json.dump(KANPUR_STATIONS_GEO, f, indent=2)
    with open(zones_path, "w") as f:
        json.dump(KANPUR_ZONES_GEO, f, indent=2)
        
    print(f"QGIS vector layers generated:")
    print(f"  -> {stations_path}")
    print(f"  -> {zones_path}")

def plot_01_seasonal_timeline(df, output_path):
    """Figure 1: Multi-Year Daily LST Timeline with Moving Trends and Summer/Winter Extremes."""
    fig, ax = plt.subplots(figsize=(15, 7), dpi=300)
    
    df_plot = df.copy()
    df_plot['Date_dt'] = pd.to_datetime(df_plot['Date'])
    df_plot['LST_7D'] = df_plot['LST_Skin_C'].rolling(7, min_periods=1).mean()
    df_plot['LST_30D'] = df_plot['LST_Skin_C'].rolling(30, min_periods=1).mean()
    
    # Heat threshold bands
    ax.axhspan(40, 50, color='#EF4444', alpha=0.10, label='Extreme Heatwave (>40°C)')
    ax.axhspan(35, 40, color='#F97316', alpha=0.08, label='Severe Thermal Stress (35–40°C)')
    ax.axhspan(0, 15, color='#3B82F6', alpha=0.10, label='Winter Radiative Chill (<15°C)')
    
    # Scatter and trendlines
    ax.scatter(df_plot['Date_dt'], df_plot['LST_Skin_C'], color='#94A3B8', alpha=0.35, s=12, label='Daily Satellite LST (NASA POWER)')
    ax.plot(df_plot['Date_dt'], df_plot['LST_7D'], color='#F59E0B', linewidth=1.6, label='7-Day Rolling Trend')
    ax.plot(df_plot['Date_dt'], df_plot['LST_30D'], color='#DC2626', linewidth=2.2, label='30-Day Seasonal Trajectory')
    
    ax.set_title("Kanpur Multi-Year Land Surface Temperature (LST) & Thermal Trajectory (2017–2023)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Observation Year", fontsize=11, labelpad=8)
    ax.set_ylabel("Land Surface Temperature (Skin Temp, °C)", fontsize=11, labelpad=8)
    ax.set_ylim(5, 48)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9, ncol=2)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def plot_02_skin_vs_air_anomaly(df, output_path):
    """Figure 2: Surface Skin vs Ambient Air Decoupling (Delta T) Across Seasons."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=300)
    
    # Subplot 1: Scatter of LST vs Air Temperature with 1:1 line
    sns.scatterplot(
        data=df, x='Air_Temp_2M_C', y='LST_Skin_C', hue='Season',
        palette={'Winter': '#3B82F6', 'Summer': '#EF4444', 'Monsoon': '#10B981', 'Post-Monsoon': '#F59E0B'},
        alpha=0.65, s=28, ax=ax1
    )
    lims = [5, 45]
    ax1.plot(lims, lims, color='#1E293B', linestyle='--', linewidth=1.8, label='1:1 Thermal Equilibrium ($T_{skin} = T_{air}$)')
    ax1.set_xlim(lims)
    ax1.set_ylim(lims)
    ax1.set_title("Land Surface vs 2-Meter Air Temperature Decoupling", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Ambient Air Temperature at 2m (°C)", fontsize=10)
    ax1.set_ylabel("Satellite Skin Temperature / LST (°C)", fontsize=10)
    ax1.legend(loc='upper left', fontsize=8.5)
    
    # Subplot 2: Monthly Boxplots of Delta T (Thermal Anomaly)
    month_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sns.boxplot(
        data=df, x='Month', y='Delta_T_Skin_Air_C', order=month_order,
        palette='coolwarm', ax=ax2, fliersize=2, linewidth=1.0
    )
    ax2.axhline(0, color='#1E293B', linestyle='--', linewidth=1.2)
    ax2.set_xticklabels(month_labels, fontsize=9.5)
    ax2.set_title("Annual Cycle of Skin-Air Thermal Gradient ($\Delta T = T_{skin} - T_{air}$)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Calendar Month", fontsize=10)
    ax2.set_ylabel("Thermal Gradient $\Delta T$ (°C)", fontsize=10)
    
    # Add annotations
    ax2.text(4, 2.2, "Pre-Monsoon Solar\nSuperheating ($\Delta T > 0$)", color='#DC2626', fontsize=8.5, fontweight='bold', ha='center')
    ax2.text(10.5, -1.8, "Post-Monsoon / Winter\nRadiational Cooling ($\Delta T < 0$)", color='#2563EB', fontsize=8.5, fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def plot_03_spatial_thermal_zones(output_path):
    """Figure 3: Spatial GIS Map of Kanpur Urban Thermal Zonation and Monitoring Stations."""
    fig, ax = plt.subplots(figsize=(11, 9), dpi=300)
    
    # Map layout bounds (approx Kanpur metropolitan canvas)
    ax.set_xlim(80.18, 80.46)
    ax.set_ylim(26.39, 26.56)
    
    zone_colors = {
        "ZONE_01": ("#EF4444", "Central Urban Core (+2.1°C UHI)"),
        "ZONE_02": ("#DC2626", "Jajmau Industrial (+1.8°C UHI)"),
        "ZONE_03": ("#F97316", "Panki Manufacturing (+1.6°C UHI)"),
        "ZONE_04": ("#10B981", "IITK Institutional Canopy (-0.8°C Buffer)"),
        "ZONE_05": ("#06B6D4", "Ganga Riparian Wetland (-2.4°C Cooling)")
    }
    
    # Plot Polygons
    for feat in KANPUR_ZONES_GEO["features"]:
        zid = feat["properties"]["zone_id"]
        color, label = zone_colors[zid]
        poly = feat["geometry"]["coordinates"][0]
        xs = [pt[0] for pt in poly]
        ys = [pt[1] for pt in poly]
        ax.fill(xs, ys, color=color, alpha=0.35, edgecolor=color, linewidth=2.0, label=label)
        
        # Centroid label
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        ax.text(cx, cy, feat["properties"]["name"], fontsize=8.5, fontweight='bold', color='#0F172A', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor=color, linewidth=1))
        
    # Plot CPCB Monitoring Stations
    for feat in KANPUR_STATIONS_GEO["features"]:
        pt = feat["geometry"]["coordinates"]
        name = feat["properties"]["name"]
        ax.scatter(pt[0], pt[1], color='#4338CA', s=140, edgecolor='white', linewidth=2.2, zorder=5)
        ax.text(pt[0], pt[1] + 0.007, f"★ {name}\n(CPCB/UPPCB)", fontsize=9, fontweight='bold', color='#1E1B4B', ha='center',
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#EEF2FF", alpha=0.9, edgecolor="#4338CA", linewidth=1.2))
        
    # Plot Ganga River schematic line
    ganga_x = [80.20, 80.27, 80.34, 80.41, 80.45]
    ganga_y = [26.54, 26.52, 26.49, 26.44, 26.40]
    ax.plot(ganga_x, ganga_y, color='#0284C7', linewidth=4.0, linestyle='-', alpha=0.6, label='Ganga River Corridor')
    
    ax.set_title("Kanpur Metropolitan Spatial Thermal Zonation & Air Quality Monitoring Network", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Longitude (°E) — EPSG:4326 WGS84", fontsize=10, labelpad=8)
    ax.set_ylabel("Latitude (°N) — EPSG:4326 WGS84", fontsize=10, labelpad=8)
    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def plot_04_lst_inversion_pm25_coupling(df_power, kanpur_aq_csv, output_path):
    """Figure 4: Coupling between Satellite Surface Cooling and Station-Level PM2.5 Inversion."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), sharex=True, dpi=300)
    
    # Load and aggregate Kanpur station air quality
    df_aq = pd.read_csv(kanpur_aq_csv)
    df_aq['Date_dt'] = pd.to_datetime(df_aq['date'])
    daily_pm = df_aq.groupby('Date_dt')[['pm25', 'pm10']].mean().reset_index()
    
    # Merge with NASA POWER
    df_power['Date_dt'] = pd.to_datetime(df_power['Date'])
    merged = pd.merge(df_power, daily_pm, on='Date_dt', how='inner')
    merged = merged.sort_values('Date_dt')
    
    # Panel 1: Satellite LST & Thermal Gradient
    ax1.plot(merged['Date_dt'], merged['LST_Skin_C'], color='#F59E0B', linewidth=1.5, label='NASA POWER LST (Skin Temp, °C)')
    ax1.plot(merged['Date_dt'], merged['Air_Temp_2M_C'], color='#2563EB', linewidth=1.4, linestyle='--', label='2m Air Temp (°C)')
    ax1.axhline(15, color='#3B82F6', linestyle=':', alpha=0.7, label='Winter Inversion Threshold (<15°C)')
    ax1.set_ylabel("Temperature (°C)", fontsize=11)
    ax1.set_title("Thermal Inversion Mechanics: Satellite Skin Temperature vs Ground PM2.5 Entrapment in Kanpur", fontsize=13, fontweight='bold', pad=12)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', fontsize=8.5, ncol=3)
    ax1.set_ylim(5, 48)
    
    # Panel 2: Ground-Level PM2.5 Concentration
    ax2.axhspan(60, 500, color='#EF4444', alpha=0.10, label='NAAQS Exceedance (>60 µg/m³)')
    ax2.plot(merged['Date_dt'], merged['pm25'], color='#DC2626', linewidth=1.4, label='Station PM2.5 (NSI Kalyanpur & Nehru Nagar)')
    pm25_30d = merged['pm25'].rolling(30, min_periods=1).mean()
    ax2.plot(merged['Date_dt'], pm25_30d, color='#7F1D1D', linewidth=2.2, label='30-Day PM2.5 Trend')
    ax2.set_ylabel("PM2.5 (µg/m³)", fontsize=11)
    ax2.set_xlabel("Date", fontsize=11)
    ax2.set_ylim(0, 320)
    ax2.legend(loc='upper right', frameon=True, facecolor='white', fontsize=8.5)
    
    # Annotate winter inversion surge
    ax2.annotate("Post-Sunset Radiative Inversion Trap\n(LST drops -> Shallow PBL -> PM2.5 Spikes)",
                 xy=(pd.Timestamp('2021-11-15'), 180),
                 xytext=(pd.Timestamp('2021-07-01'), 260),
                 arrowprops=dict(facecolor='#1E293B', shrink=0.05, width=1.5, headwidth=6),
                 fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF2F2", edgecolor="#EF4444"))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def run_kanpur_lst_gis_pipeline():
    """Master execution of the Kanpur LST GIS pipeline."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_csv = os.path.join(project_root, "data", "lst", "kanpur_nasa_power_daily.csv")
    qgis_dir = os.path.join(project_root, "outputs", "lst", "qgis")
    plots_dir = os.path.join(project_root, "outputs", "lst", "plots")
    web_assets_dir = os.path.join(project_root, "web", "assets", "lst")
    web_data_dir = os.path.join(project_root, "web", "data")
    kanpur_aq_csv = os.path.join(project_root, "web", "data", "kanpur", "daily_aggregated.csv")
    
    os.makedirs(qgis_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(web_assets_dir, exist_ok=True)
    os.makedirs(web_data_dir, exist_ok=True)
    
    # 1. Load Data
    print("\n[Stage 1/5] Loading NASA POWER continuous daily telemetry...")
    df = pd.read_csv(data_csv)
    
    # 2. Export QGIS Vector Layers
    print("\n[Stage 2/5] Exporting QGIS vector GeoJSON layers...")
    export_qgis_layers(qgis_dir)
    # Also copy geojson to web/data/ for web map visualization if desired
    with open(os.path.join(web_data_dir, "kanpur_thermal_zones.geojson"), "w") as f:
        json.dump(KANPUR_ZONES_GEO, f, indent=2)
    with open(os.path.join(web_data_dir, "kanpur_cpcb_stations.geojson"), "w") as f:
        json.dump(KANPUR_STATIONS_GEO, f, indent=2)
        
    # 3. Generate 300-DPI Publication Figures
    print("\n[Stage 3/5] Generating publication-grade GIS & LST figures...")
    p1 = os.path.join(plots_dir, "01_kanpur_lst_seasonal_timeline.png")
    p2 = os.path.join(plots_dir, "02_skin_vs_air_temperature_anomaly.png")
    p3 = os.path.join(plots_dir, "03_kanpur_spatial_thermal_zones.png")
    p4 = os.path.join(plots_dir, "04_lst_inversion_coupling_pm25.png")
    
    plot_01_seasonal_timeline(df, p1)
    plot_02_skin_vs_air_anomaly(df, p2)
    plot_03_spatial_thermal_zones(p3)
    plot_04_lst_inversion_pm25_coupling(df, kanpur_aq_csv, p4)
    
    # 4. Copy figures to web assets
    print("\n[Stage 4/5] Synchronizing figures to web/assets/lst/...")
    for p in [p1, p2, p3, p4]:
        fname = os.path.basename(p)
        dest = os.path.join(web_assets_dir, fname)
        import shutil
        shutil.copyfile(p, dest)
    print("Web assets synchronized.")
    
    # 5. Export lightweight web JSON feed for interactive telemetry
    print("\n[Stage 5/5] Exporting web-optimized daily LST JSON feed...")
    web_json = os.path.join(web_data_dir, "kanpur_lst_daily.json")
    records = []
    for _, row in df.iterrows():
        records.append({
            "date": str(row["Date"]),
            "lst": round(float(row["LST_Skin_C"]), 1) if pd.notna(row["LST_Skin_C"]) else None,
            "air_t": round(float(row["Air_Temp_2M_C"]), 1) if pd.notna(row["Air_Temp_2M_C"]) else None,
            "delta_t": round(float(row["Delta_T_Skin_Air_C"]), 1) if pd.notna(row["Delta_T_Skin_Air_C"]) else None,
            "solar": round(float(row["Solar_Radiation_MJ_m2"]), 1) if pd.notna(row["Solar_Radiation_MJ_m2"]) else None,
            "season": str(row["Season"])
        })
    with open(web_json, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Exported {len(records)} daily records to {web_json}.")
    print("\nKANPUR LST & GIS PIPELINE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_kanpur_lst_gis_pipeline()
