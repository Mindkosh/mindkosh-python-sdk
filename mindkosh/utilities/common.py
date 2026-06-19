import os
import json
import numpy as np
from typing import Dict, List

class PointCloudSegmentationAnnotation:
    def __init__(self, frame_filename, label, bin_path):
        self.frame_filename = frame_filename
        self.label = label
        self.id = id
        self.label = label
        self.bin_path = bin_path
    
    @property
    def points(self):
        return self.load_indices(self.bin_path)

    def load_indices(self, bin_path):
        """
        Mindkosh stores point indices as float32 *bytes*
        that must be reinterpreted as int32.
        """
        raw = np.fromfile(bin_path, dtype=np.float32)

        # reinterpret float32 bytes as int32 indices
        indices = raw.view(np.int32)

        return indices.astype(np.int64)


def get_annotations_from_segmentation_export_root(root_annotation_dir: str) -> Dict[str, List[PointCloudSegmentationAnnotation]]:
    object_json_dir = os.path.join(root_annotation_dir, "segmentations", "objects")
    binary_dir = os.path.join(root_annotation_dir, "segmentations", "binaryData")
    frames_list = os.path.join(root_annotation_dir, "frames_list.text")

    with open(frames_list) as f:
        frames = [line.strip().split() for line in f]

    frame_wise_annotations = {}
    for frame_id, pcd_file in frames:
        annotations = []
        frame_id = int(frame_id)

        # load frame objects json
        json_path = os.path.join(object_json_dir, f"{frame_id}.json")
        if os.path.exists(json_path) is False:
            continue
        with open(json_path) as f:
            objects = json.load(f)["annotations"]

        # assign labels per object
        for obj in objects:
            obj_id = obj["id"]
            obj_type = obj["objectType"]
            bin_path = os.path.join(binary_dir, f"object_id_{obj_id}.bin")
            new_annotation = PointCloudSegmentationAnnotation(
                frame_filename = pcd_file,
                label = obj_type,
                bin_path = bin_path
            )
            annotations.append(new_annotation)
        frame_wise_annotations[pcd_file] = annotations
    return frame_wise_annotations
