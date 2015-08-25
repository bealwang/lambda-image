#include <math.h>
#include <fftw3.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <float.h>
#include "RichardsonLucy.h"
#include "Signal.h"
#include "ToolboxFourier.h"
#include  "ToolboxSignal.h"
#include <iostream>
using namespace std;
RichardsonLucy::RichardsonLucy()
	{
		printf("Hi,you are in RichardsonLucy Deconvolutuon\n");
	}
bool RichardsonLucy::process(Signal &y, Signal &h, int iteration,int ylength)
	{
		ToolboxFourier tbFourier = ToolboxFourier(y.N, y.D);
        int k=0;
        Signal ybkp;
        Signal yold;
        
        ToolboxSignal::minConstraint(y, 0, false, tbFourier);
        
        cout<<"extLenght= "<<y.extLength<<endl;

        ybkp.clone(y);
        yold.clone(y);

        tbFourier.forwardDFT(yold);
        tbFourier.forwardDFT(h);

        for(k=1; k<=iteration; k++){
            printf("iteration: %d\n",k);
            ToolboxSignal::multiply(yold, h);

            tbFourier.inverseDFT(yold);

            ToolboxSignal::divideStable2(ybkp, yold, 1.0E-007F);

            tbFourier.forwardDFT(yold);

            ToolboxSignal::multiplyConj(yold, h);

            tbFourier.inverseDFT(yold);

            ToolboxSignal::multiply(y, yold);

            if(k<iteration){
                ToolboxSignal::copy(yold, y);
                tbFourier.forwardDFT(yold);
            }
        }
        return true;
}
