#include "ToolboxSignal.h"
#include "Signal.h"
#include "ToolboxFourier.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
using namespace std;
float ToolboxSignal::minimum(Signal &s)
{
	float min = 100000002004087730000.0F;
	if (s.isReal) {
		int lengthX = s.N[(s.D - 1)];
		int eLengthX = s.extN[(s.D - 1)];
		for (int i = 0; i < s.extLength; ++i)
			if ((i % eLengthX < lengthX) && (s.array[i] < min))
				min = s.array[i];
		return min;
	}

	for (int i = 0; i < s.extLength; i += 2) {
		float temp = s.array[i] * s.array[i] + s.array[(i + 1)] * s.array[(i + 1)];
		if (temp < min)
			min = temp;
	}
	return sqrt(min);
}
void ToolboxSignal::addConstant(Signal &s, float real, float imag)
{
	int i;
	if (s.isReal)
		for (i = 0; i < s.extLength;) {
		s.array[i] += real; ++i;
		}
	else
		for (i = 0; i < s.extLength; i += 2) {
		s.array[i] += real;
		s.array[(i + 1)] += imag;
		}
}
	void ToolboxSignal::multiplyConstant(Signal &s, float p)
	{
		for (int i = 0; i < s.extLength;) {
			s.array[i] *= p; ++i;
		}
	}
	bool ToolboxSignal::multiply(Signal &s1, Signal &s2)
	{
		if (checkCompatibility(s1, s2)) {
			if (s1.isReal)
				for (int i = 0; i < s1.extLength;i++) {
				s1.array[i] *= s2.array[i];
				}

			else
				for (int i = 0; i < s1.extLength / 2; ++i) {
				float temp1 = s1.array[(2 * i)];
				float temp2 = s2.array[(2 * i)];
				s1.array[(2 * i)] = (temp1 * temp2 - s1.array[(2 * i + 1)] * s2.array[(2 * i + 1)]);
				s1.array[(2 * i + 1)] = (temp1 * s2.array[(2 * i + 1)] + s1.array[(2 * i + 1)] * temp2);
				}

			return true;
		}
		return false;
	}
	
	bool ToolboxSignal::multiplyConj(Signal &s1, Signal &s2)
	{
		if ((!(s1.isReal)) && (checkCompatibility(s1, s2)))
		{
			for (int i = 0; i < s1.extLength / 2; ++i) {
				float temp1 = s1.array[(2 * i)];
				float temp2 = s2.array[(2 * i)];
				s1.array[(2 * i)] = (temp1 * temp2 + s1.array[(2 * i + 1)] * s2.array[(2 * i + 1)]);
				s1.array[(2 * i + 1)] = (-temp1 * s2.array[(2 * i + 1)] + s1.array[(2 * i + 1)] * temp2);
			}
			return true;
		}
		return false;
	}

	bool ToolboxSignal::add(Signal s1, Signal s2)
	{
		if (checkCompatibility(s1, s2)) {
			for (int i = 0; i < s1.extLength;) { s1.array[i] += s2.array[i]; ++i; }
			return true;
		}
		return false;
	}

	bool ToolboxSignal::addAbs(Signal s1, Signal s2)
	{
		if (checkCompatibility(s1, s2)) {
			for (int i = 0; i < s1.extLength;) { s1.array[i] += abs(s2.array[i]); ++i; }
			return true;
		}
		return false;
	}

	void ToolboxSignal::divideStable(Signal s1, Signal s2, float threshold)
	{
		if (s1.isReal) {
			for (int i = 0; i < s1.extLength; ++i)
				if (s2.array[i] < threshold) s1.array[i] = 0;
				else s1.array[i] /= s2.array[i];


		}
		else
			for (int i = 0; i < s1.extLength / 2; ++i) {
			float module = s2.array[(2 * i)] * s2.array[(2 * i)] + s2.array[(2 * i + 1)] * s2.array[(2 * i + 1)];
			if (sqrt(module) < threshold) {
				s1.array[(2 * i)] = 0;
				s1.array[(2 * i + 1)] = 0;
			}
			else {
				float temp = s1.array[(2 * i)];
				s1.array[(2 * i)] = ((s1.array[(2 * i)] * s2.array[(2 * i)] + s1.array[(2 * i + 1)] * s2.array[(2 * i + 1)]) / module);
				s1.array[(2 * i + 1)] = ((s1.array[(2 * i + 1)] * s2.array[(2 * i)] - temp * s2.array[(2 * i + 1)]) / module);
			}
			}
	}

	bool ToolboxSignal::divideStable2(Signal &s1, Signal &s2, float threshold)
	{
		if (checkCompatibility(s1, s2)) {
			if (s1.isReal) {
				for (int i = 0; i < s1.extLength; ++i)
					if (s2.array[i] < threshold) s2.array[i] =(float)0;
					else s2.array[i] = (s1.array[i] / s2.array[i]);


			}
			else
				for (int i = 0; i < s1.extLength / 2; ++i) {
				float module2 = s2.array[(2 * i)] * s2.array[(2 * i)] + s2.array[(2 * i + 1)] * s2.array[(2 * i + 1)];
				if (sqrt(module2) < threshold) {
					s2.array[(2 * i)] = 0;
					s2.array[(2 * i + 1)] = 0;
				}
				else {
					float temp = s2.array[(2 * i)];
					s2.array[(2 * i)] = ((s1.array[(2 * i)] * s2.array[(2 * i)] + s1.array[(2 * i + 1)] * s2.array[(2 * i + 1)]) / module2);
					s2.array[(2 * i + 1)] = ((s1.array[(2 * i + 1)] * temp - s1.array[(2 * i)] * s2.array[(2 * i + 1)]) / module2);
				}
				}

			return true;
		}
		return false;
	}

	bool ToolboxSignal::checkCompatibility(Signal &s1, Signal &s2)
	{
		if (s1.D != s2.D) return false;
		if (s1.isReal != s2.isReal) return false;
		//if (s1.length != s2.length) return false;
		if (s1.extLength != s2.extLength) return false;
		for (int d = 0; d < s1.D; ++d)
			if (s1.N[d] != s2.N[d]) return false;

		for (int d = 0; d < s1.D; ++d)
			if (s1.extN[d] != s2.extN[d]) return false;
		return true;
	}

	bool ToolboxSignal::resizePSF(int* dim, Signal &s, int dimlength)
	{
		if (!(s.isReal)) {
			return false;
		}
		if (dimlength != s.D) {
			return false;
		}
		for (int i = 0; i < dimlength; ++i) {
			if (s.N[i] > dim[i])
				return false;
		}
		Signal signalOld = Signal(s.N, s.D);
		for (int i = 0; i < s.extLength; ++i)
			signalOld.array[i] = s.array[i];
		for (int i = 0; i < s.D; ++i){
			signalOld.N[i] = s.N[i];
		signalOld.extN[i] = s.extN[i];
        }
		signalOld.length = s.length;
		signalOld.extLength = s.extLength;
		signalOld.isReal = true;
		signalOld.D = s.D;

		Signal dummySignal = Signal(dim, dimlength);
		for (int i = 0; i < dummySignal.extLength; ++i){
			if (i < s.array.size())
				s.array[i] = dummySignal.array[i];
			else
				s.array.push_back(dummySignal.array[i]);
		}
		for (int i = 0; i < dummySignal.D; ++i){
			s.N[i] = dummySignal.N[i];
            s.extN[i] = dummySignal.extN[i];
        }
		s.length = dummySignal.length;
		s.extLength = dummySignal.extLength;
		s.isReal = true;
		s.D = dummySignal.D;
		int* factorOld =(int*)calloc(dimlength,sizeof(int));
		int* factorNew =(int*)calloc(dimlength, sizeof(int));
		for (int i = 0; i < dimlength; ++i) {
			factorOld[i] = 1;
			factorNew[i] = 1;
			for (int j = i + 1; j < dimlength; ++j) {
				factorOld[i] *= signalOld.extN[j];
				factorNew[i] *= s.extN[j];
			}
		}
        
       // cout<<"signalOld ======"<<endl;
       // signalOld.print_signal();
       // cout<<"signal s ======"<<endl;
       // s.print_signal();
       // cout<<"factorOld len="<<dimlength<<endl;
       // cout<<"factorOld[0]="<<factorOld[0]<<" factorOld[1]="<<factorOld[1]<<endl;
       // cout<<"factorNew[0]="<<factorNew[0]<<" factorNew[1]="<<factorNew[1]<<endl;

		resizePSFRecursive(signalOld, s, 0, 0, factorOld, factorNew, 0);

       // cout<<"after resizePsfrecursive"<<endl;
       // cout<<"signalOld ======"<<endl;
       // signalOld.print_signal();
       // cout<<"signal s ======"<<endl;
       // s.print_signal();
       // cout<<"factorOld len="<<dimlength<<endl;
       // cout<<"factorOld[0]="<<factorOld[0]<<" factorOld[1]="<<factorOld[1]<<endl;
       // cout<<"factorNew[0]="<<factorNew[0]<<" factorNew[1]="<<factorNew[1]<<endl;


        		return true;
	}
	float ToolboxSignal::sum(Signal &s)
	{
		int lengthX;
		float sum = 0;
		if (s.isReal)
		{
			lengthX = s.N[(s.D - 1)];
			int extendedLengthX = s.extN[(s.D - 1)];
			int i;
			for (i = 0; i < s.extLength; ++i)
				if (i % extendedLengthX < lengthX) 
					sum += s.array[i];
			//printf("i = %d\n",i);

		}
		else
		{
			lengthX = s.extN[(s.D - 1)] / 2;
			for (int i = 0; i < s.extLength / 2; ++i)
				if ((((lengthX % 2 == 0) || (i % lengthX != lengthX - 1))) && (i % lengthX != 0)) sum += 2 * (float)sqrt(s.array[(2 * i)] * s.array[(2 * i)] + s.array[(2 * i + 1)] * s.array[(2 * i + 1)]);
				else sum += (float)sqrt(s.array[(2 * i)] * s.array[(2 * i)] + s.array[(2 * i + 1)] * s.array[(2 * i + 1)]);
		}

		return sum;
	}
	bool ToolboxSignal::clipBelow(Signal &s, float min)
	{
		bool changed = false;
		for (int i = 0; i < s.extLength; ++i)
			if (s.array[i] < min) {
			s.array[i] = min;
			changed = true;
			}

		return changed;
	}

	void ToolboxSignal::transfer(Signal &s1, Signal &s2)
	{

		s1.D = s2.D;
		s1.isReal = s2.isReal;

		s1.array = s2.array;
		s1.N = s2.N;
		s1.extN = s2.extN;

		//s1.length = s2.length;
		s1.extLength = s2.extLength;
	}

	bool ToolboxSignal::copy(Signal &s1, Signal &s2)
	{
		/*if ((s1 == NULL) || (s2 == NULL))
		return false;*/
		s1.isReal = s2.isReal;
		if (!(checkCompatibility(s1, s2))) {
			return false;
		}

		for (int i = 0; i < s1.extLength; ++i)
			s1.array[i] = s2.array[i];
		return true;
	}

	void ToolboxSignal::minConstraint(Signal &s, float min, bool saveMemory, ToolboxFourier &sFft)
	{
		/*if ((!(s.isReal)) && (!(saveMemory))) {
			Signal newS;
			newS.D = s.D; newS.isReal = s.isReal; newS.extLength = s.extLength;
			for (int q = 0; q < s.D; q++){
				newS.N[q] = s.N[q]; newS.extN[q] = s.extN[q];
			}
			for (int g = 0; g < s.extLength; g++){
				newS.array[g] = s.array[g];
			}
			sFft.inverseDFT(newS);

			if (clipBelow(newS, 0)) {
				transfer(s, newS);
				//newS = NULL;
				sFft.forwardDFT(s);
			}

		}
		else if ((!(s.isReal)) && (saveMemory)) {
			sFft.inverseDFT(s);
			clipBelow(s, 0);
			sFft.forwardDFT(s);
		}*/
		if (s.isReal) {
			clipBelow(s, 0);
		}
	}
	void ToolboxSignal::recursiveFftShift1D(Signal &s, int dimension, int shift, int currentDimension, int* coord, int coordlength)
	{
		int i;
		if ((currentDimension < s.D) && (currentDimension >= 0)) {
			if (currentDimension == dimension) {
				++currentDimension;
				recursiveFftShift1D(s, dimension, shift, currentDimension, coord, coordlength);
			}
			else {
				int newDimension = currentDimension + 1;
				for (i = 0; i < s.N[currentDimension]; ++i) {
				coord[currentDimension] = i;
					recursiveFftShift1D(s, dimension, shift, newDimension, coord, coordlength);
				}
			}

		}
		else if (currentDimension == s.D) {
			float* copy = new float[s.N[dimension]];
			for (i = 0; i < s.N[dimension]; ++i) {
				coord[dimension] = i;
				copy[i] = s.array[getPositionReal(coord, s, coordlength)];
			}
			for (i = 0; i < s.N[dimension]; ++i) {
				coord[dimension] = (i + shift);
				s.array[getPositionReal(coord, s, coordlength)] = copy[i];
			}
		}
	}
	void ToolboxSignal::fftShift1D(Signal &s, int dimension, int shift)
		{
			if ((dimension >= s.D) || (!(s.isReal))) {
				return;
			}

			int* coord = (int*)calloc(s.D,sizeof(int));
			recursiveFftShift1D(s, dimension, shift, 0, coord, s.D);
		}
	bool ToolboxSignal::fftShift(Signal &s, int* shift, int shiftlength)
	{
		if ((s.D != shiftlength) || (!(s.isReal)))
			return false;
		for (int i = 0; i < shiftlength; ++i)
			fftShift1D(s, i, shift[i]);
		return true;
	}
	void ToolboxSignal::resizePSFRecursive(Signal &signalOld, Signal &signalNew, int offsetOld, int offsetNew, int* factorOld, int* factorNew, int currentDim)
	{
		int nextDim = currentDim + 1;
		int half1 = (signalOld.N[currentDim] + 1) / 2;
		int half2 = signalOld.N[currentDim] / 2;
		int offset = signalNew.N[currentDim] - signalOld.N[currentDim];
		int i, con, offloc;
		if (currentDim < signalOld.D - 1) {
			int offsetOldModified;
			int offsetNewModified;
			for (i = 0; i < half1; ++i) {
				offsetOldModified = offsetOld + factorOld[currentDim] * i;
				offsetNewModified = offsetNew + factorNew[currentDim] * i;
				resizePSFRecursive(signalOld, signalNew, offsetOldModified, offsetNewModified, factorOld, factorNew, nextDim);
			}
			for (i = half1; i < signalOld.N[currentDim]; ++i) {
				offsetOldModified = offsetOld + factorOld[currentDim] * i;
				offsetNewModified = offsetNew + factorNew[currentDim] * (offset + i);
				resizePSFRecursive(signalOld, signalNew, offsetOldModified, offsetNewModified, factorOld, factorNew, nextDim);
			}
		}
		else {
			//System.arraycopy(signalOld.array, offsetOld, signalNew.array, offsetNew, half1);
			int dst_offset=offsetNew;
            int src_offset=offsetOld;
			for (con = 0; con < half1; con++){
				//if ()
				signalNew.array[dst_offset++] = signalOld.array[src_offset++];
			}
			//System.arraycopy(signalOld.array, offsetOld + half1, signalNew.array, offsetNew + offset + half1, half2);
			dst_offset=offsetNew+offset+half1;
            src_offset=offsetOld+half1;
			for (con = 0; con < half2; con++){
				signalNew.array[dst_offset++] = signalOld.array[src_offset++];
			}
		}
	}
	int ToolboxSignal::getPositionReal(int* coord, Signal &s, int coordlength)
	{
		int position = 0;
		int factor = 1;
		for (int i = 0; i < coordlength; ++i)
		{
			int temp = coord[i];
			temp %= s.N[i];
			if (temp < 0)
				temp += s.N[i];

			factor = 1;
			for (int j = i + 1; j < coordlength; ++j)
				factor *= s.extN[j];

			position += temp * factor;
		}
		return position;
	}
	

	
