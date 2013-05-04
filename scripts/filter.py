# filter.py
# Filters HDF5 file for specific contract and times

from front_month import *
import datetime as dt
import tables
import numpy
import time
import sys

from tables import *

# VARS
DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"
DATE = dt.date(2011,10,17) 

START_TIME = dt.time(13, 59, 59, 999999) # 8:30am = 1430 GMT
END_TIME = dt.time(17, 00, 00, 1) # 3pm = 2000 GM
#END_TIME = dt.time(19, 00, 05, 1) # 2pm = 1900 GMT = 1400 EST

NAME = "1"

############################
# Dan's definitions
############################

class BookTable(tables.IsDescription):
    """                                                                                                                                                                                              
    Basic book table                                                                                                                                                                                 
    """
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    ask         = Int64Col(shape=(10,2))
    bid         = Int64Col(shape=(10,2))
    seqnum      = Int64Col()

class ImpliedBookTable(tables.IsDescription):
    """                                                                                                                                                                                              
    Basic book table                                                                                                                                                                                 
    """
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    ask         = Int64Col(shape=(10,2))
    bid         = Int64Col(shape=(10,2))
    implied     = Int32Col()
    
class TradeTable(tables.IsDescription):
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    trade_type  = Int64Col()
    price       = Int64Col()
    quantity    = Int64Col()
    seqnum      = Int64Col()

############################
############################
"""
def tests():
    fail = 0

    if not fail:
        print "ALL TESTS PASSED"
"""
def to_ts(ts):
    return dt.datetime.fromtimestamp(float(ts)/1000000)

# date - yyyymmdd (string)
#def filter(date):
def filter():
    date = "20111017"

    # import the file
    f = tables.openFile(DATA_FOLDER + date)

    # get the front month contract only
    contract_name = get_front_month(DATE)
    front_contract = getattr(f.root, contract_name)

    print "Filtering for front month contract: ", contract_name
    print "Filtering for time: ", START_TIME, END_TIME

    #print contract_name
    #print front_contract

    # filter by time

    init = time.mktime(dt.datetime.combine(DATE, START_TIME).timetuple()) * 1000000
    end = time.mktime(dt.datetime.combine(DATE, END_TIME).timetuple()) * 1000000

    print init, end, end - init

    selected_books = front_contract.books.readWhere('(timestamp >= init) & (timestamp <= end)')
    selected_trades = front_contract.trades.readWhere('(timestamp >= init) & (timestamp <= end)')

    # setup file for export
    filter_settings = Filters(complevel = 1)
    print "Writing to: ", DATA_FOLDER + date + "f"
    f2 = tables.openFile(DATA_FOLDER + date + "f", mode = "w", title = "outfile")

    # Changed to have same group across diff front mth contracts
    group = f2.createGroup("/", "ES", "ES") 
    
    table = f2.createTable(group, "books", BookTable, "books books", filters = filter_settings)
    table.append(selected_books)

    table2 = f2.createTable(group, "trades", TradeTable, "trades trades", filters = filter_settings)
    table2.append(selected_trades)

    f.close()
    f2.close()    

if __name__ == "__main__":

    filter()
    

    #tests()
