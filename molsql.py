import os
import psycopg2
from psycopg2 import sql
import mol_display

class Database:
    def __init__(self, reset: bool=False):
        """
        Initializes a new Database object and connects to an SQLite database.

        Args:
            reset (bool, optional): If True, deletes the existing database file and creates
                a new one. Defaults to False.
        """
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cursor = self.conn.cursor()
        
        if reset:
            self.drop_tables()
            self.create_tables()

    def drop_tables(self):
        """
        Drops all tables from the database.
        """
        tables = ["Elements", "Atoms", "Bonds", "Molecules", "MoleculeAtom", "MoleculeBond"]
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
        self.conn.commit()

    def create_tables(self):
        """
        Creates the necessary tables in the PostgreSQL database for storing Elements, Atoms, Bonds, Molecules,
        and their relationships.
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Elements
                            (ELEMENT_NO   INTEGER,
                            ELEMENT_CODE VARCHAR(3) PRIMARY KEY,
                            ELEMENT_NAME VARCHAR(32),
                            COLOUR1      CHAR(6),
                            COLOUR2      CHAR(6),
                            COLOUR3      CHAR(6),
                            RADIUS       DECIMAL(3,1));""")  

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Atoms
                            (ATOM_ID      SERIAL PRIMARY KEY,
                            ELEMENT_CODE VARCHAR(3) REFERENCES Elements(ELEMENT_CODE),
                            X            DECIMAL(7,4),
                            Y            DECIMAL(7,4),
                            Z            DECIMAL(7,4));""")  

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Bonds
                            (BOND_ID SERIAL PRIMARY KEY,
                            A1      INTEGER,
                            A2      INTEGER,
                            EPAIRS  INTEGER);""")  

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Molecules
                            (MOLECULE_ID SERIAL PRIMARY KEY,
                            NAME        TEXT UNIQUE);""") 

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                            (MOLECULE_ID INTEGER,
                            ATOM_ID     INTEGER,
                            PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                            FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID));""") 

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                            (MOLECULE_ID INTEGER,
                            BOND_ID     INTEGER,
                            PRIMARY KEY (MOLECULE_ID, BOND_ID),
                            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                            FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID));""")
        self.conn.commit()

        
    def __setitem__(self, table: str, values: tuple):
        """
        Inserts a new row into the specified table in the PostgreSQL database with the given values.

        Args:
            table (str): The name of the table to insert the row into.
            values (tuple): A tuple of values to insert into the row.
        """
        placeholders = ','.join(['%s']*len(values))
        query = f"INSERT INTO {table} VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()


    def add_atom(self, molname: str, atom: mol_display.Atom):
        """
        Adds a new Atom object to the specified molecule in the database.

        Args:
            molname (str): The name of the molecule to add the atom to.
            atom (Atom): An Atom object representing the atom to add.
        """
        element_code = atom.atom.element
        x = atom.atom.x
        y = atom.atom.y
        z = atom.atom.z

        self.cursor.execute(
            "INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (%s, %s, %s, %s) RETURNING ATOM_ID",
            (element_code, x, y, z))
        atom_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = %s", (molname,))
        row = self.cursor.fetchone()
        if row is None:
            return

        mol_id = row[0]
        self['MoleculeAtom'] = (mol_id, atom_id)
        self.conn.commit()


    def add_bond(self, molname: str, bond: mol_display.Bond):
        """
        Adds a new Bond object to the specified molecule in the database.

        Args:
            molname (str): The name of the molecule to add the bond to.
            bond (Bond): A Bond object representing the bond to add.
        """
        a1 = bond.bond.a1
        a2 = bond.bond.a2
        epairs = bond.bond.epairs

        self.cursor.execute(
            "INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (%s, %s, %s) RETURNING BOND_ID",
            (a1, a2, epairs))
        bond_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = %s", (molname,))
        row = self.cursor.fetchone()
        if row is None:
            return

        mol_id = row[0]
        self['MoleculeBond'] = (mol_id, bond_id)
        self.conn.commit()

    def add_molecule(self, name: str, fp):
        """
        Adds a new molecule to the database with the given name and file pointer.

        Args:
            name (str): The name of the molecule to add.
            fp (IO): A file pointer to the molecule data file.
        """
        molecule = mol_display.Molecule()
        molecule.parse(fp)

        self.cursor.execute(
            "INSERT INTO Molecules (NAME) VALUES (%s) RETURNING MOLECULE_ID",
            (name,))
        mol_id = self.cursor.fetchone()[0]

        for i in range(molecule.atom_no):
            atom = mol_display.Atom(molecule.get_atom(i))
            self.add_atom(mol_id, atom)

        for i in range(molecule.bond_no):
            bond = mol_display.Bond(molecule.get_bond(i))
            self.add_bond(mol_id, bond)

        self.conn.commit()


    def load_mol(self, name) -> mol_display.Molecule:
        """
        Retrieves a molecule from the database with the given name, and returns a corresponding
        mol_display.Molecule object.

        Args:
            name (str): The name of the molecule to retrieve.

        Returns:
            mol_display.Molecule: A mol_display.Molecule object representing the specified molecule.
        """
        query = """SELECT Atoms.*, Elements.*
                    FROM Atoms
                    JOIN Elements ON Atoms.ELEMENT_CODE = Elements.ELEMENT_CODE
                    JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
                    JOIN Molecules ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                    WHERE Molecules.NAME = %s
                    ORDER BY Atoms.ATOM_ID ASC"""
        atoms_result = self.cursor.execute(query, (name,)).fetchall()

        query = """SELECT Bonds.*
                    FROM Bonds
                    JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
                    JOIN Molecules ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                    WHERE Molecules.NAME = %s
                    ORDER BY Bonds.BOND_ID ASC"""
        bonds_result = self.cursor.execute(query, (name,)).fetchall()

        mol = mol_display.Molecule()
        for atom in atoms_result:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])
        for bond in bonds_result:
            mol.append_bond(bond[1], bond[2], bond[3])

        return mol

    def radius(self) -> dict[str, str]:
        """
        Returns a dictionary mapping element codes to their corresponding atomic radii.

        Returns:
            dict: A dictionary mapping element codes to their corresponding atomic radii.
        """
        query = "SELECT ELEMENT_CODE, RADIUS FROM Elements"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return {element_code: radius for element_code, radius in results}

    
    def element_name(self) -> dict[str, str]:
        """
        Returns a dictionary mapping element codes to their corresponding element names.

        Returns:
            dict: A dictionary mapping element codes to their corresponding element names.
        """
        self.cursor.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        element_dict = {row[0]: row[1] for row in self.cursor.fetchall()}
        return element_dict

    def radial_gradients(self) -> str:
        """
        Returns a string containing the XML definitions for radial gradients based on element colors.

        Returns:
            str: A string containing the XML definitions for radial gradients based on element colors.
        """
        gradients = ""
        self.cursor.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        elements = self.cursor.fetchall()

        for row in elements:
            gradient = f"""\t<radialGradient id="{row[0]}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">\n\t\t<stop offset="0%" stop-color="#{row[1]}"/>\n\t\t<stop offset="50%" stop-color="#{row[2]}"/>\n\t\t<stop offset="100%" stop-color="#{row[3]}"/>\n\t</radialGradient>\n"""
            gradients += gradient

        return gradients
