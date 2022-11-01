from fff.schemas.baggage import BaggageList
from fff.schemas.flight_duration import FlightDurationFilter
from fff.schemas.flight_search import FlightSearchParameters
from fff.schemas.layover import LayoverFilter
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxNumberOfStops, MaxStopFilter


def test_flight_search():
    baggage_list = BaggageList(carry_on_bags=2, checked_bags=1)
    max_stop_filter = MaxStopFilter(number_of_stops=MaxNumberOfStops.ONE)
    passenger_list = PassengerList(adults=2, children=2)
    layover_filter = LayoverFilter(min_time=0.1, max_time=24.5)
    flight_duration_filter = FlightDurationFilter(max_time=72.1)
    flight_search = FlightSearchParameters(
        passenger_list=passenger_list,
        baggage_list=baggage_list,
        max_stop_filter=max_stop_filter,
        layover_filter=layover_filter,
        flight_duration_filter=flight_duration_filter,
    )
    assert (
        str(flight_search)
        == "/2adults/children-11-11?fs=bfc=1;cfc=2;stops=-2;layoverdur=6-1470;legdur=-4326&sort=bestflight_a"
    )
