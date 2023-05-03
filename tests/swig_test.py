# export PYTHONPATH=../python-svg:$PYTHONPATH
import molecule

# create a new molecule object
mol = molecule.molecule()

# create 3 atoms
mol.append_atom('O', 2.5369, -0.1550, 0.0000)
mol.append_atom('H', 3.0739, 0.1550, 0.0000) 
mol.append_atom('H', 2.0000, 0.1550, 0.0000)

# caution atom references in append_bond start at 1 NOT 0
mol.append_bond(1, 2, 1)
mol.append_bond(1, 3, 1)

for i in range(3):
    atom = mol.get_atom(i)
    print(atom.element, atom.x, atom.y, atom.z)
for i in range(2):
    bond = mol.get_bond(i)
    print(bond.a1, bond.a2, bond.epairs, bond.x1, bond.y1, bond.x2, bond.y2, bond.len, bond.dx, bond.dy)