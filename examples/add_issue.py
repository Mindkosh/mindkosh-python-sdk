import mindkosh

client = mindkosh.Client()

task = client.task.get(task_id=100)

#add issue
task.add_annotation_issue(
    frame_id=10, 
    issue_name='issue_name', 
    shape_id=98, 
    message='comm1'
)


frames = task.frames(search='image1', max_frames=5)
frame = frames[1]

#add issue
frame.add_issue('issue-name', message='comment')

#add issue on a shape
frame.add_issue('issue-name', message='comment', shape_id=100)

#add issue on a track
frame.add_issue('issue-name', message='comment', track_id=100)

