import glob
import tables
import numpy

dates = glob.glob('*2009/SPY/200909*') + glob.glob('*2009/SPY/200910*') + glob.glob('*2009/SPY/200911*') + glob.glob('*2009/SPY/200912*') + glob.glob('*2010/SPY/201001*')

for date in dates:
    f = tables.openFile(date)
    print date.split("/")[2].split("_")[0],
    print "\t",
    print len(f.root.SPY.SPYBIDQTY),
    print "     \t \t",
    print f.root.SPY.SPYBIDQTY[-1][0]
    f.close()
