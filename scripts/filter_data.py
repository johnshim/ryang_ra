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


def to_ts(ts):
    return dt.datetime.fromtimestamp(float(ts)/1000000)

# date - yyyymmdd (string)

def filter_time_contract(product, datestr, start_time, end_time):

    # import the file
    input_file = tables.openFile(DATA_FOLDER + datestr)

    # Convert to time date
    date = dt.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))
    
    # get the front month contract only
    contract_name = get_front_month(date, product)
    front_contract = getattr(input_file.root, contract_name)

    print "Filtering for front month contract: ", contract_name
    print "Filtering for time: ", START_TIME, END_TIME

    # filter by time

    init = time.mktime(dt.datetime.combine(date, start_time).timetuple()) * 1000000
    end = time.mktime(dt.datetime.combine(date, end_time).timetuple()) * 1000000

    print init, end, end - init

    selected_books = front_contract.books.readWhere('(timestamp >= init) & (timestamp <= end)')
    selected_trades = front_contract.trades.readWhere('(timestamp >= init) & (timestamp <= end)')

    # setup file for export
    filter_settings = Filters(complevel = 1)
    print "Writing to: ", DATA_FOLDER + datestr + "f"
    output_file = tables.openFile(DATA_FOLDER + datestr + "f", mode = "w", title = "outfile")

    # Changed to have same group across difinput_file front mth contracts
    group = output_file.createGroup("/", product, product) 
    
    book_table = output_file.createTable(group, "books", BookTable, "books books", filters = filter_settings)
    book_table.append(selected_books)

    trade_table = output_file.createTable(group, "trades", TradeTable, "trades trades", filters = filter_settings)
    trade_table.append(selected_trades)

    input_file.close()
    output_file.close()    

if __name__ == "__main__":

    START_TIME = dt.time(13, 59, 59, 999999) # 8:30am = 1430 GMT
    END_TIME = dt.time(20, 00, 00, 1) # 3pm = 2000 GMT
    #END_TIME = dt.time(19, 00, 05, 1) # 2pm = 1900 GMT = 1400 EST


    filter_time_contract("ES", "20111017", START_TIME, END_TIME)
