from mindkosh import Label, Client, PointCloudFile, ImageFile
client = Client(token='a632cdfc1cb555b09b9b046c5c45879d7b9e5557', server_host='localhost', server_port=8080)

imagepath1 = '/home/sdevgupta/Downloads/deka_synced_samples/front/383_sweep079_1651867099.762835_front.jpg'
imagepath2 = '/home/sdevgupta/Downloads/deka_synced_samples/left/382_sweep079_1651867099.737841_left.jpg'
pcdfilepath1 = '/home/sdevgupta/Downloads/deka_synced_samples/lidar/096_sweep079_1651867099.699709_lidar.pcd'

pcdfile1 = PointCloudFile(
    filepath = pcdfilepath1,
    related_files = [ImageFile(
        filepath = imagepath1, tags=["front"], 
        extra = {"intrinsic": [255.620403, 449.983682, 250.028738, 255.437477],
        "extrinsic": [[-0.71796274, -0.69501734, -0.0384775, 0], [0.6954956, -0.71852916, 0.00130833, 0], [-0.02855652, -0.0258216, 0.9992586, 0], [0, 0, 0, 1] ]}
    ),
    ImageFile(
        filepath = imagepath2, tags=["left"]
    )]
)


imagepath3 = '/home/sdevgupta/Downloads/deka_synced_samples/front/387_sweep084_1651867100.262835_front.jpg'
imagepath4 = '/home/sdevgupta/Downloads/deka_synced_samples/left/386_sweep084_1651867100.237835_left.jpg'
pcdfilepath2 = '/home/sdevgupta/Downloads/deka_synced_samples/lidar/097_sweep084_1651867100.199041_lidar.pcd'

pcdfile2 = PointCloudFile(
    filepath = pcdfilepath2,
    related_files = [ImageFile(
        filepath = imagepath1, tags=["front"], extra={'device_id':3}
    ),
    ImageFile(
        filepath = imagepath2, tags=["left"]
    )]
)

client.upload_pointcloud_data(dataset_id=1, pointcloudfiles=[pcdfile1, pcdfile2])

client.task.create(name="sensor-fusion", labels=Label(name="label1", color="#ff00cc"), dataset_id=1)