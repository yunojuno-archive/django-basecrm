from django.apps import AppConfig

from . import settings, helpers


class BaseCRMConfig(AppConfig):

    name = 'basecrm'
    verbose_name = "Base (CRM)"
    pipeline = None
    stages = None
    users = None

    def ready(self):
        super(BaseCRMConfig, self).ready()
        if settings.BASECRM_CACHE_AT_STARTUP:
            self.instantiate_objects()

    def instantiate_objects(self, force=False):
        """
        Currently we assume a single pipeline (.get_pipelines() will error if there are > 1), which
        makes keeping track of stages easier. Deals progress through stages, and sending incorrect
        user IDs can lose deals, so it's useful to have a list available
        """
        self.instantiate_pipeline(force)
        self.instantiate_stages(force)
        self.instantiate_users(force)

    def instantiate_pipeline(self, force=False):
        if force is True or self.pipeline is None:
            p = helpers.get_pipelines_from_api()
            try:
                self.pipeline = p[0]
            except Exception:
                self.pipeline = p

    def instantiate_stages(self, force=False):
        if force is True or self.stages is None:
            kwargs = {}
            if self.pipeline is not None:
                kwargs['pipeline_id'] = self.pipeline['id']
            self.stages = helpers.get_stages_from_api(**kwargs)

    def instantiate_users(self, force=False):
        if force is True or self.users is None:
            self.users = helpers.get_users_from_api(**settings.BASECRM_CACHE_USERS_FILTERS)
