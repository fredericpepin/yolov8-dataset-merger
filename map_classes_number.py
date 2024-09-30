"""
.. module:: map_classes_number
    :platform: Unix, Windows
    :synopsis: A module for remapping class numbers in label files.
    .. function:: replace_class_number_in_file(
                            labels_directory: str, 
                            original_new_tuple_list: 
                            list[tuple], 
                            replace: bool = False, 
                            output_folder_name: str = "mapped_labels") 
                            -> None
    .. function:: replace_remapped_class_number(
                            remapped_yaml_file_path: str, 
                            labels_directories: list[str], 
                            replace: bool = False, 
                            output_folder_name: str = "mapped_labels") 
                            -> None
    .. function:: replace_class_number_from_folder(folder_containing_datasets: str, 
                                               remapped_yaml_file_path: str, 
                                               replace: bool = True) -> None
Module Summary
=============

This module provides functions to remap class integers in label files 
based on mappings defined in a YAML files. YAML files are expected to 
have been previously automatically remapped with the module 
*yaml_file_merger* to provide for a clean remapping of each classes ids.
It is useful when merging datasets that may have conflicting or 
different class numbering/ids.

Functions
=========
- replace_class_number_in_file: Remaps class integers in label files 
  based on a mapping provided in a list of tuples.
  
- replace_remapped_class_number: Replaces class integers in label 
  files based on a mapping defined in a remapped YAML file.
  
- replace_class_number_from_folder: Replaces class integers in all 
  label files found within a specified folder containing multiple 
  datasets.

Usage
=====
This module is intended to be used for preprocessing label files before 
merging datasets to ensure consistent class numbering. 
"""

import os
import shutil as sh
from datetime import datetime

import re 
import yaml

import common_functions as cf
import yaml_file_merger as y

def replace_class_number_in_file(labels_directory: str,
                                 original_new_tuple_list: list[tuple], 
                                 replace = False, 
                                 output_folder_name:str = "mapped_labels" ):
    """
Function Summary
=======
Remaps class integers in label files based on a mapping provided in 
a list of tuples. This is useful when merging datasets to ensure 

:param labels_directory: Path to the directory containing label files 
    to be remapped.
:type labels_directory: str
:param original_new_tuple_list: List of tuples where each tuple 
    contains an old class integer and 
    its corresponding new class integer.
    (old,new)
:type original_new_tuple_list: list[tuple[int]]
:param replace: If True, replaces the original labels directory with 
    the remapped one and deletes the original. Default is 
    False.
:type replace: bool
:param output_folder_name: Name of the output folder for the 
    remapped labels. If not provided, it 
    will be created in the same parent 
    directory as labels_directory. Default 
    is "mapped_labels".
:type output_folder_name: str
:return: None

Example
=======
>>> replace_class_number_in_file("path/to/labels", 
>>>                               [(0, 1), (1, 2), (2, 3)])
"""
    # reorganize tuples to list of strings
    original = [str(item[0]) for item in original_new_tuple_list]
    new = [str(item[1]) for item in original_new_tuple_list]
    
    # list of all files in labels_directory
    file_names = os.listdir(labels_directory)
    print(f"number of files in original labels_folder: {len(file_names)}")

    # make output directory, in same parent directory as labels_directory
    output_dir = os.path.join(os.path.dirname(labels_directory),
                              output_folder_name)
    if replace:
        os.rename(labels_directory,labels_directory+"_original")
        output_dir = labels_directory
        labels_directory = labels_directory+"_original"
    cf.mkdir_unique(output_dir)
    os.chmod(output_dir,0o777)

    for file in file_names:
        # read file content
        file_path = os.path.join(labels_directory,file)
        with open(file_path, "r",encoding="utf-8", newline=os.linesep) as f:
            lines = f.readlines()
        # values are separated by spaces
        lines = [list(map(lambda x: x.replace("\r","").replace("\n",""), 
                          line.split(" "))) 
                          for line in lines]
        # check and compute class number to be changed
        new_lines = []
        for line in lines:
            # class integer is always the first value therefore [0]
            if str(line[0]) in original:
                # get index where value is found, to refer to same index 
                # in list of new class integers
                index = original.index(str(line[0]))
                line[0] = new[index] 
            # from list to one string
            line = " ".join(line)
            if line != "\r": new_lines.append(line) 
        # write file to output directory
        with open(os.path.join(output_dir,file), "w",encoding="utf-8") as f:
            f.writelines(new_lines)
    print(f"number of files in output folder: {len(os.listdir(output_dir))}")
    if replace:
        cf.change_permissions(labels_directory)
        sh.rmtree(labels_directory)
        print("original labels directory deleted")

def replace_remapped_class_number(remapped_yaml_file_path:str,
                                  labels_directories:list[str], 
                                  replace = False, 
                                  output_folder_name:str = "mapped_labels"):
    """
Function Summary
=======
Replaces class integers in label files based on a mapping defined in 
a remapped YAML file (see module yaml_file_merger). For datasets with 
different class numberings.

:param remapped_yaml_file_path: Path to the YAML file that defines 
    the remapped class integers.
:type remapped_yaml_file_path: str
:param labels_directories: List of paths to directories containing 
    label files to be updated.
:type labels_directories: list[str]
:param replace: If True, replaces the original labels with remapped 
    ones and deletes the originals. Default is False.
:type replace: bool
:param output_folder_name: Name of the output folder for remapped 
    labels. If not provided, it will be 
    created in the same parent directory as 
    labels_directory. Default is 
    "mapped_labels".
:type output_folder_name: str
:return: None
"""
    # regular expression to identify yaml file
    pattern = re.compile(".yaml$")
    for labels_directory in labels_directories:
        # join directory name and yaml file name for a complete path
        old_yaml = os.path.join(
            os.path.dirname(os.path.dirname(labels_directory)),
            # find first occurence of a file with .yaml extension
            next((s for s in os.listdir(
                                        os.path.dirname(
                                        os.path.dirname(labels_directory))
                                        ) if pattern.search(s)), None)
                )
        original_new_tuple_list = []
        
        # get both yaml files' parsed content
        old_yaml = y.parse_yaml_file(old_yaml)
        new_yaml = y.parse_yaml_file(remapped_yaml_file_path)
        
        new_yaml_names = [value for key, value in new_yaml["names"].items()]
        new_yaml_keys = [key for key, value in new_yaml["names"].items()]
        for key, value in old_yaml["names"].items():
            if value in new_yaml_names:
                original = key
                new = new_yaml_names.index(value)
                print(f"{value}: ({original}, {new})")
                original_new_tuple_list.append((original,new))
        replace_class_number_in_file(labels_directory,
                                     original_new_tuple_list,
                                     output_folder_name)
    
def replace_class_number_from_folder(folder_containing_datasets:str,
                                     remapped_yaml_file_path:str, 
                                     replace=True):
    """
Function Summary
=======
Replaces class integers in all label files found within a specified 
folder containing multiple datasets. The class integers are updated 
based on the mapping defined in a given remapped YAML file.
(see module yaml_file_merger)

:param folder_containing_datasets: The path to the folder that 
    contains multiple datasets, each 
    having their own 
    label files.
:type folder_containing_datasets: str
:param remapped_yaml_file_path: Path to the YAML file that defines 
    the remapped class integers.
:type remapped_yaml_file_path: str
:param replace: If True, replaces the original labels with remapped 
    ones and deletes the originals. Default is True.
:type replace: bool
:return: None
"""
    sub_datasets = [f.path 
                    for f in os.scandir(folder_containing_datasets) 
                    if f.is_dir()]
    sub_folders = [f.path  
                   for sub_dataset in sub_datasets
                   for f in os.scandir(sub_dataset) 
                   if f.is_dir()]
    labels_directories = [f.path 
                          for folder in sub_folders 
                          for f in os.scandir(folder) 
                          if f.name == "labels" ]
    replace_remapped_class_number(remapped_yaml_file_path,
                                  labels_directories,replace = True)
if __name__ == "__main__":
    pass