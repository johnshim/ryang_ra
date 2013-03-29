# front_month.py
# Given a date and contract, gets the front month contract for that date

import datetime as dt
from math import ceil

# temp vars
DATE = dt.date(2010,5,9)
CONTRACT = "ES"

CONTRACT_MONTHS = [3,6,9,12]

MONTH_CODES = {}
MONTH_CODES[1] = "H"
MONTH_CODES[2] = "H"
MONTH_CODES[3] = "H"
MONTH_CODES[4] = "M"
MONTH_CODES[5] = "M"
MONTH_CODES[6] = "M"
MONTH_CODES[7] = "U"
MONTH_CODES[8] = "U"
MONTH_CODES[9] = "U"
MONTH_CODES[10] = "Z"
MONTH_CODES[11] = "Z"
MONTH_CODES[12] = "Z"

def tests():
    """
    d = dt.date(2010,6,1)
    print get_expiration_date(d)

    d = dt.date(2011,6,10)
    print get_expiration_date(d)
    """

    fail = 0

    d = dt.date(2013,3,7)
    if get_front_month(d) != "ESH3":
        print "FAILED #1"
        fail += 1

    d = dt.date(2013,3,14)
    if get_front_month(d) != "ESM3":
        print "FAILED #2"
        fail += 1

    d = dt.date(2013,3,22)
    if get_front_month(d) != "ESM3":
        print "FAILED #3"
        fail += 1

    d = dt.date(2012,2,20)
    if get_front_month(d) != "ESH2":
        print "FAILED #4"
        fail += 1

    if not fail:
        print "ALL TESTS PASSED"

# Gets 2nd thursday in month of date
def get_expiration_date(date):

    first_day = date.replace(day=1)
    week_day = first_day.weekday()

    THURSDAY = 3

    if week_day < THURSDAY:
        first_thursday = date.replace(day = 1 + (THURSDAY - week_day))
    elif week_day > THURSDAY:
        first_thursday = date.replace(day = 1 + THURSDAY + (7 - week_day))
    else:
        first_thursday = first_day
        
    second_thursday = first_thursday.replace(day = (first_thursday.day + 7))

    return second_thursday
    
def get_front_month(date):
    
    # Grab month + year
    month = date.month
    year = date.year
    day = date.day

    # Check if a month with an expiring contract
    if month in CONTRACT_MONTHS:

        # Check if before expiration on current month
        # Roll-over occurs on second Thursday of each month

        second_thursday = get_expiration_date(date)

        if day < second_thursday.day:
            curr = CONTRACT + str(MONTH_CODES[second_thursday.month]) + str(second_thursday.year)[-1]
            return curr
        else:
            try:
                curr = CONTRACT + str(MONTH_CODES[second_thursday.month + 1]) + str(second_thursday.year)[-1]
            except KeyError: # December - rollover to next year
                curr = CONTRACT + str(MONTH_CODES[1]) + str(second_thursday.year + 1)[-1]   
            return curr

    elif month not in CONTRACT_MONTHS:
        # get next month
        next_month = ceil(float(month) / 3) * 3
        curr = CONTRACT + str(MONTH_CODES[next_month]) + str(year)[-1]
        return curr

if __name__ == '__main__':
    tests()

                              


