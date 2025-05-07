# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################


# app.py

from flask import Flask, jsonify
import datetime as dt
import numpy as np

# SQLAlchemy dependencies
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Flask Setup
app = Flask(__name__)

#################################################
# Database Setup
#################################################
# Create engine to connect to the SQLite database (make sure the relative path is correct)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """
    List all available API routes.
    """
    return (
        "<h3>Available Routes:</h3>"
        "<br>/api/v1.0/precipitation"
        "<br>/api/v1.0/stations"
        "<br>/api/v1.0/tobs"
        "<br>/api/v1.0/&lt;start&gt; (e.g., /api/v1.0/2017-01-01)"
        "<br>/api/v1.0/&lt;start&gt;/&lt;end&gt; (e.g., /api/v1.0/2017-01-01/2017-01-07)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """
    Return a JSON dictionary where each key is a date and its value is the precipitation
    for the last 12 months of data.
    """
    session = Session(engine)

    # Get the most recent date in the dataset
    recent_date_str = session.query(Measurement.date)\
                             .order_by(Measurement.date.desc())\
                             .first()[0]
    recent_date = dt.datetime.strptime(recent_date_str, "%Y-%m-%d")
    # Calculate the date one year ago from the most recent date
    one_year_ago = recent_date - dt.timedelta(days=365)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp)\
                     .filter(Measurement.date >= one_year_ago_str)\
                     .all()
    session.close()

    # Convert the query results to a dictionary format {date: prcp}
    precip_dict = {date: prcp for date, prcp in results}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """
    Return a JSON list of all station IDs.
    """
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()
    session.close()

    # Unravel results into a one-dimensional list
    station_list = list(np.ravel(results))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """
    Return a JSON list of temperature observations (tobs) for the most active station
    for the last 12 months of data.
    """
    session = Session(engine)
    
    # Identify the most active station (based on observation counts)
    active_station = session.query(Measurement.station, func.count(Measurement.station))\
                            .group_by(Measurement.station)\
                            .order_by(func.count(Measurement.station).desc())\
                            .first()[0]

    # Get the most recent date in the dataset
    recent_date_str = session.query(Measurement.date)\
                             .order_by(Measurement.date.desc())\
                             .first()[0]
    recent_date = dt.datetime.strptime(recent_date_str, "%Y-%m-%d")
    one_year_ago = recent_date - dt.timedelta(days=365)
    one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")
    
    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == active_station)\
                     .filter(Measurement.date >= one_year_ago_str)\
                     .all()
    
    session.close()

    # Unravel results into a list
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """
    Return a JSON list of the minimum temperature, the average temperature,
    and the maximum temperature for all dates greater than or equal to the start date.
    """
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start)\
                     .all()
    session.close()

    # Unpack the results and format them in a dictionary
    temp_summary = list(np.ravel(results))
    return jsonify({
        "TMIN": temp_summary[0],
        "TAVG": temp_summary[1],
        "TMAX": temp_summary[2]
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """
    Return a JSON list of the minimum temperature, the average temperature,
    and the maximum temperature for dates between the start and end date inclusive.
    """
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start)\
                     .filter(Measurement.date <= end)\
                     .all()
    session.close()

    temp_summary = list(np.ravel(results))
    return jsonify({
        "TMIN": temp_summary[0],
        "TAVG": temp_summary[1],
        "TMAX": temp_summary[2]
    })

if __name__ == '__main__':
    app.run(debug=True)
