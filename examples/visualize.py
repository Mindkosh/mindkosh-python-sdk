from mindkosh import Client, TestSet

client = Client(token='')
testset = TestSet()

task_id = 1
task = client.task.get(task_id)
frames = task.frames()

testsetframes = (frames[0], frames[1], frames[2])

testset.add(testsetframes)

testset.visualize(show_annotations=True, fill_color=0.2)
