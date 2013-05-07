#include<iostream>
#include<random>
#include<vector>
#include<map>
#include<algorithm>

#include <time.h>

using namespace std;

int test(int n){

  // generate random numbers
  random_device rd;
  default_random_engine gen(rd());
  normal_distribution<double> distbid(78600, 10000);
  normal_distribution<double> distask(78505, 10000);

  vector<int> bids;
  vector<int> asks;

  for (int i = 0; i < n; i++){
    bids.push_back(floor(distbid(gen)));
    asks.push_back(floor(distask(gen)));
  }

  // Aggregate S/D into lists [price:qty]
  timespec t0;
  clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t0);
  
  int maxbid = *max_element(bids.begin(), bids.end());
  //int minbid = *min_element(bids.begin(), bids.end());
  int maxask = *max_element(asks.begin(), asks.end());
  int minask = *min_element(asks.begin(), asks.end());
  
  vector<unsigned int> b(maxbid+1);
  vector<unsigned int> a(maxask+1);

  for (unsigned int i = 0; i < bids.size(); i++){
    b[bids[i]]++;
  }
  
  for (unsigned int i = 0; i < bids.size(); i++){
    a[asks[i]]++;
  }
  
  timespec t1, t2;
  clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t1);

  // Find Market Clearing Prices

  int demand = -1;
  int supply = -1;
  int prevd = 0;
  int prevs = 0;

  int guess = 0;
  int prevg = 0;
  
  if (maxbid > minask){
    //guess = int(floor((maxbid + minask) / 2.0));
    //cout << "GS: \t" << guess << endl;
    guess = minask;

    while (1 == 1){

      prevd = demand;
      prevs = supply;

      if (demand == -1 || supply == -1){
	demand = 0;
	supply = 0;

	for (int i = guess; i <= maxbid; i++){
	  demand += b[i];
	}

	for (int i = minask; i <= guess; i++){
	  supply += a[i];
	}
      }
      else{
	// if price goes up
	if (prevg < guess){
	  supply += a[guess];
	  demand -= b[prevg];
	}
	// if price goes down
	else if (prevg > guess){
	  supply -= a[prevg];
	  demand += b[guess];
	}
      }

      // If the Market crosses, exit

      if (demand == supply)
	break;

      if (demand > supply && prevd < prevs){
	if (min(prevd, prevs) > min(demand, supply)){
	  demand = prevd;
	  supply = prevs;
	}
	break;
      }

      if (demand < supply && prevd > prevs){
	if (min(prevd, prevs) > min(demand, supply)){
	  demand = prevd;
	  supply = prevs;
	}
	break;
      }

      prevg = guess;

      if (demand > supply)
	guess += 1;
      else if (demand < supply)
	guess -= 1;
    }
  }
  
  clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t2);

  // Calculate the times for each section of the computation
  
  timespec temp, tempCLEAR, tempAGG2;

  // Total
  temp.tv_nsec = t2.tv_nsec-t0.tv_nsec;
  if (temp.tv_nsec < 0){
    temp.tv_nsec = 1000000000 + temp.tv_nsec;
    temp.tv_sec = t2.tv_sec-t0.tv_sec - 1;
  }
  else{
    temp.tv_sec = t2.tv_sec-t0.tv_sec;    
  }

  // Aggregation
  tempAGG2.tv_nsec = t1.tv_nsec-t0.tv_nsec;
  if (tempAGG2.tv_nsec < 0){
    tempAGG2.tv_nsec = 1000000000 + tempAGG2.tv_nsec;
    tempAGG2.tv_sec = t1.tv_sec-t0.tv_sec - 1;
  }
  else{
    tempAGG2.tv_sec = t1.tv_sec-t0.tv_sec;    
  }


  // Clearing
  tempCLEAR.tv_nsec = t2.tv_nsec-t1.tv_nsec;
  if (tempCLEAR.tv_nsec < 0){
    tempCLEAR.tv_nsec = 1000000000 + tempCLEAR.tv_nsec;
    tempCLEAR.tv_sec = t2.tv_sec-t1.tv_sec - 1;
  }
  else{
    tempCLEAR.tv_sec = t2.tv_sec-t1.tv_sec;    
  }

  cout<<"Total Time: "<<temp.tv_sec<<"s \t \t : \t "<<temp.tv_nsec / 1000000.0<<"ms"<<endl;
  cout<<"Aggregation Time: "<<tempAGG2.tv_sec<<"s \t : \t "<<tempAGG2.tv_nsec / 1000000.0<<"ms"<<endl;
  cout<<"Clearing Time: "<<tempCLEAR.tv_sec<<"s \t : \t "<<tempCLEAR.tv_nsec / 1000000.0<<"ms"<<endl;
  //cout << "maxbid:\t"<<maxbid<<"\t minask:\t"<<minask<<endl;
  cout <<"Market Clearing Price: "<< guess << endl;
  cout << "Demand: " << demand << "\t Supply: "<<supply << endl;
  cout << endl << endl;

  return tempCLEAR.tv_nsec / 1000000.0;
}

int main(){
  //double sum = 0;
  
  for (int i = 1; i < 7; i++){
    cout << "M = " << pow(10,i) << endl;
    test(pow(10,i));
  }
  

  //test(pow(10,5));
}
