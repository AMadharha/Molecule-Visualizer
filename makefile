CC = clang 
CFLAGS = -Wall -std=c99 -pedantic
PYTHON_HEADER = /usr/include/python3.7m
PYTHON_LANG_LIB = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

all: output

molecule.o: molecule.c molecule.h
	$(CC) $(CFLAGS) -c molecule.c -fPIC -o molecule.o
libmol.so: molecule.o
	$(CC) molecule.o -shared -o libmol.so
molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i
molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I$(PYTHON_HEADER) -o molecule_wrap.o
_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -L$(PYTHON_LANG_LIB) -lpython3.7m -L. -lmol -dynamiclib -o _molecule.so
clean:
	rm -f *.o *.so molecule_wrap.c molecule.py output
