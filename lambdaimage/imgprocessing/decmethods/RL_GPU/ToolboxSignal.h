class Signal;
class ToolboxFourier;
class ToolboxSignal
{
public:
	static void multiplyConstant(Signal &s, float p);
	static bool multiply(Signal &s1, Signal &s2);
	static bool multiplyConj(Signal &s1, Signal &s2);

	static bool add(Signal s1, Signal s2);

	static bool addAbs(Signal s1, Signal s2);

	static void divideStable(Signal s1, Signal s2, float threshold);

	static bool divideStable2(Signal &s1, Signal &s2, float threshold);

	static bool checkCompatibility(Signal &s1, Signal &s2);

	static bool resizePSF(int* dim, Signal &s, int dimlength);

	static float sum(Signal &s);

	static bool clipBelow(Signal &s, float min);

	static void transfer(Signal &s1, Signal &s2);

	static bool copy(Signal &s1, Signal &s2);

	static void fftShift1D(Signal &s, int dimension, int shift);
	static void minConstraint(Signal &s, float min, bool saveMemory, ToolboxFourier &sFft);

	static bool fftShift(Signal &s, int* shift, int shiftlength);
	static float minimum(Signal &s);
	static void addConstant(Signal &s, float real, float imag);

private:
	static void resizePSFRecursive(Signal &signalOld, Signal &signalNew, int offsetOld, int offsetNew, int* factorOld, int* factorNew, int currentDim);

	static int getPositionReal(int* coord, Signal &s, int coordlength);

	static void recursiveFftShift1D(Signal &s, int dimension, int shift, int currentDimension, int* coord, int coordlength);
};