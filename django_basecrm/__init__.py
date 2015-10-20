# -*- coding: utf-8 -*-
default_app_config = '%s.apps.BaseCRMConfig' % __name__

from helpers import (
    get_contacts,
    get_deals,
    get_notes,
    get_pipelines,
    get_stages,
    create_contact,
    create_deal,
    create_note,
    update_contact,
    update_deal,
)
