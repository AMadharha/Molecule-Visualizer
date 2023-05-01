CC = gcc 
CFLAGS = -Wall -std=c99 -pedantic
PYTHON_HEADER = /Library/Frameworks/Python.framework/Versions/3.11/include/python3.11
PYTHON_LANG_LIB = /Library/Frameworks/Python.framework/Versions/3.11/lib
LOCAL_PYTHON = ../python
LOCAL_TESTS = ../tests

all: molecule.o ../tests/libmol.so molecule_wrap.c molecule_wrap.o _molecule.so

molecule.o: molecule.c molecule.h
	$(CC) $(CFLAGS) -c molecule.c -fPIC -o $@
$(LOCAL_TESTS)libmol.so: molecule.o
	$(CC) molecule.o -shared -o $@
molecule_wrap.c molecule.py: molecule.i
	swig -python -outdir $(LOCAL_PYTHON) molecule.i
molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I$(PYTHON_HEADER) -o $@
_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -L$(PYTHON_LANG_LIB) -lpython3.11 -L$(LOCAL_TESTS) -lmol -dynamiclib -o $@
clean:
	rm -f *.o *.so $(LOCAL_PYTHON)/*.so molecule_wrap.c $(LOCAL_PYTHON)/molecule.py
