import requests
from datetime import datetime
import os

TEQUILA_API_KEY = os.environ['TEQUILA_API_KEY']
TEQUILA_URL = "https://tequila-api.kiwi.com"


class FlightSearch:
    def __init__(self):
        self.price = 0
        self.city_from = []
        self.city_to = []
        self.depart_date = []
        self.depart_time = []
        self.return_date = []
        self.return_time = []
        self.flight_time = []
        self.layover_time = []
        self.total_travel_time = []
        self.airline = []
        self.flight_num = []
        self.depart_return_split_count = 0


    def city_iata_search(self, city):
        location_endpoint = f"{TEQUILA_URL}/locations/query"
        headers = {
            "apikey": TEQUILA_API_KEY
        }
        if len(city) != 3:
            parameters = {
                "term": city,
                "location_types": "city"
            }
        else:
            parameters = {
                "term": city,
            }
        response = requests.get(url=location_endpoint, headers=headers, params=parameters)
        results = response.json()["locations"]
        if len(city) == 3:
            city_name = results[0]["city"]["name"]
            iata_code = results[0]["code"]
        else:
            city_name = city.title()
            iata_code = results[0]["code"]
        return city_name, iata_code

    def flight_search(self, flight_parameters, destination_city):
        headers = {
            "apikey": TEQUILA_API_KEY
        }
        parameters = flight_parameters
        response = requests.get(url=f"{TEQUILA_URL}/v2/search", headers=headers, params=parameters)
        flight = response.json()

        depart_date_and_time = []
        return_date_and_time = []
        departure_time_utc = []
        arrival_time_utc = []

        for x in range(0, len(flight["data"][0]["route"])):
            self.city_from.append(
                [flight["data"][0]["route"][x]["cityFrom"], flight["data"][0]["route"][x]["cityCodeFrom"]])
            self.city_to.append([flight["data"][0]["route"][x]["cityTo"], flight["data"][0]["route"][x]["cityCodeTo"]])
            depart_date_and_time.append(flight["data"][0]["route"][x]["local_departure"])
            return_date_and_time.append(flight["data"][0]["route"][x]["local_arrival"])
            departure_time_utc.append(flight["data"][0]["route"][x]["utc_departure"])
            arrival_time_utc.append(flight["data"][0]["route"][x]["utc_arrival"])
            self.flight_time.append(self.time_calc(flight["data"][0]["route"][x]["utc_departure"],
                                                   flight["data"][0]["route"][x]["utc_arrival"]))
            self.airline.append(flight["data"][0]["route"][x]["airline"])
            self.flight_num.append(flight["data"][0]["route"][x]["flight_no"])

        if flight_parameters["flight_type"] == "round":
            for count in range(0, len(self.city_from)):
                if self.city_from[count][0] == destination_city:
                    self.depart_return_split_count = count
                    break

        self.price = flight["data"][0]["price"]
        self.depart_date, self.depart_time = self.date_and_time_split(depart_date_and_time)
        self.return_date, self.return_time = self.date_and_time_split(return_date_and_time)

        if len(depart_date_and_time) > 1:
            self.layover_time = self.layover_time_calc(departure_time_utc, arrival_time_utc)

        self.total_travel_time = self.total_travel_time_calc(departure_time_utc, arrival_time_utc,
                                                             self.depart_return_split_count)

        flight_output = {
            "price": self.price,
            "city_from": self.city_from,
            "city_to": self.city_to,
            "depart_date": self.depart_date,
            "depart_time": self.depart_time,
            "return_date": self.return_date,
            "return_time": self.return_time,
            "flight_time": self.flight_time,
            "layover_time": self.layover_time,
            "total_travel_time": self.total_travel_time,
            "airline": self.airline,
            "flight_num": self.flight_num,
            "currency": flight_parameters["curr"]
        }
        if flight_parameters["flight_type"] == "round":
            flight_output["depart_return_split_count"] = self.depart_return_split_count
        return flight_output

    def time_calc(self, initial_time, secondary_time):
        initial_string = initial_time[0:10] + " " + initial_time[11:16]
        initial_datetime = datetime.strptime(initial_string, '%Y-%m-%d %H:%M')

        secondary_string = secondary_time[0:10] + " " + secondary_time[11:16]
        secondary_datetime = datetime.strptime(secondary_string, '%Y-%m-%d %H:%M')
        difference = secondary_datetime - initial_datetime
        difference = str(difference)
        difference = difference.split(":")
        difference_string = difference[0] + "h" + difference[1] + "m"
        return difference_string

    def total_travel_time_calc(self, departure_time, arrival_time, depart_return_split):
        total_time_travel = []
        depart_total_time = self.time_calc(departure_time[0], arrival_time[depart_return_split - 1])
        return_total_time = self.time_calc(departure_time[depart_return_split], arrival_time[-1])
        total_time_travel.append(depart_total_time)
        total_time_travel.append(return_total_time)
        return total_time_travel

    def layover_time_calc(self, depart_times, arrival_times):
        layover_times = []
        for count in range(0, (len(depart_times) - 1)):
            layover_times.append(self.time_calc(arrival_times[count], depart_times[count+1]))
        return layover_times

    def date_and_time_split(self, dates_and_times):
        dates = []
        times = []
        for date_time in dates_and_times:
            date_time_split = date_time.split("T")
            dates.append(date_time_split[0])
            time = date_time_split[1].split("Z")[0]
            hours_mins = time.split(":")
            times.append(f"{hours_mins[0]}:{hours_mins[1]}")
        return dates, times
