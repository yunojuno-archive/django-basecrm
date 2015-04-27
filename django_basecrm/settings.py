# -*- coding: utf-8 -*-
from django.conf import settings

BASECRM_API_URL = getattr(settings, 'BASECRM_API_URL', None)
BASECRM_API_KEY = getattr(settings, 'BASECRM_API_KEY', None)
BASECRM_USER_AGENT = getattr(settings, 'BASECRM_USER_AGENT', 'YunoJuno/1.0')
BASECRM_INSTANTIATE_ON_START = getattr(settings, 'BASECRM_INSTANTIATE_ON_START', False)
