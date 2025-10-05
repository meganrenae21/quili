import os

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
subjects_dir = os.path.join(data_dir, 'subjects')
progress_dir = os.path.join(data_dir, 'progress')
user_file = os.path.join(data_dir, 'user.json')
attachment_dir = os.path.join(basedir, 'attachments')