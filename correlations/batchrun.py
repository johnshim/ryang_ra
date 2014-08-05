#####################################################
#
# batchrun.py
#
# This script presents an interface for using
# books2time to compute correlations over multiple 
# dates, products, etc.
#
# Given a set of book update HDF5 files according Dan's format,
# this script will convert those files to time space and compute
# the correlations between changes in the moving average of the 
# midpoint prices on selected products
# 
#
# Ron Yang 2013-2014
# University of Chicago
#
#####################################################

####################
#
# How to Use
#
# 1. Set the Data Location, Market Hours, Products, Intervals,
#    and Dates under OPTIONS below
#
# 2. Run this python script with the flag -w to write the correlations to file,
#    and with -p to print the correlations to the screen
#
#    With the -c flag, this script computes the correlations of the midpoint
#    prices, NOT the correlations of the changes in moving average
#
####################

####################
## External packages
####################

from books2time import *

# tables: Python HDF5 Library
import tables

# numpy: Python Numerical Library
import numpy as np

# Python Time libraries
import datetime as dt
import time

# Python system libraries
import sys
import glob
import subprocess

##########
## OPTIONS
##########

#####
## 1. Data Locations
# Set to directory of the HDF5 book update data files
#####

# directory on bushlnxeb01.chicagobooth.edu
# DATA_FOLDER = "/datastore/dbd/auction/book_data/arca/"

#####
## 2. Market Hours
# Restricts computations to between these hours
#####

# Start Time (e.g. market open)
# 0830 Central = 1430 GMT = 0930 Eastern
# START_TIME = dt.time(8, 30, 00, 0) 

# End Time (e.g. market close)
# 1400 Central = 2000 GMT = 1500 Eastern
# END_TIME = dt.time(14, 00, 00, 0) 

#####
## 3. Products
# Set which products/contracts to compute
#####

# List of all stocks in NYSE data
all_stocks = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]

#products = stock_list

# Example
# Computes AAPL and XOM
# products = ['AAPL', 'XOM']

#####
## 4. Intervals
# Set which intervals to compute
# in milliseconds
#####

# intervals = [1, 10, 100, 1000, 10000, 60000, 600000]
# intervals = [60000]

#####
## 5. Dates
# Set which dates to compute
#####

# You can specify these dates in two ways:
# if you type out the full date YYYYMMDD, it will add that date
# if you only type a subset of that, e.g. YYYY or YYYYMM,
# it will add all dates of that year or month, respectively
# Note: this will only process dates that stored as HDF5 files
# in the DATA_FOLDER

# Example
# Adds 2011/10/17 and all of 2010/04
# raw_dates = ['20111017', '201004']

# dates = [filename for raw_date in raw_dates for filename in glob.glob(DATA_FOLDER + raw_date + '*') ]

#############
# END OPTIONS
#############

###########
# MAIN
###########

def run(date, products, interval, folder_name='', simpleCorr=False, verbose=False, printMatrix=True, writeMatrix=False):
    
    # Keeps track of which products were computed successfully
    # Used in writing / printing correlation matrix
    valid_products = []

    datestr = date[38:46]

    if verbose:
        print "Processing DATE=", datestr, " INTERVAL=", interval

    # Skip if already processed
    if len(glob.glob('*' + str(interval) + '_*' + datestr + '_*' + ''.join(products) + '*')) != 0:
        print date, " already done."
        return 0

    filename = datestr + "_TOP.h5" # "20111017_TOP.h5"

    # Load file
    input_file = tables.openFile(DATA_FOLDER + filename)

    ## For each product
    for i in xrange(len(products)):
        if verbose:
            print "Processing ", products[i]

        product = products[i]

        books, init, end = filterData(input_file, product, START_TIME, END_TIME, datestr)

        timemidpts = toTimeSpace(books, init, end)

        if simpleCorr:
            if i == 0:
                pd = timemidpts
            else:
                pd = np.vstack(pd, timemidpts)
        else:
            if i == 0:
                pd = getDifferenceArray(timemidpts, interval)            
            else:
                pd = np.vstack((pd, getDifferenceArray(timemidpts, interval)))
                    
        valid_products.append(product)
                
    # Take correlation across stocks
    corr = np.corrcoef(pd)
            
    # Display correlation matrix
    if printMatrix:
        printCorrCoefMatrix(corr, valid_products)

    # Write correlation matrix
    if writeMatrix:
        writeCorrCoefMatrix(corr, valid_products, interval, datestr, products, folder_name)

    # Clean up
    input_file.close()
   
if __name__ == "__main__":

    # Read from file
    f = open('config.txt')
    ftext = f.read().strip()
    f.close()

    lines = ftext.split('\n')
    lines = [l.split(',') for l in lines]

    for entry in lines:
        try:
            settingName = entry[0].strip()
            setting = entry[1].strip()
        except:
            continue

        if settingName == 'run_name':
            RUN_NAME = setting
        if settingName == 'data_folder':
            DATA_FOLDER = setting
        if settingName == 'start_time':
            setting = setting.split(':')
            START_TIME = dt.time(int(setting[0]), int(setting[1]), int(setting[2]), 0) 
        if settingName == 'end_time':
            setting = setting.split(':')
            END_TIME = dt.time(int(setting[0]), int(setting[1]), int(setting[2]), 0) 
        if settingName == 'dates':
            raw_dates = [date.strip() for date in entry[1:]]
            dates = [filename for raw_date in raw_dates for filename in glob.glob(DATA_FOLDER + raw_date + '*') ]
        if settingName == 'intervals':
            intervals = [int(interval) for interval in entry[1:]]
        if settingName == 'tickers':
            products = [ticker.strip() for ticker in entry[1:]]
            if products == ['']:
                products = all_stocks
            
    print "RUN OPTIONS"
    print RUN_NAME
    print DATA_FOLDER
    print START_TIME
    print END_TIME
    print raw_dates
    print intervals
    print products

    # Create folder for output
    folder_name = RUN_NAME + "/"
    if len(glob.glob(folder_name)) == 0:
        subprocess.call("mkdir " + folder_name, shell=True)
    subprocess.call("cp config.txt " + folder_name, shell=True)

    for date in dates:
        for interval in intervals:
            run(date, products, interval, folder_name, '-c' in sys.argv, '-v' in sys.argv, '-p' in sys.argv, '-w' in sys.argv)

