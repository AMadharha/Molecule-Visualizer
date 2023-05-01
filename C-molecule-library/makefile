CC = clang 
CFLAGS = -Wall -std=c99 -pedantic
PYTHON_HEADER = /Library/Frameworks/Python.framework/Versions/3.11/include/python3.11
PYTHON_LANG_LIB = /Library/Frameworks/Python.framework/Versions/3.11/lib

all: molecule.o libmol.so molecule_wrap.c molecule_wrap.o _molecule.so

molecule.o: molecule.c molecule.h
	$(CC) $(CFLAGS) -c molecule.c -fPIC -o molecule.o
libmol.so: molecule.o
	$(CC) molecule.o -shared -o libmol.so
molecule.py molecule_wrap.c: molecule.i
	swig -python -outdir ../python molecule.i
molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I$(PYTHON_HEADER) -o molecule_wrap.o
_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -L$(PYTHON_LANG_LIB) -lpython3.11 -L. -lmol -dynamiclib -o _molecule.so
clean:
	rm -f *.o *.so molecule_wrap.c ../python/molecule.py output
