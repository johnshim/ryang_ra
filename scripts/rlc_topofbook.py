import sys
import time

if __name__ == "__main__":
    # import rlc file
    filename = sys.argv[1]

    bookUpdates = []

    c = 0

    with open(filename, 'r') as f:

        for line in f:

            ##
            # Process the line
            ##

            ##
            # Check if front month (ESZ8)
            # and not calendar spread
            ##

            symbol = line[49:53]
            
            if symbol != "ESZ8" or line[53] == '-':
                continue

            ##
            # Check if markets are open 
            # and in cts trading
            # and floor markets are open
            ##

            tradingMode = line[70]

            if tradingMode != '2':
                continue
            
            

            ##
            # Check if book update
            ##

            messageType = line[33:35]
            
            if messageType != 'MA':
                continue
            
            ##
            # Get Timestamp
            ##

            # Get seconds / centiseconds (sscc)
            # Note: this is local time
            sec = line[12:16]

            # Get year
            year = line[17:21]

            # Get month
            month = line[21:23]
            
            # Get date
            date = line[23:25]

            # Get hours
            hours = line[25:27]
            minutes = line[27:29]

            h = int(hours)
            m = int(minutes)

            # Check if floor open
            if h > 15 or h < 8 or (h == 8 and m < 30) or (h == 15 and m > 15):
                continue

            timestamp = year + "," + month + "," + date + "," + hours + "," + minutes + "," + sec[0:2] + "," + sec[2:]

            ##
            # Get Bid Bid / Best Ask
            ##
            bbo =  line.split()[2][22:60]
            if bbo == "":
                print line


            try:
                bestBid = int(bbo[0:19])
                bestAsk = int(bbo[19:])
                bookUpdates.append([timestamp, bestBid, bestAsk])
            except:
                time.sleep(1)
                c = c + 1

    print c

    with open(filename + '.top', 'w') as f:
        for update in bookUpdates:
            for item in update:
                try:
                    f.write(str(item))
                    f.write(',')
                except:
                    print item, ' broked'
            f.write('\n')
