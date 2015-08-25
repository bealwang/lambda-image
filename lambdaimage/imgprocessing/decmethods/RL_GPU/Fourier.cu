#include <iostream>
#include <cuda_runtime_api.h>
#include <cuda.h>
#include <cufft.h>
const int THREADS=64;
__global__ void kernel_divideStable2(float *data1, float *data2, float threadshold, int len);
__global__ void kernel_multiply_complex(float *data1, float *data2, int len);
__global__ void kernel_multiply_real(float *data1, float *data2, int len);
__global__ void kernel_multiplyConj(float *data1, float *data2, int len);
__global__ void kernel_copy(float *data1, float *data2, int len);
using namespace std;
void inv_forwardDFT(float *data, int nx, int ny, int nz){
    cufftReal *a=(cufftReal*)data;
    cufftComplex *A=(cufftComplex*)data;
    cufftHandle plan_forward;
    
    if(nz==1){
        cufftPlan2d(&plan_forward, nx, ny, CUFFT_R2C);
        cufftExecR2C(plan_forward, a, A);
    }
    else{
//        cout<<"nx= "<<nx<<" ny= "<<ny<<" nz= "<<nz<<endl;
        cufftPlan3d(&plan_forward, nx, ny, nz, CUFFT_R2C);
        cufftExecR2C(plan_forward, a, A);
    }
    cufftDestroy(plan_forward);
}

void inv_inverseDFT(float *data, int nx, int ny, int nz){
    cufftReal *a=(cufftReal*)data;
    cufftComplex *A=(cufftComplex*)data;
    cufftHandle plan_backward;
    
    if(nz==1){
        cufftPlan2d(&plan_backward, nx, ny, CUFFT_C2R);
        cufftExecC2R(plan_backward, A, a);
    }
    else{
        cufftPlan3d(&plan_backward, nx, ny, nz, CUFFT_C2R);
        cufftExecC2R(plan_backward, A, a);
    }
    cufftDestroy(plan_backward);
}

void inv_divideStable2(float *data1, float *data2, float threadshold, int len){
    unsigned long int block=(len+THREADS-1)/THREADS;
    kernel_divideStable2<<<block, THREADS>>>(data1, data2, threadshold, len);
} 
__global__ void kernel_divideStable2(float *data1, float *data2, float threadshold, int len){
    int offset=blockDim.x*blockIdx.x+threadIdx.x;
    if(offset>=len) return;

    if(data2[offset]<threadshold)
        data2[offset]=(float)0;
    else
        data2[offset]=data1[offset]/data2[offset];
}

void inv_multiply_complex(float * data1, float *data2, int len){
    unsigned long int block=(len/2+THREADS-1)/THREADS;
    kernel_multiply_complex<<<block, THREADS>>>(data1, data2, len/2);

}
__global__ void kernel_multiply_complex(float *data1, float *data2, int len){
        int offset=blockDim.x*blockIdx.x+threadIdx.x;
        if(offset>=len) return;

        float temp1=data1[(2*offset)];
        float temp2=data2[(2*offset)];
        data1[(2*offset)]=(temp1*temp2-data1[(2*offset+1)]*data2[(2*offset+1)]);
        data1[(2*offset+1)]=(temp1*data2[(2*offset+1)]+data1[(2*offset+1)]*temp2);
}

void inv_multiply_real(float *data1, float *data2, int len){
    unsigned long int block=(len+THREADS-1)/THREADS;
    kernel_multiply_real<<<block, THREADS>>>(data1, data2, len);
}
__global__ void kernel_multiply_real(float *data1, float *data2, int len){
    int offset=blockDim.x*blockIdx.x+threadIdx.x;
    if(offset>=len) return;
    data1[offset] *= data2[offset];
}
    
void inv_multiplyConj(float *data1, float *data2, int len){
    unsigned long int block=(len/2+THREADS-1)/THREADS;
    kernel_multiplyConj<<<block, THREADS>>>(data1, data2, len/2);
}
__global__ void kernel_multiplyConj(float *data1, float *data2, int len){
    int offset=blockDim.x*blockIdx.x+threadIdx.x;
    if(offset>=len) return;

    float temp1 = data1[(2 * offset)];
    float temp2 = data2[(2 * offset)];
    data1[(2*offset)] = (temp1*temp2+data1[(2*offset+1)]*data2[(2*offset+1)]);
    data1[(2*offset+1)] = (-temp1*data2[(2*offset+1)]+data1[(2*offset+1)]*temp2);
}

void inv_copy(float *data1, float *data2, int len){
    unsigned long int block=(len+THREADS-1)/THREADS;
    kernel_copy<<<block, THREADS>>>(data1, data2, len);
}
__global__ void kernel_copy(float *data1, float *data2, int len){
    int offset=blockDim.x*blockIdx.x+threadIdx.x;
    if(offset>=len) return;
    data1[offset]=data2[offset];
}
