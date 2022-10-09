from pydantic import BaseModel

from fff.schemas.baggage import BaggageList
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxStopFilter

# ?fs=cfc=1;stops=-1;bfc=2&sort=bestflight_a


class FlightSearchParameters(BaseModel):

    passenger_list: PassengerList
    baggage_list: BaggageList
    max_stop_filter: MaxStopFilter

    def __str__(self) -> str:
        """Return the flight search parameters as a string to be added at the end of the URL.

        Returns:
            str: the flight search parameters
        """

        result = str(self.passenger_list)

        baggage_list_str = str(self.baggage_list)
        max_stop_filter_str = str(self.max_stop_filter)
        if baggage_list_str or max_stop_filter_str:
            result = (
                result
                + "?fs="
                + ";".join(filter(None, [baggage_list_str, max_stop_filter_str]))
            )

        result = result + "&sort=bestflight_a"

        return result
