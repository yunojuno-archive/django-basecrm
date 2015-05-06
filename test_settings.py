BASECRM_API_URL='https://api.getbase.com/v2/'
BASECRM_API_KEY='xxxxxxxxx'
BASECRM_CACHE_AT_STARTUP=False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db',
    }
}
SECRET_KEY='xxxxx'
INSTALLED_APPS = (
    'django_basecrm',
)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
