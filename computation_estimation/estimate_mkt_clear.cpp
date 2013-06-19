#include<iostream>
#include<random>
#include<vector>
#include<map>
#include<algorithm>

#include<string>

#include <time.h>

using namespace std;

/*
 *
 * Code from http://stackoverflow.com/questions/15165202/random-number-generator-with-beta-distribution
 * Credit: sftrabbit
 *
 */


template <typename RealType = double>
class beta_distribution
{
public:
  typedef RealType result_type;

  class param_type
  {
  public:
    typedef beta_distribution distribution_type;

    explicit param_type(RealType a = 2.0, RealType b = 2.0)
      : a_param(a), b_param(b) { }

    RealType a() const { return a_param; }
    RealType b() const { return b_param; }

    bool operator==(const param_type& other) const
    {
      return (a_param == other.a_param &&
	      b_param == other.b_param);
    }

    bool operator!=(const param_type& other) const
    {
      return !(*this == other);
    }

  private:
    RealType a_param, b_param;
  };

  explicit beta_distribution(RealType a = 2.0, RealType b = 2.0)
    : a_gamma(a), b_gamma(b) { }
  explicit beta_distribution(const param_type& param)
  : a_gamma(param.a()), b_gamma(param.b()) { }

  void reset() { }

  param_type param() const
  {
    return param_type(a(), b());
  }

  void param(const param_type& param)
  {
    a_gamma = gamma_dist_type(param.a());
    b_gamma = gamma_dist_type(param.b());
  }

  template <typename URNG>
  result_type operator()(URNG& engine)
  {
    return generate(engine, a_gamma, b_gamma);
  }

  template <typename URNG>
  result_type operator()(URNG& engine, const param_type& param)
  {
    gamma_dist_type a_param_gamma(param.a()),
      b_param_gamma(param.b());
    return generate(engine, a_param_gamma, b_param_gamma); 
  }

  result_type min() const { return 0.0; }
  result_type max() const { return 1.0; }

  result_type a() const { return a_gamma.alpha(); }
  result_type b() const { return b_gamma.alpha(); }

  bool operator==(const beta_distribution<result_type>& other) const
  {
    return (param() == other.param() &&
	    a_gamma == other.a_gamma &&
	    b_gamma == other.b_gamma);
  }

  bool operator!=(const beta_distribution<result_type>& other) const
  {
    return !(*this == other);
  }

private:
  typedef std::gamma_distribution<result_type> gamma_dist_type;

  gamma_dist_type a_gamma, b_gamma;

  template <typename URNG>
  result_type generate(URNG& engine,
		       gamma_dist_type& x_gamma,
		       gamma_dist_type& y_gamma)
  {
    result_type x = x_gamma(engine);
    return x / (x + y_gamma(engine));
  }
};

template <typename CharT, typename RealType>
std::basic_ostream<CharT>& operator<<(std::basic_ostream<CharT>& os,
				      const beta_distribution<RealType>& beta)
{
  os << "~Beta(" << beta.a() << "," << beta.b() << ")";
  return os;
}

template <typename CharT, typename RealType>
std::basic_istream<CharT>& operator>>(std::basic_istream<CharT>& is,
				      beta_distribution<RealType>& beta)
{
  std::string str;
  RealType a, b;
  if (std::getline(is, str, '(') && str == "~Beta" &&
      is >> a && is.get() == ',' && is >> b && is.get() == ')') {
    beta = beta_distribution<RealType>(a, b);
  } else {
    is.setstate(std::ios::failbit);
  }
  return is;
}

/*
 *
 * End Code
 *
 */

double test(int n, string dist, vector<double> bidparams, vector<double> askparams){

  // generate random numbers
  random_device rd;
  default_random_engine gen(rd());

  normal_distribution<double> distbid_normal(78600, 10000);
  normal_distribution<double> distask_normal(78505, 10000);
  
  beta_distribution<double> distbid_beta(bidparams[0],bidparams[1]);
  beta_distribution<double> distask_beta(askparams[0],askparams[1]);
  

  vector<int> bids;
  vector<int> asks;

  if (dist == "NORMAL"){
    for (int i = 0; i < n; i++){
      bids.push_back(floor(distbid_normal(gen)));
      asks.push_back(floor(distask_normal(gen)));
    }
  }
  else if (dist == "BETA"){
    for (int i = 0; i < n; i++){
      asks.push_back(775 + floor(60 * distask_beta(gen)));
      bids.push_back(800 - floor(60 * distbid_beta(gen)));		    
    }
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
  /*
    cout<<"Total Time: "<<temp.tv_sec<<"s \t \t : \t "<<temp.tv_nsec / 1000000.0<<"ms"<<endl;
    cout<<"Aggregation Time: "<<tempAGG2.tv_sec<<"s \t : \t "<<tempAGG2.tv_nsec / 1000000.0<<"ms"<<endl;
    cout<<"Clearing Time: "<<tempCLEAR.tv_sec<<"s \t : \t "<<tempCLEAR.tv_nsec / 1000000.0<<"ms"<<endl;
    //cout << "maxbid:\t"<<maxbid<<"\t minask:\t"<<minask<<endl;
    cout <<"Market Clearing Price: "<< guess << endl;
    cout <<"Crosses: " << minask << "\t" << maxbid << endl;
    cout << "Demand: " << demand << "\t Supply: "<<supply << endl;
    cout << endl << endl;
  */
  return (double(tempCLEAR.tv_sec) + double(tempCLEAR.tv_nsec) / 1000000.0);
}

int main(){
  //double sum = 0;
  double time = 0;
  double max = 0;

  int t = 6;

  int maxi, maxj, maxd;

  for (int d = 40; d <= 80; d += 5){
    for (int i = 1; i <= 50; i+=5){
      for (int j = 1; j <= 50; j+=5){

	cout << "IJ:\t" << i << ", " << j << endl;

	vector<double> bp, ap;
	bp.push_back(double(i)/10);
	bp.push_back(double(j)/10);
	ap.push_back(double(i)/10);
	ap.push_back(double(j)/10);
 

	//for (int i = 1; i < 7; i++){
	//cout << "M = " << pow(10,i) << endl;
	//test(pow(10,i),"NORMAL");
	time = test(pow(10,t),"BETA",bp,ap);
	if (time > max){
	  cout << "NEWMAX:\t" << time << endl;
	  max = time;
	  maxi = i;
	  maxj = j;
	  maxd = d;
	}
      }
    }
  }
  
  cout << "MAX: \t " << max << "\t" << maxi << "\t" << maxj << "\t" << maxd << endl;
  //test(pow(10,5));
}
