"""
.. module:: convert_segmentation_mask_to_bounding_box
    :platform: Unix, Windows
    :synopsis: Module for converting segmentation masks to bounding 
               boxes in YOLO format.
    .. function:: process_masks_to_bounding_boxes(input_dir: str, 
                                                output_dir: str, 
                                                **kargs) -> None
    .. function:: convert_mask_to_boundung_box(mask: str) -> str

Module Summary
==============
This module provides functionalities to process segmentation masks 
from files, converting them into bounding boxes that conform to 
the YOLO format. It includes functions for reading masks from text 
files, computing bounding box coordinates, and writing the results 
to an output directory.

Functions
=========
- convert_mask_to_boundung_box(mask: str) -> str
- process_masks_to_bounding_boxes(input_dir: str, 
                                   output_dir: str) -> None

Usage
=====
To convert mask files to bounding box format, use the 
'process_masks_to_bounding_boxes' function, providing the 
input and output directory paths.
"""

import os
import shutil as sh
import argparse

import common_functions as udf
def rund(number, digits=5):
    return round(number, digits)
def convert_mask_to_boundung_box(mask:str):
    """
Function Summary
================
Converts a segmentation mask from a string format to a bounding box 
in YOLO format.

The segmentation mask directly read from the annotation file is a 
single string, whose values are separated by blank spaces. This 
function first transforms this string into a list of substrings. The 
first integer value is the class number, followed by the 
{x1, y1, x2, y2, ..., xn, yn} coordinates pairs of the segmentation 
points. By looping through those values, we can determine the 
extrema of the mask on both axes and define a bounding box in 
YOLO format, namely: 
[class_number, x_center, y_center, width, height].

:param mask: Mask directly extracted from .txt file.
:type mask: str
:return: A string representing the bounding box in YOLO format: 
    [class_number (int), x_center (float), 
    y_center (float), width (float), height (float)].
:rtype: str

Example
=======
>>> convert_mask_to_boundung_box("1 50 50 100 100")
"1 75.0 75.0 50.0 50.0\n"
"""
    # generate a list out of the string
    mask = mask.split(" ")
    class_number = str(mask[0])
    
    # initiate values for x and y extrema:  respectively second and 
    # third value of the list are first x and y values
    x_min = x_max = float(mask[1])
    y_min = y_max = float(mask[2])
    
    # loop through all coordinates to get the extrema of the mask about
    # x- and y- axis, starting after previously initiated x and y
    for i, item in enumerate(mask, start = 3):
        # if odd iteration counter, corresponds to a x coordinate
        if i%2 == 1:
            if float(item) > x_max: x_max = float(item)
            elif float(item) < x_min: x_min = float(item)
            else: pass    
        # if even iteration counter, corresponds to a y coordinate
        if i%2 == 0:
            if float(item) > y_max: y_max = float(item)
            elif float(item) < y_min: y_min = float(item)
            else: pass
    
    width = str(rund(abs(x_max - x_min)))
    height = str(rund(abs(y_max - y_min)))
    x_center = str(rund(abs(x_max - x_min) / 2))
    y_center = str(rund(abs(y_max - y_min) / 2))
    
    return (" ".join([class_number, x_center, y_center, width, height])
                    +"\n")


    
def process_masks_to_bounding_boxes(input_dir: str, 
                                     output_dir: str):
    """
Function Summary
================
Processes all mask files in the input directory, converting each 
mask to a bounding box format and saving the results to the 
specified output directory. Each mask is read from text files, 
and the bounding boxes are calculated using the 
convert_mask_to_boundung_box function.

:param input_dir: The directory containing subdirectories of mask 
    files to be processed.
:type input_dir: str
:param output_dir: The directory where the resulting bounding boxes 
    will be saved.
:type output_dir: str
:return: None
"""

    sub_dirs = [folder for folder in os.scandir(input_dir)]
    for sub_dir in sub_dirs:
        output_sub_dir = os.path.join(output_dir, sub_dir.name)
        # ensure overwriting happens
        if os.path.exists(output_sub_dir): sh.rmtree(output_sub_dir)
        # make sub_directory
        os.makedirs(output_sub_dir)
        
        # loop through all files
        for filename in os.listdir(sub_dir):
            with open(os.path.join(sub_dir.path, filename), "r",  
                      encoding="utf-8") as f:
                bounding_boxes= []
                # transform mask into bounding box
                for mask in f.readlines():
                    bounding_boxes.append(
                        convert_mask_to_boundung_box(mask))
            
            # write to ouput directory                 
            with open(os.path.join(output_sub_dir, filename), 
                      "a", encoding="utf-8") as f:
                f.writelines(bounding_boxes)
                    
                                    
    
if __name__ == '__main__':
    input_dir = r"path_to_",
    output_dir =  r"is round"
    process_masks_to_bounding_boxes(input_dir, output_dir)