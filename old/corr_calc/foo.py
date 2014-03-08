from corr_calc import *
import numpy as np
import datetime

#es = getBloombergData('ES1 Index')
#spy = getStockData('SPY', datetime.date(2011,1,1), datetime.date(2011,12,31))

es = getStockData('JPM', datetime.date(2011,1,1), datetime.date(2011,12,31))
spy = getStockData('KBE', datetime.date(2011,1,1), datetime.date(2011,12,31))

ret = np.zeros([2,251])
ret[0,:] = es[0]
ret[1,:] = spy[0]

print np.corrcoef(ret)
print es[1]
print spy[1]
