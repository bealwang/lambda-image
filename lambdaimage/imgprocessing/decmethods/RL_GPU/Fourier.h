void inv_forwardDFT(float *data, int nx, int ny, int nz);
void inv_inverseDFT(float *data, int nx, int ny, int nz);
void inv_divideStable2(float *data1, float *data2, float threadshold, int len);
void inv_multiply_complex(float * data1, float *data2, int len);
void inv_multiply_real(float *data1, float *data2, int len);
void inv_multiplyConj(float *data1, float *data2, int len);
void inv_copy(float *data1, float *data2, int len);
