"""
.. module:: common_functions
   :platform: Unix, Windows
   :synopsis: Utility functions for directory and list manipulation.
   .. function:: flatten_list(list_of_lists: list) -> list
   .. function:: mkdir_unique(new_dir_path: str) -> str
   .. function:: change_permissions(directory:str, mode: int = 0o777)
   .. function:: find_images_labels_folders_nested(dir: str) -> list
   .. function:: count_number_of_image_and_labels(dataset_path: str) 
                -> tuple[int, int]
Module Summary
==============
This module contains utility functions for working with file directories 
and manipulating nested lists. It includes functions to flatten a list 
of lists, create unique directories, change directory permissions, 
and recursively find directories containing specific subfolders 
("images" and "labels").

Functions
=========
- flatten_list: Flattens a nested list into a single one-dimensional 
    list.
- mkdir_unique: Creates a unique directory at a specified path.
- change_permissions: Changes the permissions of a directory and its 
    contents recursively.
- find_images_labels_folders: Searches for directories containing 
    "images" or "labels" subfolders.
- count_number_ofimage_and_labels: counts the number of images and 
    labels contained in a dataset (train, test and val all comprised
    together)

Example
=======
>>> from my_module import flatten_list, mkdir_unique, 
    find_images_labels_folders
>>> flattened = flatten_list([[1, 2, [3]], [4, 5]])
>>> print(flattened)
[1, 2, 3, 4, 5]
>>> dir_path = mkdir_unique("my_directory")
>>> folders = find_images_labels_folders("/path/to/data")
>>> print(folders)
['/path/to/data/folder1', '/path/to/data/folder2']
"""

import os
from datetime import datetime
from functools import reduce


def count_number_of_image_and_labels(dataset_path: str):
    r"""
Function Summary
================
Counts the total number of images and label files in a dataset 
structured with subdirectories containing "images" and "labels" 
folders. Usefull for debugging and making sure merges have occurred
without errors

:param dataset_path: The path to the dataset directory which contains 
    subdirectories with "images" and "labels" 
    folders.
:type dataset_path: str
:return: A tuple containing two integers: the total number of images 
    and the total number of label files found in the dataset.
    (number_images,number_labels)
:rtype: tuple[int, int]

Example
========
>>> total_images, total_labels = count_number_of_image_and_labels("path/to/dataset")
>>> print(total_images, total_labels)
(150, 150)

Notes
=====
- The function assumes that each subdirectory contains a folder named 
    "images" and a folder named "labels". If these folders are not 
    present, the function will skip that subdirectory.
"""
    sub_dirs = os.scandir(dataset_path)
    number_image = 0
    number_labels = 0
    for subfolder in sub_dirs:
        if not subfolder.is_dir():
            continue
        images_folder = os.path.join(subfolder.path, "images")
        number_image += len(os.listdir(images_folder))
        labels_folder = os.path.join(subfolder.path, "labels")
        number_labels += len(os.listdir(labels_folder))
    return number_image, number_labels

def flatten_list(self,list_of_lists:list):
    """
Function Summary
================
Flattens a list containing nested lists into a single one-dimensional 
list. If the input is not a list, it returns a list containing the 
input element.

:param list_of_lists: A list that may contain nested lists. The 
    function will recursively flatten any nested 
    structures within it.
:type list_of_lists: list
:return: A one-dimensional list containing all the elements from 
    the input list, including those from any nested lists.
:rtype: list

Example
=======
>>> flatten_list([[1, 2, [3]], [4, 5]])
[1, 2, 3, 4, 5]

>>> flatten_list(10)
[10]
"""
    if not isinstance(list_of_lists, list):
        return [list_of_lists]
    else:
        return reduce(lambda acc, x: acc + flatten_list(x), 
                      list_of_lists, [])
        
def mkdir_unique(new_dir_path):
    """
Function Summary
================
Creates a new directory at the specified path. If the directory 
already exists, a unique directory name is generated by appending 
an index to the base name, and the new directory is created.

:param new_dir_path: The path where the new directory should be 
    created. If a directory with this name already 
    exists, a unique name will be generated.
:type new_dir_path: str
:return: The path to the newly created directory, whether it is 
    the original or the unique one.
:rtype: str

Example
=======
>>> mkdir_unique("my_directory")
'my_directory'  # If it didn't exist initially

>>> mkdir_unique("my_directory")
'my_directory_1'  # If 'my_directory' already existed
"""
    # Check if the directory already exists
    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)
        return new_dir_path
    
    # Directory already exists, generate a unique name
    index = 1
    
    while True:
        unique_dir_path = f"{new_dir_path}_{index}"
        
        if not os.path.exists(unique_dir_path):
            os.makedirs(unique_dir_path,0o777)
            change_permissions(unique_dir_path)
            return unique_dir_path
        
        index += 1
def change_permissions(directory, mode = 0o777):
    # Change permissions recursively
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), mode)
        for file in files:
            os.chmod(os.path.join(root, file), mode)
            
def find_images_labels_folders(input_dir):
    """
Function Summary
================

Recursively searches through a directory to find subfolders named 
"images" or "labels". When such folders are found, the function 
adds the parent directory containing these subfolders to a list.

This function is designed to locate directories that contain images 
and labels for further processing in a dataset.


:param dir: The path of the directory to search for subfolders. 
    The search is performed recursively within all nested 
    subdirectories.
:type dir: str
:return: A list of directories that contain either an "images" or 
    "labels" subfolder.
:rtype: list

Example
=======
>>> folders = find_images_labels_folders_nested("/path/to/data")
>>> print(folders)
['/path/to/data/folder1', '/path/to/data/folder2']
"""
    folders_containing_images_labels_sub_folders = []
    def find_images_labels_folders_nested(dir):
        folder_content = os.scandir(dir)
        for file in folder_content:
            if not os.path.isdir(file):
                pass
            elif file.name == "images" or file.name == "labels":
                folders_containing_images_labels_sub_folders.append(dir)
                break
            else:
                find_images_labels_folders_nested(file) 
    if os.path.exists(os.path.join(input_dir,"images")):
        input_dir = os.path.dirname(input_dir)
    find_images_labels_folders_nested(input_dir)
    return folders_containing_images_labels_sub_folders

if __name__ == "__main__":
    pass