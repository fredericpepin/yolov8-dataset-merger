from pycocotools.coco import COCO
import requests
import os

# Adapted from https://stackoverflow.com/a/62770484/8061030
def background_images(detector_classes:list[str], number_of_images:int,
                      output_dir:str = (os.path.join(
                      os.path.dirname(__file__),
                      "background_images")),
                      instance_train_json_file = (os.path.join(
                      os.path.dirname(__file__),
                      "instances_train2017.json"))
                      ) -> None:
    """
Function Summary
================

Downloads background images from the COCO dataset, excluding those 
that contain specified classes. The function saves the images and 
blank label files in a specified directory. These background images 
are intended for use in object detection models where they are used 
as negative samples (images without objects of interest, or backgroun 
images).

:param detector_classes: A list of classes to exclude from the 
    background images. These are typically 
    classes included in training, but in 
    special cases, like in tomato detection 
    where no class is excluded, the list 
    can be empty.
:type detector_classes: list[str]
:param number_of_images: The number of background images to download. 
    It is recommended to use between 0% and 10% 
    background images relative to your dataset.
:type number_of_images: int
:param output_dir: The directory where the background images and 
    corresponding blank label files will be saved. 
    The default directory is "./background_images".
:type output_dir: str, optional
:param instance_train_json_file : json file provided by coco on their 
    website ( https://cocodataset.org/#download ) containing annotations
    of dataset. Path to this file. default value, place it in the 
    script's directory
:type output_dir: str, not really optional, must be changed if file is
changed
:return: None
:rtype: NoneType

Notes
=====
- The background images are saved to the `output_dir`, along with 
    corresponding blank `.txt` label files for each image.
- The function uses the COCO API to retrieve image metadata and 
    downloads the images via their URLs.
Example
=======
background_images(["cat", "dog"], 100)
This would download 100 images excluding those with "cat" and 
"dog", and save them in the "./background_images" directory.
"""

    # instantiate COCO specifying the annotations json path
    coco = COCO(instance_train_json_file)

    # Get list of images to exclude based on DETECTOR_CLASSES
    # Background images will not contain these.
    # These should be classes included in training.
    exclude_categorie_ids = coco.getCatIds(catNms=detector_classes)

    # Get the corresponding image ids to exclude
    exclude_img_ids = []
    for cat_id in exclude_categorie_ids:
        exclude_img_ids += coco.getImgIds(catIds=cat_id)

    # Remove duplicates
    exclude_img_ids = set(exclude_img_ids)

    # Get all image ids
    all_img_ids = coco.getImgIds()

    # Remove img ids of classes that are included in training
    background_img_ids = set(all_img_ids) - set(exclude_img_ids)

    # Get background image metadata
    background_images = coco.loadImgs(background_img_ids)

    # Create dirs
    os.makedirs(os.path.join(output_dir,"images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir,"labels"), exist_ok=True)
    print("Directories created")
    # Save the images into a local folder

    i = 0
    for image in background_images[:number_of_images]:
        img_data = requests.get(image["coco_url"]).content
        
        # Save the image
        with open(os.path.join(output_dir, "images", 
                               image["file_name"]), "wb") as handler:
            handler.write(img_data)

        # Save the corresponding blank label txt file
        with open(os.path.join(output_dir, "labels", 
                            image["file_name"][:-3] + "txt"), "wb") as handler:
            pass
        i+=1
        print(i)
    print("process done")
if __name__ == "__main__":
    background_images([],1000)