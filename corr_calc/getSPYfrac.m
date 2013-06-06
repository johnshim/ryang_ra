function [] = getSPYfrac(startdate, enddate)

    % Establish a connection to bbcomm
    % (first one usually fails???)
    c = blp;
    c = blp;

    % Download the requisite data for the ticker and date range
    tickerSPY = 'SPY US Equity';
    tickerSPYNYSE = 'SPY UP Equity';
    
    [d] = history(c, tickerSPY, 'VOLUME', startdate, enddate);
    volSPY = d(:,2);
    
    [d] = history(c, tickerSPYNYSE, 'VOLUME', startdate, enddate);
    volSPYNYSE = d(:,2);
    
    date = d(:,1);
    
    % Calculate Market Share
    share = volSPYNYSE ./ volSPY;
    
    out = {date, volSPY, volSPYNYSE, share};

    
    % Save to csv to be read by python
    dlmwrite(['blp_data_', 'NYSEFRAC', '.csv'], out, 'delimiter', ',', 'precision', 9);
    
    % print avg
    display({startdate, mean(share)});
    
    % Close connection
    close(c);
end