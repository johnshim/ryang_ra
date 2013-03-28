######################################################
#
# File: validate.py 
#
# Description: Checks output from feed parser (perl) against feed parser (python).
#
######################################################

import time
import datetime
import tables
import re

DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"

DATE = "20100509"

FRONT_MONTH_CONTRACT = "ESM0"

__DateTimeRe__ = re.compile(r"(\d{2}):(\d{2}):(\d{2}).(\d{3})")

if __name__ == '__main__':
    print "Validating"

    g_readCtr = 0
    d_readCtr = 0

    # Load Dan data (yyyymmdd)
    D_FN = DATA_FOLDER + "20100509"
    df = tables.openFile(D_FN)
    
    # Load Geoff data
    G_FN = DATA_FOLDER + "CME_ES.20100509_only"
    gf = open(G_FN, 'r')

    # While neither file is exhausted

    # Read first line
    d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[g_readCtr]
    g_line = gf.readline().split()

    while(True):
        
        # Note: should double check that front month contract from G is correct

        # Compare time-stamps
        d_ts = d_line["timestamp_s"][0:-3]
        g_ts = g_line[2]

        g_m = __DateTimeRe__.match(g_ts)        
        d_m = __DateTimeRe__.match(d_ts)

        hr, mi, se, ms = g_m.groups()
        g_time = int(hr + mi + se + ms)

        hr, mi, se, ms = d_m.groups()
        d_time = int(str(int(hr) + 5) + mi + se + ms)

        print g_time, d_time
        if g_time == d_time:
            print "date time match at", g_time, "=", d_time

            # increment both lines
            g_readCtr += 1
            d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[g_readCtr]
            g_line = gf.readline().split()
            
        else:
            print "date time mismatch"
            print "g_time =", g_time
            print "d_time =", d_time

            if g_time < d_time:
                # increment g_time
                g_line = gf.readline().split()

            if g_time > d_time:
                # increment d_time (catching end of file)
                g_readCtr += 1
                try:
                    d_line = getattr(df.root, FRONT_MONTH_CONTRACT).books[g_readCtr]
                except:
                    print "END OF D FILE"
                    break
                

        #time.sleep(0.5)
    print g_readCtr


