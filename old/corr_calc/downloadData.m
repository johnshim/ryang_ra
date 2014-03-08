function [] = downloadData()
    fn = 'futures_blp_ticksonly.csv';
    
    startdate = '1/1/2011';
    enddate = '12/31/2011';
    
    fail = 0;
    
    futureslist = importdata(fn);
    for i = 1:size(futureslist)
        ticker = futureslist{i}; %(1:size(futureslist{i}, 2)-1);
        try
            getFutures(ticker, startdate, enddate);
        catch e
            display([ticker, ' failed'])
            display(e)
            fail = fail + 1;
        end
    end
    
    
    display(fail)
end