import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import pydeck as pdk
from IPython.display import display, Markdown

st.set_option('deprecation.showPyplotGlobalUse', False)

path = 'uber-raw-data.csv'

df = pd.read_csv(path, delimiter=',')

df['Date/Time'] = df['Date/Time'].map(pd.to_datetime)

def get_dom(dt):
    return dt.day

def get_weekday(dt):
    return dt.weekday()

df['weekday']= df['Date/Time'].map(get_weekday)

def get_hour(dt):
    return dt.hour

def get_day(dt):
    return dt.day

df['day']= df['Date/Time'].map(get_day)

df['hour']= df['Date/Time'].map(get_hour)

hist = df["day"].plot.hist(bins = 30, rwidth = 0.8, range=(0.5,30.5), title = "Frequency by DoM - Uber - April 2014")
plt.xlabel('Days of the month')
st.pyplot()

def count_rows(rows):
    return len(rows)

by_date = df.groupby('day').apply(count_rows)

plt.title(('Line plot - Uber - April 2014'), fontsize=20)
plt.xlabel('Days of the month')
plt.ylabel('Frequency')
plt.plot(by_date)
st.pyplot()

plt.figure(figsize = (25, 15))
plt.bar(range(1, 31), by_date.sort_values())
plt.xticks(range(1, 31), by_date.sort_values().index)
plt.xlabel(('Date of the month'), fontsize=20)
plt.ylabel(('Frequency'), fontsize=20)
plt.title(('Frequency by DoM - Uber - April 2014'), fontsize=20);
st.pyplot()

plt.hist(df.weekday, bins = 7, rwidth = 0.8, range = (-.5, 6.5))
plt.xlabel('Days of the week')
plt.ylabel('Frequency')
plt.title(('Frequency by Weekdays - Uber - April 2014'), fontsize=20);
st.pyplot()

plt.hist(df.weekday, bins = 7, rwidth = 0.8, range = (-.5, 6.5))
plt.xlabel('Day of the week')
plt.ylabel('Frequency')
plt.title(('Frequency by weekday - Uber - April 2014'), fontsize=20)
plt.xticks(np.arange(7), 'Tue Wed Thu Fri Sat Sun Mon'.split())
st.pyplot()

df2 = df.groupby(['weekday', 'hour']).apply(count_rows).unstack()

sns.heatmap(df2, linewidths = .5);
heatmap = sns.heatmap(df2, linewidths = .5);
plt.title('Heatmap by Hour and weekdays - Uber - April 2014',fontsize=15)
heatmap.set_yticklabels(('Mar Mer Jeu Ven Sam Dim Lun').split(), rotation='horizontal');
st.pyplot()

plt.hist(df['Lat'], bins = 100, range = (40.5, 41), color = 'r',alpha = 0.5, label = 'Latitude')
plt.xlabel('Latitude')
plt.ylabel('Frequency')
plt.title('Lattitude - Uber - April 2014');
st.pyplot()

plt.hist(df['Lon'], bins = 100, range = (-74.1, -73.9), color = 'g', alpha = 0.5, label = 'Longitude')
plt.xlabel('Longitude')
plt.ylabel('Frequency')
plt.title('Longitude - Uber - April 2014');
st.pyplot()

plt.figure(figsize=(10, 10), dpi=100)
plt.title('Longitude and Latitude distribution - Uber - April 2014',fontsize=15)
plt.hist(df['Lon'], bins = 100, range = (-74.1, -73.9), color = 'g', alpha = 0.5, label = 'Longitude')
plt.legend(loc = 'best')
plt.twiny()
plt.hist(df['Lat'], bins = 100, range = (40.5, 41), color = 'r',alpha = 0.5, label = 'Latitude')
plt.legend(loc = 'upper left')
st.pyplot()

plt.figure(figsize=(15, 15), dpi=100)
plt.title('Scatter plot - Uber - April 2014')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.scatter(df['Lat'],df['Lon'],s=0.8,alpha=0.4) #Without list also shows the same plot
plt.ylim(-74.1, -73.8)
plt.xlim(40.7, 40.9)
st.pyplot()

dico = {0:'yellow', 1:'yellow', 2:'blue', 3:'yellow', 4:'yellow', 5:'yellow', 6:'yellow'}
plt.figure(figsize=(15, 15), dpi = 100)
plt.title('Scatter Plot - Uber - April 2014')
x = df["Lat"]
y = df["Lon"]
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.scatter(x, y, s = 0.7, alpha = 0.4, c = df["weekday"].map(dico))
plt.ylim(-74.1, -73.8)
plt.xlim(40.7, 40.9)
st.pyplot()

