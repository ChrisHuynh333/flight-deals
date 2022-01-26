from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_bootstrap import Bootstrap
from forms import RoundTripFlightSearchForm, OneWayTripFlightSearchForm
from flight_search import FlightSearch
import os


app = Flask(__name__)
# CSRF_TOKEN to use FlaskForms - stored as env variable
app.config["SECRET_KEY"] = os.environ['CSRF_TOKEN']
# Enable Bootstrap for WTForms
Bootstrap(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route(f"/<string:trip_type>_trip_search", methods=["GET", "POST"])
def trip_search(trip_type):
    if trip_type == "oneway":
        form = OneWayTripFlightSearchForm()
    else:
        form = RoundTripFlightSearchForm()
    if form.validate_on_submit():
        most_direct_flight = {}
        cheapest_flight = {}
        no_flights_message = None
        date_from = form.date_from.data
        adults = form.adults.data
        children = form.children.data
        infants = form.infants.data
        flight_type = trip_type
        currency = form.currency.data
        date_from_string = date_from.strftime("%d/%m/%Y")
        if trip_type == "round":
            date_to = form.date_to.data
            nights_stay = (date_to - date_from).days
            date_to_string = date_to.strftime("%d/%m/%Y")
        for x in range(0, 7):
            flight_search = FlightSearch()
            departure_city, departure_city_iata = flight_search.city_iata_search(form.departure_city.data)
            destination_city, destination_city_iata = flight_search.city_iata_search(form.destination_city.data)
            stopovers = x
            try:
                parameters = {
                    "fly_from": departure_city_iata,
                    "fly_to": destination_city_iata,
                    "date_from": date_from_string,
                    "date_to": date_from_string,
                    "adults": adults,
                    "children": children,
                    "infants": infants,
                    "flight_type": flight_type,
                    "max_sector_stopovers": stopovers,
                    "curr": currency
                }
                if trip_type == "round":
                    parameters["return_from"] = date_to_string
                    parameters["return_to"] = date_to_string
                    parameters["nights_in_dst_from"] = (nights_stay - 2)
                    parameters["nights_in_dst_to"] = (nights_stay + 2)

                flight = flight_search.flight_search(parameters, destination_city)
                if flight["price"] and not cheapest_flight:
                    cheapest_flight = flight
                elif flight["price"] and cheapest_flight:
                    if flight["price"] < cheapest_flight["price"]:
                        cheapest_flight = flight

                if flight["price"] and not most_direct_flight:
                    most_direct_flight = flight
            except IndexError:
                if x == 6:
                    no_flights_message = "Sorry, there are no available flights for this destination with these dates."
                else:
                    continue
        return render_template("flight_info.html", most_direct_flight=most_direct_flight, cheapest_flight=cheapest_flight, no_flights_message=no_flights_message,
                               trip_type="one_way")
    return render_template("one_way_trip_search.html", form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
