%module molecule
%{
    #include "molecule.h"
%}

%include "molecule.h"

%extend atom {
    // Constructor for atom with given element and coordinates
    atom(char element[3], double x, double y, double z) {
        atom *a;
        a = (atom *)malloc(sizeof(atom));
        atomset(a, element, &x, &y, &z);
        return a;
    }

    // Destructor for atom
    ~atom() {
        free($self);
    }
};

%extend bond {
    // Constructor for bond with given bond pointer
    bond(bond *bond) {
        return bond;
    }
};

%extend molecule {
    // Constructor for molecule with no initial atoms and bonds
    molecule() {
        molecule *mol;
        mol = molmalloc(0, 0);
        return mol;
    }

    // Destructor for molecule
    ~molecule() {
        molfree($self);
    }

    // Appends an atom with given element and coordinates to the molecule
    void append_atom(char element[3], double x, double y, double z) {
        atom a1;
        strcpy(a1.element, element);
        a1.x = x;
        a1.y = y;
        a1.z = z;

        molappend_atom($self, &a1);
    }

    // Appends a bond with given atom indices and electron pair count to the molecule
    void append_bond(unsigned short a1, unsigned short a2, unsigned char epairs) {
        bond b1;
        b1.a1 = a1;
        b1.a2 = a2;
        b1.atoms = $self->atoms;
        b1.epairs = epairs;
        compute_coords(&b1);

        molappend_bond($self, &b1);
    }

    // Returns a pointer to the atom at the specified index
    atom *get_atom(unsigned short i) {
        return $self->atom_ptrs[i];
    }

     // Returns a pointer to the bond at the specified index
    bond *get_bond(unsigned short i) {
        return $self->bond_ptrs[i];
    }

    // Sorts the atoms and bonds of the molecule
    void sort() {
        molsort($self);
    }
};
