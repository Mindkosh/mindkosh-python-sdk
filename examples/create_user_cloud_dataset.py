from mindkosh import Client

client = Client('token')

# create user cloud dataset for s3
dataset = client.create_dataset_from_cloud_data(
    name = 'sample user cloud dataset',
    data_type = 'pointcloud',
    resource = 'dataset-sample-3',
    directory = 'sample-files/',
    location = 'ap-south-1',
    cloud_service_type='aws'
)

# create user cloud dataset for gcp
dataset = client.create_dataset_from_cloud_data(
    name = 'test-gcp-dataset',
    data_type='pointcloud',
    directory='',
    resource='test-bucket-1',
    location='asia-south-2',
    cloud_service_type='gcp'
)

# scan files
# if manifest_file_path is None, it will try to scan all the files present at `dataset['directory']`
client.scan_user_cloud(
    dataset_id=dataset['id'],
    manifest_file_path= '/home/user/Desktop/sample_manifest_file.json'
)