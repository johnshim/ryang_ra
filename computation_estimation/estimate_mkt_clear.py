import random
import math
import time

# first generate the random numbers (200,000)

bids = []
asks = []

for i in xrange(100000):
    bids.append(math.floor(random.normalvariate(50, 5)))
    asks.append(math.floor(random.normalvariate(60, 10)))

init = time.time()

# Process the data

bd = {}
ad = {}

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

print len(bids), len(asks), len(bd.keys()), len(ad.keys())

t2 = time.time()

print t2 - init

# Find the market clearing price

maxbid = int(max(bd.keys()))
minask = int(min(ad.keys()))

demand = 0
supply = 0

prevd = demand
prevs = supply

guess = 0

print maxbid, minask

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

print demand, supply, guess

t3 = time.time()    

print t3 - t2
