from flask import Flask, request, send_from_directory, jsonify, abort
import os
from molsql import Database
import mol_display

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    file_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.isfile(file_path):
        return send_from_directory(os.path.dirname(__file__), path)
    else:
        abort(404, description="File not found")

@app.route('/get-molecules', methods=['GET'])
def get_molecules():
    db = Database(reset=False)
    db.create_tables()
    molecules = db.conn.execute("SELECT * FROM Molecules")

    molecule_dicts = []
    for molecule in molecules:
        molecule_dict = {
            "NAME": molecule[1]
        }
        molecule_dicts.append(molecule_dict)

    return jsonify(molecule_dicts)

@app.route('/upload-sdf', methods=['POST'])
def upload_sdf():
    if 'sdf_file' not in request.files:
        abort(400, description="No file provided")

    file_data = request.files['sdf_file']

    with open("temp.sdf", "wb") as f:
        f.write(file_data.read())

    with open("temp.sdf", "r") as f:
        found = False
        name = ""
        for line in f:
            if found:
                name = line.strip()
                break
            if "<NAME>" in line:
                found = True
    fp = open("temp.sdf", "r")

    db = Database(reset=False)
    db.create_tables()
    db.add_molecule(name, fp)

    os.remove("temp.sdf")
    return "File uploaded successfully."

@app.route('/get-svg', methods=['POST'])
def get_svg():
    data = request.get_json()

    if not data or "name" not in data:
        abort(400, description="Molecule name not provided")

    molecule_name = data["name"]

    db = Database(reset=False)
    mol_display.RADIUS = db.radius()
    mol_display.ELEMENT_NAME = db.element_name()
    mol_display.HEADER += db.radial_gradients()
    mol = db.load_mol(molecule_name)
    mol.sort()
    svg_filename = molecule_name + ".svg"
    with open(svg_filename, "w") as fp:
        fp.write(mol.svg())

    with open(svg_filename, "r") as fp:
        svg_content = fp.read()

    os.remove(svg_filename)
    return svg_content, 200, {"Content-Type": "image/svg+xml"}

if __name__ == '__main__':
    app.run()