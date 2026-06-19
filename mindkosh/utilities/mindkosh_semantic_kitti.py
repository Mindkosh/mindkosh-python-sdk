"""
    Converts Point cloud segmentation annotations exported from mindkosh to the
    Semantic KITTI format.
    Usage: mindkosh-semantic-kitti <ROOT_ANNOTATION_DIR> <PCD_DIR> <OUTPUT_LABEL_DIR> [CLASS_MAP_JSON]
"""

import os
import json
import sys
import numpy as np

from mindkosh.utilities.common import get_annotations_from_segmentation_export_root
from pointcloudkit import PointCloud

DEFAULT_CLASS = 0  # Unlabeled object


def main():
    # ------------ PATHS -------------
    ROOT_ANN_DIR = sys.argv[1]
    PCD_DIR = sys.argv[2]
    OUTPUT_LABEL_DIR = sys.argv[3]

    # CLASS_MAP can be passed as the 4th argv (path to a json file). If not passed,
    # fall back to the bundled semantic_kitti_sample_map.json in this utilities folder.
    if len(sys.argv) > 4 and sys.argv[4]:
        class_map_path = sys.argv[4]
    else:
        class_map_path = os.path.join(os.path.dirname(__file__), "semantic_kitti_sample_map.json")

    if os.path.exists(class_map_path):
        with open(class_map_path, 'r') as _f:
            CLASS_MAP = json.load(_f)
    else:
        CLASS_MAP = {}

    annotations = get_annotations_from_segmentation_export_root(ROOT_ANN_DIR)
    total_frames = len(annotations.keys())
    total_processed = 0
    for frame_name in annotations.keys():

        pcd_path = os.path.join(PCD_DIR, frame_name)

        num_points = len(PointCloud.read(pcd_path))
        labels = np.zeros(num_points, dtype=np.uint32)

        frame_annotations = annotations[frame_name]
        for annotation in frame_annotations:
            semantic_id = DEFAULT_CLASS
            if annotation.label in CLASS_MAP:
                semantic_id = CLASS_MAP.get(annotation.label, DEFAULT_CLASS)
            else:
                print("Annotation label " + annotation.label + " not found in semantic map file")
            indices = annotation.points

            labels[indices] = semantic_id

        out_path = os.path.join(OUTPUT_LABEL_DIR, frame_name.replace(".pcd", ".label"))
        labels.astype(np.uint32).tofile(out_path)
        total_processed += 1
        print(f"Converted {frame_name} - {total_processed}/{total_frames}")


if __name__ == "__main__":
    main()