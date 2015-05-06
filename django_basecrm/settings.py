# -*- coding: utf-8 -*-
from django.conf import settings

BASECRM_API_URL = getattr(settings, 'BASECRM_API_URL', 'https://api.getbase.com/v2/')
BASECRM_API_KEY = getattr(settings, 'BASECRM_API_KEY', None)
BASECRM_USER_AGENT = getattr(settings, 'BASECRM_USER_AGENT', 'YunoJuno/1.0')
BASECRM_CACHE_USERS = getattr(settings, 'BASECRM_CACHE_USERS', True)
BASECRM_CACHE_STAGES = getattr(settings, 'BASECRM_CACHE_STAGES', True)
BASECRM_CACHE_PIPELINE = getattr(settings, 'BASECRM_CACHE_PIPELINE', True)
BASECRM_CACHE_AT_STARTUP = getattr(settings, 'BASECRM_CACHE_AT_STARTUP', True)