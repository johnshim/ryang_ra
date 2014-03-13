#####################################################
#
# books2time.py
#
# This Python package includes methods for converting
# book updates stored in HDF5 format into time series
# and computing changes in moving averages
# 
# 
#
# Ron Yang 2013-2014
# University of Chicago
#
#####################################################

####################
## External packages
####################

# tables: Python HDF5 Library
from tables import *

# numpy: Python Numerical Library
import numpy as np

# Python Time libraries
import datetime as dt
import time

#############
# filterData
#
# Filters order book updates to restrict for a 
# single product and only during market open hours
#
# Inputs: input_file - HDF5 file object
#         contract_name - string of name of contract (e.g. 'ESH3', 'SPY')
#         START_TIME - the beginning of the time period, datetime.time object
#         END_TIME - the end of the time period, datetime.time object
#         datestr - a six-character string of format YYYYMMDD
#
#
#############

def filterData(input_file, contract_name, start_time, end_time, datestr):

    ## Convert datestr to datetime.date object
    date = dt.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))
    
    ## Filter by product

    try:
        contract = getattr(input_file.root, contract_name)
    except:
        print "ERROR: CONTRACT NOT FOUND"
        return []

    # Set up initial and end times
    init = time.mktime(dt.datetime.combine(date, start_time).timetuple()) * 1000000
    end = time.mktime(dt.datetime.combine(date, end_time).timetuple()) * 1000000

    ## Filter by time

    # Adjust time so 1st update is last update BEFORE START_TIME
    # this ensures that there are prices if there is no
    # update at start_time
    
    ts = contract.books.cols.timestamp
    pre_books = contract.books.readWhere('(timestamp <= init)')
    initNew = ts[len(pre_books)-1]

    selected_books = contract.books.readWhere('(timestamp >= initNew) & (timestamp <= end)')

    return [selected_books, init / 1000, end / 1000]

#################################################
# toTimeSpace
#
# Converts prices stored as order book updates into 
# a time series of the midpoint between
# the standing best bid / best offer
#
# Inputs: books
#         init - start of time period, milliseconds
#         end - end of time period, milliseconds
#
#################################################

def toTimeSpace(books, init, end):

    midpts = getMidpts(books)

    idx = getTimeIdx(books, init, end)

    timemidpts = midpts[idx]

    return timemidpts

##########################
# getMidpts
# 
# Computes the midpoint of the best bid and best ask
# of the asset in the book object
#
# Inputs: books - Book object
#
##########################

def getMidpts(books):
    # Compute midpoints from best bid / best ask
    bestasks = np.array([update[0,0] for update in books['ask']])
    bestbids = np.array([update[0,0] for update in books['bid']])
    midpts = (bestasks + bestbids) / 2.0

    return midpts

##########################
# getTimeIdx
# 
# Computes the index of the latest book update
# for each millisecond between init and end
#
# Inputs: books - Book object
#         init - time in milliseconds
#         end - time in milliseconds
#
##########################

def getTimeIdx(books, init, end):

    times = books['timestamp'] / 1000 # scale to milliseconds

    idx = np.searchsorted(times, np.array(range(int(init), int(end)+1)), side='left')

    return idx-1

###########################
# getDifferenceArray
#
# Calculates the percentage change of the moving average from a
# timeseries of midpoint prices
#
# This is defined as:
# average midpoint over (t, t+k) - average midpoint over (t-k, t)
#
###########################

def getDifferenceArray(timemidpts, interval):

    ret = np.cumsum(timemidpts, dtype=float)

    mv = (ret[interval - 1:] - ret[:1 - interval]) / interval

    return np.diff(mv)

###########################
# Utilities
#
###########################

## printCorrCoefMatrix
# Displays correlation coefficient matrix on screen

def printCorrCoefMatrix(corr, products):
    print '\t',
    for i in products:
        print i, '\t',
    print '\n'
    for i in xrange(len(products)):
        print products[i], '\t',
        for j in xrange(len(products)):
            print "{0:.2f}".format(corr[i,j]),
            print '\t',
        print '\n'

## writeCorrCoefMatrix
# Write correlation coefficient matrix to file

def writeCorrCoefMatrix(corr, valid_products, interval, datestr, products, folder_name=''):

    outstr = ""
    for i in xrange(len(valid_products)):
        for j in xrange(len(valid_products)):
            outstr = outstr + valid_products[i] + "," + valid_products[j] + "," + "{0:.8f}".format(corr[i,j]) + "\n"    

    f = open(folder_name + "corr" + "_" + str(interval) + "_" + datestr + ".csv", 'w')

    f.write(outstr)
    f.close()


