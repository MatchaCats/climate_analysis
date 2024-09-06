# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session =  Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"You are using the Hawaii Climate Analysis API<br/>"
        f"Route Options:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temperature/start<br/>"
        f"/api/v1.0/temperature/start/end<br/>"
        f"<p>The 'start' and 'end' dates should be in this format: MMDDYYYY.</p>",
        200,  # Status code indicating success
        {"Content-Type": "text/html"}  # Headers specifying content type
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    
    session.close()
    precipitation = { date: prcp for date, prcp in precipitation}

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    temps = list(np.ravel(results))

    return jsonify({ "tobs": temps })

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug = True)

