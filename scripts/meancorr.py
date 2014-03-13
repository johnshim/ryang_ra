import csv
import glob
import numpy as np
import sys

DATA_FOLDER = "/datastore/ryang/paper_correlations/"

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

def writeCorrCoefMatrix(corr, valid_products, interval, year, products, fb = False):

    outstr = ","
    for i in valid_products:
        outstr = outstr + i
        outstr = outstr + ','
    outstr = outstr + '\n'
    for i in xrange(len(valid_products)):
        outstr = outstr + valid_products[i]
        outstr = outstr + ','
        for j in xrange(len(valid_products)):
            outstr = outstr + "{0:.8f}".format(corr[i,j]) + ","    
        outstr = outstr + '\n'

    if fb:
        f = open("corr" + "_" + str(interval) + "_" + year + "_" + ''.join(products) + ".filter.csv", 'w')
    else:
        f = open("corr" + "_" + str(interval) + "_" + year + "_" + ''.join(products) + ".csv", 'w')
    f.write(outstr)

    f.close()

if __name__ == "__main__":

    # Grab set of products
    try:
        yr = sys.argv[1]
        interval = sys.argv[2]

        if sys.argv[3] == 'cvxxom':
            products = ['CVX', 'XOM']
            DATA_FOLDER = DATA_FOLDER + 'pairs/CVXXOM/'
        elif sys.argv[3] == 'aaplgoog':
            products = ['AAPL', 'GOOG']
            DATA_FOLDER = DATA_FOLDER + 'pairs/AAPLGOOG/'
        elif sys.argv[3] == 'hdlow':
            products = ['HD', 'LOW']
            DATA_FOLDER = DATA_FOLDER + 'pairs/HDLOW/'
        elif sys.argv[3] == 'gsms':
            products = ['GS', 'MS']
            DATA_FOLDER = DATA_FOLDER + 'pairs/GSMS/'
        elif sys.argv[3] == 'subset':
            products = ['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
            DATA_FOLDER = DATA_FOLDER + 'matrix/' 

        DATA_FOLDER = DATA_FOLDER + interval + "/" + yr + "/"

        dates = glob.glob(DATA_FOLDER + '*' + interval + "_*" + yr + '*')
    except:
        dates = []
        print "Error"
        sys.exit()

    print len(dates)

    product_index = {}
    for p in xrange(len(products)):
        product_index[products[p]] = p

    correlation = np.zeros([len(products), len(products), len(dates)])
    n = np.zeros([len(products), len(products)])

    mins = np.ones([len(products), len(products)])
    mindates = np.zeros([len(products), len(products)])

    # Check if we want to flag low correlation days

    try:
        if sys.argv[4] == '-f':
            FLAG = True
    except:
        FLAG = False
    to_flag = []

    for date in xrange(len(dates)):
        input_file = open(dates[date], 'r')

        reader = csv.reader(input_file, delimiter=',')
        for row in reader:
            stock1 = product_index[row[0]]
            stock2 = product_index[row[1]]

            # only fill in UR
            if stock1 < stock2:

                # Check if we need to flag this one
                if FLAG:
                    if float(row[2]) < 0.1:
                        to_flag.append([dates[date].split("_")[2], row[0], row[1], float(row[2])])
                    else:
                        correlation[stock1, stock2, date] += float(row[2])
                        n[stock1, stock2] += 1
                else:
                    correlation[stock1, stock2, date] += float(row[2])
                    n[stock1, stock2] += 1

            if stock1 == stock2:
                correlation[stock1, stock2, date] += 0.5
                n[stock1, stock2] += 0.5

            if float(row[2]) < mins[stock1, stock2]:
                mins[stock1, stock2] = float(row[2])
                mindates[stock1, stock2] = date

        input_file.close()

    n = n + np.transpose(n)
    print n
    correlation =  np.sum(correlation, 2)
    correlation = np.divide(correlation, n)



    #print correlation

    correlation = correlation + np.transpose(correlation)

    #for i in xrange(len(products)):
    #    for j in xrange(len(products)):
    #        print products[i], products[j], mins[i, j], dates[int(mindates[i, j])].split("_")[2]

    #printCorrCoefMatrix(correlation, products)
    if FLAG:
        #for i in to_flag:
        #    print i

        f = open(''.join(products) + '_' + yr + '_' + interval + '_flags.csv','w')
        for i in to_flag:
            for j in i:
                f.write(str(j))
                f.write(',')
            f.write('\n')
        f.close()

    #for flag in to_flag:
    #    print flag

    if FLAG:
        writeCorrCoefMatrix(correlation, products, interval, yr, products, True)
        #np.savetxt(''.join(products) + '_' + yr + '_' + interval + '_filter.csv', correlation, delimiter=',')
    else:
        writeCorrCoefMatrix(correlation, products, interval, yr, products)
        #np.savetxt(''.join(products) + '_' + yr + '_' + interval + '.csv', correlation, delimiter=',')
    #np.savetxt('subset_' + yr + "_" + interval + '.csv', correlation, delimiter=',')
    
