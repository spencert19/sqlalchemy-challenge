# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
    f"Honolulu, Hawaii climate API</br>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start_date/<start_date><br/>"
    f"/api/v1.0/start_date/<start_date>/end_date/<end_date><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_list.append(prcp_dict)

#Return the JSON representation of your dictionary.
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    station_data = session.query(*sel).all()

    stations = []
    for station,name,lat,lon,el in station_data:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

#Return a JSON list of stations from the dataset.
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():

#Query the dates and temperature observations of the most-active station for the previous year of data.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last_year).all()

    tob_numbers = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tob_numbers.append(tobs_dict)

#Return a JSON list of temperature observations for the previous year.
    return jsonify(tob_numbers) 


@app.route("/api/v1.0/start_date/<start_date>")
def temp_start(start):

#Return a JSON list of the minimum temperature, the average temperature, 
#and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    temperature = []
    for min_temp, avg_temp, max_temp in start_query:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temperature.append(temps_dict)


@app.route("/api/v1.0/start_date/<start_date>/end_date/<end_date>")
def temp_start_end(start, end):

#Return a JSON list of the minimum temperature, the average temperature, 
#and the maximum temperature for a specified start or start-end range.
#For a specified start date and end date, calculate TMIN, TAVG, 
#and TMAX for the dates from the start date to the end date, inclusive.
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

