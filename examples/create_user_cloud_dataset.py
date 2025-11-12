from mindkosh import Client

client = Client('token')

# create dataset
dataset = client.create_dataset_from_cloud_data(
    name = 'sample user cloud dataset',
    data_type = 'pointcloud',
    resource = 'dataset-sample-3',
    directory = '228c712b-154e-41f0-bc36-d3bd3da9f701/',
    location = 'ap-south-1'
)

# scan files
# if manifest_file_path is None, it will try to scan all the files present at `dataset['directory']`
client.scan_user_cloud(
    dataset_id=dataset['id'],
    manifest_file_path= '/home/user/Desktop/sample_manifest_file.json'
)