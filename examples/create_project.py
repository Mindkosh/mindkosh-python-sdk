import os
import string
import random
from mindkosh import Project
  
N = 4

random_projectname = ''.join( random.choices(string.ascii_uppercase + string.digits, k = N) )
project_object = Project()

new_project = project_object.create(
                    "test_project_" + random_projectname,
                    "This is an example description"
                )

project_list = project_object.get()

# Get project IDS 
keys = list(project_list.keys())
print( keys )

# Get a task
example_project = project_list[keys[0]]
print( example_project.name )

# Update name of the task
example_project.update_name( "New name - " + example_project.name )
