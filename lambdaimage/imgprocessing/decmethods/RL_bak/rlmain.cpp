#include <iostream>
#include <getopt.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <vector>
#include <iomanip>
#include "tiff.h"
#include "tiffio.h"
#include <stdlib.h>
#include "image.h"
#include "Signal.h"
#include "ToolboxSignal.h"
#include "RichardsonLucy.h"
#include "ToolboxFourier.h"
using namespace std;
extern "C" void deconvRL(float *yy, int y_nx, int y_ny, int y_nz, float* hh, int h_nx, int h_ny, int h_nz, int iter);
void deconvRL(float *yy, int y_nx, int y_ny, int y_nz, float* hh, int h_nx, int h_ny, int h_nz, int iter){
	int iteration = iter;

	int bw, bh, bd;
    bw=y_nx;
    bh=y_ny;
    bd=y_nz;
    cout<<"bw= "<<bw<<endl;
    cout<<"bh= "<<bh<<endl;
    cout<<"bd= "<<bd<<endl;
	float *tifpic = (float*)malloc(sizeof(float)*bw*bh*bd);
    for(int i=0; i<bw*bh*bd; i++) 
        tifpic[i]=yy[i];

    //read psf
	int kw, kh, kd;
    kw=h_nx;
    kh=h_ny;
    kd=h_nz;
	float *tifpsf = (float*)malloc(sizeof(float)*kw*kh*kd);
    for(int i=0; i<kw*kh*kd; i++)
        tifpsf[i]=hh[i];

	Signal y(tifpic, bd, bh, bw), h(tifpsf, kd, kh, kw);
	float background = ToolboxSignal::minimum(y);
	ToolboxSignal::addConstant(y, -background, 0);
	ToolboxSignal::multiplyConstant(h, 1.0 / ToolboxSignal::sum(h));

	int* shift =(int*)calloc(h.D,sizeof(int));
	for (int d = 0; d < h.D;) { shift[d] = (h.N[d] / 2); ++d; }
	ToolboxSignal::fftShift(h, shift, h.D);
	int ylength = bw*bh*bd;
	int hlength = kw*kh*kd;
	if (!(ToolboxSignal::checkCompatibility(y, h))) {
	    cout<<"check Compatibility"<<endl;
		if (!(ToolboxSignal::resizePSF(y.N,h,y.D))) {
			printf("PSF image and current image are of incompatible sizes.\nThis means that they are either of different dimension (e.g. a 2D PSF and a 3D image)\n or that the PSF has greater dimensions (e.g. a bigger width) than the image.");
            return ;
		}
	}

	RichardsonLucy::process(y,h,iteration,ylength);

    for(int k=0; k<bd; k++){
        int bw, bh, ebw, ebh;
        if(y.D==2){
            bw=y.N[1]; bh=y.N[0];
            ebw=y.extN[1]; ebh=y.extN[0];
        }
        else{
            bw=y.N[2]; bh=y.N[1];
            ebw=y.extN[2]; ebh=y.extN[1];
        }
        for(int j=0; j<bh; j++)
            for(int i=0; i<bw; i++){
                yy[k*bh*bw+i+bw*j]=y.array[k*ebw*ebh+j*ebw+i];
            }
    }
     
    free(tifpic);
    free(tifpsf);
    free(shift);
    return ;
}
