# Copyright (C) 2022 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat
    
class MINDKOSH_API_V1():
    """ Build parameterized API URLs """

    def __init__(self, host, https=False):
        if host.startswith('https://'):
            https = True
        if host.startswith('http://') or host.startswith('https://'):
            host = host.replace('http://', '')
            host = host.replace('https://', '')
        scheme = 'https' if https else 'http'
        self.base = '{}://{}/api/v1/'.format(scheme, host)

#   Project API calls
#   -----------------
    @property
    def projects(self):
        return self.base + 'projects'

    def projects_id(self, project_id):
        return f"{self.projects}/{project_id}"

    def projects_page(self,page_id):
        return f"{self.projects}?page={page_id}"

#   User API calls
#   --------------
    @property
    def users_self(self):
        return self.base + 'users/self'

#   Task API calls
#   -------------- 
    @property
    def tasks(self):
        return f"{self.base}tasks"

    def tasks_page(self, page_id):
        return f"{self.tasks}?page={page_id}"

    def tasks_id(self, task_id):
        return f"{self.tasks}/{task_id}"

    def tasks_id_data(self, task_id):
        return f"{self.tasks_id(task_id)}/data"

    def tasks_id_frame_id(self, task_id, frame_id, quality):
        return f"{self.tasks_id(task_id)}/data?type=frame&number={frame_id}&quality={quality}"

    def tasks_id_status(self, task_id):
        return f"{self.tasks_id(task_id)}/status"

    def tasks_id_annotations_format(self, task_id, fileformat):
        return f"{self.tasks_id(task_id)}/annotations?format={fileformat}"

    def tasks_id_annotations_filename(self, task_id, name, fileformat):
        return f"{self.tasks_id(task_id)}/annotations?format={fileformat}&filename={name}"
        


        