# -*- coding: utf-8 -*-
from django.apps import AppConfig

from . import (
    utils as base_api,
    exceptions as base_exceptions,
    settings as base_settings
)
from helpers import (
    get_pipelines_from_api,
    get_stages_from_api,
    get_users_from_api
)

class BaseCRMConfig(AppConfig):
    name = 'django_basecrm'
    verbose_name = "BaseCRM API client SDK for Django"
    pipeline = None
    stages = None
    users = None

    def ready(self):
        super(BaseCRMConfig, self).ready()
        if base_settings.BASECRM_INSTANTIATE_ON_START:
            self.instantiate_objects()

    def instantiate_objects(self):
        """
        Currently we assume a single pipeline (.get_pipelines() will error if there are > 1), which
        makes keeping track of stages easier. Deals progress through stages, and sending incorrect
        user IDs can lose deals, so it's useful to have a list available
        """
        p = get_pipelines_from_api()
        try:
            self.pipeline = p[0]
        except:
            self.pipeline = p

        pipeline_id = self.pipeline['id']
        self.stages = get_stages_from_api(pipeline_id=pipeline_id)
        self.users = get_users_from_api()
