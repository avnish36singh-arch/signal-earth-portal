import pandas as pd
import json

# 1. Kanpur Data
df_daily = pd.read_csv('data/kanpur/daily_aggregated.csv')
df_monthly = pd.read_csv('data/kanpur/monthly_averages.csv')

total_station_days = len(df_daily)
kalyanpur_days = len(df_daily[df_daily['location_name'] == 'NSI Kalyanpur'])
nehru_nagar_days = len(df_daily[df_daily['location_name'] == 'Nehru Nagar'])
valid_pm25_obs = int(df_daily['pm25'].notna().sum())

df_daily['date'] = pd.to_datetime(df_daily['date'])
dates = df_daily['date'].drop_duplicates().sort_values().reset_index(drop=True)
date_diffs = dates.diff()

last_window_1 = None
first_window_2 = None
for i, d in enumerate(date_diffs):
    if d.days > 100:
        last_window_1 = dates[i-1]
        first_window_2 = dates[i]
        break

hiatus_first_missing = (last_window_1 + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
hiatus_last_missing = (first_window_2 - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
hiatus_days_inclusive = (first_window_2 - last_window_1).days - 1

pooled_winter_mean = float(df_monthly[df_monthly['month'].isin([12, 1, 2])]['pm25'].mean())
pooled_summer_mean = float(df_monthly[df_monthly['month'].isin([6, 7, 8, 9])]['pm25'].mean())
pooled_monsoon_mean = float(df_monthly[df_monthly['month'].isin([7, 8, 9])]['pm25'].mean())
pooled_ratio_winter_summer = pooled_winter_mean / pooled_summer_mean
pooled_ratio_winter_monsoon = pooled_winter_mean / pooled_monsoon_mean

nov_mean = float(df_monthly[df_monthly['month'] == 11]['pm25'].mean())
aug_mean = float(df_monthly[df_monthly['month'] == 8]['pm25'].mean())
peak_to_min_ratio = nov_mean / aug_mean

kalyanpur_winter = float(df_monthly[(df_monthly['location_name'] == 'NSI Kalyanpur') & df_monthly['month'].isin([12, 1, 2])]['pm25'].mean())
kalyanpur_summer = float(df_monthly[(df_monthly['location_name'] == 'NSI Kalyanpur') & df_monthly['month'].isin([6, 7, 8, 9])]['pm25'].mean())
kalyanpur_ratio = kalyanpur_winter / kalyanpur_summer

nehru_winter = float(df_monthly[(df_monthly['location_name'] == 'Nehru Nagar') & df_monthly['month'].isin([12, 1, 2])]['pm25'].mean())
nehru_summer = float(df_monthly[(df_monthly['location_name'] == 'Nehru Nagar') & df_monthly['month'].isin([6, 7, 8, 9])]['pm25'].mean())
nehru_ratio = nehru_winter / nehru_summer

# 2. Delhi Data
delhi_metrics = {}
df_delhi = pd.read_csv('enviornment_rajivgangulaly/data/processed/air_quality_clean.csv')
delhi_metrics['total_records'] = len(df_delhi)
delhi_metrics['aqi_official_valid_days'] = int(df_delhi['AQI_Official'].sum())
delhi_metrics['pm25_valid_observations'] = int(df_delhi['PM2.5'].notna().sum())

# Delhi seasonal calculations
d_winter = df_delhi[df_delhi['Month'].isin([12, 1, 2])]['PM2.5'].mean()
d_monsoon = df_delhi[df_delhi['Month'].isin([6, 7, 8, 9])]['PM2.5'].mean()
d_peak = df_delhi[df_delhi['Month'].isin([11, 12, 1])]['PM2.5'].mean()
d_core_monsoon = df_delhi[df_delhi['Month'].isin([7, 8, 9])]['PM2.5'].mean()
delhi_metrics['winter_mean_ug_m3'] = round(d_winter, 2)
delhi_metrics['monsoon_mean_ug_m3'] = round(d_monsoon, 2)
delhi_metrics['winter_to_monsoon_ratio'] = round(d_winter / d_monsoon, 2)
delhi_metrics['peak_haze_mean_ug_m3'] = round(d_peak, 2)
delhi_metrics['core_monsoon_mean_ug_m3'] = round(d_core_monsoon, 2)
delhi_metrics['peak_to_core_monsoon_ratio'] = round(d_peak / d_core_monsoon, 2)

# Dominant pollutant on official AQI days
official_df = df_delhi[df_delhi['AQI_Official'] == True]
delhi_metrics['pm25_dominant_days'] = int((official_df['Dominant_Pollutant'] == 'PM2.5').sum())
delhi_metrics['pm10_dominant_days'] = int((official_df['Dominant_Pollutant'] == 'PM10').sum())
delhi_metrics['pm25_pct'] = round(100.0 * delhi_metrics['pm25_dominant_days'] / len(official_df), 1)
delhi_metrics['pm10_pct'] = round(100.0 * delhi_metrics['pm10_dominant_days'] / len(official_df), 1)
delhi_metrics['particulate_total_pct'] = round(delhi_metrics['pm25_pct'] + delhi_metrics['pm10_pct'], 1)

computed = {
    "kanpur": {
        "total_station_days": total_station_days,
        "kalyanpur_station_days": kalyanpur_days,
        "nehru_nagar_station_days": nehru_nagar_days,
        "valid_pm25_observations": valid_pm25_obs,
        "hiatus_last_window_1": last_window_1.strftime('%Y-%m-%d'),
        "hiatus_first_window_2": first_window_2.strftime('%Y-%m-%d'),
        "hiatus_first_missing_date": hiatus_first_missing,
        "hiatus_last_missing_date": hiatus_last_missing,
        "hiatus_days_inclusive": hiatus_days_inclusive,
        "pooled_winter_mean_ug_m3": round(pooled_winter_mean, 2),
        "pooled_summer_mean_ug_m3": round(pooled_summer_mean, 2),
        "pooled_monsoon_mean_ug_m3": round(pooled_monsoon_mean, 2),
        "pooled_winter_to_summer_ratio": round(pooled_ratio_winter_summer, 2),
        "pooled_winter_to_monsoon_ratio": round(pooled_ratio_winter_monsoon, 2),
        "nov_peak_mean_ug_m3": round(nov_mean, 2),
        "aug_min_mean_ug_m3": round(aug_mean, 2),
        "peak_to_min_ratio": round(peak_to_min_ratio, 2),
        "kalyanpur_winter_to_summer_ratio": round(kalyanpur_ratio, 2),
        "nehru_nagar_winter_to_summer_ratio": round(nehru_ratio, 2)
    },
    "delhi": delhi_metrics
}

with open('data/computed_values.json', 'w') as f:
    json.dump(computed, f, indent=2)

print("Computed Values Summary:")
print(json.dumps(computed, indent=2))
