import os
import re
import validators
from mindkosh.datasets.helpers import validate_custom_meta_data
from enum import Enum
from mindkosh.exceptions import DatasetFileError

__all__ = ["PointCloudFile", "ImageFile", "MainImage"]


class Dataset:

    DEFAULT_BUCKET_REGION = 'ap-south-1'

    class DataType(Enum):
        IMAGE = 'image'
        VIDEO = 'video'
        POINTCLOUD = 'pointcloud'
        AUDIO = 'audio'

        @classmethod
        def values(cls):
            return tuple((x.value, x.name) for x in cls)

    class StorageMethod(Enum):
        USER_CLOUD = 'user_cloud'
        VK_CLOUD = 'vk_cloud'


def validate_tags(tags):
    if not isinstance(tags, (list, tuple)) or len(tags) > 10:
        raise DatasetFileError(
            "tags: a list/tuple (max length 10) is required."
        )

    if not all(
        isinstance(tag, str) and re.compile(r"^[a-zA-Z0-9+\-=\._:/]+$").match(tag)
        for tag in tags
    ):
        raise DatasetFileError(
            "tags: tag shouldn't contain a whitespace or disallowed special chars"
        )

class BaseFile:
    def __init__(
        self,
        filepath: str,
        related_files: list = [],
        supported_file_url: str = '',
        custom_meta_data: dict = {},
        tags: list = []
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Invalid filepath: '{filepath}'")
        
        self.filepath = filepath
        self.related_files = related_files
        if supported_file_url and not validators.url(supported_file_url):
            raise DatasetFileError('Invalid supported_file_url')
        validate_custom_meta_data(custom_meta_data)
        self.extra = {}
        if supported_file_url:
            self.extra['supported_file_url'] = supported_file_url
        if custom_meta_data:
            self.extra['custom_meta_data'] = custom_meta_data
        validate_tags(tags)
        self.tags = tags
        self._size = os.path.getsize(filepath)
        
    def _validate_related_files(self, basefile_extension):
        if len(self.related_files) > 20:
            raise DatasetFileError('Max 20 related files allowed for a pointcloud file')
        device_ids = []
        for related_file in self.related_files:
            if type(related_file).__name__ != "ImageFile":
                raise DatasetFileError('invalid related file object')
            
            device_id = related_file._extra.get('device_id', None)
            if device_id is None or not isinstance(device_id, int) or device_id < 0:
                raise DatasetFileError('Related file requires a positive integer value as device_id')
            if device_id in device_ids:
                raise DatasetFileError(f'device_id must be unique for each relatedfiles of a BaseFile')     
            device_ids.append(device_id)

            related_file.validate_extra(basefile_extension)


class PointCloudFile(BaseFile):
    def __init__(self,
        filepath: str,
        related_files: list = [],
        supported_file_url: str = '',
        custom_meta_data: dict = {},
        tags: list = []
    ):
        super().__init__(filepath, related_files, supported_file_url, custom_meta_data, tags)
        extension = os.path.splitext(filepath)[1]
        if extension != '.pcd':
            raise DatasetFileError("Invalid pcd file")
        self._validate_related_files(extension)
            

class MainImage(BaseFile):
    def __init__(self,
        filepath: str,
        related_files: list = [],
        tags: list = []
    ):
        super().__init__(filepath, related_files, tags)
        extension = os.path.splitext(filepath)[1]
        if extension not in ('.jpg', '.png', '.jpeg'):
            raise DatasetFileError(f"'{extension}' files are not supported")
        self._validate_related_files(extension)


class ImageFile:
    def __init__(self, filepath: str, tags: list = [], extra: dict = {}):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Invalid filepath: '{filepath}'")
        extension = os.path.splitext(filepath)[1]
        if extension not in ('.jpg', '.png', '.jpeg'):
            raise DatasetFileError(f"'{extension}' files are not supported")
            
        self.filepath = filepath
        self._extra = extra
        self.extra = None
        validate_tags(tags)
        self.tags = tags
        self._size = os.path.getsize(filepath)

    def validate_extra(self, basefile_extension):
        allowed_extra = ['device_id', 'supported_file_url']
        if basefile_extension == '.pcd':
            allowed_extra.extend(['intrinsic', 'extrinsic', 'distortion', 'mirror', 'cameraModel'])
        
        _custom_meta_data = {}
        for k,v in self._extra.items():
            if k not in allowed_extra:
                _custom_meta_data[k] = v
        validate_custom_meta_data(_custom_meta_data)
        
        errors = []        
        supported_url = self._extra.get('supported_file_url', None)
        if supported_url and not validators.url(supported_url):
            errors.append('Invalid supported_file_url')

        if basefile_extension == '.pcd':
            if 'cameraModel' in self._extra and self._extra['cameraModel'] not in ('PINHOLE', 'FISHEYE'):
                errors.append('Invalid choice for cameraModel')
            if 'mirror' in self._extra and not isinstance(self._extra['mirror'], int):
                errors.append('Invalid mirror value')

            intrinsic = self._extra.get('intrinsic', None)
            if intrinsic and (len(intrinsic)!=4 or not all(isinstance(item, (int,float)) for item in intrinsic)):
                errors.append('Invalid intrinsic values')
            
            distortion = self._extra.get('distortion', None)
            if distortion and (len(distortion)>10 or not all(isinstance(item, (int,float)) for item in distortion)):
                errors.append('Invalid distortion values')

            extrinsic = self._extra.get('extrinsic', None)
            if extrinsic and (len(extrinsic)!=4 or not all(len(grid)==4 and all(isinstance(item, (int,float)) \
                                                             for item in grid) for grid in extrinsic)):
                errors.append('Invalid extrinsic values')

        if errors:
            raise DatasetFileError(str(errors))
        
        self.extra = self._extra
        delattr(self, '_extra')
