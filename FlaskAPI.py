import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
# Establish DBAPI connection
engine = create_engine('sqlite:///./Resources/hawaii.sqlite')
base = automap_base()
base.prepare(engine, reflect = True)
station = base.classes.station
measurement = base.classes.measurement
session = Session(engine)
app = Flask(__name__)
# List all routes that are available
@app.route('/')
def home():
    return (
        f'Available Routes:<br/>'
        f'<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'- Last year dates and percipitation observations<br/>'
        f'<br/>'
        f'/api/v1.0/stations<br/>'
        f'- Stations from the dataset<br/>'
        f'<br/>'
        f'/api/v1.0/tobs<br/>'
        f'- Previous year temperature observations (tobs)<br/>'
        f'<br/>'
        f'/api/v1.0/start<br/>'
        f'- List of the Min temperature, the Avg temperature, and the Max temperature for given start or start-end range<br/>'
        f'<br/>'
        f'/api/v1.0/start/end<br/>'
        f'- Min temperature, the Avg temperature, and the Max temperature for given start or start-end range<br/>'
    )
# Return the query results as a dictionary, with date as the key and prcp as the value.
@app.route('/api/v1.0/precipitation')
def prcp():
    last_year = dt.date(2017, 8, 24) - dt.timedelta(days=365)
    rain = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > last_year).\
        order_by(measurement.date).all()
    prcp_totals = []
    for result in rain:
        row = {}
        row['date'] = rain[0]
        row['prcp'] = rain[1]
        prcp_totals.append(row)
    return jsonify(prcp_totals)
# Return a JSON dictionary of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    stations_query = session.query(station.name, station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
   # last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 24) - dt.timedelta(days=365)
    temperature = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > last_year).\
        order_by(measurement.date).all()
    tobs_yr = []
    for result in temperature:
        row = {}
        row['date'] = temperature[0]
        row['tobs'] = temperature[1]
        tobs_yr.append(row)
    return jsonify(tobs_yr)
# Return a JSON list of the minimum, average, and max temperature after a given start date.
@app.route('/api/v1.0/<start>')
def start(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)
# Return a JSON list of the minimum, average, and max temperature between a given start-end range (inclusive).
@app.route('/api/v1.0/<start>/<end>')
def end(start, end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)
if __name__ == '__main__':
    app.run(host ='127.0.0.1', port ='5000')


