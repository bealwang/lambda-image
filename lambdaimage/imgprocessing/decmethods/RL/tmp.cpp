#include <iostream>
using namespace std;

extern "C" void deconvRL(float *yy, int y_nx, int y_ny, int y_nz, float* hh, int h_nx, int h_ny, int h_nz, int iter);
void deconvRL(float *yy, int y_nx, int y_ny, int y_nz, float* hh, int h_nx, int h_ny, int h_nz, int iter){
	cout<<"hello from c++"<<endl;
}
