# filter.py
# Filters HDF5 file for specific contract and times

from front_month import *
import datetime as dt
import tables
import numpy

from tables import *

# VARS
DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"
DATE = dt.date(2011,10,16) # WTF?

START_TIME = dt.time(13, 59, 59, 999999) # 9am = 1400 GMT
#END_TIME = dt.time(20, 00, 00, 1) # 3pm = 2000 GM
END_TIME = dt.time(14, 00, 05, 1) # 3pm = 2000 GMT

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

def tests():
    fail = 0

    if not fail:
        print "ALL TESTS PASSED"




def to_ts(ts):
    return dt.datetime.fromtimestamp(float(ts)/1000000)

# date - yyyymmdd (string)
def filter(date):

    # import the file
    f = tables.openFile(DATA_FOLDER + date)

    # get the front month contract only
    contract_name = get_front_month(DATE)
    front_contract = getattr(f.root, contract_name)

    print contract_name
    #print front_contract

    # TODO: REWRITE USING WHERE STATEMENTS FOR EFFICIENCY

    # filter by time
    selected_books = [x[:] for x in front_contract.books if (to_ts(x['timestamp']).time() > START_TIME and to_ts(x['timestamp']).time() < END_TIME)]

    selected_trades = [x[:] for x in front_contract.trades if (to_ts(x['timestamp']).time() > START_TIME and to_ts(x['timestamp']).time() < END_TIME)]

    # setup file for export
    f2 = tables.openFile("out", mode = "w", title = "outfile")

    # Changed to have same group across diff front mth contracts
    group = f2.createGroup("/", "ES", "ES") 
    #group = f2.createGroup("/", contract_name, contract_name)
    
    table = f2.createTable(group, "books", BookTable, "books books")
    table.append(selected_books)

    table2 = f2.createTable(group, "trades", TradeTable, "traes trdes")
    table2.append(selected_trades)

    f2.close()    

if __name__ == "__main__":

    filter("20111017")
    

    #tests()
