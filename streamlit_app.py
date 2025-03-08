import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns 
import streamlit as st
import folium
from streamlit_folium import st_folium 
from folium.plugins import HeatMap
sns.set(style='dark')

def create_air_pollution(df):
    air_pollution_df = df.groupby(by= ['station', 'year']).agg({
        "PM2.5": "mean",
        "RAIN": "mean",
        }).sort_values(by=['station'], ascending=True)
    air_pollution_df = air_pollution_df.reset_index()

    return air_pollution_df

def pm25_trend(df):
    pm25_trend_df = df.groupby(by=['station', 'year'])["PM2.5"].mean().sort_values(ascending=False).reset_index()
    return pm25_trend_df

def create_folium(df):
    map = df.groupby(by='station')['PM2.5'].nunique().sort_values(ascending=False).reset_index()
    return map

def air_quality_trend(df):
    air_quality_df = df.groupby(by=['station', 'year']).agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "NO2": "mean",
        "CO": "mean",
        "O3": "mean"
    }).reset_index()

    def categorize_air_quality(row):
        if row['PM2.5'] <= 50 and row['PM10'] <= 30 and row['SO2'] <= 40 and row['NO2'] <= 40 and row['CO'] <= 1000 and row['O3'] <= 50:
            return "Good"
        elif row['PM2.5'] <= 100 or row['PM10'] <= 60 or row['SO2'] <= 80 or row['NO2'] <= 80 or row['CO'] <= 2000 or row['O3'] <= 100: 
            return "Satisfactory"
        elif row['PM2.5'] <= 250 or row['PM10'] <= 90 or row['SO2'] <= 380 or row['NO2'] <= 180 or row['CO'] <= 10000 or row['O3'] <= 168:
            return "Moderate"
        elif row['PM2.5'] <= 350 or row['PM10'] <= 120 or row['SO2'] <= 800 or row['NO2'] <= 280 or row['CO'] <= 17000 or row['O3'] <= 208: 
            return "Poor"
        elif row['PM2.5'] <= 430 or row['PM10'] <= 250 or row['SO2'] <= 1600 or row['NO2'] <= 400 or row['CO'] <= 34000 or row['O3'] <= 748:
            return "Very Poor"
        else:
            return "Severe"  

    air_quality_df['kategori'] = air_quality_df.apply(categorize_air_quality, axis=1)

    return air_quality_df


all_df = pd.read_csv("all_data.csv")

years = all_df['year'].unique()
stations = all_df['station'].unique()

# sidebar
with st.sidebar:
    selected_year = st.multiselect("Year:", years, default=years)
    selected_station = st.multiselect("Station:", stations, default=stations)
    
    filtered_df = all_df[(all_df['year'].isin(selected_year)) & (all_df['station'].isin(selected_station))]
    
pm25_data = pm25_trend(filtered_df)
air_pollution = create_air_pollution(filtered_df)
map_df = create_folium(filtered_df)
aqi_df = air_quality_trend(filtered_df)

st.header("Air Pollution in China")


air_quality_category = aqi_df.iloc[0]['kategori']

st.metric("AQI", value=air_quality_category)

filtered_aqi = aqi_df[aqi_df['kategori'] == air_quality_category][['year', 'station', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']]
st.dataframe(filtered_aqi)
    

st.subheader("Air Pollution Trend")

plt.figure(figsize=(12,6))
sns.lineplot(data=pm25_data, x='year', y='PM2.5', hue='station', marker='o')

plt.title("Tren PM2.5 per Stasiun")
plt.xlabel("Tahun")
plt.ylabel("Konsentrasi PM2.5")
plt.legend(title='Stasiun', bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.5, )

st.pyplot(plt)

st.subheader("Hubungan Curah Hujan dengan PM2.5")

plt.figure(figsize=(10,6))
sns.scatterplot(data=air_pollution, x='RAIN', y='PM2.5', hue='station', style='station', alpha=0.7)

sns.regplot(data=air_pollution, x="RAIN", y='PM2.5', scatter=False, color='black', line_kws={'linestyle':'dashed'})

plt.title("Hubungan Curah Hujan dengan PM2.5 di Berbagai Kota")
plt.xlabel("Curah Hujan (mm)")
plt.ylabel("PM2.5 (µg/m³)")
plt.legend(title='Stasiun', bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.5)

st.pyplot(plt)


station_coords = {
    "Aotizhongxin": (39.982, 116.417),
    "Changping": (40.220, 116.231),
    "Dingling": (40.290, 116.220),
    "Dongsi": (39.929, 116.417),
    "Guanyuan": (39.933, 116.339),
    "Gucheng": (39.907, 116.152),
    "Huairou": (40.409, 116.630),
    "Nongzhanguan": (39.933, 116.461),
    "Shunyi": (40.128, 116.654),
    "Tiantan": (39.886, 116.421),
    "Wanliu": (39.974, 116.295),
    "Wanshouxigong": (39.886, 116.354)
}

map_df['latitude'] = map_df['station'].map(lambda x: station_coords.get(x, (None, None))[0])
map_df['longitude'] = map_df['station'].map(lambda x: station_coords.get(x, (None, None))[1])

station_avg = map_df.groupby("station")[["PM2.5", "latitude", "longitude"]].mean().reset_index()

m = folium.Map(location=[station_avg['latitude'].mean(), station_avg['longitude'].mean()], zoom_start=10)

# Menambahkan Heatmap ke peta
HeatMap(data=station_avg[['latitude', 'longitude', "PM2.5"]].values, radius=15).add_to(m)

# Menampilkan peta di Streamlit
st.subheader("Peta Polusi Udara Berdasarkan Stasiun")
st_folium(m, width=700, height=500)
