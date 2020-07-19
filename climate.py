import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"Welcome to our home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (Enter a start date to view temperature observations since that time.)<br/>"
        f"/api/v1.0/<start>/<end> (Enter start and end dates to view temperature observations during that period.)"
    )
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    precip_data = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    precip_output = []
    for date, precipitation in precip_data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = precipitation
        precip_output.append(precip_dict)    
    
    return jsonify(precip_output)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    same_station = session.query(Station.name).filter(Measurement.station == Station.station).distinct().all()
    session.close()
    
    station_output = []
    for name in same_station:
        station_dict = {}
        station_dict["name"] = name
        station_output.append(station_dict)    
    
    return jsonify(station_output)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close()

    for date in latest_date:
        latest_date_dict = {}
        latest_date_dict["date"] = date

    latest_date_fixed = datetime.strptime(latest_date_dict.get("date"), "%Y-%m-%d")
    beginning_date = latest_date_fixed - dt.timedelta(days = 365)

    session = Session(engine)
    most_active_station = session.query(Measurement.station).\
        filter(Measurement.date > beginning_date).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).\
        first()
    session.close()
    
    for name in most_active_station:
        active_dict = {}
        active_dict["name"] = name
    
    session = Session(engine)
    dates_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_dict.get("name")).\
        filter(Measurement.date > beginning_date).\
        order_by(desc(Measurement.date)).all()
    session.close()
    
    dates_temps_output = []
    for date, temperature in dates_temps:
        dates_temps_dict = {}
        dates_temps_dict["date"] = date
        dates_temps_dict["temperature"] = temperature
        dates_temps_output.append(dates_temps_dict)
    
    return jsonify(dates_temps_output)


@app.route("/api/v1.0/<start>")
def start(start):
    
    str_start = str(start)
    
    session = Session(engine)
    start_temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= str_start).all()
    session.close()
                                
    start_temps_data = []
    for min, max, avg in start_temps:
        start_temps_dict = {}
        start_temps_dict["Minimum Temperature"] = min
        start_temps_dict["Maximum Temperature"] = max
        start_temps_dict["Average Temperature"] = avg
        start_temps_data.append(start_temps_dict)

    return jsonify(start_temps_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)
    start_end_temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    
    start_end_temps_data = []
    for min, max, avg in start_end_temps:
        start_end_temps_dict = {}
        start_end_temps_dict["Minimum Temperature"] = min
        start_end_temps_dict["Maximum Temperature"] = max
        start_end_temps_dict["Average Temperature"] = avg
        start_end_temps_data.append(start_end_temps_dict)
    
    return jsonify(start_end_temps_data)


if __name__ == "__main__":
    app.run(debug=False)