#ifndef SIGNAL_H
#define SIGNAL_H
#include <vector>
//using std::vector;
class Signal//implements Cloneable
{
public:
	int D;
	bool isReal;
	int* N ;
	int* extN ;
	int length;
	int extLength;
	std::vector<float> array;

public:
    void print_signal();
    void clone(Signal &src);
	Signal();
	Signal(int* M, int Mlength);
	Signal(float* im, int depth, int height, int width);
    ~Signal();
private:
	int mirror(int k, int K);
};
#endif
