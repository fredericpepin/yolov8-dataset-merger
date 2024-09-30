"""
.. module:: supervisely_json_to_yolov8
    :platform: Unix, Windows
    :synopsis: Module for converting supervisely JSON annotation
    to bounding boxes in YOLO format.
    .. function: 
        json_syntax_to_yolov8_file(file_path: str) -> list[str]
    .. function: 
        json_syntax_to_yolov8_all(input_dir: str, output_dir: str) -> None
Module Summary
=======

module containing functions to transform JSON Supervisely annotations of
a dataset to YOLOv8 annotations.

"""
import os
import shutil as sh
import json

all_classes = []
all_classes_map_tuple_list = []

def rund(number:float, digits = 6):
    # can call the rund function without each time specifying a new 
    # number of digits after comma. So by defining "digits" as optional
    # input with default value, you define a precision for the whole
    # file
    return round(number, digits)

def json_syntax_to_yolov8_file(file_path: str) -> list[str]:
    """
Function Summary
=======

takes a supervisely file (JSON format), parses data contained in file,
and transforms to a yolov8 format.

:param file_path:
:type file_path: str
:return: list of all bounding boxes, each bounding box is a string with
    format '<class ID> <normalized x_center> <normalized y_center> 
    <normalized box width> <normalized box height>\\n' 
:rtype: list[str]
    """
    with open(file_path, "r") as f:
            dic = json.load(f)

    global all_classes 
    global all_classes_map_tuple_list
    
    bounding_boxes = []
    width_picture = float(dic["size"]["width"])
    height_picture= float(dic["size"]["height"])
    
    # retrieving relevant info from json file
    for object in dic["objects"]:
        object_class = object["classTitle"]
        if object_class not in all_classes: 
            all_classes.append(object_class)
        object_class = str(all_classes.index(object_class))
        
        # top left and bottom right points of bounding box
        (top_left_x, top_left_y) = [float(value) 
                                    for value 
                                    in object["points"]["exterior"][0]]
        (bottom_right_x, bottom_right_y) = [float(value) 
                                            for value 
                                            in object["points"]["exterior"][1]]
        
        # center positioning offset 
        x_min, x_max = ( (top_left_x,bottom_right_x) 
                        if top_left_x <= bottom_right_x 
                        else (bottom_right_x, top_left_x)
                        )  
        y_min, y_max = ( (top_left_y, bottom_right_y) 
                        if top_left_y <= bottom_right_y 
                        else (bottom_right_y, top_left_y)
                        )
        
        # normalized width and center coordinates of bounding box
        width_norm = abs(x_max - x_min) / width_picture
        height_norm = abs(y_max - y_min) / height_picture
        x_center_norm = ((x_max - x_min)/2 + x_min) / width_picture
        y_center_norm = ((y_max - y_min)/2 + y_min) / height_picture

        # building string to write to yolo annotation file for one buil-
        # ding box and appending it to the list of all bounding boxes
        # of one file
        bounding_boxes.append(" ".join([object_class, 
                                        str(rund(x_center_norm)),
                                        str(rund(y_center_norm)),
                                        str(rund(width_norm)), 
                                        str(rund(height_norm))]) + "\n")

    return bounding_boxes

def json_syntax_to_yolov8_all(input_dir: str, output_dir: str = "") -> None:
    """
Function Summary
=======

call the parsing function on all files contained in a given input direc-
tory, write the YOLOv8 formatted data to a .txt file in output directory
 
:param input_dir: path to directory containing supervisely annotations
:type input_dir: str
:param output_dir: (optional) path to output directory, where to store
    the yolov8 annotations. default behavior, creates a directory
    called 'yolov8_annoations' in the parent directory of input_dir 
:type output_dir: str
"""
    
    # if an output directory is not given, default behavior, come back
    # one directory in tree and make an output directory called
    # "yolov8_annotations"
    if output_dir == "":
        output_dir = os.path.join(os.path.dirname(input_dir),
                                  "yolov8_annotations")
    # overwriting output_dictionary if it already exists
    if os.path.exists(output_dir):  sh.rmtree(output_dir)
    os.makedirs(output_dir) 
    
    # loop through directory's content and calling 
    # parsing function on each file.
    for i, file in enumerate(os.scandir(input_dir)):
        # only if it is a .json file
        if (file.name.split(".")[-1] == "json"):
            bounding_boxes = json_syntax_to_yolov8_file(file) 
            
            # write yolov8 bounding boxes list to a new .txt file in 
            # the output directory
            with open(os.path.join(output_dir, file.name.split(".")[0]+".txt"),
                      "w", 
                      encoding="utf-8") as f:
                [f.write(bounding_box) for bounding_box in bounding_boxes]


if __name__ == "__main__":
    try:
        input_dir = r"path_to_directory_containing_supervisely_annotations"
        # output_dir = r"path_to_desired_output_directory" # optional
        json_syntax_to_yolov8_all(input_dir)
    except:
        pass
    

    
    