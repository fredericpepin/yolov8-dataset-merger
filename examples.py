"""
.. module:: examples (miscellaneous)
    .. function:: main(path_to_all_datasets_folder: str) -> None
    
Module Summary
==============

Module to show case some miscellaneous pieces of code. Functions are
nevertheless usable


    """
import os
import time
from resolve_filenames_conflicts import merge_datasets
import ultralytics.data.converter as u
from ultralytics import YOLO


def coco_to_yolo():
    """
Example transform COCO Dataset in YOLOv8
======================================

.. code-block::

    import ultralytics.data.converter as u
    u.convert_coco(r"TomatoLaboro\annotations",r".\output_labels",True)
    
    """
    u.convert_coco(r"TomatoLaboro\annotations",r".\test__",True)
    
def main(path_to_all_datasets_folder: str, ):
    """
Dataset Merger Code Example
===========================

.. code-block::

    import os
    import time
    from resolve_filenames_conflicts import merge_datasets
    tic = time.time()
    path_to_all_datasets_folder = r"path/to/folder/containing/all/datasets"
    # output in the script's directory
    output_path = os.path.dirname(__file__)
    merge_datasets(path_to_all_datasets_folder,output_path)
    toc = time.time()
    print(f"execution time: {toc-tic:0.4f} seconds")

:param path_to_all_datasets_folder: _description_
:type path_to_all_datasets_folder: str
    """
    tic = time.time()
    output_path = os.path.dirname(__file__)
    merge_datasets(path_to_all_datasets_folder,output_path)
    toc = time.time()
    print(f"execution time: {toc-tic:0.4f} seconds")


def train_model(dataset_path: str, model ):
    """
Train Model Example Code
========================

.. code-block::

    from ultralytics import YOLO
    # based on a pre-trained yolo omdel
    model = YOLO("yolov8n-seg.pt")
    results = model.train(data = r"path/to/dataset",epochs=100)

:param dataset_path: _description_
:type dataset_path: str
:param model: pre trained model, YOLO("yolov8n-seg.pt")
:type model: _type_, optional
    """
    # based on a pre-trained yolo omdel
    model = YOLO("yolov8n-seg.pt")
    results = model.train(data = dataset_path,epochs=100)
