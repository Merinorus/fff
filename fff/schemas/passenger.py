from pydantic import BaseModel, NonNegativeInt


class PassengerList(BaseModel):

    adults: NonNegativeInt = 0
    students: NonNegativeInt = 0
    seniors: NonNegativeInt = 0
    youths: NonNegativeInt = 0
    children: NonNegativeInt = 0
    toddlers_in_seat: NonNegativeInt = 0
    infant_on_lap: NonNegativeInt = 0

    def __str__(self) -> str:
        """Return the passenger list as a string to be added to the website URL.

        Returns:
            str: the passenger list
        """
        result = ""
        if self.adults:
            result = result + f"/{self.adults}adults"
        if self.seniors:
            result = result + f"/{self.seniors}seniors"
        if self.students:
            result = result + f"/{self.students}students"
        if self.youths or self.children or self.toddlers_in_seat or self.infant_on_lap:
            children_str = "/children"
            for i in range(self.toddlers_in_seat):
                children_str = children_str + "-1S"
            for i in range(self.infant_on_lap):
                children_str = children_str + "-1L"
            for i in range(self.children):
                children_str = children_str + "-11"
            for i in range(self.youths):
                children_str = children_str + "-17"
            result = result + children_str
        return result
