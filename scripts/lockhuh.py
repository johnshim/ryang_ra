import tables

thedate = "20081221"

f = tables.openFile('/datastore/dbd/auction/book_data/cme/' + thedate)

i = 0

book = f.root.ESH9.books

while True:
    try:
        if book[i]['bid'][0][0] == book[i]['ask'][0][0]:
            print book[i]['timestamp_s'], book[i]['bid'][0][0]
        i = i + 1
    except:
        print i
        break
        
