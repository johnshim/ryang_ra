import csv
import glob
import numpy as np
import sys

DATA_FOLDER = "/datastore/ryang/correlations/"

def printCorrCoefMatrix(corr, products):
    print '\t',
    for i in products:
        print i, '\t',
    print '\n'
    for i in xrange(len(products)):
        print products[i], '\t',
        for j in xrange(len(products)):
            print "{0:.5f}".format(corr[i,j]),
            print '\t',
        print '\n'


if __name__ == "__main__":
    try:
        yr = sys.argv[1]
        interval = sys.argv[2]

        if sys.argv[3] == 'cvxxom':
            products = ['CVX', 'XOM']
            DATA_FOLDER = DATA_FOLDER + 'CVXXOM/'
        elif sys.argv[3] == 'aaplgoog':
            products = ['AAPL', 'GOOG']
            DATA_FOLDER = DATA_FOLDER + 'AAPLGOOG/'
        elif sys.argv[3] == 'hdlow':
            products = ['HD', 'LOW']
            DATA_FOLDER = DATA_FOLDER + 'HDLOW/'
        elif sys.argv[3] == 'gsms':
            products = ['GS', 'MS']
            DATA_FOLDER = DATA_FOLDER + 'GSMS/'
        elif sys.argv[3] == 'subset':
            products = ['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
            DATA_FOLDER = DATA_FOLDER + 'subset/'

        dates = glob.glob(DATA_FOLDER + '*' + interval + "_*" + yr + '*')
    except:
        dates = []
        print "Error"
        sys.exit()

    print len(dates)
    #products = ['CVX', 'XOM']
    #products = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]
    #products = ['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
    product_index = {}
    for p in xrange(len(products)):
        product_index[products[p]] = p

    correlation = np.zeros([len(products), len(products), len(dates)])
    n = np.zeros([len(products), len(products)])

    mins = np.ones([len(products), len(products)])
    mindates = np.zeros([len(products), len(products)])

    to_flag = []

    for date in xrange(len(dates)):
        input_file = open(dates[date], 'r')

        reader = csv.reader(input_file, delimiter=',')
        for row in reader:
            stock1 = product_index[row[0]]
            stock2 = product_index[row[1]]

            n[stock1, stock2] += 1

            # only fill in UR
            if stock1 < stock2:
                #print row
                correlation[stock1, stock2, date] += float(row[2])

            if stock1 == stock2:
                correlation[stock1, stock2, date] += 0.5

            if float(row[2]) < mins[stock1, stock2]:
                mins[stock1, stock2] = float(row[2])
                mindates[stock1, stock2] = date

        input_file.close()

    #correlation = np.divide(correlation, n) #len(dates)

    print np.min(correlation,2)
    print np.max(correlation,2)
    print n

    correlation =  np.sum(correlation, 2)
    correlation = correlation / len(dates)
    correlation = correlation + np.transpose(correlation)

    for i in xrange(len(products)):
        for j in xrange(len(products)):
            print products[i], products[j], mins[i, j], dates[int(mindates[i, j])].split("_")[2]

    printCorrCoefMatrix(correlation, products)
    #np.savetxt(''.join(products) + '_' + yr + '_' + interval + '.csv', correlation, delimiter=',')
    #np.savetxt('subset_' + yr + "_" + interval + '.csv', correlation, delimiter=',')
    
