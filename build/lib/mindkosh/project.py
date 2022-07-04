# Copyright (C) 2022 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat

import requests
from .core import MINDKOSH_API_V1
import os

class Project:

    def __init__( self, token='', verbose_output=True, server_host='app.mindkosh.com', server_port='80', https=True ):
        
        # Check for token in evironment variables, if not set it to blank string
        self.token = token
        if 'MK_TOKEN' in os.environ:
            self.token = os.environ.get('MK_TOKEN')

        if self.token=="":
            raise Exception( "No Access token specified." )

        #If env variable MK_TOKEN doesn't exist, token must be specified maunally per object
        self.auth_header = { "Authorization": "Token " + self.token}

        self.verbose_output = verbose_output

        self.server_host = server_host
        self.server_port = server_port
        self.https = https

        api = MINDKOSH_API_V1('%s:%s' % (self.server_host, self.server_port), self.https)
        self.api = api
        session = requests.Session()
        self.session = session

    
    def create( self, name, description=None, **kwargs ):

        if not name or set(name)=={' '}:
            print("set a valid project name")
            return
        try:
            user_url = self.api.users_self
            user_response = self.session.get(user_url, headers=self.auth_header)
            user_response.raise_for_status()

            url = self.api.projects
            data = { 
                "name": name,
                "description" : description if description and set(description)!={' '} else None
            }
            response = self.session.post(url, json=data, headers=self.auth_header)
            response.raise_for_status()
            response_json = response.json()
            if self.verbose_output == True :
                print(f"New project created. id : {response_json['id']}, name : {response_json['name']}")
        
        except requests.exceptions.HTTPError as e:
            print(e)


    def update_name( self, id, name ):
        url = self.api.projects_id(id)

        if not name or set(name)=={' '}:
            print("Enter a valid project name")
            return

        try:
            response = self.session.patch(url, data={'name':name}, headers=self.auth_header)
            response.raise_for_status()
            response_json = response.json()
            if self.verbose_output == True :
                print(f"Name updated for project id {response_json['id']}. New name : {response_json['name']}")
        
        except requests.exceptions.HTTPError as e:
            print(e)


    def update_description( self, id, description ):
        url = self.api.projects_id(id)

        if not description or set(description)=={' '}:
            print("Enter a valid project description")
            return
        try:
            response = self.session.patch(url, data={'description':description}, headers=self.auth_header)
            response.raise_for_status()
            response_json = response.json()
            if self.verbose_output == True :
                print(f"Description updated for project id {response_json['id']}. New Description : {response_json['description']}")
        
        except requests.exceptions.HTTPError as e:
            print(e)


    def delete(self, id):

        url = self.api.projects_id(id)
        response = self.session.delete(url, headers=self.auth_header)
        try:
            response.raise_for_status()
            if self.verbose_output == True :
                print(f"Project id {id} deleted")
        except requests.exceptions.HTTPError as e:
            print(e) 


    def get(self):
        try:
            url = self.api.projects
            response = self.session.get(url, headers=self.auth_header)
            response.raise_for_status()
            page = 1
            v=[]
            while True:
                response_json = response.json()

                for r in response_json['results']:
                    d_tmp = {}
                    d_tmp["id"] = r["id"]
                    d_tmp["name"] = r["name"]
                    d_tmp["description"] = r["description"]
                    tasks = r["tasks"]
                    tasks = [{"id":i['id'],"name":i['name'],"mode":i['mode'],"status":i['status']} for i in tasks]
                    d_tmp["tasks"] = tasks
                    d_tmp["status"] = r["status"]
                    d_tmp["owner"] = r["owner"]["name"]
                    d_tmp["assignee"] = r["assignee"]["name"]
                    v.append(d_tmp)
        
                if not response_json['next']:
                    break
                    
                page += 1
                url = self.api.projects_page(page)
                response = self.session.get(url, headers=self.auth_header)
                response.raise_for_status()

        except requests.exceptions.HTTPError as e: 
            print(e)

        self.new_lst = {}
        for i in v: 
            new_project = IndividualProject( self.token, self.verbose_output, self.server_host, self.server_port, self.https )
            new_project.populate( i["id"], i["name"], i["tasks"], i["status"], i["description"], i["owner"], i["assignee"] )
            all_p = new_project
            s = {i["id"]:all_p}
            self.new_lst.update(s)

        return self.new_lst


class IndividualProject:
    def __init__( self, token, verbose_output, server_host, server_port, https ):
        self.parent_project_instance = Project( token, verbose_output, server_host, server_port, https )

    def populate( self, id, name, tasks, status, description, owner, assignee ):
        self.id = id
        self.name = name
        self.description = description
        self.tasks = tasks
        self.status = status
        self.owner = owner
        self.assignee = assignee

    def __str__(self):
        return str(self.__dict__)

    def delete(self):
        self.parent_project_instance.delete(self.id)

    def update_name(self,name):
        self.parent_project_instance.update_name(self.id,name)

    def update_description(self,description):
        self.parent_project_instance.update_description(self.id,description)
