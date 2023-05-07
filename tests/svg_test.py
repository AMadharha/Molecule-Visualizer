from molsql import Database
import mol_display

# Create a database and tables
db = Database(reset=False)
db.create_tables()

fp = open ('ChEBI_135595.sdf')
db.add_molecule('something', fp)

# Create svg
mol_display.RADIUS = db.radius()
mol_display.ELEMENT_NAME = db.element_name()
mol_display.HEADER += db.radial_gradients()

for molecule in ['something']: 
    mol = db.load_mol(molecule)
    mol.sort()
    name = molecule + ".svg"

    # Write the initial SVG
    with open(name, "w") as fp:
        fp.write(mol.svg())

    # Adjust the viewBox and update the SVG
    updated_svg_content = mol.adjust_svg_viewbox(name)
    clean_svg_content = mol.remove_namespace_prefix(updated_svg_content, "ns0:")

    # Write the updated SVG content to the file
    with open(name, "w") as fp:
        fp.write(clean_svg_content)