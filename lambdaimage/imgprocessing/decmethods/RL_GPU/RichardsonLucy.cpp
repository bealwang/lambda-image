#include <math.h>
#include <cuda_runtime_api.h>
//#include <fftw3.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <float.h>
#include "RichardsonLucy.h"
#include "Signal.h"
#include "ToolboxFourier.h"
#include "ToolboxSignal.h"
#include "Fourier.h"
bool InitCUDA(int i)
{
    int count = 0;

    cudaGetDeviceCount(&count);
    if(count == 0) {
        fprintf(stderr, "There is no device.\n");
        return false;
    }
    if(i == count) {
        fprintf(stderr, "There is no device supporting CUDA.\n");
        return false;
    }
    cudaSetDevice(i%count);
    return true;
}
RichardsonLucy::RichardsonLucy()
	{
		printf("Hi,you are in RichardsonLucy Deconvolutuon\n");
	}
bool RichardsonLucy::process(Signal &y, Signal &h, int iteration,int ylength)
	{
		ToolboxFourier tbFourier = ToolboxFourier(y.N, y.D);
        int k=0;
       // Signal ybkp;
       // Signal yold;
        
        ToolboxSignal::minConstraint(y, 0, false, tbFourier);

       // ybkp.clone(y);
       // yold.clone(y);
        unsigned long int mem_cost=y.extLength*sizeof(float)*4/1024/1024;
        //printf("mem cost: %lu MB\n", mem_cost);

        float *y_dev;
        float *ybkp_dev;
        float *yold_dev;
        float *h_dev;
        int nx, ny, nz;
        cudaEvent_t start, stop;
        cudaEventCreate(&start);
        cudaEventCreate(&stop);
        
        if(y.D==2){
            nx=y.N[0];
            ny=y.N[1];
            nz=1;
        }
        else{
            nx=y.N[0];
            ny=y.N[1];
            nz=y.N[2];
        }
        int extLength=y.extLength;

        cudaMalloc((void**)&y_dev, sizeof(float)*extLength);
        cudaMalloc((void**)&ybkp_dev, sizeof(float)*extLength);
        cudaMalloc((void**)&yold_dev, sizeof(float)*extLength);
        cudaMalloc((void**)&h_dev, sizeof(float)*extLength);

        cudaMemcpy(y_dev, (float*)&y.array[0], sizeof(float)*extLength, cudaMemcpyHostToDevice);
                inv_copy(ybkp_dev, y_dev, extLength);
                inv_copy(yold_dev, y_dev, extLength);
       // cudaMemcpy(ybkp_dev, (float*)&ybkp.array[0], sizeof(float)*extLength, cudaMemcpyHostToDevice);
       // cudaMemcpy(yold_dev, (float*)&yold.array[0], sizeof(float)*extLength, cudaMemcpyHostToDevice);
        cudaMemcpy(h_dev, (float*)&h.array[0], sizeof(float)*extLength, cudaMemcpyHostToDevice);

        inv_forwardDFT(yold_dev, nx, ny, nz);
        inv_forwardDFT(h_dev, nx, ny, nz);

        cudaEventRecord(start, 0);
        for(k=1; k<=iteration; k++){

            //printf("iteration: %d\n",k);
            inv_multiply_complex(yold_dev, h_dev, extLength);

            inv_inverseDFT(yold_dev, nx, ny, nz);

            inv_divideStable2(ybkp_dev, yold_dev, 1.0E-007F, extLength);

            inv_forwardDFT(yold_dev, nx, ny, nz);

            inv_multiplyConj(yold_dev, h_dev, extLength);

            inv_inverseDFT(yold_dev, nx, ny, nz);

            inv_multiply_real(y_dev, yold_dev, extLength);

            if(k<iteration){
                inv_copy(yold_dev, y_dev, extLength);
                inv_forwardDFT(yold_dev, nx, ny, nz);
            }
        }

        cudaEventRecord(stop, 0);
        cudaEventSynchronize(stop);
        float elapasedTime;
        cudaEventElapsedTime(&elapasedTime, start, stop);
        //printf("gpu kernel time: %f\n", elapasedTime);
        printf("gpu_3d_kernel: %dx%dx%d    iter: %d   time: %f\n", y.N[2],y.N[1],y.N[0],iteration,elapasedTime/1000.0f);

        cudaMemcpy((float*)&y.array[0], y_dev, sizeof(float)*extLength, cudaMemcpyDeviceToHost);
        cudaFree(y_dev);
        cudaFree(ybkp_dev);
        cudaFree(yold_dev);
        cudaFree(h_dev);
        return true;
}
