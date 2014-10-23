import os

import dj_database_url

INSTALLED_APPS = ('inventory',)
MIDDLEWARE_CLASSES = ()
SECRET_KEY = os.environ.get('SECRET_KEY', '*q5ne7-4=vlewvfv8von1peb!+(dsk2&n364f()54i^mv2lz4y')
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL', 'postgres://localhost/inventory')),
}
