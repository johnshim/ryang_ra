import tables
from tables import *

# Import filter code, front month
import main
import front_month

# Python Libraries
import datetime as dt
import numpy as np
import numpy

import glob
import sys

import gc

# Data Folders
#ARCA_DATA_FOLDER = "/datastore/dbd/auction/book_data/arca/"
ARCA_DATA_FOLDER = "/datastore/ryang/auction/book_data/arca/"
#CME_DATA_FOLDER = "/datastore/dbd/auction/book_data/cme/"
CME_DATA_FOLDER = "/datastore/ryang/auction/book_data/cme/"

# Convert Books to Time Space
# i.e. entry for each millisecond
def toTimeSpace(books, init, end):
    # Extract the relevant timestamps
    times1000 = books['timestamp']
    times = times1000 / 1000 # scale to milliseconds

    # Scale init, end
    init = init / 1000
    end = end / 1000

    # total number of milliseconds
    total_interval = end - init

    # Offset for times
    offset = times[0]

    preset = times[0] - init
    postset = end - times[-1]

    # timemidpts: array of midpoint prices
    timemidpts = numpy.zeros(total_interval + 1)

    # Holds time of latest book update
    oldUpdateTime = times[0]
    oldPrice = 0

    bidp = books['bid'][:][:,:,0]
    bidq = books['bid'][:][:,:,1]

    askp = books['ask'][:][:,:,0]
    askq = books['ask'][:][:,:,1]

    idx = np.searchsorted(times, np.array(range(int(init), int(end)+1)), side='right')

    timebidp = bidp[idx-1]
    timebidq = bidq[idx-1]

    timeaskp = askp[idx-1]
    timeaskq = askq[idx-1]

    return [timebidp, timebidq, idx, timeaskp, timeaskq]

# Convert Books to Sparse Time Space
# e.g. index = number of milliseconds since market open
def toSparse(books, init, end):
    times1000 = books['timestamp']
    times = times1000 / 1000 # scale to milliseconds
    
    # Scale init and end
    init = init / 1000
    end = end / 1000

    # Find last index of unique timestamps (e.g. index of latest update at each millisecond)
    uniquetimes = np.unique(times)
    idx = np.searchsorted(times, uniquetimes, side='right')
    
    # Transform times into milliseconds since open
    mssinceinit = uniquetimes - init

    # If first entry is *before* market open (i.e. no update at market open)
    # Set that update time to market open
    if times[0] < init:
        mssinceinit[0] = 0

    # Grab corresponding bid/ask prices/qtys
    bidp = books['bid'][:][:,:,0]
    bidq = books['bid'][:][:,:,1]

    askp = books['ask'][:][:,:,0]
    askq = books['ask'][:][:,:,1]

    bidp = bidp[idx-1]
    bidq = bidq[idx-1]
    askp = askp[idx-1]
    askq = askq[idx-1]

    # reshape times into column vector
    mssinceinit = np.reshape(mssinceinit, (-1, 1))

    # concatenate indices with prices/qtys
    timebidp = np.concatenate([mssinceinit,bidp],1)
    timebidq = np.concatenate([mssinceinit,bidq],1)

    timeaskp = np.concatenate([mssinceinit,askp],1)
    timeaskq = np.concatenate([mssinceinit,askq],1)

    return [timebidp, timebidq, mssinceinit, timeaskp, timeaskq]

# Write to HDF5 File
# 1 product, 1 side, 1 date, price or qty
def HDF5_style(data, product, side, pq, date):

    fn = date + "_" + product + "_" + side + "_" + pq + ".h5"

    h5file = tables.openFile(fn, mode = "w", title = "Test file")
    group = h5file.createGroup("/", product, product)

    ca = h5file.createCArray(group, product+side+pq, tables.IntAtom(), data.shape)
    ca[:] = data

    h5file.close()

# Write to HDF5 File
# All sides, prices and qtys on one file
def HDF5_style_unified(bidp, bidq, askp, askq, product, date, init, end):

    fn = date + "_" + product + ".h5"

    h5file = tables.openFile(fn, mode = "w", title = date + "_" + product)
    group = h5file.createGroup("/", product, product)

    bp = h5file.createCArray(group, product+"BIDPRICE", tables.IntAtom(), bidp.shape)
    bp[:] = bidp

    bq = h5file.createCArray(group, product+"BIDQTY", tables.IntAtom(), bidq.shape)
    bq[:] = bidq

    ap = h5file.createCArray(group, product+"ASKPRICE", tables.IntAtom(), askp.shape)
    ap[:] = askp

    aq = h5file.createCArray(group, product+"ASKQTY", tables.IntAtom(), askq.shape)
    aq[:] = askq

    startstop = np.array([init,end])
    #print "SS",startstop
    times = h5file.createCArray(group, "TIMES", tables.IntAtom(), startstop.shape)
    times[:] = startstop

    h5file.close()

if __name__ == "__main__":

    yr = sys.argv[1]

    try:
        product = sys.argv[2]
    except:
        product = ['SPY','ES']

    arca_dates = glob.glob(ARCA_DATA_FOLDER + yr + "*")
    cme_dates = glob.glob(CME_DATA_FOLDER + yr + "*")

    START_TIME = dt.time(8, 30, 00, 0) # 1430 GMT = 9:30AM Eastern = 8:30PM Central
    END_TIME = dt.time(15, 00, 00, 0) # 2000 GMT = 4:00PM Eastern = 3:00PM Central

    failures = []

    print cme_dates
    
    for date in cme_dates:
            date = date.split('/')[-1].split('_')[0]

            print date
            if dt.date(int(date[0:4]),int(date[4:6]),int(date[6:8])).weekday() > 4:
                # Skip if weekend
                continue

            if 'implied' in date:
                continue

            date = date.split('/')[-1]

            # Skip if already processed
            if len(glob.glob(date + '_ES.h5')) != 0:
                print date, " already done."
                #continue

            #print date
            try:

                cme_product = front_month.get_front_month(dt.date(int(date[0:4]), int(date[4:6]), int(date[6:8])), "ES")

                cme_file = tables.openFile(CME_DATA_FOLDER + date)

                try:
                    cme_temp = main.filterData(cme_file, cme_product, START_TIME, END_TIME, date)
                except Exception as e:
                    cme_file.close()
                    failures.append([date, cme_product, e])
                    continue
            
                books = cme_temp[0]
                init = cme_temp[1]
                end = cme_temp[2]

                print init, end

                if len(books) == 0:
                    print date, ' is empty.'
                    cme_file.close()
                    failures.append([date, cme_product, "File Empty"])
                    continue

                cme_temp = toSparse(books, init, end)

                bp = cme_temp[0]
                bq = cme_temp[1]
                idx = cme_temp[2]
                ap = cme_temp[3]
                aq = cme_temp[4]

                print init,end
                HDF5_style_unified(bp, bq, ap, aq, "ES", date, init, end)

                print init,end
                cme_file.close()
            except Exception as e:
                print e
                print date, 'failed'
                failures.append([date, cme_product, e])
                continue
    

    for date in arca_dates:
        gc.collect()

        print date
        date = date.split('/')[-1].split('_')[0]
        if dt.date(int(date[0:4]),int(date[4:6]),int(date[6:8])).weekday() > 4:
            # Skip if weekend
            continue

        if 'implied' in date:
            continue
        
        print date
        try:



            # Skip if already processed
            if len(glob.glob(date + '_SPY.h5')) != 0:
                print date, " already done."
                continue

            arca_product = 'SPY'

            nyse_file = tables.openFile(ARCA_DATA_FOLDER + date + "_TOP.h5")
            #nyse_file = tables.openFile(ARCA_DATA_FOLDER + date + "_SPY.h5")
            
            arca_temp = main.filterData(nyse_file, arca_product, START_TIME, END_TIME, date)

            books = arca_temp[0]
            init = arca_temp[1]
            end = arca_temp[2]

            if len(books) == 0:
                print date, ' is empty.'
                nyse_file.close()
                failures.append([arca_product, date, "File Empty"])
                continue

            arca_temp = toSparse(books, init, end)        

            bp = arca_temp[0]
            bq = arca_temp[1]
            idx = arca_temp[2]
            ap = arca_temp[3]
            aq = arca_temp[4]

            HDF5_style_unified(bp, bq, ap, aq, "SPY", date, init, end)

            nyse_file.close()
        except Exception as e:
            print e
            print date, 'failed'
            failures.append([arca_product, date, e])
            nyse_file.close()
            continue

    print failures
