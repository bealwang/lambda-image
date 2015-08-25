
bool getImage_d_w_h(char *filename, int &d, int &w, int &h);
void readTIFFImage(char *filename, float* buffer,int width,int height,int num);
void writeImage(char *output, float *result,int width,int height,int num);
float my_map(float *ff, int lenght);
