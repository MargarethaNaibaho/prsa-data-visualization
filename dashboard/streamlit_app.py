import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Kualitas Udara",
    page_icon=":bar_chart:",
    layout="wide",
)
st.logo("dashboard/assets/laskar_ai_logo.png") # dashboard/ dipakai hanya untuk supaya bisa deploy streamlit

df = pd.read_csv("dashboard/all_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

st.sidebar.header("Filter Rentang Tanggal")
start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal:",
    [df['date'].min().date(), df['date'].max().date()]
)

st.sidebar.text("Made with ❤️ by Margaretha Gok Asi Naibaho")

if start_date and end_date:
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    df_filtered = df.loc[mask]
else:
    df_filtered = df.copy()

st.header("Dashboard Visualisasi Kualitas Udara di China (2013 - 2017)")
st.markdown("Tugas ini diselesaikan oleh Margaretha Gok Asi Naibaho untuk menyelesaikan submission modul Dicoding - Belajar Analisis Data dengan Python")
col1, col2 = st.columns(2)
# Business Question 1 untuk menampilkan rata-rata O3 dan SO2 per stasiun
avg_o3_so2_per_station = df_filtered.groupby('station')[['O3', 'SO2']].mean().reset_index().sort_values(by=['O3', 'SO2'], ascending=False)

with col1:
    fig, ax = plt.subplots(figsize=(16, 8))
    # Set style
    plt.style.use('ggplot')
    # Plot O3
    sns.barplot(data=avg_o3_so2_per_station.reset_index(), x='station', y='O3', color='skyblue', label='O₃')
    # Plot SO2
    sns.barplot(data=avg_o3_so2_per_station.reset_index(), x='station', y='SO2', color='salmon', label='SO₂')
    plt.title('Rata-rata O₃ dan SO₂ per stasiun')
    plt.ylabel('Rata-rata konsemtrasi (μg/m³)')
    plt.xlabel('Stasiun')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("\n\n\n")

# Business Question 2 untuk menampilkan rata-rata WSPM per stasiun
avg_wspm_per_station = df_filtered.groupby('station')['WSPM'].mean().sort_values(ascending=False)

with col2:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=avg_wspm_per_station.index, y=avg_wspm_per_station.values, color='lightgreen')
    plt.title('Kecepatan Angin (WSPM) Rata-rata per Stasiun')
    plt.ylabel('WSPM (m/s)')
    plt.xlabel('Stasiun')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# Melihat korelasi antara WSPM dengan O3, SO2, PM2.5, dan PM10
cols_corr1 = ['WSPM', 'O3', 'SO2', 'PM2.5', 'PM10']
corr_matrix1 = df_filtered[cols_corr1].corr()

col3, col4 = st.columns(2)

with col3:
    fig4, ax4 = plt.subplots(figsize=(6, 6))
    sns.heatmap(corr_matrix1, annot=True, cmap='coolwarm', ax=ax4)
    ax4.set_title('Korelasi WSPM dengan Polutan (O3, SO2, PM2.5, PM10)')
    plt.tight_layout()
    st.pyplot(fig4)

# Business Question 3 untuk menampilkan perbandingan kualitas udara
# O3 dan SO2 pada hari kerja vs akhir pekan
df_filtered['weekday'] = df_filtered['date'].dt.weekday
df_filtered['day_type'] = df_filtered['weekday'].apply(lambda x: 'Akhir Pekan' if x >= 5 else 'Hari Kerja')

avg_pollutants_by_daytype = df_filtered.groupby(['station', 'day_type'])[['O3', 'SO2']].mean().reset_index()

with col4:
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))
    sns.barplot(data=avg_pollutants_by_daytype, x='station', y='O3', hue='day_type', palette='Blues', ax=ax[0])
    ax[0].set_title('Perbandingan Rata-rata O₃ per  Stasiun: Weekend vs Weekday')
    ax[0].set_xlabel('Stasiun')
    ax[0].set_ylabel('Rata-rata O₃ (μg/m³)')
    ax[0].tick_params(axis='x', rotation=45)
    plt.tight_layout()

    sns.barplot(data=avg_pollutants_by_daytype, x='station', y='SO2', hue='day_type', palette='Oranges', ax=ax[1])
    ax[1].set_title('Perbandingan Rata-rata SO₂ per  Stasiun: Weekend vs Weekday')
    ax[1].set_xlabel('Stasiun')
    ax[1].set_ylabel('Rata-rata SO₂ (μg/m³)')
    ax[1].tick_params(axis='x', rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# Business Question 4 untuk melihat hubungan polutan partikulat (PM2.5, PM10)
# dengan cuaca (temperature, pressure)

col5, col6 = st.columns(2)

# Korelasi PM dengan TEMP dan PRES
with col5:
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(df_filtered[['PM2.5', 'PM10', 'TEMP', 'PRES']].corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Korelasi antara Partikulat dan Cuaca')
    plt.tight_layout()
    st.pyplot(fig)

# Lineplot rata-rata PM berdasarkan bin suhu
df_temp_grouped = df_filtered.groupby('temp_bin')[['PM2.5', 'PM10']].mean().reset_index()
df_temp_grouped['temp_bin'] = df_temp_grouped['temp_bin'].astype(str)

with col6:
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.lineplot(data=df_temp_grouped, x='temp_bin', y='PM2.5', label='PM2.5', marker='o')
    sns.lineplot(data=df_temp_grouped, x='temp_bin', y='PM10', label='PM10', marker='o')
    plt.title('Rata-rata PM2.5 dan PM10 Berdasarkan Rentang Suhu')
    plt.xlabel('Rentang Suhu (°C)')
    plt.ylabel('Konsentrasi (μg/m³)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    st.pyplot(fig)