command = '/home/qedu/code/env/bin/gunicorn'
pythonpath = '/home/qedu/code/qedu'
bind = '127.0.0.1:8003'
workers = 3
user = 'qedu'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=lms.settings'
