import http.server
import socketserver
import os
import mimetypes
from molsql import Database
import json
import cgi
import mol_display

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        file_path = 'index.html' if self.path == '/' else self.path[1:]
        file_path = os.path.join(os.path.dirname(__file__), file_path)

        if os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)

            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                response = f.read()
            self.wfile.write(response)
        elif self.path == "/get-molecules":
            db = Database(reset=False)
            db.create_tables()
            molecules = db.conn.execute("SELECT * FROM Molecules")

            molecule_dicts = []
            for molecule in molecules:
                molecule_dict = {
                    "NAME": molecule[1] 
                }
                molecule_dicts.append(molecule_dict)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(molecule_dicts), "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            response = "<html><body><h1>File not found</h1></body></html>"
            self.wfile.write(response.encode())

    def do_POST(self):
        if self.path == '/upload-sdf':
            content_type, pdict = cgi.parse_header(self.headers.get("Content-Type"))
            
            if content_type == "multipart/form-data":
                pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
                pdict["CONTENT-LENGTH"] = int(self.headers.get("Content-Length"))
                form_data = cgi.parse_multipart(self.rfile, pdict)

                file_data = form_data["sdf_file"][0]

                with open("temp.sdf", "wb") as f:
                    f.write(file_data)

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

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"File uploaded successfully.")

                os.remove("temp.sdf")
        elif self.path == '/get-svg':
            # Read the request data
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            # Parse the JSON data
            data = json.loads(post_data)

            # Access the molecule name
            molecule_name = data["name"]

            # Process the molecule name as needed (e.g., retrieve the SVG)
            db = Database(reset=False)
            mol_display.RADIUS = db.radius()
            mol_display.ELEMENT_NAME = db.element_name()
            mol_display.HEADER += db.radial_gradients()
            mol = db.load_mol(molecule_name)
            mol.sort()
            svg_filename = molecule_name + ".svg"
            with open(svg_filename, "w") as fp:
                fp.write(mol.svg())

            # Read the SVG content from the file
            with open(svg_filename, "r") as fp:
                svg_content = fp.read()

            # Send the response with the SVG content
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            self.wfile.write(svg_content.encode())

            # Remove the temporary SVG file
            os.remove(svg_filename)


PORT = 8000
handler = MyRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    httpd.serve_forever()
