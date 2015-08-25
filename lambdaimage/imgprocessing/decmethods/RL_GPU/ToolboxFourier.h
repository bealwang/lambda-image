class FFT1D;
class Signal;
class ToolboxFourier
{
        int* dimensions;
        int length;
        public:
        ToolboxFourier(int* dim, int dimlength);
        ~ToolboxFourier();

        void forwardDFT(Signal &s);

        void inverseDFT(Signal &s);

        bool forwardFFTW(Signal &s);

        bool inverseFFTW(Signal &s);
};
