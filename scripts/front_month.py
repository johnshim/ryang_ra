# front_month.py
# Given a date and contract, gets the CME-style front month contract for that date
# Note that this is calculated for contracts that deliver in Mar/Jun/Sep/Dec

import datetime as dt
from math import ceil

MONTH_CODES = {3:"H", 6:"M", 9:"U", 12:"Z"}

def tests():
    fail = 0

    d = dt.date(2013,3,7)
    if get_front_month(d, "ES") != "ESH3":
        print "FAILED #1"
        fail += 1

    d = dt.date(2013,3,14)
    if get_front_month(d, "ES") != "ESM3":
        print "FAILED #2"
        fail += 1

    d = dt.date(2013,3,22)
    if get_front_month(d, "ES") != "ESM3":
        print "FAILED #3"
        fail += 1

    d = dt.date(2012,2,20)
    if get_front_month(d, "ES") != "ESH2":
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
        second_thursday = date.replace(day = 1 + (THURSDAY - week_day) + 7)
    elif week_day > THURSDAY:
        second_thursday = date.replace(day = 1 + THURSDAY + (7 - week_day) + 7)
    else:
        second_thursday = first_day(day = 1 + 7)
        
    return second_thursday
    
def get_front_month(date, contract):
    
    # Grab month + year
    month = date.month
    year = date.year
    day = date.day

    # Check if a month with an expiring contract
    if month in MONTH_CODES.keys():

        # Check if before expiration on current month
        # Roll-over occurs on second Thursday of each month

        second_thursday = get_expiration_date(date)

        if day < second_thursday.day:
            curr = contract + str(MONTH_CODES[second_thursday.month]) + str(second_thursday.year)[-1]
            return curr
        else:
            try:
                curr = contract + str(MONTH_CODES[second_thursday.month + 3]) + str(second_thursday.year)[-1]
            except KeyError: # December - rollover to next year
                curr = contract + str(MONTH_CODES[3]) + str(second_thursday.year + 1)[-1]   
            return curr

    elif month not in MONTH_CODES.keys():
        # get next month
        next_month = ceil(float(month) / 3) * 3
        curr = contract + str(MONTH_CODES[next_month]) + str(year)[-1]
        return curr

if __name__ == '__main__':
    tests()

                              


