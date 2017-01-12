from datetime import datetime
import datetime
from datetime import date



# Check if the int given year is a leap year
# return true if leap year or false otherwise
def is_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


THIRTY_DAYS_MONTHS = [4, 6, 9, 11]
THIRTYONE_DAYS_MONTHS = [1, 3, 5, 7, 8, 10, 12]

# Inputs -> month, year Booth integers
# Return the number of days of the given month
def get_month_days(month, year):
    if month in THIRTY_DAYS_MONTHS:   # April, June, September, November
        return 30
    elif month in THIRTYONE_DAYS_MONTHS:   # January, March, May, July, August, October, December
        return 31
    else:   # February
        if is_leap_year(year):
            return 29
        else:
            return 28

# Checks the month of the given date
# Selects the number of days it needs to add one month
# return the date with one month added
def add_month(date):
    current_month_days = get_month_days(date.month, date.year)
    next_month_days = get_month_days(date.month + 1, date.year)

    delta = datetime.timedelta(days=current_month_days)
    if date.day > next_month_days:
        delta = delta - datetime.timedelta(days=(date.day - next_month_days) - 1)

    return date + delta


def add_year(date):
    if is_leap_year(date.year):
        delta = datetime.timedelta(days=366)
    else:
        delta = datetime.timedelta(days=365)

    return date + delta


# Validates if the expected_value is equal to the given value
def test_equal(expected_value, value):
    if expected_value == value:
        print("Test Passed")
        return True
    print( "Test Failed : " + str(expected_value) + " is not equal to " +str(value))
    return False

def calculated_basis_date(basis_id,start_date):
    based_date = date.today()
    # timedelta(days=subscription_validity_days)
    if basis_id == 'ANNUAL':
        based_date = add_year(start_date)
    elif basis_id == 'QTLY':
        based_date = start_date + datetime.timedelta(days=90)
    elif basis_id == 'MNTHLY':
        based_date = add_month(start_date)
    elif basis_id == 'WEEKLY':
        based_date = start_date + datetime.timedelta(days=7)
    elif basis_id == 'DAILY':
        based_date = start_date + datetime.timedelta(days=1)
    elif basis_id == 'ONCE':
        based_date = start_date
    elif basis_id == 'SEMIAN':
        based_date = start_date + datetime.timedelta(days=180)
    elif basis_id == 'BIAN':
        based_date = start_date + datetime.timedelta(days=180)
    elif basis_id == 'CUSTOM':
        based_date = add_year(start_date)

    return based_date
