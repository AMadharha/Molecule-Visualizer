from molsql import Database
import mol_display

# Create a database and tables
db = Database(reset=True)
db.create_tables()

db['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
db['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
db['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
db['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)

fp = open('water.sdf')
db.add_molecule('Water', fp)

fp = open ('caffeine.sdf')
db.add_molecule('Caffeine', fp)

fp = open ('CID.sdf')
db.add_molecule('Isopentanol', fp)

# Create svg
mol_display.RADIUS = db.radius()
mol_display.ELEMENT_NAME = db.element_name()
mol_display.HEADER += db.radial_gradients()

for molecule in ['Water', 'Caffeine', 'Isopentanol']: 
    mol = db.load_mol(molecule)
    mol.sort()
    fp = open(molecule + ".svg", "w")
    fp.write(mol.svg())
    fp.close()