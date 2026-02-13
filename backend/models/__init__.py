# This file makes the 'models' folder a Python package
# Python packages allow us to import code from this folder

# Import all models so they can be used easily
from .user import User
from .job import Job
from .application import Application
from .resume import Resume

# This allows us to do:
# from models import User, Job, Application, Resume
# Instead of:
# from models.user import User
# from models.job import Job
# etc.
