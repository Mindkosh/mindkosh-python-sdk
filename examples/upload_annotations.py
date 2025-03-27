from mindkosh import Client

sdk_token = "<enter sdk token here>"
client = Client(token=sdk_token)

# List tasks
tasks = client.task.get()
print(tasks)
# [task1, task2]

# Get a particular task's object
task = tasks[1]
print(task.name)
# task2

annotation_format = 'coco'
annotation_file = './example_coco.zip'

# Specify annotation format and path of the file. Please give it some time before you start checking for the annotation on the web platform.
# Optionally you can also specify a webhook_url. The specified URL will be called when the annotations are processed.
task.upload_annotations(
    annotation_format=annotation_format,
    local_path=annotation_file
)