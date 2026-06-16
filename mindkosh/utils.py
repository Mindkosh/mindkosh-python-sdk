# Copyright (C) 2024 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat

import re
from enum import Enum


class AnnotationFormats:

    POINTCLOUD = {"mindkosh_3d" : "Mindkosh-3D"}
    BASIC_2D = {
            "coco": "COCO 1.0",
            "datumaro": "Datumaro 1.0",
            "voc": "PASCAL VOC 1.1",
            "segmentation_mask": "Segmentation mask 1.1",
            "yolo": "YOLO 1.1",
            "mindkosh": "Mindkosh 1.1"
        }
    IMAGE = dict(BASIC_2D , **{"cvat" : "CVAT for images 1.1"})
    VIDEO = dict(BASIC_2D , **{"cvat" : "CVAT for video 1.1"})

    @classmethod
    def validate(cls,anno_format,category,upload=False):
        available = getattr(cls,category.upper())
        if category!='pointcloud' and upload:
            available['cvat'] = 'CVAT 1.1'
        try:
            return available[anno_format.lower()]
        except KeyError:
            raise Exception(f"Annotation format should be one of '{list(available.keys())}")


def verify_name(name,prop):
    if name and isinstance(name,str):
        name = re.sub(r'\s+', ' ', name.strip())
        if name and re.match(r'^[a-zA-Z0-9_ +!\-_*\'().]+$', name):
            return name
    raise Exception(f"Invalid {prop} name : '{name}'")


class TaskProperty():
    TOOLS = [
        {'name': 'polygon', 'is_active': True},
        {'name': 'bounding-box', 'is_active': True},
        {'name': 'polyline', 'is_active': True},
        {'name': 'keypoint', 'is_active': True},
        {'name': 'cuboid', 'is_active': True}
    ]

    class JOB_MODES(Enum):
        VALIDATION = 'validation'
        QC = 'qc'


class TaskType():
    LOCAL = "local"
    S3 = "s3"

    def __repr__(self):
        return str(self)
    
