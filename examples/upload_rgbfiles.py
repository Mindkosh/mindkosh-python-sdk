from mindkosh import Client, ImageFile, MainImage

client = Client(token='')

imagepath1 = '/img_001.jpg'
imagepath2 = '/img_002.jpg'
imagepath3 = '/img_003.jpg'
imagepath4 = '/img_004.jpg'
imagepath5 = '/img_005.jpg'
imagepath6 = '/img_006.jpg'

rgbimgpath1 = '/rgb-img_001.jpg'
rgbimgpath2 = '/rgb-img_002.jpg'
rgbimgpath3 = '/rgb-img_003.jpg'


rgbfile1 = MainImage(
    filepath = rgbimgpath1,
    related_files = [ImageFile(
        filepath = imagepath1, tags=['tag1','tag2'], extra={'device_id':1}
    ),
    ImageFile(
        filepath = imagepath2, tags = ['right'], extra={'device_id':4}
    ),
    ImageFile(
        filepath = imagepath3, tags=['tag1','tag2'], extra={'device_id':3}
    ),
    ImageFile(
        filepath = imagepath4, tags = ['right'], extra={'device_id':5}
    )],
    tags = ['dataset-1']
)

rgbfile2 = MainImage(
    filepath = rgbimgpath1,
    related_files = [ImageFile(
        filepath = imagepath5, tags=['tag1','tag2'], extra={'device_id':1}
    ),
    ImageFile(
        filepath = imagepath6, tags = ['right'], extra={'device_id':2}
    )]
)

rgbfile3 = MainImage(filepath=rgbimgpath1,related_files=[],tags=['dataset-2'])

client.upload_mainimages(dataset_id=3, rgbfiles=[rgbfile1, rgbfile2, rgbfile3])