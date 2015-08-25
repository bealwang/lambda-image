libdeconv.so : deconv.o
	gcc -shared -Wl,-soname,libdeconv.so -o libdeconv.so deconv.o

deconv.o : deconv.c
	gcc -c -fPIC deconv.c -o deconv.o

m.PHONY : clean
clean :
	rm -vf libdeconv.so deconv.o deconv.pyc
