# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/raeza/Desktop/GitHub1/sqlalchemy-challenge/Resources/hawaii.sqlite")


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
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"

    )


@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    """Return a list of precipitation data for 12 mths including date and prcp"""

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    twelve_months_ago = last_date - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).all()
    session.close()
    
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

    results = session.query(station.station).all()
    session.close()

    stations = [result[0] for result in results]

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    """Return a list of dates and temperature observations for the most active station"""

    active_stations = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc())

    most_active_station = active_stations.first()[0]

    most_recent_date_active = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        order_by(desc(measurement.date)).\
        first()

    most_recent_date = most_recent_date_active.date
    most_recent_tobs = most_recent_date_active.tobs

    one_year_prior = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station, measurement.date >= one_year_prior).\
        all()

    session.close()

    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


if __name__ == '__main__':
    app.run(debug=True)

 