import os
import json
from datetime import datetime

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import *
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "my_secret_key"

#raise an error for undefined Jinja variables
app.jinja_env.undefined = StrictUndefined

# Run 'source secrets.sh in terminal'
# Pass Google JS API key to render_template
gkey = os.environ['GOOGLE_API_KEY']
PORT = int(os.environ.get("PORT", 5000))


@app.route('/')
def homepage():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/reservations')
def reservations():
    """Reservations Page"""

    #query all existing reservations
    reservations = Reservation.get_all_reservations()

    #query all unique dates
    dates = Reservation.get_all_dates()

    # return homepage with reservations and secret google api key
    return render_template("reservations.html", reservations=reservations, dates=dates, gkey=gkey)


@app.route('/restaurant_list')
def restaurant_list():
    """List of all Restaurants."""

    #query all restaurants in database
    restaurants = Restaurant.get_all_restaurants()

    # return list of restaurants
    return render_template("restaurant_list.html", restaurants=restaurants)


@app.route('/resto_markers', methods=['POST'])
def resto_markers():
    """Provide restaurant details for homepage map in JSON format"""

    #query unique dates in reservation database
    dates = Reservation.get_all_dates()

    #parse form inputs for query
    date = request.form.get("date")
    resto = request.form.get("resto")
    people = request.form.get("people")

    if date == "":
        date = dates
    else:
        date = [datetime.strptime('2016 ' + date, '%Y %b %d, %a')]

    if resto == "":
        resto = '%'
    else:
        resto = "%"+resto+"%"

    if people == "":
        people = [2, 4, 6]
    else:
        people = [int(people)]

    resto_markers = db.session.query(Reservation, Opentable, Restaurant).filter(Reservation.time != None, Reservation.date.in_(date), Restaurant.name.ilike(resto), Reservation.people.in_(people)).join(Opentable).join(Restaurant).all()

    resto_dict = {}
    counter = 1
    for resto in resto_markers:
        resto_dict[counter] = {'name': resto[2].name, 'lat': resto[2].lat, 'lng': resto[2].lng}
        counter += 1

    resto_json = json.dumps(resto_dict)
    return resto_json


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    connect_to_db(app)
    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0", port=PORT)
