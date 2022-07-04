# Copyright (C) 2022 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat

import re
import os
import sys
import glob
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .core import MINDKOSH_API_V1
from .utils import ResourceType

class Task:

    def __init__(self, token='', verbose_output=True, server_host='app.mindkosh.com', server_port='80', https=True):
        
        #Check for token in evironment variables, if not set it to blank string
        self.token = token
        if 'MK_TOKEN' in os.environ:
            self.token = os.environ.get('MK_TOKEN')

        if self.token=="":
            raise Exception( "No Access token specified." )

        #If env variable MK_TOKEN doesn't exist, token must be specified maunally per object
        self.auth_header = { "Authorization": "Token " + self.token}

        self.verbose_output = verbose_output

        self.available_formats = {
                                "coco": "COCO 1.0",
                                "datumaro": "Datumaro 1.0",
                                "pascal": "PASCAL VOC 1.1",
                                "segmentation_mask":"Segmentation mask 1.1",
                                "yolo":"YOLO 1.1"
                            }
        self.server_host = server_host
        self.server_port = server_port
        self.https = https

        api = MINDKOSH_API_V1('%s:%s' % (self.server_host, self.server_port), self.https)
        self.api = api
        session = requests.Session()
        self.session = session


    def delete(self, task_id):

        try:
            url = self.api.tasks_id(task_id)
            response = self.session.delete(url, headers=self.auth_header)
            response.raise_for_status()
            if self.verbose_output == True :
                print(f"Task id {task_id} deleted")
        except requests.exceptions.HTTPError as e:  
            print(e)


    def update_name(self,task_id,name):

        if not name or set(name)=={' '}:
            print("Enter a valid task name")
            return

        try:
            url = self.api.tasks_id(task_id)
            response = self.session.patch(url, json={"name":name}, headers=self.auth_header)
            response.raise_for_status()
            if self.verbose_output == True :
                print(f"Task id {task_id} updated. New name : {name}")
        except requests.exceptions.HTTPError as e:
            print(e)


    def update_project_id(self,task_id,new_project_id):

        project_id = new_project_id
        #if new project id is None then we will remove the project from the task, else we need a valid project id
        if project_id:
            p_url = self.api.projects_id(project_id)
            p_response = self.session.get(p_url, headers=self.auth_header)

            if p_response.status_code==404:
                print(f"project id {project_id} not found")
                return 

        try:
            url = self.api.tasks_id(task_id)
            response = self.session.patch(url, json={'project_id':project_id}, headers=self.auth_header)
            response.raise_for_status()
            if self.verbose_output == True :
                print(f"Task id {task_id} updated. New project_id : {project_id}")
        except requests.exceptions.HTTPError as e:
            print(e)


    def download_annotations(self, task_id, fileformat, filename, location, **kwargs):

        if location:
            if os.path.isdir(location)==False:
                print(f"'{location}' is not a valid directory")
                return
            if location[-1]=="/":
                filename = location + filename
            else:    
                filename = location + "/" + filename

        
        if fileformat not in self.available_formats.keys():
            print(f"Fileformat should be one of '{self.available_formats.keys()}'")
            return
        
        try:
            url = self.api.tasks_id(task_id)
            response = self.session.get(url, headers=self.auth_header)
            response.raise_for_status()
            response_json = response.json()

            url = self.api.tasks_id_annotations_filename(task_id, response_json['name'], self.available_formats[fileformat])

            while True:
                response = self.session.get(url, headers=self.auth_header)
                response.raise_for_status()
                if self.verbose_output == True :
                    print( "Processing export..", end="\r" )
                if response.status_code == 201:
                    break
                else:
                    time.sleep(2)
                    

            response = self.session.get(url + '&action=download', headers=self.auth_header)
            response.raise_for_status()
            with open(filename, 'wb') as fp:
                fp.write(response.content)
                print(f"Downloaded : {filename}")


        except requests.exceptions.HTTPError as e:
            print(e)


    
    def create(self,name,labels,resources,project_id=None,segment_size=0,recursive=False,category="imageset",resource_type="local",**kwargs):

        if not name or set(name)=={' '}:
            print("Enter a valid task name")
            return

        if verify_labels(labels)==False:
            return

        if resource_type=="local":
            files = verify_resources(resources,recursive,category)
            if files==False:
                return
            if files==[]:
                print("No data to be uploaded")
                return
        else:
            return
                
        tools = [{'name': 'polygon', 'is_active': True}, {'name': 'bounding-box', 'is_active': True}, \
                {'name': 'polyline', 'is_active': True}, {'name': 'keypoint', 'is_active': True}, \
                 {'name': 'cuboid', 'is_active': True}]

        
        try:
            url = self.api.tasks
            data = {'name': name,
                    'labels': labels,
                    'segment_size': segment_size,
                    'project_id': project_id,
                    'tools' : tools,                   
            }
            response = self.session.post(url, json=data, headers=self.auth_header)
            response.raise_for_status()
            response_json = response.json()
            task_id = response_json['id']
            if self.verbose_output == True :
                print(f"Task created. id : {task_id}, name : {name}")
            
            if category=="imageset":
                print(f"{len(files)} images to be uploaded")

            self.upload_local_data( task_id,files)
            
            if self.verbose_output == True :
                print( 'Saving task to the database' )

            url = self.api.tasks_id_status(task_id)
            response = self.session.get(url, headers=self.auth_header)
            response_json = response.json()

            if response_json['state']!="Started":
                print(response_json['message'])
                self.delete(task_id)
                return
            while response_json['state'] != 'Finished':
                msg = response_json['message']
                if response_json["state"]=="Failed":
                    print(msg)
                    self.delete(task_id)
                    return
                msg = list(msg.split(" "))
                if msg[0]=="Processing":
                    print(f"{msg[3]}  Data Saved",end="\r")
                    time.sleep(1.5)

                response = self.session.get(url, headers=self.auth_header)
                response_json = response.json()

            if self.verbose_output == True :
                print("100% ")
                print("Data Uploaded")

            if self.verbose_output == True :
                while response_json['state'] != 'Finished':
                    response = self.session.get(url, headers=self.auth_header)
                    response_json = response.json()
                    logger_string = f"Awaiting compression for task {task_id}. Status : {response_json['state']}, Message : {response_json['message']}"
                    if self.verbose_output == True :
                        print(logger_string)

        except requests.exceptions.HTTPError as e:
            print(e)
    

    def upload_local_data(self, task_id,files):

        try:
            url = self.api.tasks_id_data(task_id)
            fields = {
                    'client_files[{}]'.format(i):( os.path.basename(f), open(f, 'rb')) for i, f in enumerate(files)
                    }
                    
            fields['image_quality'] = "70"
            enc = MultipartEncoder(fields=fields)
            headers = self.auth_header
            headers["Content-Type"] = enc.content_type
            response = self.session.post(url,data=enc,headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
 
    
    def get(self):
        try:
            url = self.api.tasks
            response = self.session.get(url, headers=self.auth_header)
            response.raise_for_status()
            page = 1
            v=[]
            while True:
                response_json = response.json()
                
                for r in response_json['results']:
                    d_tmp = {}
                    d_tmp["id"]=r["id"]
                    d_tmp["name"] = r["name"]
                    d_tmp["project_id"] = r["project_id"]
                    d_tmp["project_name"] = r["project_name"] if "project_name" in r else None
                    d_tmp["status"] = r["status"]
                    d_tmp["owner"] = r["owner"]["name"]
                    d_tmp["assignee"] = r["assignee"]["name"] if r["assignee"] else None
                    d_tmp["mode"] = r["mode"]
                    d_tmp["labels"] = r["labels"]
                    d_tmp["size"] = r["size"] if "size" in r else None
                    d_tmp["segment_size"] = r["segment_size"]
                    d_tmp["category"] = r["category"] if "category" in r else None
                    d_tmp["tools"] = [i['name'] for i in r['tools'] if i['is_active']]
                                       
                    v.append(d_tmp)
        
                if not response_json['next']:
                    break
                page += 1
                url = self.api.tasks_page(page)
                response = self.session.get(url, headers=self.auth_header)
                response.raise_for_status()


        except requests.exceptions.HTTPError as e:
            print(e)

        self.new_lst = {}
        for i in v:
            new_task = IndividualTask( self.token, self.verbose_output, self.server_host, self.server_port, self.https )
            new_task.populate( i["id"], i["name"], i["labels"],i["mode"],i["tools"],i["status"],i["project_id"],i["project_name"],i["owner"],i["assignee"],i["segment_size"],i["size"],i["category"] )
            all_p = new_task
            s = {i["id"]:all_p}
            self.new_lst.update(s)

        return self.new_lst
    

class IndividualTask:
    
    def __init__( self, token, verbose_output, server_host, server_port, https ):
        self.parent_task_instance = Task( token, verbose_output, server_host, server_port, https )

    def populate( self, id, name, labels, mode, tools, status, project_id, project_name, owner, assignee, segment_size, size, category):
        self.id = id
        self.name = name
        self.size = size
        self.segment_size = segment_size
        self.project_id = project_id
        self.project_name = project_name
        self.mode = mode
        self.status = status
        self.tools = tools
        self.labels = labels
        self.category = category
        self.owner = owner
        self.assignee = assignee

    def __str__(self):
        return str(self.__dict__)

    def delete(self):
        self.parent_task_instance.delete( self.id )

    def update_name(self,name):
        self.parent_task_instance.update_name( self.id,name )

    def update_project( self, new_project_id ):
        self.parent_task_instance.update_project_id( self.id, new_project_id )

    def download_annotations( self, fileformat="COCO 1.0", filename=None, location=None ):
        if not filename:
            filename = str(self.id) + "_" + fileformat + ".zip"
        self.parent_task_instance.download_annotations( self.id, fileformat, filename, location )



def verify_resources(resources,recursive,category):

    files = []
    if not (category=="imageset" or category=="video"):
        print("category can be either imageset or video")
        return False

    if category=="video":
        if type(resources)==list:
            if len(resources)!=1:
                print("Please upload a single video file")
            else:
                resource = resources[0]
        elif type(resources)==str:
            resource = resources
        else:
            print("Please upload a single valid video file")
            return False

        if not os.path.exists(resource):
            print(f"'{resource}' does not exist")
            return False
        else:
            if not resource.endswith(".mp4"):
                print(f"'{resource}' is not an mp4 file")
                return False
            else:
                return [resource]

    for resource in resources:
        if recursive==True:
            if os.path.isdir(resource):
                files += [y for x in os.walk(resource) for y in glob.glob(os.path.join(x[0], '*.jp*g'))]
                files += [y for x in os.walk(resource) for y in glob.glob(os.path.join(x[0], '*.png'))]

            else:
                temp = glob.glob(resource)
                if temp==[]:
                    print(f"Could not find '{resource}'")
                    return False
                files+=temp
        else:
            if os.path.isdir(resource):
                files+=[ os.path.join( resource, i ) for i in os.listdir(resource) if i.endswith(('.jpg', '.png', 'jpeg')) ]

            else:
                temp = glob.glob(resource)
                if temp==[]:
                    print(f"Could not find {resource}")
                    return False
                files+=temp
    return files


def verify_labels(labels):

    if not (type(labels)==list or type(labels)==tuple):
        print("labels should be either a list or a tuple")
        return False

    names = []
    for label in labels: 

        if len(label)<2:
            print(f"label '{label}' required at least a name and color")
            return False

        if len(label)==2 and (("name" not in label) or ("color" not in label)):
                print(f"label '{label}' got unexpected parameters")
                return False

        if len(label)==3:
            if ("name" not in label) or ("color" not in label) or ("attributes" not in label):
                print(f"label '{label}' got unexpected parameters")
                return False
            #check attributes
            attributes = label["attributes"]
            if type(attributes)!=list:
                print(f"attributes format is not correct for label {label}")
                return False

        if len(label)>3:
            print(f"label format '{label}' is not correct")
            return False
        
        #Check name    
        name = label["name"]
        if name==None or set(name)=={" "}:
            print(f"Please enter a valid name for label '{label}'")
            return False
        if name in names:
            print("label name '{name}' is not unique")
            return False
        
        #check color
        color = label["color"]        
        if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            print(f"color '{color}' is not valid for label '{label}'")
            return False
       
        
        names.append(name)

    return True
