
import os
from mindkosh import Client, ImageFile

client = Client()

#Uploading list of images or/and directories without extra data
def upload_data(dataset_id):
    client.upload_data(
        dataset_id = dataset_id,
        resources = ['/example_images/'],
        tags = ['penguine']
    )
#upload_data(dataset_id=5)


#Uploading images with extra data
def upload_imagefiles(dataset_id):
    dir = '/home/user/Desktop/images/'
    imagefiles = [ImageFile(
        filepath=os.path.join(dir, file),
        tags=['tag1'],
        extra={'supported_file_url':'url'}
        ) for file in os.listdir(dir) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

    client.upload_imagefiles(
        dataset_id = dataset_id,
        imagefiles = imagefiles
    )
#upload_imagefiles(dataset_id=5)
