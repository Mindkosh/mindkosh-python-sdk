from mindkosh import Client, TestSet

client = Client('token')
testset = TestSet()

tasks = client.task.get()

# get first 3 tasks from task list
t1 = tasks[0]
t2 = tasks[1]
t3 = tasks[2]

# visualize 5 frames from each task
testsetframes = []
for task in (t1, t2, t3):
    frames = task.frames()
    testsetframes += (frames[0], frames[1], frames[2])


testset.add_frames(testsetframes)
testset.visualize(show_annotations=True, fill_color=0.3)
# testset.download_annotations(location='/home/usr/Desktop/annotations',format='coco')
