import os
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#-----------------------------------------------#
# Database  
#-----------------------------------------------#
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#-----------------------------------------------#
# Flask  
#-----------------------------------------------#
app = Flask(__name__)

#-----------------------------------------------#
# API Routes
#-----------------------------------------------#

@app.route("/")
def welcome():
    """List all Applicable API routes."""
    return (
        f"Available API Routes:<br/>"
        f"================= <br/>"
        f"<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"<br/>"
        f"Temperature(s) for an entire year: /api/v1.0/tobs<br/>"
        f"<br/>"
        f"Temperature stats from Start Date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"<br/>"
        f"Temperature stats from Start Date to End Date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    startdt = []
    for min,avg,max in queryresult:
        startdt_dict = {}
        startdt_dict["Min"] = min
        startdt_dict["Average"] = avg
        startdt_dict["Max"] = max
        startdt.append(startdt_dict)
    return jsonify(startdt)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    startstop = []
    for min,avg,max in queryresult:
        startstop_dict = {}
        startstop_dict["Min"] = min
        startstop_dict["Average"] = avg
        startstop_dict["Max"] = max
        startstop.append(startstop_dict)
    return jsonify(startstop)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date, Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)
    return jsonify(tobsall)
     

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)
    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)
    return jsonify(precipitation)

if __name__ == '__main__':
    app.run(debug=True)