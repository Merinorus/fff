from fff.schemas.baggage import BaggageList
from fff.schemas.flight_search import FlightSearchParameters
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxNumberOfStops, MaxStopFilter


def test_flight_search():
    baggage_list = BaggageList(carry_on_bags=2, checked_bags=1)
    max_stop_filter = MaxStopFilter(number_of_stops=MaxNumberOfStops.ONE)
    passenger_list = PassengerList(adults=2, children=2)
    flight_search = FlightSearchParameters(
        passenger_list=passenger_list,
        baggage_list=baggage_list,
        max_stop_filter=max_stop_filter,
    )
    assert (
        str(flight_search)
        == "/2adults/children-11-11?fs=bfc=1;cfc=2;stops=-2&sort=bestflight_a"
    )
