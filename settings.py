BASECRM_API_URL = 'https://api.getbase.com/v2/'
BASECRM_API_KEY = 'xxxxxxxxx'
BASECRM_CACHE_AT_STARTUP = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = 'basecrm'

INSTALLED_APPS = (
    'basecrm',
)
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
