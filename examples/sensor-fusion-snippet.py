from mindkosh import Label, Client, PointCloudFile, ImageFile

client = Client(token='')

front_cam1 = 'front_0000.jpg'
left_cam1 = 'left_0000.jpg'
pcdfilepath1 = 'lidar_0000.pcd'

pcdfile1 = PointCloudFile(
    filepath=pcdfilepath1,
    related_files=[
        ImageFile(
            filepath=front_cam1,
            tags=["front"],
            extra={
                # fx, fy, cx, cy
                "intrinsic": [255.520403, 449.883682, 250.828738, 255.237477],

                # Projection matrix from lidar to camera
                "extrinsic": [
                    [-0.735827, -0.65789, -0.0384775, 0],
                    [0.6567956, -0.70452916, 0.00140833, 0],
                    [-0.02255652, -0.0248216, 0.9993586, 0],
                    [0, 0, 0, 1]
                ],

                # Camera projection model - PINHOLE OR FISHEYE
                # For FISHEYE, mirrorParameter is also needed
                "cameraModel": "PINHOLE",
                "device_id": 1
            }
        ),
        ImageFile(
            filepath=left_cam1,
            tags=["left"],
            extra={
                "device_id": 2
            }
        )]
)


front_cam2 = 'front_0001.jpg'
left_cam2 = 'left_0001.jpg'
pcdfilepath2 = 'lidar_0001.pcd'

pcdfile2 = PointCloudFile(
    filepath=pcdfilepath2,
    related_files=[
        ImageFile(
            filepath=front_cam2,
            tags=["front"],
            extra={
                # fx, fy, cx, cy
                "intrinsic": [255.520403, 449.883682, 250.828738, 255.237477],

                # Projection matrix from lidar to camera
                "extrinsic": [
                    [-0.735827, -0.65789, -0.0384775, 0],
                    [0.6567956, -0.70452916, 0.00140833, 0],
                    [-0.02255652, -0.0248216, 0.9993586, 0],
                    [0, 0, 0, 1]
                ],

                # Camera projection model - PINHOLE OR FISHEYE
                # For FISHEYE, mirrorParameter is also needed
                "cameraModel": "PINHOLE",
                "device_id": 1
            }
        ),
        ImageFile(
            filepath=left_cam2,
            tags=["left"],
            extra={
                "device_id": 2
            }
        )
    ]
)

client.upload_pointcloud_data(
    dataset_id=1,
    pointcloudfiles=[pcdfile1, pcdfile2]
)

client.task.create(
    name="sensor-fusion-example",
    labels=[
        Label(name="label1", color="#ff00cc", sequence=1)
    ],
    dataset_id=1
)
