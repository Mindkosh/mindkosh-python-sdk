import zipfile
import os
import json


def is_valid_zip(file):
    """returns zip reference"""
    if os.path.getsize(file) > 500 * 10**6:
        raise Exception("annotation file is too large")
    try:
        zip_ref =  zipfile.ZipFile(file)
        zip_ref.testzip()  
    except zipfile.BadZipFile:
        raise Exception("Invalid zip file")
    return zip_ref

def read_by_lines(zip_ref, filename):
    with zip_ref.open(filename) as file:
        for line in file:
            yield line.decode('utf-8').strip()

def get_labels(zip_ref, filename):
    labels = []
    for label in read_by_lines(zip_ref, filename):
        labels.append(label)
    return labels

def get_images_size_mapping(zip_ref, filename):
    mapping = {}
    for line in read_by_lines(zip_ref, filename):
        try:
            img,size = line.split(' ')
        except ValueError:
            raise Exception("Each image should have its size (width,height)")
        
        img = os.path.split(img)[-1]
        mapping[img] = eval(size)

    return mapping

def get_bbox(points):
    xpoints = []
    ypoints = []
    for i in range(len(points)):
        if i%2:
            ypoints.append(points[i])
        else:
            xpoints.append(points[i])

    min_x, max_x = min(xpoints), max(xpoints)
    min_y, max_y = min(ypoints), max(ypoints)
    width = round(max_x - min_x, 2)
    height = round(max_y - min_y, 2)
    return [min_x, min_y, width, height]

def convert_yolo_to_coco(yolo_dataset_path) -> None:
    """
    param yolo_dataset_path: path to yolo datasets
    """

    zip_ref = is_valid_zip(yolo_dataset_path)
    labels = get_labels(zip_ref, 'obj.names')
    images_size_mapping = get_images_size_mapping(zip_ref, 'train.txt')
    
    annotation_file_names = [
        f for f in zip_ref.namelist()
        if f.startswith("obj_train_data/") and f.endswith(".txt")
    ]

    coco_images = []
    coco_annotations = []
    image_idx = 1
    anno_idx = 1

    for image_name, size in images_size_mapping.items():
        coco_image = {
            "id": image_idx,
            "width": size[0],
            "height": size[1],
            "file_name": image_name
        }
        
        coco_images.append(coco_image)

        annotation_file = os.path.join('obj_train_data', os.path.splitext(image_name)[0] + '.txt')
        for annotation in read_by_lines(zip_ref, annotation_file):
            points = [float(x) for x in annotation.split()]

            if len(points)%2==0:
                points = points[:-1]

            coco_seg = [points[i]*size[0] if i%2==1 else points[i]*size[1] for i in range(1,len(points))]
            coco_anno = {
                "id": anno_idx,
                "image_id": image_idx,
                "category_id": int(points[0]),
                "segmentation": [coco_seg],
                "area": 0,
                "bbox": get_bbox(points[1:]),
                "iscrowd": 0,
                "attributes": {"occluded": False}
            }
            anno_idx += 1

            coco_annotations.append(coco_anno)
        image_idx += 1
            
    
    instances_default = {
        "licenses": [
        {
            "name": "",
            "id": 0,
            "url": ""
        }
        ],
        "info": {
            "contributor": "",
            "date_created": "",
            "description": "",
            "url": "",
            "version": "",
            "year": ""
        }
    }

    coco_categories = []
    for idx, label in enumerate(labels):
        coco_lable = {
            "id": idx,
            "name": label,
            "supercategory": ""
        }
        coco_categories.append(coco_lable)

    instances_default["images"] = coco_images
    instances_default["categories"] = coco_categories
    instances_default["annotations"] = coco_annotations
    
    _save_annotations(yolo_dataset_path, instances_default)

def _save_annotations(dir, data):
    if not os.path.isdir(dir):
        dir = os.path.dirname(dir)
    if not os.path.exists(dir):
        raise Exception(f"Directory {dir} does not exist")
    
    coco_dir = os.path.join(dir, 'coco_annotations')
    os.makedirs(coco_dir)
    
    coco_anno_file = os.path.join(coco_dir, 'instances_default.json')
    with open(coco_anno_file, 'w') as f:
        json.dump(data, f, indent=4)