CC = gcc 
CFLAGS = -Wall -std=c99 -pedantic
PYTHON_HEADER = /Library/Frameworks/Python.framework/Versions/3.11/include/python3.11
PYTHON_LANG_LIB = /Library/Frameworks/Python.framework/Versions/3.11/lib

all: molecule.o libmol.so molecule_wrap.c molecule_wrap.o ${OLDPWD}/_molecule.so

molecule.o: molecule.c molecule.h
	$(CC) $(CFLAGS) -c molecule.c -fPIC -o $@
libmol.so: molecule.o
	$(CC) $(CFLAGS) molecule.o -shared -o $@
molecule_wrap.c molecule.py: molecule.i
	swig -python -outdir ${OLDPWD} molecule.i
molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I$(PYTHON_HEADER) -o $@
${OLDPWD}/_molecule.so: molecule_wrap.o
	$(CC) $(CFLAGS) molecule_wrap.o -shared -L$(PYTHON_LANG_LIB) -lpython3.11 -L${OLDPWD} -lmol -dynamiclib -o $@
clean:
	rm -f *.o ${OLDPWD}/*.so *.so molecule_wrap.c ${OLDPWD}/molecule.py
