#include "Signal.h"
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
using namespace std;
    void Signal::print_signal(){
        cout<<"D="<<D<<endl;
        cout<<"isReal="<<isReal<<endl;
        cout<<"N[0]="<<N[0]<<" N[1]="<<N[1]<<endl;
        cout<<"extN[0]="<<extN[0]<<" extN[1]"<<extN[1]<<endl;
        cout<<"lenght="<<length<<endl;
        cout<<"extLenght"<<extLength<<endl;
        cout<<"arry.size="<<array.size()<<endl;
        cout<<"array[0]="<<array[0]<<endl;
        cout<<"array[1]="<<array[1]<<endl;
        cout<<"array[100]="<<array[100]<<endl;
       // cout<<"array[2071]="<<array[2071]<<endl;
        cout<<"array[-1]="<<array[array.size()-1]<<endl;
    }
    Signal::Signal(){
        N=NULL;
        extN=NULL;
    }
    Signal::~Signal(){
        free(N);
        free(extN);
    }
    void Signal::clone(Signal &src){
       D=src.D;
       isReal=src.isReal;
       delete N;
       delete extN;
       N=(int*)malloc(sizeof(int)*D);
       extN=(int*)malloc(sizeof(int)*D);
       for(int i=0; i<D; i++){
         N[i]=src.N[i];
         extN[i]=src.extN[i];
       }
       length=src.length;
       extLength=src.extLength;
       array.resize(src.array.size());
       for(int i=0; i<src.array.size(); i++)
            array[i]=src.array[i];
    } 
            
	Signal::Signal(int* M, int Mlength)
	{
		isReal = true;
		D = Mlength;
		N = (int *)calloc(D, sizeof(int));
		extN = (int *)calloc(D, sizeof(int));
		for (int i = 0; i < Mlength; i++){ 
			N[i] = M[i]; 
		}
		for (int i = 0; i < Mlength; i++){ 
			extN[i] = M[i]; 
		}
		extN[(D - 1)] = (2 * (M[(D - 1)] / 2 + 1));
		length = 1;
		extLength = 1;
		for (int i = 0; i < D; ++i) {
			length *= N[i];
			extLength *= extN[i];
		}
		for (int i = 0; i < extLength; ++i) {
			array.push_back(0);
		}
	}
	Signal::Signal(float* im, int depth, int height, int width)
	{
		isReal = true;
		//float *temp;
		if (depth == 1) {
			D = 2;
			N = new int[2];
			extN = new int[2];
			N[0] = height;
			extN[0] = N[0];
			N[1] = width;
			extN[1] = (2 * (N[1] / 2 + 1));
			length = (N[0] * N[1]);
			extLength = (extN[0] * extN[1]);
			int x, y, contribY, conbY;
			float *temp = (float *)calloc(extLength,sizeof(float));
			for (y = 0; y < N[0]; ++y) {
				contribY = y * extN[1];
				conbY = y * N[1];
				for (x = 0; x < N[1];) {
					temp[x + contribY] = im[(x + conbY)];
					++x;
				}
			}
			for (y = 0; y < extN[0]; ++y) {
				contribY = y * extN[1];
				for (x = 0; x < extN[1];) {
					array.push_back(temp[(x + contribY)]);
					++x;
				}
			}
			free(temp);
		}
		else {
			D = 3;
			N = new int[3];
			extN = new int[3];
			N[0] = depth;
			extN[0] = N[0];
			N[1] = height;
			extN[1] = N[1];
			N[2] = width;
			extN[2] = (2 * (N[2] / 2 + 1));

			length = (N[0] * N[1] * N[2]);
			extLength = (extN[0] * extN[1] * extN[2]);

			int sliceArea = extN[2] * extN[1];
			int area = N[2] * N[1];
			float *temp = (float *)calloc(extLength, sizeof(float));
			for (int z = 0; z < N[0]; ++z) {
				int contribZ = z * sliceArea;
				int conbZ = z * area;
				for (int y = 0; y < N[1]; ++y) {
					int contribYZ = contribZ + y * extN[2];
					int conbYZ = conbZ + y * N[2];
					for (int x = 0; x < N[2];x++) {
						temp[x + contribYZ] = im[(x + conbYZ)];
					}
				}
			}
			for (int z = 0; z < N[0]; ++z) {
				int contribZ = z * sliceArea;
				for (int y = 0; y < N[1]; ++y) {
					int contribYZ = contribZ + y * extN[2];
					for (int x = 0; x < extN[2];x++) {
						array.push_back(temp[(x + contribYZ)]);
					}
				}
			}
			free(temp);
		}
		
	}

	int Signal::mirror(int k, int K)
	{
		if (k < 0) k = -k;
		k %= (2 * K - 2);
		if (k >= K) k = 2 * K - 2 - k;
		return k;
	}
