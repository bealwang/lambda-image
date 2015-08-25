#include "ToolboxFourier.h"
#include "Signal.h"
#include <fftw3.h>
#include <stdlib.h>
ToolboxFourier::ToolboxFourier(int* dim, int dimlength)
{
        fftwf_init_threads();
        fftwf_plan_with_nthreads(4);
        length = dimlength;
        dimensions = (int*)calloc(length,sizeof(int));
        for (int i = 0; i < length; ++i) {
                dimensions[i] = dim[i]; 
        }
}
ToolboxFourier::~ToolboxFourier(){
    free(dimensions);
    fftwf_cleanup_threads();
}
void ToolboxFourier::forwardDFT(Signal &s)
{
        //    if(useFFTW)
        forwardFFTW(s);
        //    else
        //        forwardFFT(s);
}

void ToolboxFourier::inverseDFT(Signal &s)
{
        //    if(useFFTW)
        inverseFFTW(s);
        //   else
        //       inverseFFT(s);
}
bool ToolboxFourier::forwardFFTW(Signal &s){
        fftwf_complex *out;
        fftwf_plan plan_forward;
        int nx=dimensions[0];
        int ny=dimensions[1];
        float *in=(float*)&s.array[0];
        out=(fftwf_complex*)&s.array[0];
        if(length==2){
           plan_forward=fftwf_plan_dft_r2c_2d(nx, ny, in, out, FFTW_ESTIMATE);
        }
        else{
           int nz=dimensions[2];
           plan_forward=fftwf_plan_dft_r2c_3d(nx, ny, nz, in, out, FFTW_ESTIMATE);
        }
        fftwf_execute(plan_forward);
        fftwf_destroy_plan(plan_forward);
        s.isReal=false;
        return true;
}
bool ToolboxFourier::inverseFFTW(Signal &s){
        int nx=dimensions[0];
        int ny=dimensions[1];
        float *in2=(float*)&s.array[0];
        fftwf_complex *out=(fftwf_complex*)&s.array[0];
        fftwf_plan plan_backward;
        if(length==2){
            plan_backward=fftwf_plan_dft_c2r_2d(nx, ny, out, in2, FFTW_ESTIMATE);
        }
        else{
            int nz=dimensions[2];
            plan_backward=fftwf_plan_dft_c2r_3d(nx, ny, nz, out, in2, FFTW_ESTIMATE);
        }
        fftwf_execute(plan_backward);
        s.isReal=true; 
        return true;
}
