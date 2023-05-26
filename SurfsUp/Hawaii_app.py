# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify, request
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()
# reflect the tables


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_end<br/>"
    )



@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    """Return a list of precipitation data for 12 mths including date and prcp"""

#Retrieve the last date in 'measurement'and calculate the date that is 12 months prior to the last date. 

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    twelve_months_ago = last_date - dt.timedelta(days=365)

#Query precipitation data for the last 12 months.
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).all()
    session.close()

# Create a dictionary showing the last 12 months of precipitation analysis. 
    prcp_date = []
    for date, prcp in results:
        rain_dict = {}
        rain_dict['date'] = date       
        rain_dict['prcp'] = prcp
        prcp_date.append(rain_dict)

    return jsonify(prcp_date)


@app.route('/api/v1.0/stations')
def station_names():

    session = Session(engine)

    """Return a list of stations"""

#Query and retrieve list of stations. 

    results = session.query(station.station).all()
    session.close()

    stations = [result[0] for result in results]

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    """Return a list of dates and temperature observations for the most active station"""

#Query to see which stations are most active. 
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc())
#Query the last 12 months of temperature observation data for the most active station. 
    most_active_station = active_stations.first()[0]

    most_recent_date_active = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        order_by(desc(measurement.date)).\
        first()

    most_recent_date = most_recent_date_active.date


    one_year_prior = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
#Query to retrive the data. 
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station, measurement.date >= one_year_prior).\
        all()

    session.close()

#Create a dictionary for temperature observations for the previous year. 
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


@app.route('/api/v1.0/<start>')
def temperature_stats_start(start):
    session = Session(engine)

#Query to retrive the data for a specified start date. 

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        all()

    session.close()

#Create a dictionary for minimum, average, and maximum temperature. 
    stats_dict = {}
    stats_dict['TMIN'] = results[0][0]
    stats_dict['TAVG'] = results[0][1]
    stats_dict['TMAX'] = results[0][2]

    return jsonify(stats_dict)



@app.route('/api/v1.0/<start>/<end>')
def temperature_stats_start_end(start, end):
    session = Session(engine)

#Query to retrive the data for a specified start and end date. 
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start, measurement.date <= end).\
        all()

    session.close()


#Create a dictionary for minimum, average, and maximum temperature. 
    stats_dict = {}
    stats_dict['TMIN'] = results[0][0]
    stats_dict['TAVG'] = results[0][1]
    stats_dict['TMAX'] = results[0][2]

    return jsonify(stats_dict)


if __name__ == '__main__':
    app.run(debug=True)


 