import os
import string
import random
from mindkosh import Task
  
N = 4

task_object = Task( )

random_taskname = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
new_task = task_object.create(
                    "test_task_" + random_taskname,
                    [ {"name":"label1","color":"#fff000"},{"name":"label2","color":"#fffccc"} ],
                    [ os.path.join("examples", "example_images") ],
                    segment_size=2
                )

task_list = task_object.get()

# Get task IDS 
keys = list(task_list.keys())
print( keys )

# Get a task
example_task = task_list[keys[0]]
print( example_task.name )

# Update name of the task
example_task.update_name( "New name - " + example_task.name )

print("\n Downloading annotations")
example_task.download_annotations( fileformat="coco", filename="example_task_annotations_coco.zip" )
