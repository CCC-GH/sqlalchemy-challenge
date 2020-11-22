#%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

#import numpy as np
import pandas as pd

import datetime as dt

# Reflect Tables into SQLAlchemy ORM
# Python SQL toolkit and Object Relational Mapper
#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Establish DBAPI connection
engine = create_engine('sqlite:///./Resources/hawaii.sqlite')

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
base.classes.keys()

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Design a query to retrieve the last 12 months of precipitation data and plot the results
lastDate = session.query(measurement.date).order_by(measurement.date.desc()).first().date

# Calculate the date 1 year ago from the last data point in the database
lastYear = dt.datetime.strptime(lastDate, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
precipScore = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= lastYear).\
    order_by(measurement.date).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
precip_df = pd.DataFrame(precipScore, columns = ['Date', 'Precipitation'])
precip_df.set_index('Date', inplace=True)

# Sort the dataframe by date
# Use Pandas Plotting with Matplotlib to plot the data
chart = precip_df.plot(figsize=(10,4)).get_figure()
plt.title('Last 12 Month Precipitation from all Stations', fontsize=14)
plt.ylabel('Inches', fontsize=11)
plt.xlabel('Date', fontsize=11)
plt.xticks(rotation=45)
plt.legend(loc='upper right')
chart.savefig('Output/Precipitation_Last12m.png', bbox_inches='tight')
plt.show()

# Use Pandas to calcualte the summary statistics for the precipitation data
precip_df.describe()

# Design a query to show how many stations are available in this dataset?
stationLocs = session.query(station)
stationCount = stationLocs.count()
print(f'There are {stationCount} stations.')

# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
ActiveStationsDesc = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
mostActiveStationName = ''
mostActiveStation = ActiveStationsDesc[0][0]
for loc in stationLocs:
    if(loc.station == ActiveStationsDesc[0][0]):
        mostActiveStationName = loc.name 
print(f'\033[1mMost active is:\033[0m {mostActiveStationName}')
print(f'\033[1mStation:\033[0m {ActiveStationsDesc[0][0]}')
print(f'\033[1mCount:\033[0m {ActiveStationsDesc[0][1]}')
print('\nStations by descending order counts:')
print('\033[1mStation      Counts\033[0m')
for ActiveStationsDesc in ActiveStationsDesc:
    print(ActiveStationsDesc[0], '  ', ActiveStationsDesc[1])

# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature of the most active station?
tempFreq = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.station == mostActiveStation).all()
print('\nLowest, highest and average temperatures:')
print(f'\033[1mLow:\033[0m {tempFreq[0][0]}')
print(f'\033[1mHigh:\033[0m {tempFreq[0][1]}')
print(f'\033[1mAvg:\033[0m {round(tempFreq[0][2],2)}')

# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
temp = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == mostActiveStation).filter(measurement.date >= lastYear).\
    group_by(measurement.date).all()
temp_df = pd.DataFrame(data=temp, columns=['date', 'tobs'])
temp_df = temp_df.set_index('date', drop=True)
plt.hist(temp_df['tobs'], bins=12)
plt.title(f'{mostActiveStationName} (most active)', fontsize=14)
plt.ylabel('Frequency', fontsize=11)
plt.xlabel('Temperature', fontsize=11)
plt.savefig('output/TempActiveStation_Last12m.png')
plt.legend(['TOBS'], loc='upper right')
plt.show()