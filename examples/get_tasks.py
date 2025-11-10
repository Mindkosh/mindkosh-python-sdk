from mindkosh import Client

client = Client('token')

# fetch list of task objects
task_list = client.task.get()  

for task in task_list:
    # perform task operation here
    # example: task.add_label(new_label)
    print(task.task_id, task.name)

# Get a single task
task_id = 100
example_task = client.task.get(task_id=task_id)
print(example_task.name)
