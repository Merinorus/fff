from fff.schemas.passenger import PassengerList


def test_passenger_url_part():
    passenger_list = PassengerList(
        adults=8,
        children=4,
        infant_on_lap=2,
        seniors=6,
        students=7,
        toddlers_in_seat=3,
        youths=5,
    )
    assert (
        str(passenger_list)
        == "/8adults/6seniors/7students/children-1S-1S-1S-1L-1L-11-11-11-11-17-17-17-17-17"
    )
