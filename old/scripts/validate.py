######################################################
#
# File: validate.py 
#
# Description: Checks output from feed parser (perl) against feed parser (python).
#
######################################################

import time
import sys
import datetime
import tables
import re

# parameters - should find some way to write these as arguments

DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"

DATE = "20100509"

FRONT_MONTH_CONTRACT = "ESM0"

__DateTimeRe__ = re.compile(r"(\d{2}):(\d{2}):(\d{2}).(\d{3})")

def quit(df, gf):
    df.close()
    gf.close()
    sys.exit()

# Prints formatted time (hhMMssmmm -> hh:MM:ss:mmm)
def print_time(t):
    s = list(str(t))
    s.insert(6,":")
    s.insert(4,":")
    s.insert(2,":")
    return ''.join(s)

if __name__ == '__main__':

    d_readCtr = 0
    g_readCtr = 0

    mismatches = []

    # Load Dan data (yyyymmdd)
    D_FN = DATA_FOLDER + DATE
    df = tables.openFile(D_FN)
    
    # Load Geoff data
    G_FN = DATA_FOLDER + "CME_ES.20100509_only"
    gf = open(G_FN, 'r')

    # Preliminary Parsing / Checking
    d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[d_readCtr]
    g_line = gf.readline().split()

    # Read depth
    g_depth = int(g_line[4])
    #print "g depth:", g_depth

    d_depth = d_line['ask'].shape[0]
    #print "d depth:", d_depth

    depth = min(g_depth, d_depth)

    # Check that in Dan's data, we have same depth on both books
    if d_depth != d_line['bid'].shape[0]:
         print "Depth is not symmetrical in D Data."
         print "EXITING"
         quit(df, gf)

    # Check that we have the right front month
    if FRONT_MONTH_CONTRACT != g_line[0]:
        print "Front Months do not match"
        print "EXITING"
        quit(df, gf)

    while(True):
        
        # Compare time-stamps
        # Note: D is CST, G is GMT so we add 5 hrs to D timestamp to convert all to GMT

        d_ts = d_line["timestamp_s"][0:-3]
        g_ts = g_line[2]

        g_m = __DateTimeRe__.match(g_ts)        
        d_m = __DateTimeRe__.match(d_ts)

        hr, mi, se, ms = g_m.groups()
        g_time = int(hr + mi + se + ms)

        hr, mi, se, ms = d_m.groups()
        d_time = int(str(int(hr) + 5) + mi + se + ms)

        if g_time == d_time:
            #print "date time match at", g_time, "=", d_time

            # Check other data fields
            # ASSUMPTION: In geoff's data, the depth is constant
            # ASSUMPTION: The depth is the same on both sides


            g_bids = map(float, g_line[5:5 + 2*depth])
            g_asks = map(float, g_line[5 + 2*depth:])


            d_bids = d_line['bid'][0:depth]
            d_asks = d_line['ask'][0:depth]

            #print "g bids: ", g_bids
            #print "d bids: ", d_bids

            for i in xrange(depth):
                # Check ith depth level

                # Check bids + volume

                #print g_bids[2*i], float(d_bids[i,0])
                if g_bids[2*i] != float(d_bids[i,0]) / 100:
                    curr_error = ["Bid Price Mismatch"]
                    curr_error.append(g_time)
                    mismatches.append(curr_error)
                    #print "Bid Price Mismatch"
                    #time.sleep(1)
            
                #print g_bids[2*i + 1], float(d_bids[i,1])
                if g_bids[2*i + 1] != float(d_bids[i,1]):
                    curr_error = ["Bid Vol Mismatch"]
                    curr_error.append(g_time)
                    mismatches.append(curr_error)
                    #print "Bid Vol Mismatch"
                    #time.sleep(1)

                # Check asks + volume

                #print g_asks[2*i], float(d_asks[i,0])
                if g_asks[2*i] != float(d_asks[i,0]) / 100:
                    curr_error = ["Ask Price Mismatch"]
                    curr_error.append(g_time)
                    mismatches.append(curr_error)
                    #print "Ask Price Mismatch"
                    #time.sleep(1)
            
                #print g_asks[2*i + 1], float(d_asks[i,1])
                if g_asks[2*i + 1] != float(d_asks[i,1]):
                    curr_error = ["Ask Vol Mismatch"]
                    curr_error.append(g_time)
                    mismatches.append(curr_error)
                    #print "Ask Vol Mismatch"
                    #time.sleep(1)


            # increment both lines
            try:
                d_readCtr += 1
                d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[d_readCtr]
            except IndexError:
                #print "END OF D FILE"
                break

            g_readCtr += 1
            g_line = gf.readline().split()
            if not g_line:
                #print "END of G FILE"
                break
            
        else:

            curr_error = []

            #print "date time mismatch"
            #print "\tg_time =", g_time
            #print "\td_time =", d_time



            if g_time < d_time:

                curr_error.append("Unmatched Entry in G")
                curr_error.append(g_time)
                mismatches.append(curr_error)

                # increment g_time
                g_readCtr += 1
                g_line = gf.readline().split()
                if not g_line:
                    #print "END OF G FILE"
                    break

            if g_time > d_time:

                curr_error.append("Unmatched Entry in D")
                curr_error.append(d_time)
                mismatches.append(curr_error)

                # increment d_time (catching end of file)
                d_readCtr += 1
                try:
                    d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[d_readCtr]
                except IndexError:
                    #print "END OF D FILE"
                    break
                
    # Print out summary information
    print "D entries read: ", d_readCtr
    print "G entries read: ", g_readCtr

    print "Last D entry: ", print_time(d_time)
    print "Last G entry: ", print_time(g_time)

    for m in mismatches:
        print m

    quit(df, gf)
