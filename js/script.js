// Form file text
document.getElementById('sdf_file').addEventListener('change', function (e) {
    const fileName = e.target.files[0]?.name || 'No file selected';
    document.getElementById('file-name').textContent = fileName;
});

// Uploading SDF
const form = document.getElementById("sdf-form");
form.addEventListener('submit', function(event) {
    event.preventDefault();

    const file = document.getElementById("sdf_file").files[0];
    const formData = new FormData();
    formData.append("sdf_file", file);

    fetch("/upload-sdf", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (response.ok) {
            // Call the function to fetch molecules and update the table
            fetchMoleculesAndUpdateTable();
        } else {
            throw new Error("Failed to upload SDF file");
        }
    })
    .catch(error => console.error(error))
})

// Create molecule table
function fetchMoleculesAndUpdateTable() {
    const moleculeTable = document.getElementById("molecule-select-table");
    moleculeTable.innerHTML = "";
    fetch("/get-molecules")
        .then(response => response.json())
        .then(molecules => {
            const headerRow = document.createElement("tr");

            const nameHeader = document.createElement("th");
            nameHeader.textContent = "Name";

            const selectHeader = document.createElement("th");
            selectHeader.textContent = "Visualize";

            headerRow.appendChild(nameHeader);
            headerRow.appendChild(selectHeader);
            moleculeTable.appendChild(headerRow);

            molecules.forEach(molecule => {
                const row = document.createElement("tr");

                const nameCell = document.createElement("td");
                nameCell.textContent = molecule.NAME;

                const visualizeCell = document.createElement("td");
                
                const visualizeButton = document.createElement("button");
                visualizeButton.textContent = "Visualize";
                visualizeButton.classList.add("visualize-button");

                visualizeButton.addEventListener("click", () => {
                    fetch("/get-svg", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ name: molecule.NAME })
                    })
                    .then(response => {
                        if (response.ok) {
                            return response.text();
                        } else {
                            throw new Error("Failed to fetch SVG");
                        }
                    })
                    .then(svg => {
                        // Get a reference to the SVG container element
                        const svgContainer = document.getElementById("svg-container");

                        // Create a new DOM parser
                        const parser = new DOMParser();

                        // Parse the SVG content
                        const svgDoc = parser.parseFromString(svg, "image/svg+xml");

                        // Create a rect element for the background
                        const backgroundRect = svgDoc.createElementNS("http://www.w3.org/2000/svg", "rect");

                        // Set the rect attributes
                        backgroundRect.setAttribute("width", "100%");
                        backgroundRect.setAttribute("height", "100%");
                        backgroundRect.setAttribute("fill", "rgb(200,200,200)");

                        // Insert the background rect as the first child of the SVG element
                        svgDoc.documentElement.insertBefore(backgroundRect, svgDoc.documentElement.firstChild);

                        // Serialize the modified SVG content
                        const serializer = new XMLSerializer();
                        const modifiedSvg = serializer.serializeToString(svgDoc.documentElement);

                        // Set the innerHTML of the container to the modified SVG content
                        svgContainer.innerHTML = modifiedSvg;
                    })
                    .catch(error => console.error(error));
                });

                visualizeCell.appendChild(visualizeButton);
                row.appendChild(nameCell);
                row.appendChild(visualizeCell);
                moleculeTable.appendChild(row);
            })
        })
        .catch(error => console.error(error));
}

fetchMoleculesAndUpdateTable();

