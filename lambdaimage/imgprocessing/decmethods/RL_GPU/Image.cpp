#include "tiffio.h"
#include <map>
#include <string.h>
#include <stdlib.h>
#include "common.h"
TIFF * image;
bool getImage_d_w_h(char *filename, int &d, int &w, int &h)
{
    TIFF *image;
    image = TIFFOpen(filename, "r");
    if(image==NULL)
	return false;
    d = TIFFNumberOfDirectories(image);
//    TIFFClose(image);
 //   image = TIFFOpen(filename, "r");
    TIFFGetField(image, TIFFTAG_IMAGEWIDTH, &w); 
  //  TIFFClose(image);
   // image = TIFFOpen(filename, "r");
    TIFFGetField(image, TIFFTAG_IMAGELENGTH, &h);
    TIFFClose(image);
    return true;
}
void readTIFFImage(char *filename, float* buffer,int width,int height,int num)
{
    uint16 photo, bps, spp, fillorder;
    unsigned long imageOffset, result;
    int stripMax;
    unsigned char *buffer1, tempbyte,*buffer2;
    unsigned long bufferSize, count;

    TIFF* tiff = TIFFOpen(filename, "r");
    int nTotalFrame = TIFFNumberOfDirectories(tiff);    
    uint16 bitspersample;
    uint32 samplesperpixel=1;
    uint32 bitsperpixel;
    DWORD dwBytePerLine;
    DWORD dwLeng;
    LPBYTE pData;
    float *bufferTmp;
    int i;
    tsize_t stripSize,stripCount;
    tstrip_t strip;

    TIFFGetField(tiff, TIFFTAG_BITSPERSAMPLE, &bitspersample);
    bitspersample=bitspersample/8;
    TIFFSetDirectory(tiff,num);
    stripSize = TIFFStripSize (tiff);
    stripCount = TIFFNumberOfStrips (tiff);

    if(bitspersample==4)
    {
        bufferTmp=(float*)malloc(sizeof(float)*width*height);
        for (strip = 0; strip < stripCount; strip++)
        {
            TIFFReadEncodedStrip(tiff, strip, bufferTmp+strip*stripSize/4, (tsize_t) -1);
        }
        for(i=0;i<width*height;i++)
        {
            buffer[i]=bufferTmp[i];
        }
        free(bufferTmp);
    }
    else
    {
    imageOffset = 0;
    bufferSize = TIFFNumberOfStrips (tiff) * stripSize;
    buffer2 = (unsigned char *) malloc(bufferSize);
    for(i=0;i<width;i++)
    {
        TIFFReadScanline(tiff,buffer2+i*height*bitspersample,i,samplesperpixel);
    }

    for(i=0;i<width*height;i++)
    {
        if(bitspersample==1)
            buffer[i]=(int)buffer2[i];
//            buffer[i]=(float)buffer2[i];
        else if(bitspersample==2)
            buffer[i]=(int)buffer2[2*i]+((int)buffer2[2*i+1])*256;
 //           buffer[i]=(float)buffer2[2*i]+((float)buffer2[2*i+1])*256;
    }
    free(buffer2);
    }

    TIFFClose(tiff);
}

void writeImage(char *output, float *result,int width,int height,int num)
{
    char out[100];
	strcpy(out, output);
    char str[10];
    // Define an image
   // TIFF *image;
    int i,j;
    float *buffer = (float*)malloc(sizeof(float)*width*height);
    // Open the TIFF file
    for(i=0;i<height;i++)
    {
	    for(j=0;j<width;j++)
	    {
		    buffer[j+(height-i-1)*width]=(float)result[i*width+j];
	    }
    }
    sprintf(str, "%d", num);
    strcat(out, str);
    strcat(out, ".tif");

    //if((image = TIFFOpen(out, "w")) == NULL){
	//    printf("Could not open output.tif for writing\n");
	//    exit(42);
    //}
    // We need to set some values for basic tags before we can add any data
    TIFFSetField(image, TIFFTAG_IMAGEWIDTH, width);
    TIFFSetField(image, TIFFTAG_IMAGELENGTH, height);
    //TIFFSetField(image, TIFFTAG_COMPRESSION, COMPRESSION_NONE);
    TIFFSetField(image, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
    TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
    TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, sizeof(float)*8);
    TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 1);
    TIFFSetField(image, TIFFTAG_SAMPLEFORMAT, SAMPLEFORMAT_IEEEFP);


    TIFFSetField(image, TIFFTAG_COMPRESSION, COMPRESSION_LZW);

    // Write the information to the file
    TIFFWriteEncodedStrip(image, 0, result, width*height*(sizeof(float)));
    // Close the file
    TIFFWriteDirectory(image);
//    TIFFClose(image);
    free(buffer);
}                 
float my_map(float *ff,int length){
	typedef std::map<float,int> Mid;
	Mid paris;
	int tag,frequency;
	float ffmin;
	Mid::iterator loc;
	for(tag=0;tag<length;tag++){
		if((loc=paris.find(ff[tag]))==paris.end()){
			paris.insert(Mid::value_type(ff[tag],1));
		}       
		else{
			loc->second +=1;
		}       
	}       
	ffmin = paris.begin()->first;
	frequency = paris.begin()->second;
	for(Mid::const_iterator it = paris.begin();  it!=paris.end(); it++) {
		if(it->second >= frequency){ 
			if(it->first < ffmin || it->second > frequency){
				ffmin = it->first ;
			}      
			frequency = it->second;
		}    
	}
	return   ffmin;
}
