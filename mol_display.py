from molecule import molecule
import re
from xml.etree import ElementTree

# CONSTANTS
RADIUS = None
ELEMENT_NAME = None

HEADER = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">\n"""
 
FOOTER = """</svg>"""

OFFSET_X = 500 
OFFSET_Y = 500

class Atom:
    def __init__(self, c_atom):
        """
        Initializes a new Atom object with the given atomic number.

        Args:
            c_atom (atom): An atom from the molecule module with attributes 
                           element (str), x (double), y (double), and z (double).
        """
        self.atom = c_atom
        self.z = c_atom.z

    def svg(self) -> str:
        """
        Returns an SVG circle element representing this Atom object.

        The position, radius, and fill color of the circle are determined by the
        attributes of the underlying Atom object.

        Returns:
            str: An SVG circle element as a string.
        """
        x = (self.atom.x * 100.0) + OFFSET_X
        y = (self.atom.y * 100.0) + OFFSET_Y
        radi = RADIUS[self.atom.element]
        color = ELEMENT_NAME[self.atom.element]

        return f'\t<circle cx="{x}" cy="{y}" r="{radi}" fill="url(#{color})"/>\n\t<text x="{x-10}" y="{y+10}" font-size="24" font-family="Arial" fill="lightgrey">{self.atom.element}</text>\n'
    
class Bond:
    def __init__(self, c_bond):
        """
        Initializes a new Bond object with the given bond type.

        Args:
            c_bond (bone): A bond from the molecule module with attributes
                           a1, a2, epairs, atoms, x1, x2, y1, y2, z, len, dx, and dy
        """
        self.bond = c_bond
        self.z = c_bond.z

    def svg(self) -> str:  
        """
        Returns an SVG polygon element representing this Bond object.

        The position and shape of the polygon are determined by the attributes of the
        underlying Bond object.

        Returns:
            str: An SVG polygon element as a string.
        """
        x1 = ((self.bond.x1 * 100) + OFFSET_X) - (self.bond.dy * 10)
        y1 = ((self.bond.y1 * 100) + OFFSET_Y) + (self.bond.dx * 10)
        
        x2 = ((self.bond.x1 * 100) + OFFSET_X) + (self.bond.dy * 10)
        y2 = ((self.bond.y1 * 100) + OFFSET_Y) - (self.bond.dx * 10)

        x3 = ((self.bond.x2 * 100) + OFFSET_X) + (self.bond.dy * 10)
        y3 = ((self.bond.y2 * 100) + OFFSET_Y) - (self.bond.dx * 10)

        x4 = ((self.bond.x2 * 100) + OFFSET_X) - (self.bond.dy * 10)
        y4 = ((self.bond.y2 * 100) + OFFSET_Y) + (self.bond.dx * 10)

        return '\t<polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x1, y1, x2, y2, x3, y3, x4, y4)

class Molecule(molecule):
    def svg(self) -> str:
        """
        Returns an SVG string representing this Molecule object.

        The SVG string is generated from the underlying Atom and Bond objects in the
        Molecule, sorted by atomic number and bond type, respectively.

        Returns:
            str: An SVG string representing this Molecule object.
        """
        atoms = []
        for i in range(self.atom_no):
            atoms.append(Atom(self.get_atom(i)))
        bonds = []
        for i in range(self.bond_no):
            bonds.append(Bond(self.get_bond(i)))

        atoms.sort(key=lambda atom: atom.z)
        bonds.sort(key=lambda bond: bond.z)

        svg_strings = []
        while atoms and bonds:
            a1 = atoms[0]
            b1 = bonds[0] 
            if a1.z < b1.z:
                svg_strings.append(a1.svg())
                atoms.pop(0)
            else:
                svg_strings.append(b1.svg())
                bonds.pop(0)
        svg_strings += [atom.svg() for atom in atoms] + [bond.svg() for bond in bonds]

        return HEADER + "".join(svg_strings) + FOOTER
    
    def parse(self, file):
        """
        Parses a sdf data file and populates this Molecule object with Atom and Bond objects.

        Args:
            file (IO): An IO object representing the molecule data file.
        """
        atom_count, bond_count = 0, 0

        for i in range(3):
            file.readline()

        line = file.readline().strip()
        atom_count = int(line.split()[0])
        bond_count = int(line.split()[1])

        for i in range(atom_count):
            line = file.readline().strip()
            atom_info = line.split()
            self.append_atom(atom_info[3], float(atom_info[0]), float(atom_info[1]), float(atom_info[2]))

        for i in range(bond_count):
            line = file.readline().strip()
            bond_info = line.split()
            self.append_bond(int(bond_info[0])-1, int(bond_info[1])-1, int(bond_info[2]))

    def adjust_svg_viewbox(self, svg_file: str) -> str:
        """
        Adjust the viewbox of an SVG file to fit all circle elements, with an additional 200x200 padding.

        Args:
            svg_file (str): Path to the input SVG file.

        Returns:
            str: The updated SVG content as a string.
        """
        with open(svg_file, 'r') as file:
            svg_content = file.read()

        root = ElementTree.fromstring(svg_content)
        circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
        coords = [(float(circle.get('cx')), float(circle.get('cy'))) for circle in circles]

        min_x = min(x for x, y in coords) - 100
        min_y = min(y for x, y in coords) - 100
        max_x = max(x for x, y in coords) + 100
        max_y = max(y for x, y in coords) + 100

        viewBox = f"{min_x} {min_y} {max_x - min_x} {max_y - min_y}"
        root.set('viewBox', viewBox)

        updated_svg_content = ElementTree.tostring(root, encoding='unicode')

        return updated_svg_content

    
    def remove_namespace_prefix(self, svg_content: str, prefix: str = "ns0:") -> str:
        """
        Removes a specified namespace prefix from an SVG content string.

        Args:
            svg_content (str): The SVG content string to process.
            prefix (str, optional): The namespace prefix to remove. Defaults to "ns0:".

        Returns:
            str: The SVG content string with the specified namespace prefix removed.
        """
        pattern_open = re.compile(rf"<{prefix}(\w+)")
        svg_content = pattern_open.sub(r"<\1", svg_content)

        pattern_close = re.compile(rf"</{prefix}(\w+)>")
        svg_content = pattern_close.sub(r"</\1>", svg_content)

        return svg_content


