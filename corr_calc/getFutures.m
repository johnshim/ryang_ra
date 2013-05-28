function [] = getFutures(ticker, startdate, enddate)

    % Get the Bloomberg API jar
    %cd 'C:\Users\ryang8\Downloads'
    %javaaddpath('.\blpapi-3.6.1-0.jar')

    % Establish a connection to bbcomm
    % (first one usually fails???)
    c = blp;
    c = blp;

    % Download the requisite data for the ticker and date range
    [d] = history(c, ticker, 'LAST_PRICE', startdate, enddate)
    settle = d(:,2);
    
    [d] = history(c, ticker, 'VOLUME', startdate, enddate)
    vol = d(:,2);
    
    display([settle, vol])
    vol(1:10)
    
    % Save to csv to be read by python
    dlmwrite('blp_data_temp.csv', [settle,vol], 'delimiter', ',', 'precision', 9);
    
    % Close connection
    close(c);
end