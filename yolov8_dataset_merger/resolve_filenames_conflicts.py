"""
.. module:: resolve_filenames_conflicts
    :platform: Unix, Windows
    :synopsis: A module for merging datasets containing images and labels
    of yolov8 format.
    .. function:: resolve_filenames_conflicts_and_merge(path_list: list[str], 
                                                    output_name=None, 
                                                    base_directory=None)
                                                    -> None
    .. function:: merge_datasets(path_to_folder_containing_datasets: str, 
                                  output_dataset_path: str = None) -> None
                                  
Module Summary
==============

This module provides functionality to merge multiple datasets that cont- 
ain images and corresponding label files. The datasets are expected to be 
structured in subdirectories for training, testing, and validation, with 
each containing their respective 'images' and 'labels' directories. 

The module includes functions for resolving filename conflicts during 
the merge process, as well as generating a consolidated YAML file that 
contains class remapping information.

Functions
=========
1. resolve_filenames_conflicts_and_merge(path_list: list[str], 
                                        output_name=None, 
                                        base_directory=None) -> None
   - Merges multiple directories containing images and labels, resolving 
     filename conflicts by appending suffixes to duplicate filenames.

2. merge_datasets(path_to_folder_containing_datasets: str, 
                 output_dataset_path: str = None) -> None
   - Merges datasets from a specified folder into a single dataset, 
     organizing the output into subdirectories for training, testing, 
     and validation. Creates a merged YAML file containing class 
     remapping information.

Dependencies
============
- `yaml_file_merger`: For merging YAML files.
- `map_classes_number`: For remapping class identifiers in label files.
- `common_functions`: For utility functions such as creating unique 
  directories.

Notes
=====
Ensure that the datasets being merged follow the expected directory 
structure for the module to function correctly. Typically, this means
that a yolov8 dataset folder contains a .yaml file containing metadata,
subfolders called "train", "test" and "val" or "valid". These subfolders
have their own subfolders that should be called "images" and "labels".
Any discrepancy in the names will result in failure of the functions.
"""

import os
from collections import Counter
import shutil as sh

from yolov8_dataset_merger import yaml_file_merger 
from yolov8_dataset_merger import map_classes_number 
from yolov8_dataset_merger import common_functions as cf

# for debugging
def are_there_conflicts(folder:str):
    """_summary_
    returns a dictionary of file names that occur more than once in the 
    given directory, with filenames as key and
    number of occurences as value
    Args:
        folder (str): path/to/folder

    Returns:
        dict
    """
    content = os.listdir(folder)
    counts = Counter(content)
    conflicts = {}
    for key, value in counts.items():
        if value > 1:
            conflicts[key] = value
    return conflicts        
    
def resolve_filenames_conflicts_and_merge(path_list:list[str], 
                                          output_name = None, 
                                          base_directory=None):
    """
Function Summary
=======
Merges multiple directories that contain subdirectories named 
"images" and "labels". The function resolves filename conflicts 
by appending a suffix to conflicting ones. This is useful for 
consolidating datasets while maintaining unique identifiers.

Parameters
==========
:param path_list: A list of directories to be merged. Each directory 
    must contain subdirectories named "images" and "labels". Those 
    directories are typically "train", "test" and "val" or "valid", for 
    yolov8
:type path_list: list[str]
:param output_name: The name of the output directory. If not 
    provided, a default output directory will be created. This is on the
    level of "train", "test" and "valid"
:type output_name: str, optional
:param base_directory: The base directory where the output 
    directory will be stored. It is the global output merged dataset 
    directory. If not provided, it will default 
    to the parent directory of the first images directory.
:type base_directory: str, optional
:return: None
"""
    # parse images and labels directory paths
    images = [item + os.sep+"images" for item in path_list]
    labels = [item + os.sep+"labels" for item in path_list]
    if len(images) == len(labels):
        image_dict = {}
        list_all = []
        for i,path in enumerate(images):
            # apply split extension lambda function to all filenames in
            # given directory "path" and get file_name_w/0_extension
            file_wo_ext = list(map(lambda x: os.path.splitext(x)[0],
                                   os.listdir(path)))
            
            # append all filenames w/o extension to a single list
            list_all += file_wo_ext
            
        # count all occurences of a filename in the list of all
        # filenames. gives a dictionary with filename as key,
        # occurences as value    
        counts = Counter(list_all)
              
        # handling default output directory name, if no name is given
        # base directory is the merged dataset folder, whereas output
        # is for the new subdirectory, for instance new train. 
        if base_directory is None:
            base_directory = os.path.dirname(os.path.dirname(images[0]))
        output_dir = (base_directory 
                      + os.sep 
                      + "output" 
                      if output_name is None else 
                      base_directory + os.sep + output_name) 
        
        # make output directory and sub directories "images" and "labels"
        output_images_directory = output_dir + os.sep + "images"
        os.makedirs(output_images_directory,mode=0o777)
        output_labels_directory = output_dir + os.sep + "labels"
        os.makedirs(output_labels_directory, mode=0o777)
        
        # loop in images folder paths list
        for index, image_folder in enumerate(images):
            # get corresponding labels folder
            labels_folder = labels[index]
            
            # loop through the files of image folder
            for filename in os.listdir(image_folder):
                
                # get the filename and it's extension
                file_wo_ext = os.path.splitext(filename)[0] 
                file_ext = os.path.splitext(filename)[1]
                
                # if there are more than 1 occurences of that filename
                if file_wo_ext in counts and counts.get(file_wo_ext) > 1:
                    # one occurence will be computed, substract one for 
                    # the upcoming loops
                    counts[file_wo_ext] -= 1
                    
                    # build the new file name
                    new_file_name = file_wo_ext + f"_{counts.get(file_wo_ext)}"
                    
                    # add image extension to filename
                    new_image_file = new_file_name + file_ext
                    
                    # build old and new label filename, these are .txt files
                    old_label_file = file_wo_ext + ".txt"
                    new_label_file = new_file_name + ".txt"
                    
                    # copy image file to output/images directory with 
                    # new image filename
                    sh.copy2(image_folder + os.sep + filename,
                             output_images_directory + os.sep + new_image_file)
                    
                    # copy old label file to output labels directory 
                    # with new label filename
                    sh.copy2(labels_folder + os.sep + old_label_file, 
                             output_labels_directory + os.sep + new_label_file)
                    
                # if filename is unique, copy these also 
                # to their respective output dir.
                else:
                    old_label_file = file_wo_ext + ".txt"
                    sh.copy2(image_folder + os.sep + filename,
                             output_images_directory + os.sep + filename)
                    sh.copy2(labels_folder + os.sep + old_label_file, 
                             output_labels_directory + os.sep + old_label_file)
    else:
        print("not the same number of images and labels folders")
              
def merge_datasets(path_to_folder_containing_datasets:str,
                   output_dataset_path:str = None):
    """
    Function Summary
    =======
    Merges multiple datasets contained within a specified folder into a 
    single dataset. This function organizes the merged dataset into 
    subdirectories for training, testing, and validation. It creates
    a merged .yaml file which contains metadata, most importantly 
    class ids and their remapped numbering, with the submodule 
    *yaml_file_merger*. It will then modify the label files to change
    the class ids according the the remapping in the yaml file, with
    submodule *map_classes_number*.   

    :param path_to_folder_containing_datasets: The path to the folder 
        that contains the individual datasets with their respective 
        training, testing, and validation folders, and their yaml file.
    :type path_to_folder_containing_datasets: str
    :param output_dataset_path: The optional path where the merged 
        dataset will be saved. If not provided, the merged dataset will 
        be created in the same parent directory as the input datasets.
    :type output_dataset_path: str, optional
    :return: None

    Example
    =======
    >>> merge_datasets("path/to/folder/containing/datasets")
    """
    
    # initialize lists of paths of all datasets in given folder
    datasets_paths = [path_to_folder_containing_datasets 
                      + os.sep 
                      + dataset_path 
                      for dataset_path in 
                      os.listdir(path_to_folder_containing_datasets)]
    # if list not empty
    if datasets_paths:
        # make output directory in same parent directory as 
        # datasets_paths if none was given
        if output_dataset_path is None: 
            output_dataset_path = os.path.join(
                            os.path.dirname(path_to_folder_containing_datasets), 
                            "merged_dataset")
        else: output_dataset_path = output_dataset_path+os.sep+"merged_dataset"
        output_dataset_path = cf.mkdir_unique(output_dataset_path)
        
        # merge yaml files
        yaml_file_path = yaml_file_merger.merge_yaml_files_from_folder(
            path_to_folder_containing_datasets,output_dataset_path)
        
        # remap classes in all labels.txt file
        map_classes_number.replace_class_number_from_folder(
            path_to_folder_containing_datasets, yaml_file_path)
        
        train = [folder+os.sep+"train" for folder in datasets_paths 
                 if os.path.exists(folder+os.sep+"train")]
        test = [folder+os.sep+"test" for folder in datasets_paths 
                if os.path.exists(folder+os.sep+"test")]
        valid = [folder+os.sep+"valid" for folder in datasets_paths 
                 if os.path.exists(folder+os.sep+"valid")]
        valid += [folder+os.sep+"val" for folder in datasets_paths 
                  if os.path.exists(folder+os.sep+"val")]
        
        # merge subdirectories
        if train: resolve_filenames_conflicts_and_merge(train,
                                                        "train",
                                                        output_dataset_path)
        if test: resolve_filenames_conflicts_and_merge(test,
                                                       "test",
                                                       output_dataset_path)
        if valid: resolve_filenames_conflicts_and_merge(valid,
                                                        "valid",
                                                        output_dataset_path)
    else:
        print(f"\n{path_to_folder_containing_datasets}\ncontains nothing")
   
if __name__ == "__main__":
    pass
    