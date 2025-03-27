import os
import string
import random
from mindkosh import Client, Label

client = Client('token')

N = 4
random_taskname = ''.join(random.choices(
    string.ascii_uppercase + string.digits, k=N))

name="test_task_" + random_taskname
dataset_id = 1


label1 = Label(
    name = 'label1',
    color = '#fffccc',
    extra = {'width':100,'height':100,'length':100},
    attributes = [
        {
            'name' : 'a1',
            'input_type' : 'checkbox',
            'default_value' : True,
            'mutable' : False,
            'values' : ['true']
        }

    ]
    )

label2 = Label(
    name = 'label2',
    color = '#ffcc00',
    extra = {'width':100,'height':100,'length':100},
    attributes = [
        {
            'name' : 'a2',
            'input_type' : 'radio',
            'default_value' : 'any',
            'mutable' : True,
            'values' : ['true']
        }

    ]
    )


#create task
client.task.create(
        name = name,
        labels = [label1,label2],
        dataset_id = dataset_id,
        batches=2
    )


task_list = client.task.get()  # return list of task objects

# Get task IDS
keys = [task.task_id for task in task_list]
print(keys)

# Get a task
example_task = client.task.get(task_id=keys[0])
print(example_task.name)

# Update name of the task
example_task.update_name("New name - " + example_task.name)

