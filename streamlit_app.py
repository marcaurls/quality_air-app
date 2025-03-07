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

def create_rfm_df(df):
    df['date'] = pd.to_datetime(df['date'])
    recency = df[df['PM2.5'] > 100].groupby('station')['date'].max()
    recency = (df['date'].max() - recency).dt.days

    # berapa kali dalam setahun polusi tinggi terjadi
    frequency = df[df['PM2.5'] > 100].groupby("station")['date'].count()

    # rata-rata PM2.5 per statiun
    magnitude = df.groupby('station')['PM2.5'].mean()


    rfm = pd.DataFrame({"station":recency.index, "Recency":recency.values, "Frequency":frequency.values, "Magnitude":magnitude.values})

    # skala nilai
    rfm['R_Score'] = pd.cut(rfm['Recency'].rank(method='first'), bins=4, labels=[4,3,2,1])
    rfm['F_Score'] = pd.cut(rfm['Frequency'].rank(method='first'), bins=4, labels=[1,2,3,4])
    rfm['M_Score'] = pd.cut(rfm['Magnitude'].rank(method='first'), bins=4, labels=[1,2,3,4])

    rfm["RFM_Score"] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
    
    return rfm

def create_folium(df):
    map = df.groupby(by='station')['PM2.5'].nunique().sort_values(ascending=False).reset_index()
    return map

all_df = pd.read_csv("all_data.csv")

pm25_data = pm25_trend(all_df)
air_pollution = create_air_pollution(all_df)
rfm_df = create_rfm_df(all_df)
map_df = create_folium(all_df)


st.header("Air Pollution in China")

st.subheader("Air Pollution Trend")


plt.figure(figsize=(12,6))
sns.lineplot(data=pm25_data, x='year', y='PM2.5', hue='station', marker='o')

plt.title("Tren PM2.5 per Stasiun")
plt.xlabel("Tahun")
plt.ylabel("Konsentrasi PM2.5")
plt.legend(title='Stasiun', bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.5, )

st.pyplot(plt)

st.subheader("Hubungan Curah Hujan dengan PM2.5 di Berbagai Kota")

plt.figure(figsize=(10,6))
sns.scatterplot(data=air_pollution, x='RAIN', y='PM2.5', hue='station', style='station', alpha=0.7)

sns.regplot(data=air_pollution, x="RAIN", y='PM2.5', scatter=False, color='black', line_kws={'linestyle':'dashed'})

plt.title("Hubungan Curah Hujan dengan PM2.5 di Berbagai Kota")
plt.xlabel("Curah Hujan (mm)")
plt.ylabel("PM2.5 (µg/m³)")
plt.legend(title='Stasiun', bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.5)

st.pyplot(plt)



st.subheader("Daerah dengan Polusi Tertinggi on RFM Parameters")

col1, col2, col3, = st.columns(3)
with col1:
    avg_recency = round(rfm_df.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
    
with col2:
    avg_frequency = round(rfm_df.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
    
with col3:
    avg_magnitude = round(rfm_df.Magnitude.mean(), 2)
    st.metric("Average PM2.5", value=avg_magnitude)
    

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35,15))
colors = ['#03045e', '#023e8a', '#0077b6', '#0096c7', '#00b4d8', '#48cae4', '#90e0ef',
          '#ade8f4', '#caf0f8', '#41a7f5', '#64b7f6', '#90cbf9']

sns.barplot(y="Recency", x='station', 
            data=rfm_df.sort_values(by='Recency', ascending=False),
            palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Station", fontsize=30)
ax[0].set_title("By Recency (days)", loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=90)

sns.barplot(y="Frequency", x='station', 
            data=rfm_df.sort_values(by='Frequency', ascending=False),
            palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Station", fontsize=30)
ax[1].set_title("By Frequency", loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)

sns.barplot(y="Magnitude", x='station', 
            data=rfm_df.sort_values(by='Magnitude', ascending=False),
            palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Station", fontsize=30)
ax[2].set_title("By PM2.5", loc='center', fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)

st.pyplot(fig)


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