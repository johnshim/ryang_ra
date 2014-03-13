import tables
import sys


print sys.argv[1]

f = tables.openFile(sys.argv[1])
try:
    print f.root.SPY.SPYBIDQTY[-1]
except:
    print f.root.ES.ESBIDQTY[-1]
