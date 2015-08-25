
//using namespace std;
//class ToolboxFourier;
//class ToolboxSignal;
class Signal;
class RichardsonLucy         // extends AbstractAlgorithm implements ItemListener
{
public:
	RichardsonLucy();
	static bool process(Signal &y, Signal &h, int iteration,int ylength);
//	bool useInputImg = true;
	//int K = 10;
//private:
//	bool useInputImgdef = 1;
//	int Kmin = 1;
//	int Kmax = 1000000;
//	int Kdef = 10;
};
