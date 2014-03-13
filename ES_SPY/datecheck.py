import datetime
import glob
import sys
import os

y = sys.argv[1]
product = sys.argv[2]

cwd = os.getcwd()
path = cwd + "/" + y + "/" + product + "/"
print path


#years = [2005, 2006, 2007, 2008, 2009, 2010, 2011]
months = [1,2,3,4,5,6,7,8,9,10,11,12]

#product = ['ES','SPY']

ys = [int(y)]

for year in ys:
    for month in months:
        for day in xrange(1,31):
            # Create date
            try:
                d = datetime.date(year, month, day)
            except:
                continue

            wd = d.weekday()
            if wd < 5:

                if month < 10:
                    m = "0" + str(month)
                else:
                    m = str(month)

                if day < 10:
                    d = "0" + str(day)
                else:
                    d = str(day)

                # Check if there
                s = str(year) + m + d
                g = glob.glob(path + s + '*')

                if len(g) != 1:
                    print s
