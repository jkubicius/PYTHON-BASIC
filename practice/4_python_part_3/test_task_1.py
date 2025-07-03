"""
Write tests for calculate_days function
Note that all tests should pass regardless of the day test was run
Tip: for mocking datetime.now() use https://pypi.org/project/pytest-freezegun/
"""

from task_1 import calculate_days, WrongFormatException
import pytest


@pytest.mark.freeze_time("2021-10-06")
def test_calculate_days_wrong_format():
    with pytest.raises(WrongFormatException, match="Wrong format of the date."):
        calculate_days('10-07-2021')


@pytest.mark.freeze_time("2021-10-06")
def test_calculate_days_past():
    assert calculate_days('2021-10-05') == 1


@pytest.mark.freeze_time("2021-10-06")
def test_calculate_days_future():
    assert calculate_days('2021-10-07') == -1