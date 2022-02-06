from flask import Flask, render_template, url_for, redirect, flash, request
from flask_bootstrap import Bootstrap
from forms import FlightSearchForm
from flight_search import FlightSearch
import os
from datetime import datetime, timedelta


app = Flask(__name__)
# CSRF_TOKEN to use FlaskForms - stored as env variable
app.config["SECRET_KEY"] = os.environ['CSRF_TOKEN']
# Enable Bootstrap for WTForms
Bootstrap(app)

# Route for home page
@app.route("/")
def home():
    return render_template("index.html")

# Route for trip_search. trip_type will either be "oneway" or "round" strings, based on the search method the
# user chooses on the home page.
@app.route(f"/<string:trip_type>_trip_search", methods=["GET", "POST"])
def trip_search(trip_type):
    # form imported from forms.py
    form = FlightSearchForm()
    # User clicks and begins the flight search and we receive a POST request.
    # We will start with most_direct_flight and cheapest_flight as empty dics and fill them with the data to be
    # sent to the Tequila API to retrieve the flight data.
    # error_message will begin as None and be assigned data if an error message is needed. This will pop up on the
    # search results page if a flight cannot be found for the user's search criteria.
    if request.method == "POST":
        most_direct_flight = {}
        cheapest_flight = {}
        error_message = None
        date_from = form.date_from.data
        # date_to will initially be assigned None so we've at least declared the variable, as it's needed for future
        # if statements below. However, date_to is only needed for round trip searches, as a one-way trip search will
        # not need a second date (only requires departure date).
        date_to = None
        adults = form.adults.data
        children = form.children.data
        infants = form.infants.data
        flight_type = trip_type
        currency = form.currency.data
        # We receive date_from initially as a datetime object formatted %Y/%m/%d. The Tequila API requires the date
        # to be passed as a string, with the format %d/%m/%Y, so we create a new string, and reformat it for the API.
        date_from_string = date_from.strftime("%d/%m/%Y")

        # If the user is wanting to do a round trip search, the API will require these additional data fields:
        # date_to is the date for the return flight
        # nights_stay is required for round_trip searches by the Tequila API. We will get the delta between the
        # date_to and date_from datetime variables.
        # date_to_string, like date_from_string, will convert the datetime to the required string with the proper format
        # for the API.
        if trip_type == "round":
            date_to = form.date_to.data
            nights_stay = (date_to - date_from).days
            date_to_string = date_to.strftime("%d/%m/%Y")

        # The following if statements are to catch errors caused by the user inputs.

        # We retrieve today and tomorrow's dates for the date inputs and search criteria for the flight dates.
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)

        # We will allow the user to begin searches starting from tomorrow/next day, since users will rarely search for
        # flights on same day. if date_from is before tomorrow's date, the search will not go through.
        if tomorrow > date_from:
            # We add this if statement for round flight searches where date_to is True, and check to make sure date_to's
            # date is not before tomorrow's date as well.
            if date_to:
                if tomorrow > date_to:
                    flash("Your travel dates cannot be before tomorrow's date.")
                    return redirect(url_for("trip_search", trip_type=trip_type))
            # else statement to capture one way flight searches
            else:
                flash("Your travel dates cannot be before tomorrow's date.")
                return redirect(url_for("trip_search", trip_type=trip_type))

        # For round trip flight searches, the return date cannot be before the departure date.
        if trip_type == "round":
            if date_from > date_to:
                flash("You may not have a return date earlier than your departure date.")
                return redirect(url_for("trip_search", trip_type=trip_type))

        # The Tequila API will only allow searches to a max of 9 passengers.
        if int(adults) + int(children) + int(infants) > 9:
            flash("You may only search for flights with a total of 9 passengers.")
            return redirect(url_for("trip_search", trip_type=trip_type))

        # We initially will make a call to the Tequila API to retrieve the correct city/airport from the user's input.
        # Because the call is within the for loop below, and we do not need to repeatedly make the call once we've
        # retrieved the information the first time, once we get the city information, we will turn city_code_depart and
        # city_code_destination to True, and no longer make the API calls specifically for city data.
        # This will speed up the application and flight searches.
        city_code_depart = False
        city_code_destination = False
        
        # If we find a most_direct_flight, found_most_direct_flight will be turned True, and we will set x to the
        # highest iteration futher below as we are only then interested in the cheapest flight, so we'll max out
        # the number of stopovers allowed, and the first flight returned will be the cheapest available.
        found_most_direct_flight = False

        # We will do 6 flight searches (range(0, 6)). The count iteration pertains to the number of max
        # stopovers/layovers we will pass to the Tequila API. We care about increasing the number of stops because
        # we are returning the cheapest flight possible to the user, these flight routes generally have a larger number
        # of stopovers. I've found the largest number of stopovers for a flight to some of the most remote regions is
        # usually 4 (for a single flight direction), so I've gone up to 5 stopovers just to be more inclusive in case
        # there is a change for a flight with 5 stopovers.
        for x in range(0, 6):
            # We will use OOP and create a new flight_search object for each flight. This allows us to re-initialize all
            # the flight data to empty/None and retrieve new data to compare to our existing data (ie: if the new flight
            # is cheaper than the currently stored one, we will replace the old flight data with the new flight data).
            flight_search = FlightSearch()
            # As mentioned, we will increase the stopovers allowed based on the loop iteration.
            stopovers = x
            # As mentioned, because we only need to retrieve the city data once, we initially set a False variable,
            # and will turn it True once we get the desired city data.
            # For both departure and destination city, we will have a try/except block. We will try to retrieve the
            # city data based on the user's input. Although the Tequila API city/airport search is quite robust with
            # spelling errors, this try/except will catch inputs will large errors/inaccuracies. Our algorithm also only
            # searches based on cities, so if the user inputs a province/state or country, the program would normally
            # crash. With the try/except, we will instead return an error and give the user an opportunity to fix their
            # input.
            if not city_code_depart:
                try:
                    departure_city, departure_city_iata = flight_search.city_iata_search(form.departure_city.data)
                    city_code_depart = True
                except KeyError:
                    flash("The departure city you entered could not be found. Please ensure the spelling of the "
                          "city or the three letter airport IATA code is correct.")
                    return redirect(url_for("trip_search", trip_type=trip_type))
            if not city_code_destination:
                try:
                    destination_city, destination_city_iata = flight_search.city_iata_search(form.destination_city.data)
                    city_code_destination = True
                except KeyError:
                    flash("The destination city you entered could not be found. Please ensure the spelling of the "
                          "city or the three letter airport IATA code is correct.")
                    return redirect(url_for("trip_search", trip_type=trip_type))

            # Once we get the the correct city/airport data from the Tequila API based on the user's input, we will
            # start the flight search through the Tequila API. The search is within a try/except block in case the API
            # does not return a flight based on the user's parameters.

            # The search algorithm and data is done via OOP, see flight_search.py for the details on how the search
            # functions.

            # These are the parameters we will pass to the Tequila API.
            # fly_from = the departure city airport IATA code
            # fly_to = destination city airport IATA code
            # date_from and date_to: Tequila will search the departure date based on a range of dates (date_from to
                # date_to), however, we are only interested in flights with a single departure date (based on the user
                # input). Because the API requires both of these parameters, we will pass the same date for both.
            # adults, children, infants = number of each type of passenger
            # flight_type = "oneway" or "round"
            # max_sector_stopovers = The maximum number of stopovers allowed per flight route search
            # curr = the currency for the flight_search cost. We allow CAD, USD, and EUR.
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

                # If we are doing a round trip search, we require these additional parameters to be added on
                # return_from and return_to:
                #  like explained above for date_from and date_to but for the return date.

                # nights_in_dst_from and nights_in_dst_to:
                #   For round trip searches, Tequila API requires these parameters. It's the range of dates the
                #   traveller is willing to stay before their return flight. Because we assume based on their depart
                #   and return dates they gave, that that would intuitively be the number of nights they would like
                #   to stay. We +/- 2 nights to add a little more robustness to the flight search. This is mainly
                #   for overseas flights as cheaper flights will generally require an overnight stay at a stopover.
                if trip_type == "round":
                    parameters["return_from"] = date_to_string
                    parameters["return_to"] = date_to_string
                    parameters["nights_in_dst_from"] = (nights_stay - 2)
                    parameters["nights_in_dst_to"] = (nights_stay + 2)

                # We pass the parameters and destination_city to the flight_search method in flight_search.py
                # We pass destination_city separately since it's used to determine the round flight
                # departure/return "split". Because the flights are returned as a list of flights, it is not obvious
                # where the 'split' occurs. Therefore, we use the destination city in our algorithm to determine this.)
                flight = flight_search.flight_search(parameters, destination_city)

                # First, we work to find the cheapest_flight. Because we are looking at up to 5 flight routes (each with
                # increasing number of stopovers), we will check each subsequent flight's price to see if it's cheaper
                # than what we've previously recorded as the cheapest flight.

                # The first if statement will assign the first flight as the cheapest_flight
                if flight["price"] and not cheapest_flight:
                    cheapest_flight = flight

                # Each subsequent flight_search will compare its price to the price we have currently have assigned to
                # cheapest_flight. If the new flight price is lower, we will assign the new flight to cheapest_flight.
                elif flight["price"] and cheapest_flight:
                    if flight["price"] < cheapest_flight["price"]:
                        cheapest_flight = flight

                # Because each subsequent flight_search will increase the possible number of stopovers. We're only
                # interested in the first flight_search that returns a True result for the most_direct_flight.
                # This way, the user will be returned both the most_direct_flight and cheapest_flight to compare.
                if flight["price"] and not most_direct_flight:
                    most_direct_flight = flight
                    found_most_direct_flight = True
                
                if most_direct_flight and found_most_direct_flight:
                    x = 4
            # As mentioned previously, I found roughly 4 stopovers to be the max number required to fly anywhere in the
            # world from location. Therefore, allowed the search algorithm to go up to 5 stopovers. If a flight was not
            # found and returned after this many searches, it's most likely that a flight does not currently exist for
            # the user's input parameters. The most likely scenario is the user's search dates are too far out into the
            # future, and flights for those departure/destination cities have not yet been established.

            # The if/else statement will finally record something when stopovers/x == 5. Otherwise, the except block
            # may still catch errors when flights were not found, but the else statement allows the for loop to
            # continue. For example, when x == 0, aka trying to find flights with 0 stopovers, this is most likely not
            # possible for overseas flights if you are not flying out from main international hubs, so we will enter
            # the except block, but because x != 5, we will continue from the else statement, and increase x by 1 in
            # the for loop.

            except IndexError:
                if x == 5:
                    error_message = "Sorry, there are no available flights for this destination with these dates."
                else:
                    continue

        return render_template("flight_info.html", most_direct_flight=most_direct_flight, cheapest_flight=cheapest_flight, error_message=error_message,
                               trip_type=trip_type)
    return render_template("trip_search.html", form=form, trip_type=trip_type)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
