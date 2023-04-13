import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt
import missingno as msno


st.set_option('deprecation.showPyplotGlobalUse', False)


st.title("Analyse des données Uber")

# Charger les données
DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/geojson/vancouver-blocks.json"
LAND_COVER = [[[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]]
INITIAL_VIEW_STATE = pdk.ViewState(latitude=49.254, longitude=-123.13, zoom=11, max_zoom=16, pitch=45, bearing=0)

polygon = pdk.Layer(
    "PolygonLayer",
    LAND_COVER,
    stroked=False,
    get_polygon="-",
    get_fill_color=[0, 0, 0, 20],
)

geojson = pdk.Layer(
    "GeoJsonLayer",
    DATA_URL,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="properties.valuePerSqm / 20",
    get_fill_color="[255, 255, properties.growth * 255]",
    get_line_color=[255, 255, 255],
)

r = pdk.Deck(layers=[polygon, geojson], initial_view_state=INITIAL_VIEW_STATE)
#st.pydeck_chart(r)

path2 = "https://raw.githubusercontent.com/uber-web/kepler.gl-data/master/nyctrips/data.csv"
df3 = pd.read_csv(path2, delimiter=',')





# Les fonctions get_day, get_hour et get_weekday doivent être définies ici
def get_dom(dt):
    return dt.day

def get_weekday(dt):
    return dt.weekday()


def get_hour(dt):
    return dt.hour

def get_day(dt):
    return dt.day

def count_rows(rows):
    return len(rows)

# Traitement des données et création de nouvelles colonnes
# ADD columbs pickup_ and dropoff_ (day, weekday and hour)
df3['tpep_pickup_datetime'] = df3['tpep_pickup_datetime'].map(pd.to_datetime)
df3['pickup_day']= df3['tpep_pickup_datetime'].map(get_day)
df3['pickup_hour']= df3['tpep_pickup_datetime'].map(get_hour)
df3['pickup_weekday']= df3['tpep_pickup_datetime'].map(get_weekday)


df3['tpep_dropoff_datetime'] = df3['tpep_dropoff_datetime'].map(pd.to_datetime)
df3['dropoff_day']= df3['tpep_dropoff_datetime'].map(get_day)
df3['dropoff_hour']= df3['tpep_dropoff_datetime'].map(get_hour)
df3['dropoff_weekday']= df3['tpep_dropoff_datetime'].map(get_weekday)

# Get the unique pickup hours and store them in a list
pickup_hours = df3["pickup_hour"].value_counts().index.tolist()

# Get the count of pickups for each hour and store them in a list
pickup_counts = df3["pickup_hour"].value_counts().tolist()

df3["tip_percentage"] = (df3["tip_amount"] / df3["fare_amount"]) * 100

df3["tip_percentage"].fillna(0, inplace=True)

# Filter the DataFrame to keep only rows where the "tip_percentage" is between 0 and 100 (inclusive)
df3 = df3[(df3["tip_percentage"] >= 0) & (df3["tip_percentage"] <= 100)]

# Use the clip() function to ensure all "tip_percentage" values are within the range [0, 100]
# This step might not be necessary, as the filtering in the previous line should have already taken care of this
df3["tip_percentage"] = df3["tip_percentage"].clip(0, 100)

# Extract the "fare_amount" and "tip_percentage" columns from the DataFrame
fare_amount = df3["fare_amount"]
tip_percentage = df3["tip_percentage"]

# Create a DataFrame with only the dropoff_latitude and dropoff_longitude columns
dropoff_df = df3[['dropoff_latitude', 'dropoff_longitude']]

# Create a ScatterplotLayer for the dropoff locations using PyDeck
dropoff_layer = pdk.Layer(
    "ScatterplotLayer",
    data=dropoff_df,
    get_position=["dropoff_longitude", "dropoff_latitude"],
    get_radius=30,
    get_fill_color=[0, 0, 255, 140],
    pickable=True,
    auto_highlight=True
)

# Calculate the mean latitude and longitude for the center of the map
center_lat = df3['dropoff_latitude'].mean()
center_lon = df3['dropoff_longitude'].mean()

# Create a ViewState object to set the initial view of the map
view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=12,
    pitch=0
)

# Create a PyDeck map (Deck object) with the dropoff_layer and view_state
dropoff_map = pdk.Deck(layers=[dropoff_layer], initial_view_state=view_state, tooltip={"text": "Dropoff: {dropoff_latitude}, {dropoff_longitude}"})


st.subheader("Heures de prise en charge Uber")
pickup_hours_fig = plt.figure() 
pickup_hours_bar = plt.bar(pickup_hours, pickup_counts)
plt.xlabel("Heure")
plt.ylabel("Nombre de prises en charge")
st.pyplot(pickup_hours_fig)


st.subheader("Distribution des pourcentages de pourboire en fonction du montant de la course")
fare_amount_tip_percentage_fig = plt.figure()
fare_amount_tip_percentage = sns.kdeplot(x=fare_amount, y=tip_percentage, cmap="Blues", shade=True, common_norm=True)
plt.xlim(0, 60)
plt.ylim(0, 60)
st.pyplot(fare_amount_tip_percentage_fig)

# Heures de pointe par jour pour chaque Uber
st.subheader("Heures de pointe par jour pour chaque Uber")

fig, ax1 = plt.subplots()
ax1.plot(df3[df3['VendorID'] == 1].groupby(['pickup_hour', 'pickup_day'])['VendorID'].count().unstack(), label="Uber 1")
ax1.plot(df3[df3['VendorID'] == 2].groupby(['pickup_hour', 'pickup_day'])['VendorID'].count().unstack(), label="Uber 2")
ax1.set_xlabel("Rush Hours")
ax1.set_ylabel("Number of Rides")
ax1.set_title("Rush Hours by Day for Each Uber")
ax1.legend()


xticks = df3['pickup_hour'].unique()
xticks.sort()
ax1.set_xticks(xticks)
ax1.set_xticklabels([f"{hour:02d}:00" for hour in xticks], rotation=45)

st.pyplot(fig)

# Points de dépose des passagers
st.subheader("Points de dépose des passagers")
st.pydeck_chart(dropoff_map)

# Nombre de trajets par VendorID et heure
st.subheader("Nombre de trajets par VendorID et heure")

heatmap_data = df3.groupby(['VendorID', 'pickup_hour'])['VendorID'].count().reset_index(name='num_rides')
heatmap_data = heatmap_data.pivot('VendorID', 'pickup_hour', 'num_rides')
heatmap_data.fillna(0, inplace=True)
heatmap_data = heatmap_data.astype(int)

plt.figure(figsize=(12, 6))
heatmap_plot = sns.heatmap(heatmap_data, cmap='viridis', annot=True, fmt='d', annot_kws={"fontsize": 8})
plt.title('Number of Rides by VendorID and Hour')
plt.xlabel("Hour")
plt.ylabel("VendorID")

st.pyplot(heatmap_plot.figure)

# Montant total de la course par VendorID et heure
st.subheader("Montant total de la course par VendorID et heure")

g = sns.catplot(
    data=df3,
    x='pickup_hour',
    y='total_amount',
    hue='VendorID',
    kind='bar',
    height=6,
    aspect=2,
    ci=None,
)

g.fig.suptitle("Total Fare Amount by VendorID and Hour")
g.set(xlabel="Hour")
g.set(ylabel="Total Fare Amount")

st.pyplot(g.fig)
