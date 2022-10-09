from fff.schemas.baggage import BaggageList


def test_both_baggage_types():
    baggage_list = BaggageList(carry_on_bags=2, checked_bags=3)
    assert str(baggage_list) == "bfc=3;cfc=2"


def test_carry_on_baggage_only():
    baggage_list = BaggageList(carry_on_bags=1, checked_bags=0)
    assert str(baggage_list) == "cfc=1"


def test_checked_baggage_only():
    baggage_list = BaggageList(carry_on_bags=0, checked_bags=1)
    assert str(baggage_list) == "bfc=1"


def test_no_baggage():
    baggage_list = BaggageList(carry_on_bags=0, checked_bags=0)
    assert str(baggage_list) == ""


def test_default_baggage():
    baggage_list = BaggageList()
    assert str(baggage_list) == "cfc=1"
