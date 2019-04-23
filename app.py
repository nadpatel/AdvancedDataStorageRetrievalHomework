
#################################################
# import Flask
#################################################
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurements

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Define homepage and routes 
#################################################

@app.route("/")
def home():
    print("Climate Query - Hawaii")
    return (
        f"Welcome to my 'Home' page that will help you plan your next trip to Hawaii (based on data between 2010-2017)"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/station<br/>"
        f"- List of station names (collected the data)<br/>"
        f"<br/>"
        f"/api/v1.0/trip1<br/>"
        f"- List of MIN/MAX/AVG temperatures when given start for all dates greater than or equal to start date <br/>"
        f"<br/>"
        f"/api/v1.0/trip2<br/>"
        f"- List of MIN/MAX/AVG temperatures when given start and end dates for all dates in between inclusive of the start and end dates <br/>"
    )  

#################################################
#Precipitation Route
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Query  database for percipitations by date (as key)
    precipitation = session.query(Measurement.prcp).group_by(Measurement.date).all()
    print("Server received request for 'precipitation' page...")

# Create a list of dicts with `date` and `prcp` as the keys and values
    precipitation_totals = []
    for result in precipitation:
        result["date"] = precipitation[0]
        result["prcp"] = precipitation[1]
        precipitation_totals.append(result)

    #Jsonify 
    return jsonify(precipitation_totals)

#################################################
# Station Route
#################################################

@app.route("/api/v1.0/station")
def station():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

#################################################
#Temperature route
#################################################
@app.route("/api/v1.0/tobs")
def temperature():
    """Returns a dates and temperatures froma year before the last data point"""
    #Query for the dates and temperature observations from a year from the last data point.

    last_temp= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = last_temp - dt.timedelta(days=365)
    dates_and_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.date<=last_temp).all()
   
    print("Here are all the temperature observations from the prior year")
   
    for result in dates_and_temps:
        result["date"] = dates_and_temps[0]
        result["tobs"] = dates_and_temps[1]
        dates_and_temps.append(result)

    return jsonify(dates_and_temps)

#################################################
# Vacation start and end date route
#################################################

#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)