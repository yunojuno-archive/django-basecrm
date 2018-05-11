from django.conf import settings

BASECRM_API_URL = getattr(settings, 'BASECRM_API_URL', 'https://api.getbase.com/v2/')
BASECRM_API_KEY = getattr(settings, 'BASECRM_API_KEY', None)
BASECRM_USER_AGENT = getattr(settings, 'BASECRM_USER_AGENT', 'YunoJuno/1.0')
BASECRM_CACHE_USERS = getattr(settings, 'BASECRM_CACHE_USERS', True)
BASECRM_CACHE_STAGES = getattr(settings, 'BASECRM_CACHE_STAGES', True)
BASECRM_CACHE_PIPELINE = getattr(settings, 'BASECRM_CACHE_PIPELINE', True)
BASECRM_CACHE_AT_STARTUP = getattr(settings, 'BASECRM_CACHE_AT_STARTUP', True)
BASECRM_CACHE_USERS_PER_PAGE = getattr(settings, 'BASECRM_CACHE_USERS_PER_PAGE', 100)
BASECRM_CACHE_USERS_STATUS = getattr(settings, 'BASECRM_CACHE_USERS_STATUS', 'active')
BASECRM_CACHE_USERS_FILTERS = {
    'per_page': BASECRM_CACHE_USERS_PER_PAGE,
    'status': BASECRM_CACHE_USERS_STATUS
}
if BASECRM_CACHE_USERS_STATUS in (None, '*'):
    del BASECRM_CACHE_USERS_FILTERS['status']
