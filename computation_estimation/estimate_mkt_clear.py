import random
import math
import time
import collections
import cython
import numpy

# first generate the random numbers (200,000)

bids = []
asks = []

M = 100000

for i in xrange(M):
    bids.append(int(math.floor(random.normalvariate(1000, 20))))
    asks.append(int(math.floor(random.normalvariate(1050, 10))))

init = time.time()

# Process the data

bd = {}
ad = {}

barr = numpy.array(bids)
aarr = numpy.array(asks)

counts = numpy.bincount(barr)

counts = [(i, v) for i, v in enumerate(counts) if v]

print counts

tc = time.time()

for bid in bids:
    try:
        bd[bid] = bd[bid] + 1
    except:
        bd[bid] = 1

for ask in asks:
    try:
        ad[ask] = ad[ask] + 1
    except:
        ad[ask] = 1

t2 = time.time()

print len(bids), len(asks), len(bd.keys()), len(ad.keys())

#print "Aggregate S/D Curve: ", (t2 - init) * 1000
print "AGG SD: ", 1000*(tc - init), 1000*(t2 - tc)

t2 = time.time()

# Find the market clearing price

maxbid = int(max(bd.keys()))
minask = int(min(ad.keys()))

demand = 0
supply = 0

prevd = demand
prevs = supply

guess = 0

print "MB, MA", maxbid, minask

if maxbid > minask:

    guess = int(math.floor((maxbid + minask) / 2))

    while True:

        prevd = demand
        prevs = supply

        #guess = int(math.floor((maxbid + minask) / 2))
        print "guess", guess

        demand = 0
        supply = 0

        for price in xrange(guess, maxbid):
            try:
                demand = demand + bd[price]
            except:
                demand = demand

        for price in xrange(minask, guess):
            try:
                supply = supply + ad[price]
            except:
                supply = supply

        print "D/S:", demand, supply

        if demand == supply:
            break

        if demand > supply and prevd < prevs:
            if min(prevd, prevs) > min(demand, supply):
                demand = prevd
                supply = prevs
            break

        if demand < supply and prevd > prevs:
            if min(prevd, prevs) > min(demand, supply):
                demand = prevd
                supply = prevs
            break

        if demand > supply:
            guess = guess + 1
        elif demand < supply:
            guess = guess - 1

t3 = time.time()    

print demand, supply, guess

print "Find Market Clearing Price: ", (t3 - t2) * 1000
