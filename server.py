from flask import Flask, request, send_from_directory, jsonify, abort
import os
from molsql import Database
import mol_display

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    Returns the contents of the 'index.html' file located in the same directory as this script.

    This function is a route handler for the root URL ('/') using the HTTP GET method. It serves
    the 'index.html' file from the current directory to the client.

    Returns:
        Response object: The contents of the 'index.html' file with appropriate headers and status code.
    """
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    """
    Serves a static file from the current directory based on the given relative path.

    This function is a route handler for the URL with a path variable. It attempts to locate
    and serve the requested file from the current directory. If the file is not found,
    a 404 error is raised with a custom description.

    Args:
        path (str): The relative path of the requested file.

    Returns:
        Response object: The contents of the requested file with appropriate headers and status code,
                         or a 404 error if the file is not found.
    """
    file_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.isfile(file_path):
        return send_from_directory(os.path.dirname(__file__), path)
    else:
        abort(404, description="File not found")

@app.route('/get-molecules', methods=['GET'])
def get_molecules():
    """
    Retrieves a list of molecules from the database and returns them as a JSON response.

    This function connects to the database, creates tables if necessary, and queries for all
    records in the Molecules table. It then formats the results into a list of dictionaries,
    with each dictionary representing a single molecule, and returns the list as a JSON response.

    Returns:
        Response object: A JSON response containing a list of molecule dictionaries, with each
                         dictionary containing the molecule's name.
    """
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
    """
    Uploads a given SDF file and adds its data to the Molecules table in the database.

    This function first checks if the SDF file is provided in the request. If not, it raises a 400
    error. It then extracts the molecule name from the file and checks if it already exists in the
    database. If it does, a 400 error is raised. Otherwise, the molecule is added to the database,
    and a success message is returned.

    Returns:
        str: A success message indicating that the file has been uploaded successfully.
    Raises:
        HTTPException: A 400 error if the SDF file is not provided or if the name already exists
                    in the database.
    """
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
    found = False

    db = Database(reset=False)
    db.create_tables()
    query = "SELECT * FROM Molecules WHERE NAME = ?"
    result = db.conn.execute(query, (name,)).fetchone()

    if result is not None:
        os.remove("temp.sdf")
        abort(400, description="Name already exists in the database")

    db.add_molecule(name, fp)

    os.remove("temp.sdf")
    return "File uploaded successfully."

@app.route('/get-svg', methods=['POST'])
def get_svg():
    """
    Uploads a given SDF file and adds its data to the Molecules table in the database.
    This function first checks if the SDF file is provided in the request. If not, it raises a 400
    error. It then extracts the molecule name from the file and checks if it already exists in the
    database. If it does, a 400 error is raised. Otherwise, the molecule is added to the database,
    and a success message is returned.

    Returns:
        str: A success message indicating that the file has been uploaded successfully.
    Raises:
        HTTPException: A 400 error if the SDF file is not provided or if the name already exists
                    in the database.
    """
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
    updated_svg_content = mol.adjust_svg_viewbox(svg_filename)
    clean_svg_content = mol.remove_namespace_prefix(updated_svg_content, "ns0:")
    with open(svg_filename, "w") as fp:
        fp.write(clean_svg_content)

    with open(svg_filename, "r") as fp:
        svg_content = fp.read()
    
    os.remove(svg_filename)
    return svg_content, 200, {"Content-Type": "image/svg+xml"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))