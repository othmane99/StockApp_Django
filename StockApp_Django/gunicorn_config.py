import multiprocessing
import os

bind = '127.0.0.1:8000'

# Determine the number of workers based on CPU count
workers = multiprocessing.cpu_count() * 2 + 1

# Set the path to your Django project
pythonpath = '/home/othmane/Desktop/BeyondCom_1/venv1/src'

# Change to the directory containing your Django project
chdir = '/home/othmane/Desktop/BeyondCom_1/venv1/src'

# Set the user and group that should run the Gunicorn process
# Replace 'your_username' and 'your_group_name' with appropriate values
user = 'othmane'
group = 'othmane'

# Set the timeout for worker processes
timeout = 30
