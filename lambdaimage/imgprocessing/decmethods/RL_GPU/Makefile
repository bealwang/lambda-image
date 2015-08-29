BIN	:= libdeconv.so

C_SOURCES := Image.cpp Signal.cpp ToolboxFourier.cpp ToolboxSignal.cpp RichardsonLucy.cpp rlmain.cpp

C_OBJS := $(patsubst %.cpp, %.o, $(C_SOURCES))

$(BIN): $(C_OBJS) deconv.o Fourier.cu_o
	#gcc  -lstdc++ -shared -Wl,-soname,libdeconv.so -O2 -o $(BIN) Fourier.cu_o deconv.o $(C_OBJS) -L../tiff -ltiff  -L/usr/local/cuda-6.5/lib64 -lcudart -lcufft -lm
	gcc  -lstdc++ -shared -Wl,-soname,libdeconv.so -O2 -o $(BIN) Fourier.cu_o deconv.o $(C_OBJS) -L../tiff -ltiff -L/home/wb/opt/fftw/ -lfftw3f -lpthread -lfftw3f_threads -lm -L/usr/local/cuda-6.5/lib64 -lcudart -lcufft -lm
	cp libdeconv.so ..


deconv.o: deconv.c
	gcc -O2 -fPIC -c deconv.c
Image.o: Image.cpp image.h
	g++ -O2 -fPIC -c Image.cpp 
Signal.o: Signal.cpp Signal.h
	g++ -O2 -fPIC -c Signal.cpp 
ToolboxSignal.o: ToolboxSignal.cpp ToolboxSignal.h
	g++ -O2 -fPIC -c ToolboxSignal.cpp 
ToolboxFourier.o: ToolboxFourier.cpp ToolboxFourier.h
	g++ -O2 -fPIC -c ToolboxFourier.cpp 
RichardsonLucy.o: RichardsonLucy.cpp RichardsonLucy.h
	#g++ -O2 -fPIC -c RichardsonLucy.cpp 
	nvcc -Xcompiler -fPIC -O2 -c -o $@ RichardsonLucy.cpp  

Fourier.cu_o:Fourier.cu Fourier.h
	nvcc -Xcompiler -fPIC -O2 -c -o $@ Fourier.cu  

rlmain.o: rlmain.cpp image.h Signal.h ToolboxFourier.h ToolboxSignal.h RichardsonLucy.h
	g++  -fPIC -O2 -c rlmain.cpp

clean:
	rm -f $(BIN) *.o 
