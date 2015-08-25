#include <stdlib.h>
#include <stdio.h>
extern void deconvRL(float *yy, int y_nx, int y_ny, int y_nz, float* hh, int h_nx, int h_ny, int h_nz, int iter);


void deconv(float *y, int y_nx, int y_ny, int y_nz, float* h, int h_nx, int h_ny, int h_nz, int iter){
    int i=0;
    float sum=0.0;
    
    printf("inv deconv from \n");
    deconvRL(y, y_nx, y_ny, y_nz, h, h_nx, h_ny, h_nz, iter);
    
    printf("inv C \n");

    //for(i=0; i<y_nx*y_ny*y_nz; i++)
    //    y[i]+=10;
}
