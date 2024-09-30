"""
.. module:: yaml_file_merger
    :platform: Unix, Windows
    :synopsis: A module for parsing and merging YAML files containing 
                class mappings.
    .. function:: parse_yaml_file(yaml_file: str) -> dict
    .. function:: merge_yaml_files(yaml_files_paths_list: list[str], 
                                    output_path: str = None) -> str
    .. function:: merge_yaml_files_from_folder(folder_containing_datasets: str, 
                                                output_path: str = None) -> str

Module Summary
===========
This module provides functions to parse and merge YAML files that 
contain class mappings for different datasets. It ensures that improper 
formatting of yaml files is handled, remapping class names to unique 
integers and maintaining a count of the total classes. 
This functionality is especially useful when  combining datasets that 
may have conflicting or different class 
numbering.

Functions
=========
- parse_yaml_file: Parses a YAML file, converting the "names" key 
  into a dictionary format and ensuring the file's content is valid 
  for further processing.
  
- merge_yaml_files: Merges multiple YAML files into a single YAML 
  file, remapping class names to unique class integers and updating 
  the total class count.

- merge_yaml_files_from_folder: Merges all YAML files found within 
  subdirectories of a specified folder, compiling their contents and 
  remapping class names to unique integers.
"""

import os
import re
import yaml

def parse_yaml_file(yaml_file:str):
    r"""
Function Summary
=======
Parses a YAML file by removing any tab characters and converting 
the names specified in the file into a dictionary format. This 
function ensures that the resulting content is valid for further 
processing.

:param yaml_file: The file path to the YAML file that needs to be 
    parsed.
:type yaml_file: str
:return: A dictionary containing the parsed content of the YAML file. 
    The "names" key, if initially a list, is transformed into a 
    dictionary where the index is the key and the corresponding 
    name is the value.
:rtype: dict

Example
=======
>>> parsed_content = parse_yaml_file("path/to/yaml_file.yaml")
>>> print(parsed_content)
{'names': {0: 'class_1', 1: 'class_2', ...}}

Notes
=====
- This function replaces tab characters with double spaces since 
    tabs are not allowed in YAML syntax.
"""
    # newline = os.linesep, for me on windows, got rid of empty lines. 
    # might need to be changed for unix systems?
    with open(yaml_file,"r",encoding="utf-8",newline=os.linesep) as f:
        lines = f.readlines()
    # replace tabs with double spaces, remove trailing spaces, in each 
    # line. tabs are illegal in YAML
    lines = [line.replace("\t", " "*2).rstrip() for line in lines]

    # make a string (stream format) out of list
    lines = "\n".join(lines)
    
    # make a yaml format out of string  
    content = yaml.safe_load(lines)

    # avoid list format for classes
    if isinstance(content["names"],list):
        temp_dict = {}
        # list index as key for dictionary, value as value
        for i, name in enumerate (content["names"]):
            temp_dict[i] = name
        content["names"] = temp_dict

    return content

def merge_yaml_files(yaml_files_paths_list:list[str], output_path = None):
    r"""
Function Summary
=======
Merges multiple YAML files that contain class mappings into a single 
YAML file. This function ensures that class names are remapped to 
unique class integers and updates the total class count in the 
output.


:param yaml_files_paths_list: A list of paths to the YAML files 
    that need to be merged.
:type yaml_files_paths_list: list[str]
:param output_path: The optional path where the merged YAML file 
    will be saved. If not provided, it defaults 
    to the parent directory of the first dataset.
:type output_path: str, optional
:return: The path to the merged YAML file that was created.
:rtype: str

Example
=======
>>> merged_path = merge_yaml_files(["path/to/dataset1/data.yaml", 
...                                   "path/to/dataset2/data.yaml"])
>>> print(merged_path)
"path/to/parent/merged_data.yaml"

Notes
=====
- The function assumes that each YAML file contains a "names" key 
    mapping class integers to class names.
- If a class name already exists in the output dictionary, it 
    will not be added again.
- The total number of classes ('nc') is updated in the output 
    YAML file based on the unique class names.
"""
    # initialize output dictionary
    yaml_dict_out= None
    
    # loop over all data.yaml files to merge them
    for file in yaml_files_paths_list:
        
        # get yaml file content with the right format        
        yaml_dict = parse_yaml_file(file)        
        
        # initialize output dictionary
        if yaml_dict_out is None:
            yaml_dict_out = yaml_dict
            
        else:
            # lists of class names and keys in the output dictionary
            names = [value for key, value in yaml_dict_out["names"].items()]
            keys = [key for key, value in yaml_dict_out["names"].items()]
            
            # class names and keys in the file's dictionary
            for key, value in yaml_dict["names"].items():
                # if this class name is already in the output dictionary
                if value in names:
                    pass
                # otherwhise, write a new class name at the last key + 1 
                else:
                    names.append(value)
                    new_key = int(keys[-1]) + 1
                    keys.append(new_key)
                    yaml_dict_out["names"][new_key] = value
    # update number of classes
    yaml_dict_out["nc"] = str(len(yaml_dict_out["names"]))
    
    # output data.yaml file. If none was given, will be put in parent 
    # dictionary of the first dataset
    if output_path == None:
      output_path = (os.path.dirname(os.path.dirname(yaml_files_paths_list[0]))
                       + os.sep 
                       +  "merged_data.yaml")
    else: output_path = output_path + os.sep + "merged_data.yaml"
    with open(output_path, "w",encoding="utf-8") as f:
        yaml.safe_dump(yaml_dict_out,f)
        
    return output_path
   
def merge_yaml_files_from_folder(folder_containing_datasets:str, output_path=None):
    r"""
Function Summary
================
Merges all YAML files found within subdirectories of a specified 
folder into a single YAML file. The function searches for the first 
YAML file in each dataset folder and compiles their contents while 
remapping class names to unique integers.

:param folder_containing_datasets: The path to the folder that 
    contains multiple dataset subdirectories, each expected to 
    have a YAML file with class mappings.
:type folder_containing_datasets: str
:param output_path: The optional path where the merged YAML file 
    will be saved. If not provided, it defaults to the parent 
    directory, namely folder containing all subdatasets.
:type output_path: str, optional
:return: The path to the merged YAML file that was created.
:rtype: str

Example
=======
>>> merged_yaml_path = merge_yaml_files_from_folder("path/to/dataset_folder")
>>> print(merged_yaml_path)
"path/to/parent/merged_data.yaml"

Notes
=====
- The function expects each subdirectory to contain at least one 
    YAML file. If no YAML file is found, the corresponding folder 
    will be skipped.
- The merged YAML file will contain unique class mappings from 
    all the input YAML files.
"""
    datasets_folders = [folder_containing_datasets 
                        + os.sep 
                        + folder 
                        for folder in os.listdir(folder_containing_datasets)] 
    yaml_file_list = []
    pattern = re.compile(".yaml$")
    for folder in datasets_folders:
        try:
            # join directory name and yaml file name for a complete path
            yaml_file = os.path.join(folder,
                    # find first occurence of a file with .yaml extension
                    next((s for s in os.listdir(folder) 
                        if pattern.search(s)), None)
            )
            yaml_file_list.append(yaml_file)
        except Exception as e:
            print(e)
    return merge_yaml_files(yaml_file_list,output_path)
    
    
if __name__ == "__main__":
    pass