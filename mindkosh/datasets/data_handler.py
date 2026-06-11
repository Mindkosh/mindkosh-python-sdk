# Copyright (C) 2023 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat

import os
import time
import json
import asyncio
import httpx
import aiohttp
import threading
import requests
import logging
from PIL import Image
from typing import Union

from mindkosh.datasets.utils import convert_image_to_bytes
from mindkosh.datasets.helpers import DatasetFile

logger = logging.getLogger(__name__)


class DataSetUploader:
    def __init__(
        self,
        dataset_id: int,
        batch_key: str,
        file_upload_url: str,
        stream_url: str,
        heartbeat_url: str,
        headers: dict,
        data_type: str = 'image',
        sequence_starter: int = 1
    ):

        self.dataset_id = dataset_id
        self.batch_key = batch_key
        self.file_upload_url = file_upload_url
        self.stream_url = stream_url
        self.headers = headers
        self.heartbeat_url = heartbeat_url
        self._data_type = data_type
        self._sequence = sequence_starter
        self.stop_heartbeat = threading.Event()

    def _skip_file(self,
        message: dict
    ):
        """
        Returns prefixed filename and updates files count if the file is already uploaded.
        Throws error for other errors
        """
        try:
            prefixed_filename = message['filename'][-1]
        except KeyError:
            raise Exception(message)
        self._skipped += 1
        self._sequence += 1

        return prefixed_filename

    def _upload_single_file(
        self,
        session: requests.Session,
        datasetfile: Union[str, DatasetFile],
        tags: list,
        convert_tiff_to: str = '.png',
        extra: dict = {},
        **kwargs
    ):

        filepath = datasetfile
        if (type(datasetfile).__name__ == "DatasetFile"):
            filepath = datasetfile.filepath

        base_name = os.path.basename(filepath)
        file_name, extension = os.path.splitext(base_name)

        if extension == '.tiff':
            tiff_im = Image.open(filepath)
            im = tiff_im.convert("RGB")
            byte_im, file_size = convert_image_to_bytes(
                filepath, im, convert_tiff_to)
            base_name = file_name + convert_tiff_to
        else:
            byte_im = open(filepath, 'rb').read()
            file_size = os.path.getsize(filepath)

        data = {
            "dataset_id": self.dataset_id,
            "file_name": base_name,
            "file_size": file_size,
            "meta_data": {
                "batch_key": self.batch_key,
                "sequence": self._sequence
            }
        }

        if (type(datasetfile).__name__ == "DatasetFile"):
            if (datasetfile.tags):
                data['meta_data']['tags'] = datasetfile.tags
            if (datasetfile.extra):
                data['meta_data']['extra'] = datasetfile.extra
            if (datasetfile.related_files):
                data['meta_data']['related_files'] = datasetfile.related_files
        else:
            if tags:
                data['meta_data']['tags'] = tags
            if extra:
                data['meta_data']['extra'] = extra

        resp = session.post(url=self.file_upload_url,
                             json=data, headers=self.headers)
        if resp.status_code == requests.codes.bad_request:
            return self._skip_file(resp.json())

        resp.raise_for_status()
        resp_json = resp.json()
        self._sequence += 1

        presigned_url = resp_json['url']
        fields = resp_json['fields']
        payload = fields

        res = session.post(
            presigned_url,
            headers={},
            data=payload,
            files={'file': byte_im}
        )
        res.raise_for_status()

    def _upload_single_imagefile(
        self,
        session: requests.Session,
        imagefile,
        **kwargs
    ):
        """
        Used in:
            - Uploading images with extra and tags for image datasets.
            - Uploading related files of a pcd file.
        """

        filepath = imagefile.filepath
        base_name = os.path.basename(filepath)
        byte_im = open(filepath, 'rb').read()

        data = {
            "dataset_id": self.dataset_id,
            "file_name": base_name,
            "file_size": imagefile._size,
            "meta_data": {
                "batch_key": self.batch_key,
                "sequence": getattr(imagefile, 'sequence', None) or self._sequence
            }
        }

        if imagefile.tags:
            data['meta_data']['tags'] = imagefile.tags
        if imagefile.extra:
            data['meta_data']['extra'] = imagefile.extra

        resp = session.post(url=self.file_upload_url,
                             json=data, headers=self.headers)
        if resp.status_code == requests.codes.bad_request:
            #check and skip uploading if the file is already uploaded
            prefixed_filename = self._skip_file(resp.json())
            imagefile.prefixed_filename = prefixed_filename
            return
        
        resp.raise_for_status()
        resp_json = resp.json()
        self._sequence += 1

        presigned_url = resp_json['url']
        fields = resp_json['fields']
        imagefile.prefixed_filename = fields['key'].split('/')[-1]
        payload = fields

        res = session.post(
            presigned_url,
            headers={},
            data=payload,
            files={'file': byte_im}
        )
        res.raise_for_status()

    def _upload_single_base_file(self, session: requests.Session, basefile, **kwargs):
        base_name = os.path.basename(basefile.filepath)
        data = {
            "dataset_id": self.dataset_id,
            "file_name": base_name,
            "file_size": basefile._size,
            "meta_data": {
                "batch_key": self.batch_key,
                "sequence": self._sequence
            }
        }

        if basefile.tags:
            data['meta_data']['tags'] = basefile.tags

        related_files = []
        for related_file in basefile.related_files:
            if related_file.prefixed_filename:
                related_files.append(related_file.prefixed_filename)
        if related_files:
            data['meta_data']['related_files'] = related_files

        resp = session.post(url=self.file_upload_url,
                             json=data, headers=self.headers)
        if resp.status_code == requests.codes.bad_request:
            return self._skip_file(resp.json())

        resp.raise_for_status()
        resp_json = resp.json()
        self._sequence += 1

        presigned_url = resp_json['url']
        fields = resp_json['fields']
        payload = fields

        res = session.post(
            presigned_url,
            headers={},
            data=payload,
            files={'file': open(basefile.filepath, 'rb').read()}
        )
        res.raise_for_status()

    def _upload_raw_files(self, session, files_to_upload, uploader, tags, extra, *args, **kwargs):
        _uploaded = 1
        for datasetfile in files_to_upload:
            uploader(session, datasetfile, tags, extra)
            print(f'Files uploading... {_uploaded}', end='\r')
            _uploaded += 1

    def _upload_fileobjects(self, session, fileobjects, uploader, *args, **kwargs):
        _uploaded = 1
        for fileobject in fileobjects:
            uploader(session, fileobject)
            print(f'Files uploading... {_uploaded}', end='\r')
            _uploaded += 1

    def _check_final_status(self, session: requests.Session):
        for _ in range(20):
            response = session.get(self.stream_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            if response.json()['status'].lower() == "completed":
                return
            print('processing  . . . . . . . . . ', end='\r') 

            time.sleep(3)

    def _send_heartbeat(self, session: requests.Session):
        while not self.stop_heartbeat.is_set():
            response = session.post(
                self.heartbeat_url,
                json={
                    "batch_key": self.batch_key,
                    "final": False
                },
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()

            self.stop_heartbeat.wait(timeout=5)
        
        response = session.post(
            self.heartbeat_url,
            json={
                "batch_key": self.batch_key,
                "final": True
            },
            headers=self.headers
        )
        response.raise_for_status()

    def files_upload_thread(self, raw_filepaths=None, imagefiles=None, basefiles=None, tags=[], extra={}, *args, **kwargs):
        if raw_filepaths:
            bulk_uploader = self._upload_raw_files
            uploader = self._upload_single_file
            files_to_upload = raw_filepaths
        else:
            bulk_uploader = self._upload_fileobjects
            if imagefiles:
                uploader = self._upload_single_imagefile
                files_to_upload = imagefiles
            elif basefiles:
                uploader = self._upload_single_base_file
                files_to_upload = basefiles
            else:
                raise Exception('No data to upload')

        num_of_files = len(files_to_upload)
        self._finished, self._skipped = 0, 0
        try:

            with requests.Session() as session:
                # heartbeat_thread = threading.Thread(
                #     target=self._send_heartbeat, 
                #     args=(session,),
                #     daemon=True
                # )
                # heartbeat_thread.start()
                # time.sleep(.5)
                bulk_uploader(session, files_to_upload, uploader, tags, extra)

                # self.stop_heartbeat.set()
                # heartbeat_thread.join()

                self._check_final_status(session)

        except Exception as e:
            raise e

        print(f"Files skipped: {self._skipped}. Files uploaded: {num_of_files - self._skipped}")
        return self._finished


class DataSetUploaderAsync:
    def __init__(
        self,
        dataset_id,
        batch_key,
        file_upload_url,
        stream_url,
        heartbeat_url,
        headers,
        data_type
    ):
        self.dataset_id = dataset_id
        self.batch_key = batch_key
        self.file_upload_url = file_upload_url
        self.stream_url = stream_url
        self.headers = headers
        self.heartbeat_url = heartbeat_url
        self._sequence = 1
        self._skipped = 0

    def _skip_file(self,
        message: dict
    ):
        """
        Returns prefixed filename and updates files count if the file is already uploaded.
        Throws error for other errors
        """
        try:
            prefixed_filename = message['filename'][-1]
        except KeyError:
            raise Exception(message)
        self._skipped += 1
        self._sequence += 1

        return prefixed_filename

    async def _upload_single_file(
        self,
        client: httpx.AsyncClient,
        filepath: str,
        semaphore: asyncio.Semaphore,
        tags: list = [],
        convert_tiff_to: str = '.png',
        extra: dict = {},
        **kwargs
    ):
        async with semaphore:
            base_name = os.path.basename(filepath)
            file_name, extension = os.path.splitext(base_name)

            if extension == '.tiff':
                tiff_im = Image.open(filepath)
                im = tiff_im.convert("RGB")
                byte_im, file_size = convert_image_to_bytes(
                    filepath, im, convert_tiff_to)
                base_name = file_name + convert_tiff_to
            else:
                byte_im = open(filepath, 'rb').read()
                file_size = os.path.getsize(filepath)

            data = {
                "dataset_id": self.dataset_id,
                "file_name": base_name,
                "file_size": file_size,
                "meta_data": {
                    "batch_key": self.batch_key,
                    "sequence": self._sequence
                }
            }

            if tags:
                data['meta_data']['tags'] = tags
            if extra:
                data['meta_data']['extra'] = extra

            resp = await client.post(self.file_upload_url, json=data, headers=self.headers)
            if resp.status_code == httpx.codes.bad_request:
                return self._skip_file(resp.json())
            resp.raise_for_status()
            resp_json = resp.json()
            self._sequence += 1

            upload_response = await client.post(
                resp_json['url'], 
                data=resp_json['fields'], 
                files={'file': byte_im}
            )
            upload_response.raise_for_status()
            self._uploaded += 1
            print(f'Files uploading... {self._uploaded}', end='\r')

    async def _upload_single_imagefile(
        self,
        client: httpx.AsyncClient,
        imagefile: object,
        semaphore: asyncio.Semaphore,
        **kwargs
    ):
        async with semaphore:
            filepath = imagefile.filepath
            base_name = os.path.basename(filepath)
            byte_im = open(filepath, 'rb').read()

            data = {
                "dataset_id": self.dataset_id,
                "file_name": base_name,
                "file_size": imagefile._size,
                "meta_data": {
                    "batch_key": self.batch_key,
                    "sequence": getattr(imagefile, 'sequence', None) or self._sequence
                }
            }

            if imagefile.tags:
                data['meta_data']['tags'] = imagefile.tags
            if imagefile.extra:
                data['meta_data']['extra'] = imagefile.extra

            resp = await client.post(self.file_upload_url, json=data, headers=self.headers)
            if resp.status_code == httpx.codes.bad_request:
                #check and skip uploading if the file is already uploaded
                prefixed_filename = self._skip_file(resp.json())
                imagefile.prefixed_filename = prefixed_filename
                return
            resp.raise_for_status()
            resp_json = resp.json()
            self._sequence += 1

            fields = resp_json['fields']
            imagefile.prefixed_filename = fields['key'].split('/')[-1]
            upload_response = await client.post(
                resp_json['url'], 
                data = fields, 
                files = {'file': byte_im}
            )
            upload_response.raise_for_status()
            self._uploaded += 1
            print(f'Files uploading... {self._uploaded}', end='\r')

    async def _upload_single_base_file(
        self,
        client: httpx.AsyncClient,
        basefile: object,
        semaphore: asyncio.Semaphore,
        **kwargsself
    ):
        async with semaphore:
            base_name = os.path.basename(basefile.filepath)
            data = {
                "dataset_id": self.dataset_id,
                "file_name": base_name,
                "file_size": basefile._size,
                "meta_data": {
                    "batch_key": self.batch_key,
                    "sequence": self._sequence
                }
            }

            if basefile.tags:
                data['meta_data']['tags'] = basefile.tags

            related_files = []
            for related_file in basefile.related_files:
                if related_file.prefixed_filename:
                    related_files.append(related_file.prefixed_filename)
            if related_files:
                data['meta_data']['related_files'] = related_files

            resp = await client.post(
                url=self.file_upload_url,
                json=data,
                headers=self.headers
            )
            if resp.status_code == httpx.codes.bad_request:
                return self._skip_file(resp.json())

            resp.raise_for_status()
            resp_json = resp.json()
            self._sequence += 1

            presigned_url = resp_json['url']
            fields = resp_json['fields']
            payload = fields

            res = await client.post(
                presigned_url,
                headers={},
                data=payload,
                files={'file': open(basefile.filepath, 'rb').read()}
            )
            res.raise_for_status()

    async def _upload_raw_files(self, client: httpx.AsyncClient, uploader, file_paths: list, tags: list = [], extra: dict = {}, *args, **kwargs):
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_UPLOADS)
        tasks = [uploader(client, path, semaphore) for path in file_paths]
        await asyncio.gather(*tasks)

    async def _upload_fileobjects(self, client: httpx.AsyncClient, uploader, imagefiles: list, *args, **kwargs):
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_UPLOADS)
        tasks = [uploader(client, imagefile, semaphore) for imagefile in imagefiles]
        await asyncio.gather(*tasks)

    async def send_heartbeat(self, client: httpx.AsyncClient, stop_event: asyncio.Event):        
        while not stop_event.is_set():
            try:
                response = await client.post(
                    self.heartbeat_url,
                    json={
                        "batch_key": self.batch_key,
                        "final": False
                    },
                    headers=self.headers
                )
                response.raise_for_status()
            except Exception as e:
                raise e
                
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=5)
            except asyncio.TimeoutError:
                pass
        
        try:
            resp = await client.post(
                self.heartbeat_url,
                json={
                    "batch_key": self.batch_key,
                    "final": True
                },
                headers=self.headers
            )
            resp.raise_for_status()
        except Exception as e:
            raise e

    async def _check_upload_status(self, client: httpx.AsyncClient):        
        max_attempts = 20
        attempt = 1 
        while attempt < max_attempts:
            try:
                response = await client.get(self.stream_url, headers=self.headers)
                response.raise_for_status()         
                if response.json()['status'].lower() == "completed":
                    return
                print('processing     ........ ', end='\r')       
            except Exception as e:
                raise e
            
            await asyncio.sleep(5)
            attempt += 1

    async def files_upload_thread(
        self,
        raw_filepaths: list = [],
        imagefiles: list = [],
        basefiles: list = [],
        tags: list = [],
        extra: dict = {}         
    ):
        if raw_filepaths:
            bulk_uploader = self._upload_raw_files
            uploader = self._upload_single_file
            files_to_upload = raw_filepaths
        else:
            bulk_uploader = self._upload_fileobjects
            if imagefiles:
                uploader = self._upload_single_imagefile
                files_to_upload = imagefiles
            elif basefiles:
                uploader = self._upload_single_base_file
                files_to_upload = basefiles
            else:
                raise Exception('No data to upload')
        
        self._uploaded = 0
        self.MAX_CONCURRENT_UPLOADS = 20
        #stop_heartbeat = asyncio.Event()
        limits = httpx.Limits(max_keepalive_connections=self.MAX_CONCURRENT_UPLOADS, max_connections=self.MAX_CONCURRENT_UPLOADS)
        
        async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
            # heartbeat_task = asyncio.create_task(
            #     self.send_heartbeat(
            #         client,
            #         stop_heartbeat
            #     )
            # )

            await bulk_uploader(client, uploader, files_to_upload, tags, extra)
            
            #stop_heartbeat.set()
            #await heartbeat_task
            
            await self._check_upload_status(client)
            print('Files uploaded: ', self._uploaded, ', Files skipped: ', self._skipped)

