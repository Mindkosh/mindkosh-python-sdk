from mindkosh import Client, Label

client = Client(token='')

task_id = 1
task = client.task.get(task_id)

new_label = Label(
    name = 'new label',
    color = '#fffccc',
    type = 'instance_mask',
    sequence = 1, # sequence values should be unique for all the labels of a task.
    attributes = [
        {
            'name' : 'property1',
            'input_type' : 'checkbox',
            'default_value' : True,
            'mutable' : False,
            'sequence' : 1,
            'values' : ['true']
        },

        {
            'name' : 'property2',
            'input_type' : 'radio',
            'default_value' : 'some value',
            'mutable' : True,
            'sequence' : 2,
            'values' : ['some value']
        },

    ]
)

# adds or updates labels
updated_task = task.add_label(new_label)
