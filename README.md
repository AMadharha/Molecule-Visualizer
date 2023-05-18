# Molecule Visualizer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/ankushmadharha/)

Website: https://moleculevisualizer.tech

# Project Description
Molecule Visualizer is a web application that allows users to visualize and interact with molecular structures in 2D. It enables users to upload molecular data files, explore the molecular structure, and download visualizations in various formats.

# Pages
## Home Page
The [homepage](http://moleculevisualizer.tech/index.html) of Molecule Visualizer provides users with a brief introduction to the fundamentals of molecular structure. It covers the basic building blocks of matter, such as atoms, molecules, and chemical bonds (covalent and ionic bonds), as well as the concept of atomic number. The homepage also highlights the importance of molecular geometry in determining the properties and behavior of molecules.

## How it Works Page
The ["How It Works"](http://moleculevisualizer.tech/works.html) page offers a technical description of the Molecule Visualizer's implementation for users interested in the underlying technology. The visualizer is built on a C library for representing and manipulating molecules, which is then interfaced with Python using SWIG. The Python module `mol_display.py` is responsible for parsing SDF files and outputting SVG files, while also handling the database of elements. This allows the visualizer to recognize and display a wide variety of molecular structures based on their SDF input files. The final SVG is then displayed on the page for analysis.

## Visualizer
The [Visualizer](http://moleculevisualizer.tech/visualizer.html) page is the core of the Molecule Visualizer application, allowing users to upload SDF files and visualize molecules. Users can upload molecules in SDF format, which are then saved in the database for future access. The page also provides a selection interface for choosing previously uploaded molecules to visualize. This makes it easy for users to interact with and explore various molecular structures and their properties.

# Sample Molecule
Here is a sample molecule (zinc phthalocyanine) visualized by the visualzier: 

![Molecule Image](https://raw.githubusercontent.com/AMadharha/Molecule-Visualizer/main/samples/molecule.png "Sample Molecule")

# Project Specifications
* C (C99 Standard)
* Python version 3.11.3
* Flask version 2.3.2
* Hosted on Heroku

