#include<iostream>
#include<random>
#include<vector>
#include<map>

#include <time.h>

using namespace std;

int main(){

  // Parameters
  const int n = 100000;


  // generate random numbers
  default_random_engine gen;
  normal_distribution<double> distbid(1000, 5);
  normal_distribution<double> distask(1010, 5);

  vector<int> bids;
  vector<int> asks;

  for (int i = 0; i < n; i++){
    bids.push_back(floor(distbid(gen)));
    asks.push_back(floor(distask(gen)));
  }

  timespec t1, t2;
  clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t1);

  // Aggregate S/D into Maps
  map<int, int> bidMap;
  map<int, int> askMap;

  for (int i = 0; i < bids.size(); i++){
    bidMap[bids[i]]++;
  }

  for (int i = 0; i < asks.size(); i++){
    askMap[asks[i]]++;
  }

  // Find Market Clearing Prices

  cout << bidMap.begin()->first << " " << bidMap.rbegin()->first << endl;
  cout << askMap.begin()->first << " " << askMap.rbegin()->first << endl;

  int maxbid = bidMap.rbegin()->first;
  int minask = askMap.begin()->first;

  int demand = 0;
  int supply = 0;
  int prevd = 0;
  int prevs = 0;

  int guess = 0;

  if (maxbid > minask){
    guess = int(floor((maxbid + minask) / 2.0));

    while (1 == 1){
      prevd = demand;
      prevs = supply;

      demand = 0;
      supply = 0;

      for (int i = guess; i <= maxbid; i++){
	map<int, int>::iterator it = bidMap.find(i);
	if (it != bidMap.end())
	  demand += bidMap[i];
      }

      for (int i = minask; i <= guess; i++){
	map<int, int>::iterator it = askMap.find(i);
	if (it != askMap.end())
	  supply += askMap[i];
      }

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

      if (demand > supply)
	guess += 1;

      if (demand < supply)
	guess -= 1;


    }
  }

  clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t2);

  timespec temp;
  temp.tv_sec = t2.tv_sec-t1.tv_sec;
  temp.tv_nsec = t2.tv_nsec-t1.tv_nsec;

  cout<<temp.tv_sec<<":"<<temp.tv_nsec / 1000000<<endl;

  cout << guess << endl;

}
