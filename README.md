# Mindkosh Python SDK

The Mindkosh Python SDK offers a simple, user-friendly way to interact with the Mindkosh data annotation platform.

Easily manage large Data labeling projects and the teams that work on them. All while using a feature-rich Annotation tool.
Learn more about the [Mindkosh data annotaiton platform](#https://mindkosh.com/annotation-platform)

[Read documentation](#https://docs.mindkosh.com/getting-started/welcome)

## Table of contents:
* [Setup](#setup)
  * [Requirements](#requirements)
  * [Installation](#installation)
* [Getting started](#getting-started)
* [Managing projects.](#projects)
  * [Create a new project.](#create-project)
  * [Get all projects.](#getall-projects)
  * [Update project name](#update-name)
  * [Update project description](#update-description)
  * [Delete a project.](#delete-project)
* [Managing tasks.](#tasks)
  * [Create a new task](#create-task) 
  * [Get all tasks](#getall-tasks)
  * [Update task name](#update-name)
  * [Update project id](#update-project_id)
  * [Download annotations](#download-annotations)
  * [Delete task](#delete-task)


## Setup

### Requirements

* Python >= 3.7
* Account on the Mindkosh platform (Create on now)
* SDK Token (contact us for getting one)


### Installation

* Install the package
```sh
python setup.py install
```


## Getting started

```py
from mindkosh import Task, Project
task_obj = Task(token)
project_obj = Project(token)
```

To get started, create a Task/Project object using the token provided to you. You can also set the token
in an environment variable(MK_TOKEN) instead of passing as a parameter to the object constructor.


## Managing projects

### Create project
```py
project_obj.create(name, description=None) 
```
To create a project, enter a name and an optional description.



### Get all projects

```py
myprojects = project_obj.get()

for i in myprojects:  
    print(myprojects[i].id, myprojects[i].name)

for i in myprojects:  
    print(myprojects[i])
```


### Update project details

```py
p1.update_name("new name")
p1.update_description("New description")
```

### Delete project
```py
p1.delete()
```

## Managing Tasks

### Create task
Create a new task :
```py
task_obj.create( name, labels, resources, segment_size=0,category="imageset")
```

Parameters:
* labels - A list of labels for the annotation task. eg: 
```py
labels = [{"name":"label1","color":"#fff000"},{"name":"label2","color":"#fffccc"}]
```
* segment_size - Number of images in each job. Only valid for resource_type="imageset"
* resources - A list of images or directories containing images. You can also use wildcards to select certain types of files.
* project_id - Optional - ID of the project this task should belong to.
* category - "imageset" for images or "video" for video.


### Get all tasks

```py
mytasks = task_obj.get()

for i in mytasks:  
    print(mytasks[i].id, mytasks[i].name)

for i in mytasks:  
    print(mytasks[i])
```


### Update task details

```py
t1 = mytasks[1] # task_id : 1
t1.update_name("New name")
t1.update_project_id(new_valid_project_id)  
```

### Download annotations

```py
t1.download_annotations(fileformat="coco", filename="id_fileformat.zip", location=None)
```

location should be the directory where you want to download annotations, filename should be the name of your annotations file (default location and filename is your current directory and "id_fileformat.zip"). fileformat can be any of the following:

* Available formats and their parameter names:
* COCO - "coco"
* Datumaro - "datumaro
* Pascal VOC - "pascal_voc
* Segmentation mask - "segmentation_mask"
* YOLO - "yolo"


### Delete task
Delete a task - 
```py
t1.delete()
```
