#include "molecule.h"

/**
 * @brief Sets the properties of an atom structure.
 * 
 * This function sets the element and coordinates (x, y, z) of a given atom structure. If the atom
 * pointer is not allocated, the function prints an error message to standard error and exits the program.
 *
 * @param atom Pointer to the atom structure to be modified.
 * @param element Null-terminated string representing the chemical element symbol (up to 2 characters).
 * @param x Pointer to a double value representing the x-coordinate of the atom.
 * @param y Pointer to a double value representing the y-coordinate of the atom.
 * @param z Pointer to a double value representing the z-coordinate of the atom.
 */
void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
    if(atom == NULL) {
        fprintf(stderr, "atomset(): atom is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

/**
 * @brief Retrieves the properties of an atom structure.
 * 
 * This function retrieves the element and coordinates (x, y, z) of a given atom structure and stores
 * them in the provided pointers. If the atom pointer is not allocated, the function prints an error
 * message to standard error and exits the program.
 *
 * @param atom Pointer to the atom structure from which properties are to be retrieved.
 * @param element A character array (size 3) to store the retrieved chemical element symbol (up to 2 characters).
 * @param x Pointer to a double value where the x-coordinate of the atom will be stored.
 * @param y Pointer to a double value where the y-coordinate of the atom will be stored.
 * @param z Pointer to a double value where the z-coordinate of the atom will be stored.
 */
void atomget(atom *atom, char element[3], double *x, double *y, double *z) {
    if(atom == NULL) {
        fprintf(stderr, "atomget(): atom is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

/**
 * @brief Sets the properties of a bond structure.
 * 
 * This function sets the properties (atom indices, atoms array, electron pairs) of a given bond
 * structure and calls the compute_coords() function to calculate the bond's coordinates. If the bond
 * pointer is not allocated, the function prints an error message to standard error and exits the program.
 *
 * @param bond Pointer to the bond structure to be modified.
 * @param a1 Pointer to an unsigned short value representing the index of the first atom in the bond.
 * @param a2 Pointer to an unsigned short value representing the index of the second atom in the bond.
 * @param atoms Pointer to an atom array containing the atom structures involved in the bond.
 * @param epairs Pointer to an unsigned char value representing the number of electron pairs in the bond.
 */
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    if(bond == NULL) {
        fprintf(stderr, "bondset(): bond is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
    compute_coords(bond);
}

/**
 * @brief Retrieves the properties of a bond structure.
 * 
 * This function retrieves the properties (atom indices, atoms array, electron pairs) of a given bond
 * structure and stores them in the provided pointers. If the bond pointer is not allocated, the function
 * prints an error message to standard error and exits the program.
 *
 * @param bond Pointer to the bond structure from which properties are to be retrieved.
 * @param a1 Pointer to an unsigned short value where the index of the first atom in the bond will be stored.
 * @param a2 Pointer to an unsigned short value where the index of the second atom in the bond will be stored.
 * @param atoms Pointer to an atom array pointer where the address of the atom structures involved in the bond will be stored.
 * @param epairs Pointer to an unsigned char value where the number of electron pairs in the bond will be stored.
 */
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    if(bond == NULL) {
        fprintf(stderr, "bondget(): bond is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

/**
 * @brief Computes the coordinates and properties of a bond structure.
 * 
 * This function calculates the coordinates, length, direction, and average z-coordinate of a bond
 * structure based on the positions of the two atoms involved in the bond. The bond structure
 * should already have the atom indices and atom array set.
 *
 * @param bond Pointer to the bond structure for which properties and coordinates are to be computed.
 */
void compute_coords(bond *bond) {
    atom *a1 = bond->atoms + bond->a1;
    atom *a2 = bond->atoms + bond->a2;

    bond->x1 = a1->x;
    bond->y1 = a1->y;

    bond->x2 = a2->x;
    bond->y2 = a2->y;

    bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));

    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;

    bond->z = (a1->z + a2->z) / 2.0;
}

/**
 * @brief Allocates memory for a molecule structure with a given number of atoms and bonds.
 * 
 * This function allocates memory for a molecule structure and initializes its properties based on
 * the specified maximum number of atoms and bonds. It also allocates memory for the atoms and bonds
 * arrays and their corresponding pointer arrays. If any memory allocation fails, the function
 * prints an error message and exits the program.
 *
 * @param atom_max The maximum number of atoms allowed in the molecule.
 * @param bond_max The maximum number of bonds allowed in the molecule.
 * @return Pointer to the allocated and initialized molecule structure.
 */
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {
    molecule *mol = malloc(sizeof(molecule));

    mol->atom_max = atom_max;
    mol->atom_no = 0;
    mol->atoms = malloc(sizeof(atom)*atom_max);
    mol->atom_ptrs = malloc(sizeof(atom*)*atom_max);

    mol->bond_max = bond_max;
    mol->bond_no = 0;
    mol->bonds = malloc(sizeof(bond)*bond_max);
    mol->bond_ptrs = malloc(sizeof(bond*)*bond_max);
 
    if(mol == NULL || mol->atoms == NULL || mol->atom_ptrs == NULL || mol->bonds == NULL || mol->bond_ptrs == NULL) {
        fprintf(stderr, "molmalloc(): malloc failure.");
        exit(EXIT_FAILURE);
    }

    return mol;
}

/**
 * @brief Creates a copy of the given molecule structure.
 * 
 * This function creates a deep copy of the provided molecule structure, including its atoms and bonds.
 * It first allocates memory for a new molecule structure using molmalloc() with the same maximum
 * number of atoms and bonds as the source molecule. Then, it iterates through the atoms and bonds
 * of the source molecule, appending them to the new molecule. If the source molecule is not allocated,
 * the function prints an error message to standard error and exits the program.
 *
 * @param src Pointer to the source molecule structure to be copied.
 * @return Pointer to the newly created and initialized molecule structure that is a copy of the source molecule.
 */
molecule *molcopy(molecule *src) {  
    if(src == NULL) {
        fprintf(stderr, "molcopy(): src molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    molecule *dst = molmalloc(src->atom_max, src->bond_max);

    for(int i = 0; i < src->atom_no; i++) {
        molappend_atom(dst, &src->atoms[i]);
    }
    for(int i = 0; i < src->bond_no; i++) {
        molappend_bond(dst, &src->bonds[i]);
    }

    dst->atom_no = src->atom_no;
    dst->bond_no = src->bond_no;

    return dst;
}

/**
 * @brief Frees the memory allocated for a molecule structure.
 * 
 * This function frees the memory allocated for a molecule structure, including its atoms, bonds,
 * and the corresponding pointer arrays. If the molecule pointer is not allocated, the function
 * prints an error message to standard error and exits the program.
 *
 * @param ptr Pointer to the molecule structure to be freed.
 */
void molfree(molecule *ptr) {
    if(ptr == NULL) {
        fprintf(stderr, "molfree(): molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    free(ptr->atom_ptrs);
    free(ptr->bond_ptrs);
    free(ptr->atoms);
    free(ptr->bonds);
    free(ptr);
}

/**
 * @brief Appends an atom to a molecule structure.
 * 
 * This function appends an atom to the specified molecule structure. If the molecule or atom
 * pointer is not allocated, the function prints an error message to standard error and exits the program.
 * If the maximum allowed number of atoms in the molecule is reached, the function reallocates
 * memory for the atoms array and the corresponding pointer array, doubling their size. If the reallocation
 * fails, the function prints an error message to standard error and exits the program.
 *
 * @param molecule Pointer to the molecule structure to which the atom should be appended.
 * @param atom Pointer to the atom structure to be appended to the molecule.
 */
void molappend_atom(molecule *molecule, atom *atom) {
    if(molecule == NULL) {
        fprintf(stderr, "molappend_atom(): molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }
    if(atom == NULL) {
        fprintf(stderr, "molappend_atom(): atom is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    if(molecule->atom_max == molecule->atom_no) {
        if(molecule->atom_max == 0) {
            molecule->atom_max = 1; 
        }
        else {
            molecule->atom_max *= 2;
        }
        
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom)*molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*)*molecule->atom_max);

        if(molecule->atoms == NULL || molecule->atom_ptrs == NULL) {
            fprintf(stderr, "molappend_atom(): realloc failure.");
            exit(EXIT_FAILURE);
        }

        for(int i = 0; i < molecule->atom_no; i++) {
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }
    }

    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no++;
}

/**
 * @brief Appends a bond to a molecule structure.
 * 
 * This function appends a bond to the specified molecule structure. If the molecule or bond
 * pointer is not allocated, the function prints an error message to standard error and exits the program.
 * If the maximum allowed number of bonds in the molecule is reached, the function reallocates
 * memory for the bonds array and the corresponding pointer array, doubling their size. If the reallocation
 * fails, the function prints an error message to standard error and exits the program.
 *
 * @param molecule Pointer to the molecule structure to which the bond should be appended.
 * @param bond Pointer to the bond structure to be appended to the molecule.
 */
void molappend_bond(molecule *molecule, bond *bond) {
    if(molecule == NULL) {
        fprintf(stderr, "molappend_bond(): molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }
    if(bond == NULL) {
        fprintf(stderr, "molappend_bond(): bond is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    if(molecule->bond_max == molecule->bond_no) {
        if(molecule->bond_max == 0) {
            molecule->bond_max = 1; 
        }
        else {
            molecule->bond_max *= 2;
        }
    
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*molecule->bond_max);

        if(molecule->bonds == NULL || molecule->bond_ptrs == NULL) {
            fprintf(stderr, "molappend_bond(): realloc failure.");
        }

        for(int i = 0; i < molecule->bond_no; i++) {
            molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }

    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no++;
}

/**
 * @brief Sorts the atoms and bonds of a molecule structure.
 * 
 * This function sorts the atoms and bonds of the given molecule structure in ascending order based
 * on their properties. If the molecule pointer is not allocated, the function prints an error message
 * to standard error and exits the program. The sorting is performed using the qsort() function, along
 * with the atom_compare() and bond_compare() functions as comparison criteria.
 *
 * @param molecule Pointer to the molecule structure whose atoms and bonds should be sorted.
 */
void molsort(molecule *molecule) {
    if(molecule == NULL) {
        fprintf(stderr, "molsort(): molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom*), atom_compare);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond*), bond_compare);
}

/**
 * @brief Compares two atoms based on their z-coordinates.
 * 
 * This function is used as a comparison function for sorting atoms in a molecule structure. It takes
 * two void pointers (which are expected to be pointers to atom pointers), dereferences them, and
 * compares the z-coordinates of the two atoms. The function returns -1 if the first atom has a
 * lower z-coordinate, 1 if the first atom has a higher z-coordinate, and 0 if their z-coordinates are equal.
 *
 * @param a Void pointer to the first atom pointer.
 * @param b Void pointer to the second atom pointer.
 * @return -1 if the first atom's z-coordinate is lower, 1 if higher, and 0 if equal to the second atom's z-coordinate.
 */
int atom_compare(const void *a, const void *b) {
    atom *a_ptr, *b_ptr;

    a_ptr = *(atom**)a;
    b_ptr = *(atom**)b;

    if(a_ptr->z < b_ptr->z) return -1;
    if(a_ptr->z > b_ptr->z) return 1;

    return 0;
}

/**
 * @brief Compares two bonds based on their z-coordinates.
 * 
 * This function is used as a comparison function for sorting bonds in a molecule structure. It takes
 * two void pointers (which are expected to be pointers to bond pointers), dereferences them, and
 * compares the z-coordinates of the two bonds. The function returns -1 if the first bond has a
 * lower z-coordinate, 1 if the first bond has a higher z-coordinate, and 0 if their z-coordinates are equal.
 *
 * @param a Void pointer to the first bond pointer.
 * @param b Void pointer to the second bond pointer.
 * @return -1 if the first bond's z-coordinate is lower, 1 if higher, and 0 if equal to the second bond's z-coordinate.
 */
int bond_compare(const void *a, const void *b) {
    bond *a_ptr, *b_ptr;

    a_ptr = *(bond**)a;
    b_ptr = *(bond**)b;

    if(a_ptr->z < b_ptr->z) return -1;
    if(a_ptr->z > b_ptr->z) return 1;

    return 0;
}

/**
 * @brief Creates an X-axis rotation matrix.
 * 
 * This function generates a 3x3 rotation matrix for rotating a point around the X-axis by a specified
 * angle in degrees. The resulting rotation matrix is stored in the provided xform_matrix variable.
 *
 * @param xform_matrix A 3x3 matrix to store the X-axis rotation matrix.
 * @param deg The angle in degrees to rotate around the X-axis.
 */
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = deg * (PI / 180.0);

    xform_matrix[0][0] = 1.0;
    xform_matrix[0][1] = 0.0;
    xform_matrix[0][2] = 0.0;

    xform_matrix[1][0] = 0.0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);

    xform_matrix[2][0] = 0.0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

/**
 * @brief Creates a Y-axis rotation matrix.
 * 
 * This function generates a 3x3 rotation matrix for rotating a point around the Y-axis by a specified
 * angle in degrees. The resulting rotation matrix is stored in the provided xform_matrix variable.
 *
 * @param xform_matrix A 3x3 matrix to store the Y-axis rotation matrix.
 * @param deg The angle in degrees to rotate around the Y-axis.
 */
void yrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = deg * (PI / 180.0);

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0.0;
    xform_matrix[0][2] = sin(rad);

    xform_matrix[1][0] = 0.0;
    xform_matrix[1][1] = 1.0;
    xform_matrix[1][2] = 0.0;

    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0.0;
    xform_matrix[2][2] = cos(rad);
}

/**
 * @brief Creates a Z-axis rotation matrix.
 * 
 * This function generates a 3x3 rotation matrix for rotating a point around the Z-axis by a specified
 * angle in degrees. The resulting rotation matrix is stored in the provided xform_matrix variable.
 *
 * @param xform_matrix A 3x3 matrix to store the Z-axis rotation matrix.
 * @param deg The angle in degrees to rotate around the Z-axis.
 */
void zrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = deg * (PI / 180.0);

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0.0;

    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0.0;

    xform_matrix[2][0] = 0.0;
    xform_matrix[2][1] = 0.0;
    xform_matrix[2][2] = 1.0;
}

/**
 * @brief Transforms a molecule using a given transformation matrix.
 * 
 * This function applies a transformation matrix to all the atoms in the provided molecule.
 * It then recalculates bond coordinates based on the transformed atom positions.
 * The transformation matrix should be a 3x3 matrix.
 *
 * @param molecule A pointer to the molecule to be transformed.
 * @param matrix The 3x3 transformation matrix to apply to the molecule.
 */
void mol_xform(molecule *molecule, xform_matrix matrix) {
    if(molecule == NULL) {
        fprintf(stderr, "mol_xform(): molecule is not malloc'd.");
        exit(EXIT_FAILURE);
    }

    for(int a = 0; a < molecule->atom_no; a++) {
        double vector[3][1] = {{molecule->atoms[a].x}, {molecule->atoms[a].y}, {molecule->atoms[a].z}};
        double xformed[3][1] = {{0},{0},{0}};
        for (int i = 0; i < 3; i++) {
            for (int k = 0; k < 3; k++) {
                xformed[i][0] += matrix[i][k] * vector[k][0];
            }
        }
        molecule->atoms[a].x = xformed[0][0];
        molecule->atoms[a].y = xformed[1][0];
        molecule->atoms[a].z = xformed[2][0];
    }

    for(int b = 0; b < molecule->bond_no; b++) {
        compute_coords(&molecule->bonds[b]);
    }
}
