import os
import string
import random
from mindkosh import Client

N = 4

random_projectname = ''.join(random.choices(
    string.ascii_uppercase + string.digits, k=N))
client = Client()

new_project = client.project.create(
    "test_project_" + random_projectname,
    "This is an example description"
)

project_list = client.project.get()  # return list of project objects

# Get project IDS
keys = [project.id for project in project_list]
print(keys)

# Get project tasks
example_project = client.project.get(project_id=new_project.project_id)
print(example_project.tasks)


# Update name of the project
example_project.update_name("New name - " + example_project.name)
