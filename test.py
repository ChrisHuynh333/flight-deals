from datetime import datetime

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

# cheapest_flight_return_date_test = datetime.strptime(cheapest_flight["return_date"][-1], "%Y-%m-%d").date()
            # most_direct_flight_return_date_test = datetime.strptime(most_direct_flight["return_date"][-1], "%Y-%m-%d").date()
            # print(cheapest_flight_return_date_test, most_direct_flight_return_date_test, date_to_final)
            #
            # if cheapest_flight_return_date_test == date_to_final:
            #     cheapest_arrival_date = True
            # if most_direct_flight_return_date_test == date_to_final:
            #     cheapest_arrival_date = True
            #
            # if cheapest_flight_return_date_test > date_to_final and most_direct_flight_return_date_test > date_to_final:
            #     most_direct_flight.clear()
            #     cheapest_flight.clear()
            #     date_to = date_to - timedelta(days=1)
            #     attempt_count += 1
            # elif cheapest_flight_return_date_test < date_to_final and most_direct_flight_return_date_test < date_to_final:
            #     most_direct_flight.clear()
            #     cheapest_flight.clear()
            #     date_to = date_to + timedelta(days=1)
            #     attempt_count += 1
            # elif cheapest_flight_return_date_test > date_to_final:
            #     cheapest_flight.clear()
            #     date_to = date_to - timedelta(days=1)
            #     attempt_count += 1
            # elif cheapest_flight_return_date_test < date_to_final:
            #     cheapest_flight.clear()
            #     date_to = date_to + timedelta(days=1)
            #     attempt_count += 1
            # elif most_direct_flight_return_date_test > date_to_final:
            #     most_direct_flight.clear()
            #     date_to = date_to - timedelta(days=1)
            #     attempt_count += 1
            # else:
            #     most_direct_flight.clear()
            #     date_to = date_to + timedelta(days=1)
            #     attempt_count += 1
            # if attempt_count == 5:
            #     if cheapest_flight_return_date_test == date_to_final and most_direct_flight_return_date_test != date_to_final:
            #         most_direct_flight.clear()
            #     if cheapest_flight_return_date_test != date_to_final and most_direct_flight_return_date_test == date_to_final:
            #         cheapest_flight.clear()
            #     break