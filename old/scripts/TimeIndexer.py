import tables
import numpy

from tables import *
import numpy as np


"""
TimeIndexer

Provides map between times and current book at that time

"""

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


class TimeIndexer(object):
    
    timeindexmap = {}

    def __init__(self, h5_file):
        f = tables.openFile(h5_file)
        
        contract_name = "ES"

        books = f.root.ES.books

        init = books.cols.timestamp[0]
        end = books.cols.timestamp[-1]
        print init / 1000000., end / 1000000.

        diff = end - init

        nexttime = 1
        currtime = 0

        for i in xrange(init, end+1000, 1000):

            if i % 1000000 == 0:
                print i / 1000000

            if i == books.cols.timestamp[nexttime]:
                self.timeindexmap[i] = nexttime
                currtime = nexttime
                nexttime += 1
            elif i < books.cols.timestamp[nexttime]:
                self.timeindexmap[i] = currtime
            elif i > books.cols.timestamp[nexttime]:
                while i > books.cols.timestamp[nexttime]:
                    self.timeindexmap[i-1] = nexttime
                    currtime = nexttime
                    nexttime += 1
                self.timeindexmap[i] = nexttime
                currtime = nexttime
                nexttime += 1

        f.close()

class TimeIndexFinder(object):
    
    times = []
    indices = []
    timeindexdict = {}
    indextimedict = {}

    books = []

    curr = -1
    
    def __init__(self, h5_file):
        f = tables.openFile(h5_file)

        self.times = f.root.ES.books.cols.timestamp[:]
        self.indices = range(0, len(self.times))

        self.timeindexdict = dict(zip(self.times,self.indices))
        self.indextimedict = dict(zip(self.indices,self.times))

        f.close()

    def get_index(self, time):
        #ctr = 0
        if self.curr == -1:
            while(True):
                #ctr += 1
                try:
                    t = self.timeindexdict[time]
                    self.curr = t
                    self.next = t+1
                    return t
                except:
                    time -= 1000
        else:
            while(True):
                #print self.curr, self.next, len(self.indextimedict)
                if time >= self.indextimedict[self.curr] and time < self.indextimedict[self.next]:
                    return self.curr
                elif time < self.indextimedict[self.curr]:
                    return self.curr - 1
                else:
                    self.curr += 1
                    self.next += 1

    def get_index_original(self, time):
        
        while(True):
            #ctr += 1
            try:
                t = self.timeindexdict[time]
                self.curr = t
                self.next = t+1
                return t
            except:
                time -= 1000


# get_midpts(ti, books, time)
# Returns array of the midpoint price
# where midpt price = (best bid + best ask) / 2

# ti: TimeIndex object
# books: Book object
# times: interval for prices

def get_midpts(ti, books, times):
    midpt = np.zeros([len(times) + 1])
    #t = time.time()
    #foo = 0
    for x in times:
        #foo += 1
        #if x % 10000000 == 0:
        #    t2 = time.time() - t
        #    print ((times[-1]-times[0])*(t2)/(x-times[0])) / 60.

        b = books[ti.get_index(x)]
        try:
            midpt[(x - times[0]) / 1000] = (b['ask'][0,0] + b['bid'][0,0]) / 2.0
        except:
            #print foo
            #print x, times[0], x - times[0]
            #print times[-1] - x, len(times)
            sys.exit()
    
    return midpt
