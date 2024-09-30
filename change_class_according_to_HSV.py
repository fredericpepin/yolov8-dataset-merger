"""
.. module:: change_class_according_to_HSV
    :platform: Unix, Windows
    :synopsis: modify labels classes IDs by determining ripeness of 
                tomato with its color.
    .. function: get_pixel_coordinates(x_normalized: float,
                            y_normalized: float, 
                            image_width: float, 
                            image_height: float) -> tuple[float]
    .. function: is_ripe_tomato(hsv_region: np.ndarray) -> bool
    .. function:: check_tomato_ripeness(image: np.ndarray, 
                                        x_normalized: float, 
                                        y_normalized: float, 
                                        box_width_norm: float, 
                                        box_height_norm: float, 
                                        ratio_center_box: int = 4) 
                                        -> bool
    .. function:: change_class_based_on_color_all(input_dir: str, 
                                                    output_dir: str, 
                                                    ripe: int = 2, 
                                                    unripe: int = 4, 
                                                    ratio_center_box: int = 4) 
                                                    -> None
    .. function:: draw_bounding_boxes(image: np.ndarray, 
                                    bounding_boxes: list[list[str]], 
                                    ratio_center_box: int = 4) 
                                    -> np.ndarray
Module Summary
==============

Module meant to change fruit class based on the color of the detected 
fruit.

Motivation: some datasets only identify tomatoes as such, without dif-
ferentiating between ripe and unripe fruits. This is true for a spe-
cial case, the TomatoOcclusion dataset, which addresses the problematic
of occlusion of fruits by branches, leaves and other fruits, or a mix 
of all the latters. 

In order to be compatible with other quality datasets (like TomatoLaboro)
the need arises to characterize the ripeness of Tomatoes. 


Based on the bounding box geometry and position, detect the presence of
color spectrum (red) in a square box around center point of a bounding 
box (red is ripe). An enhanced approach would be to sample more regions
in the bounding box, as it could be that a branch / leaf is present at 
middle point. But this also leads to the problem of a false detection
of red of a ripe tomato behind an unripe one. Detection of partially
hidden unripe tomatoes will also lead to problems if a red tomato 
overlaps the center of the former. Thus, the detection of occluded 
unripe tomato should be in my opinion left out. It is also less critical
then the detection of ripe tomatoes in the bigger picture.
Another stance could also be, falsely characterizing a unripe tomato 
is not critical, because unripe tomatoes continue to ripe also after
harvest anyway. Therefore, the marginal phenomenon of characterizing 
an occluded unripe tomato as ripe because a red tomato overlaps 
ther region of interest at mid point doesn't have big repercussions and
is likely to rarely happen in a given dataset.
    """


import os
import shutil as sh

import cv2
import numpy as np

import common_functions as udf

# Convert normalized coordinates to pixel values
def get_pixel_coordinates(x_normalized: float, y_normalized: float, 
                          image_width: float, 
                          image_height: float) -> tuple[float]:
    """
Function Summary
================

compute absolute geometry in pixel sizes out of normalized yolov8 
coordinates

:param x_normalized: 
:type x_normalized: float
:param y_normalized: 
:type y_normalized: float
:param image_width: absolute image width
:type image_width: float
:param image_height: absolute image height
:type image_height: float
:return: tuple of (x_pixel, y_pixel), absolute x and y values in the
    coordinate system of the image
:rtype: tuple[float]
    """
    x_pixel = int(x_normalized * image_width)
    y_pixel = int(y_normalized * image_height)
    return x_pixel, y_pixel

# Define a function to check if a given color is red (ripe tomato) with 
# wider ranges
def is_ripe_tomato(hsv_region: np.ndarray) -> bool:
    """ 
Function Summary
================

Determines if a given Region of Interest (hsv_region) contains any red 
pixels, indicating ripeness. In this case, hsv_region is a space 
containing the hsv values of each pixel in a given geometrical region.

Each pixel in the HSV region is checked to see if its HSV values fall
into either of these ranges. If a pixel's values fall into one of these
ranges, the corresponding mask will have a 1 (white) at that pixel's 
location. If not, the mask will have a 0 (black).

:param hsv_region: image is first transformed to a color space with 
    cv2.cvtColor method, and a subspace is created for the Region of 
    Interest at center point, which is hsv_region. here, has 3 axes
:type hsv_region: np.array 
:return: ripe (True) or unripe (False)
:rtype: bool
    """
    # Convert the region to a NumPy array
    hsv_region = np.array(hsv_region, dtype=np.uint8)

    # Define the red color range in HSV
    #lower red  [hue, saturation, value]
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])

    #upper red [hue, saturation, value]
    lower_red2 = np.array([170,50,50])
    upper_red2 = np.array([180,255,255])

    
    # Check if the pixels in region falls within the red ranges for hue
    # saturation and value
    mask1 = cv2.inRange(hsv_region, lower_red, upper_red)
    mask2 = cv2.inRange(hsv_region, lower_red2, upper_red2)
    
    # If either mask has significant values, it's ripe
    if cv2.countNonZero(mask1) > 0 or cv2.countNonZero(mask2) > 0:
        return True
    return False

def check_tomato_ripeness(image, x_normalized, y_normalized, 
                          box_width_norm, box_height_norm,
                          ratio_center_box: int = 4) -> bool:
    """
Functíon Summary
================

Determines if a tomato within a bounding box in the image is ripe 
by evaluating the color within the bounding box in the HSV 
color space. The image is sampled around the center of the bounding 
box, and the HSV values of the region are analyzed to check for the 
presence of red, indicating ripeness.

The function takes normalized coordinates for the center of the 
bounding box and normalized box dimensions, converts them to pixel 
coordinates, and samples a region around the center. The region is 
converted to the HSV color space, and the ripeness is checked by 
determining if any pixels fall within the red color range.

:param image: Input image in BGR color space
:type image: np.ndarray
:param x_normalized: Normalized x-coordinate 
    for the center of the bounding box.
:type x_normalized: float
:param y_normalized: Normalized y-coordinate 
    for the center of the bounding box.
:type y_normalized: float
:param box_width_norm: Normalized width of the 
    bounding box, as a proportion of the image 
    width.
:type box_width_norm: float
:param box_height_norm: Normalized height of the 
    bounding box, as a proportion of the image 
    height.
:type box_height_norm: float
:param ratio_center_box: Ratio that determines the size of the 
    sample region in relation to the box 
    dimensions. The default value is 4, 
    meaning the sample region will be 1/4th 
    the size of the box.
:type ratio_center_box: int, optional
:return: A boolean indicating whether the tomato in the region is 
            ripe (True) or unripe (False).
:rtype: bool
"""
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Convert normalized coordinates to pixel indices for center and box dimensions
    x_center_pixel, y_center_pixel = get_pixel_coordinates(x_normalized,
                                                           y_normalized,
                                                           width, 
                                                           height)
    box_width_pixel = int(box_width_norm * width)
    box_height_pixel = int(box_height_norm * height)
    box_edge_pixel = (box_width_pixel 
                      if box_width_pixel >= box_height_pixel
                      else box_height_pixel)
    
    # Define the region around the center of the bounding box to sample from
    x_start = max(x_center_pixel - box_edge_pixel // ratio_center_box, 0)
    y_start = max(y_center_pixel - box_edge_pixel // ratio_center_box, 0)
    x_end = min(x_center_pixel + box_edge_pixel // ratio_center_box, width)
    y_end = min(y_center_pixel + box_edge_pixel // ratio_center_box, height)

    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Get the HSV values in the bounding box region
    hsv_region = hsv_image[y_start:y_end, x_start:x_end]
    
    # Check if the region is ripe
    return is_ripe_tomato(hsv_region)

def change_class_based_on_color_all(input_dir, output_dir="",
                                    ripe=2, 
                                    unripe=4,
                                    ratio_center_box: int = 4) -> None:
    """
Function Summary
================

This function processes images of subdirectories "train, test, valid"
in a given dataset directory to classify bounding boxes of tomatoes 
based on their ripeness by analyzing the color in a Region of Interest 
(ROI) around each bounding box's center point. 
It updates the class IDs in the label files based on the ripeness 
of each detected tomato.

The function reads all images and their corresponding label files 
in the specified directory, checks the ripeness of the tomatoes 
inside the bounding boxes using HSV color values, and updates 
the class ID in the label files accordingly. Additionally, it 
generates copies of the images with bounding boxes drawn on them 
for visual verification.

:param input_dir: Path to the input directory containing folders 
    of images and labels.
:type input_dir: str
:param output_dir: Path to the output directory where the modified 
    label files and image copies will be saved.
    if value is left out, default behavior creates
    another directory in the parent dataset folder
    called "image_copies_with_bounding_boxes" 
:type output_dir: str
:param ripe: The class ID numberto assign to ripe tomatoes. Default is 
    irrelevant, must be changed to fit a given structure in main .yaml 
    file 
:type ripe: int, optional
:param unripe: The class ID to assign to unripe tomatoes. 
    Default is irrelevant, must be changed to fit a given structure 
    in main .yaml file 
:type unripe: int, optional
:param ratio_center_box: Ratio that defines the size of the 
    sampling region for checking ripeness, 
    relative to the bounding box size. 
    Default is 4.
:type ratio_center_box: int, optional
:return: None
:rtype: NoneType
"""
    
    # if an output directory is not given, default behavior, creates
    # a directory in original dataset directory called
    # "image_copies_with_bounding_boxes"
    if output_dir == "":
        output_dir = os.path.join(input_dir,
                                  "image_copies_with_bounding_boxes")
    if os.path.exists(output_dir): sh.rmtree(output_dir)
    os.mkdir(output_dir, mode = 0o777)

    for folder in udf.find_images_labels_folders(input_dir):
        images_folder = os.path.join(folder.path, "images")
        labels_folder = os.path.join(folder.path, "labels")
        for image in os.scandir(images_folder):
            # making sure, reading only files
            if not os.path.isdir(image):
                # Read image
                img = cv2.imread(image.path)
                # Read the corresponding label file
                label_file_path = os.path.join(labels_folder, 
                                               image.name.split(".")[0] 
                                               + ".txt")
                # building a list of lists, deepest list is a list of 
                # the bounding box's data
                with open(label_file_path, "r") as f:
                    bounding_boxes = [line.strip().split(" ") 
                                      for line in f.readlines()]
                # create a copy of the image with th main bounding box
                # and the region of interest around center point 
                image_copy = draw_bounding_boxes(cv2.imread(image.path),
                               bounding_boxes,
                               ratio_center_box = ratio_center_box)
                image_copy_name, image_copy_ext = os.path.splitext(image.name)
                image_copy_path = os.path.join(output_dir, 
                                               image_copy_name 
                                               + "-wbbox" 
                                               + image_copy_ext)
                # save image with bounding boxes drawn on it
                cv2.imwrite(image_copy_path, image_copy )
                
                # Process each bounding box and checking for ripeness
                for index in range(len(bounding_boxes)):
                    (class_id, 
                     x_center_norm, 
                     y_center_norm, 
                     box_width_norm, 
                     box_height_norm) = bounding_boxes[index]
                    
                    # Check if the tomato is ripe based on the bounding
                    # box region
                    if check_tomato_ripeness(img, 
                                             float(x_center_norm), 
                                             float(y_center_norm), 
                                             float(box_width_norm), 
                                             float(box_height_norm),
                                ratio_center_box=ratio_center_box):
                        bounding_boxes[index][0] = str(ripe)  
                    else:
                        bounding_boxes[index][0] = str(unripe)  
                    
                    # Rebuild the bounding box as a string
                    bounding_boxes[index] = (" ".join(bounding_boxes[index]) 
                                            + "\n")
                
                # Write the updated bounding boxes to the label file
                with open(label_file_path, "w", encoding="utf-8") as f:
                    print(bounding_boxes)
                    [f.write(bounding_box) for bounding_box in bounding_boxes]       
            else:
                continue
def draw_bounding_boxes(image: np.ndarray, bounding_boxes:list[list[str]], 
                        ratio_center_box: int = 4) -> np.ndarray:
    """
Function Summary
================

Draws bounding boxes around objects (tomatoes) in an image based on 
the provided bounding box coordinates, which are in a normalized 
format. In addition to the main bounding box, the function draws a 
smaller square box around the center of each object, sized proportionally 
to the original bounding box (longest edge). This smaller box is used 
for further analysis, such as checking for color or ripeness.

green rectangles for the main bounding boxes and blue rectangles for 
the smaller boxes around the center points.

:param image: The input image on which the bounding boxes will be 
    drawn. This image is typically in BGR color space.
:type image: np.ndarray
:param bounding_boxes: A list of bounding boxes, where each bounding 
    box is a list containing the class ID, 
    normalized x and y center coordinates, 
    and normalized width and height of the box.
:type bounding_boxes: list of lists of strings
:param ratio_center_box: The ratio that defines the size of the 
    smaller box relative to the main bounding 
    box. The default value is 4, meaning the 
    smaller box will be 1/4th the size of the 
    original bounding box.
:type ratio_center_box: int, optional
:return: A copy of the input image with the bounding boxes drawn on it.
:rtype: np.ndarray

Notes
=====
- The normalized coordinates for the bounding boxes are converted 
    to pixel coordinates based on the dimensions of the input image.
- The smaller box around the center point is square, and its size 
    is determined by the larger of the two dimensions (width or height) 
    of the main bounding box.
"""

    height, width = image.shape[:2]
    image_copy = image.copy()

    for box in bounding_boxes:
        (class_id,
         x_center_norm,
         y_center_norm,
         box_width_norm,
         box_height_norm) = box

        # Convert normalized coordinates to pixel coordinates
        x_center_pixel, y_center_pixel = get_pixel_coordinates(
                                                float(x_center_norm), 
                                                float(y_center_norm), 
                                                width, 
                                                height)
        box_width_pixel = int(float(box_width_norm) * width)
        box_height_pixel = int(float(box_height_norm) * height)

        # Main bounding box coordinates
        x_start = max(x_center_pixel - box_width_pixel // 2, 0)
        y_start = max(y_center_pixel - box_height_pixel // 2, 0)
        x_end = min(x_center_pixel + box_width_pixel // 2, width)
        y_end = min(y_center_pixel + box_height_pixel // 2, height)

        # Smaller box around centerpoint
        small_box_width = box_width_pixel // ratio_center_box
        small_box_height = box_height_pixel // ratio_center_box
        # largest edge of box to build a square box around the middle
        small_box_edge = (small_box_width 
                                if small_box_width >= small_box_height 
                                else small_box_height)
        small_x_start = max(x_center_pixel - small_box_edge // 2, 0)
        small_y_start = max(y_center_pixel - small_box_edge // 2, 0)
        small_x_end = min(x_center_pixel + small_box_edge //2, width)
        small_y_end = min(y_center_pixel + small_box_edge // 2, height)

        # Draw the main bounding box
        cv2.rectangle(image_copy,            
                      (x_start, y_start), 
                      (x_end, y_end), 
                      (0, 255, 0), # Green color for main box
                      2)  
        # Draw the smaller box
        cv2.rectangle(image_copy, 
                      (small_x_start, small_y_start), 
                      (small_x_end, small_y_end), 
                      (255, 0, 0), # Blue color for small box
                      1)  
    return image_copy


if __name__ == "__main__":
    input_dir = r"path_to_your_dataset"
   # output_dir = r"" #optional
    change_class_based_on_color_all(input_dir)