r"""
.. module:: build_sphinx

Module Summary
==============

This module automates the generation of Sphinx documentation for a 
Python package using the 'sphinx-apidoc' command and provides 
utilities to clean up old documentation files before building the new 
documentation. The module also includes functionality to handle the 
execution of a Makefile (or make.bat on Windows) to build the 
documentation in different formats (e.g., HTML, LaTeX).

Functions
=========

- 'clean_rst_files(directory: str)': Deletes all '.rst' files in the 
  specified directory, except for 'index.rst'.
  
- 'clean_build_directory(output_dir: str)': Deletes all contents in 
  the '_build' directory, except the directory itself.

- 'build_documentation(exclude_patterns: list[str], output_dir: str, 
  source_dir: str)': Generates Sphinx documentation using 
  'sphinx-apidoc' and builds the output in the specified format.

- 'Makefile(output_dir: str, format: str = 'html')': Runs the 
  appropriate Makefile (or make.bat) to generate the documentation in 
  the specified format.

Example
=======

To run the script, ensure that `sphinx-apidoc` is installed and 
available in your system's PATH, then call the `build_documentation()` 
function with your desired parameters:

.. code-block::

    exclude_patterns = ["*test*", ".vscode", 
                        "datasets_to_merge", "merged_dataset*", 
                        "runs", "instances_train2017.json", 
                        "yolov8n-seg.pt", "yolov8n.pt"]
    output_dir = r"C:\path\to\your\docs"
    source_dir = r"C:\path\to\your\package-or-dir-containg-modules"
    build_documentation(exclude_patterns, output_dir, source_dir)

Notes
============
- usefull `primer tutorial <https://towardsdatascience.com/documenting-python-code-with-sphinx-554e1d6c4f6d>`_ 
- 'sphinx-apidoc' must be installed.
- 'sphinx' must be configured in the output directory for building the 
  documentation. This can be done with command 'sphinx-quickstart'.
  Note that after configuration with the sphinx wizard, you'll
  need to modify the conf.py file in output directory. For consistent 
  style and behavior, configure as follow:
  
.. code-block::

    # Configuration file for the Sphinx documentation builder.
    #
    # For the full list of built-in configuration values, see the documentation:
    # https://www.sphinx-doc.org/en/master/usage/configuration.html
    # -- Path setup --------------------------------------------------------------
    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))
    # -- Project information -----------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

    project = 'YOLOv8 Dataset Merger'
    copyright = '2024, Frederic Pepin'
    author = 'Frederic Pepin'
    release = '2024-09-30'

    # -- General configuration ---------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.napoleon'
    ]

    templates_path = ['_templates']
    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

    # -- Options for HTML output -------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

    html_theme = 'sphinx_rtd_theme'
    html_static_path = ['_static']

"""

import subprocess
import os
import sys
import shutil as sh

def clean_rst_files(directory: str):
    r"""
    Function Summary
    ================
    
    Deletes all .rst files in the specified directory except 'index.rst'.
    
    :param directory: The directory to search for .rst files.
    :type directory: str
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".rst") and file != "index.rst":
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

def clean_build_directory(output_dir: str):
    r"""
    Function Summary
    ================
    Deletes all contents of the '_build' directory except the director
    itself.
    
    :param output_directory: The path to the output directory (docs) 
        containing the '_build' directory.
    :type output_directory: str
    """
    build_directory = os.path.join(output_dir, "_build")
    for item in os.listdir(build_directory):
        item_path = os.path.join(build_directory, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
            print(f"Deleted file: {item_path}")
        elif os.path.isdir(item_path):
            sh.rmtree(item_path)
            print(f"Deleted directory and contents: {item_path}")

def build_documentation(exclude_patterns: list[str],
                      output_dir: str = "docs", 
                      source_dir = os.path.dirname(__file__)):
    r"""
Function Summary
================

Generates Sphinx documentation using the sphinx-apidoc command.

This function searches the current working directory for modules 
to be documented (by default) or given source folder. The output is 
saved to the specified directory (defaults to 'docs' in the current 
working directory). Specific file patterns can be excluded from the 
documentation generation.

:param exclude_patterns: A list of patterns to exclude from the 
    documentation generation (e.g., test files, configuration folders, 
    or non-module files).
:type exclude_patterns: list[str]
:param output_dir: The directory where the generated documentation 
    will be saved (defaults to 'docs').
:type output_dir: str
:param source_dir: The directory of the source code (defaults to the 
    current file's directory).
:type source_dir: str
:return: None
:rtype: None

Notes
=====
- The function changes the working directory to the script's location 
    before running the `sphinx-apidoc` command.
- The command output is captured for debugging purposes.
- in the index.rst file, *modules* should be appended:

::
    
    .. toctree::
   :maxdepth: 2
   :caption: Contents:
   modules
   [...]
   
"""
    args= ["sphinx-apidoc", "-o", ]
    args += [output_dir, source_dir]
    args += exclude_patterns
    
    # clean old content
    clean_rst_files(output_dir)
    clean_build_directory(output_dir)

    # parse docstrings to reStructuredText files
    os.chdir(os.path.dirname(__file__))    
    subprocess.run(args, shell=True)
    
    # Build html files 
    Makefile(output_dir)
    
def Makefile(output_dir, format:str = "html"):
    r"""
    Function Summary
    ================
    
    Execute Makefile independently of OS

    :param output_dir: where documentation will be contained
    :type path_to_make_script: str
    :param format: format to export to, html is default. 
        other formats are latexpdf, see sphinx documentation for 
        necessary dependencies
    :type format: str
    """
    if sys.platform == "win32":
        path_to_make_file = os.path.join(output_dir, "make.bat")
    else:
        path_to_make_file = os.path.join(output_dir, "make")
        
    subprocess.run([path_to_make_file, format], 
                    shell=True,
                    )

if __name__ == "__main__":
    
    exclude_patterns = ["*test*", ".vscode", 
            "datasets_to_merge", "merged_dataset*", "runs", 
            "instances_train2017.json", "yolov8n-seg.pt" "yolov8n.pt"]
    output_dir = r"C:\Users\FPepin\Synology\TwoWaysSync\__TU_BERLIN\_ProjektIAT_Robotergreifer\perception\yolov8_dataset_merger\docs"
    source_dir = r"C:\Users\FPepin\Synology\TwoWaysSync\__TU_BERLIN\_ProjektIAT_Robotergreifer\perception\yolov8_dataset_merger"
    build_documentation(exclude_patterns,output_dir,source_dir)

