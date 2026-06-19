"""
    Copy image files from source_dir (up to max_depth levels deep) to output_dir,
    prepending filenames with their subdirectory names.
    Usage: mindkosh-copy-files <INPUT_DIR> <OUTPUT_DIR> [MAX_DEPTH=2]
"""

import os
import shutil
from pathlib import Path
import sys

def copy_images_with_prefix(source_dir, output_dir, max_depth=2):
    os.makedirs(output_dir, exist_ok=True)
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    
    for root, dirs, files in os.walk(source_dir):
        # Calculate current depth
        depth = root.replace(source_dir, '').count(os.sep)
        if depth > max_depth:
            continue
        
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                source_path = os.path.join(root, file)
                
                # Get relative path without the source_dir
                rel_path = os.path.relpath(root, source_dir)
                
                # Create new filename with directory prefix
                if rel_path == '.':
                    new_filename = file
                else:
                    prefix = rel_path.replace(os.sep, '_')
                    new_filename = f"{prefix}_{file}"
                
                output_path = os.path.join(output_dir, new_filename)
                shutil.copy2(source_path, output_path)
                print(f"Copied: {source_path} -> {output_path}")

def main():
    source_directory = sys.argv[1]
    output_directory = sys.argv[2]
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    copy_images_with_prefix(source_directory, output_directory, max_depth)


if __name__ == "__main__":
    main()