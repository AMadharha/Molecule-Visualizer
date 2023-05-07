from setuptools import setup, Extension
import sysconfig
import os

c_molecule_directory = "C-molecule-library"

molecule_module = Extension('_molecule',
                            sources=[os.path.join(c_molecule_directory, 'molecule_wrap.c'),
                                     os.path.join(c_molecule_directory, 'molecule.c')],
                            include_dirs=[sysconfig.get_path('include')],
                            extra_compile_args=['-Wall', '-std=c99', '-pedantic'],
                            extra_link_args=[os.path.join(os.path.dirname(__file__), 'libmol.so')],
                            )

setup(
    name='_molecule',
    version='0.1',
    description='Molecule extension module',
    ext_modules=[molecule_module],
)
