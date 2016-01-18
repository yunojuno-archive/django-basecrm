# -*- coding: utf-8 -*-

from django.apps import apps as django_apps

from . import (
    utils as base_api,
    exceptions as base_exceptions,
    settings as base_settings,
)

"""
All functions at this level are simple wrappers that accept (as kwargs) any extra GET vars to be
sent to the API call. In addition, the special 'id' kwarg parameter will affect the API endpoint
URL itself instead of being appended as a GET var.
"""

def get_contacts(**kwargs):
    """
    Hits the API for contacts. If given an 'id' kwarg it will request that specific ID contact;
    any other kwargs will be passed to the API as GET params; e.g. page=2.

    Returns a list of contact dicts unless the 'id' param is set in which case it returns a dict
    """
    resp = base_api.request(base_api.RETRIEVE, 'contacts', kwargs)
    return base_api.parse(resp)

def create_contact(contact_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to create
    """
    if base_api.validate_contact_dict(base_api.CREATE, contact_dict):
        resp = base_api.request(base_api.CREATE, 'contacts', None, data=contact_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass

def update_contact(id, contact_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to update
    """
    if base_api.validate_contact_dict(base_api.UPDATE, contact_dict, skip_id=True):
        resp = base_api.request(base_api.UPDATE, 'contacts', {'id': id}, data=contact_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass

def get_deals(**kwargs):
    """
    Hits the API for deals. If given an 'id' kwarg it will request that specific ID deal;
    any other kwargs will be passed to the API as GET params; e.g. page=2.

    Returns a list of deal dicts unless the 'id' param is set in which case it returns a dict
    """
    resp = base_api.request(base_api.RETRIEVE, 'deals', kwargs)
    return base_api.parse(resp)

def create_deal(deal_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to create
    """
    if base_api.validate_deal_dict(base_api.CREATE, deal_dict):
        resp = base_api.request(base_api.CREATE, 'deals', None, data=deal_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass

def update_deal(id, deal_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to update
    """
    if base_api.validate_deal_dict(base_api.UPDATE, deal_dict, skip_id=True):
        resp = base_api.request(base_api.UPDATE, 'deals', {'id': id}, data=deal_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass


def get_leads(**kwargs):
    """
    Hits the API for leads. If given an 'id' kwarg it will request that specific ID lead;
    any other kwargs will be passed to the API as GET params; e.g. page=2.

    Returns a list of lead dicts unless the 'id' param is set in which case it returns a dict
    """
    resp = base_api.request(base_api.RETRIEVE, 'leads', kwargs)
    return base_api.parse(resp)


def create_lead(lead_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to create
    """
    if base_api.validate_lead_dict(base_api.CREATE, lead_dict):
        resp = base_api.request(base_api.CREATE, 'leads', None, data=lead_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass


def update_lead(id, lead_dict):
    """
    Runs local validation on the given dict and gives passing ones to the API to update
    """
    if base_api.validate_lead_dict(base_api.UPDATE, lead_dict, skip_id=True):
        resp = base_api.request(base_api.UPDATE, 'leads', {'id': id}, data=lead_dict)
        return base_api.parse(resp)
    else:
        # validation failed but the exception was suppressed
        pass

def get_notes(resource_type=None, resource_id=None, **kwargs):
    """
    Hits the API for notes. If resource_type and/or resource_id are
    specified they will be added to the query as GET params
    """
    if resource_type is not None:
        if resource_type not in ['lead', 'contact', 'deal']:
            raise base_exceptions.BaseCRMValidationError('Invalid resource type')
        else:
            kwargs['resource_type'] = resource_type

    if resource_id is not None:
        if resource_type is None:
            raise base_exceptions.BaseCRMValidationError('Resource type required when specifying resource ID')
        else:
            kwargs['resource_id'] = resource_id

    resp = base_api.request(base_api.RETRIEVE, 'notes', kwargs)
    return base_api.parse(resp)

def create_note(resource_type, resource_id, content):
    """
    Posts to the notes endpoint of the API.
    """
    if resource_type is None:
        raise base_exceptions.BaseCRMValidationError('Resource type required')
    elif resource_type not in ['lead', 'contact', 'deal']:
        raise base_exceptions.BaseCRMValidationError('Invalid resource type')

    if resource_id is None:
        raise base_exceptions.BaseCRMValidationError('Resource ID required')

    note_dict = {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'content': content
    }

    resp = base_api.request(base_api.CREATE, 'notes', data=note_dict)
    return base_api.parse(resp)

def get_pipelines():
    """
    Note that we don't expect these to change often, so we are essentially caching this for the
    duration (there's no cachebusting)
    """
    if base_settings.BASECRM_CACHE_PIPELINE:
        app_conf = django_apps.get_app_config('django_basecrm')
        app_conf.instantiate_pipeline()
        pipeline = app_conf.pipeline
    else:
        pipeline = get_pipelines_from_api()
    return pipeline

def get_stages():
    """
    Note that we don't expect these to change often, so we are essentially caching this for the
    duration (there's no cachebusting)
    """
    if base_settings.BASECRM_CACHE_STAGES:
        app_conf = django_apps.get_app_config('django_basecrm')
        app_conf.instantiate_stages()
        stages = app_conf.stages
    else:
        stages = get_stages_from_api()
    return stages

def get_users():
    """
    Note that we don't expect these to change often, so we are essentially caching this for the
    duration (there's no cachebusting)
    """
    if base_settings.BASECRM_CACHE_USERS:
        app_conf = django_apps.get_app_config('django_basecrm')
        app_conf.instantiate_users()
        users = app_conf.users
    else:
        users = get_users_from_api()
    return users

def get_user_ids():
    return [x['id'] for x in get_users()]

def get_stage_ids():
    return [x['id'] for x in get_stages()]

def get_pipelines_from_api(**kwargs):
    """
    This is the API method, called by the appConfig.instantiate method
    """
    resp = base_api.request(base_api.RETRIEVE, 'pipelines', kwargs)
    if base_api.count(resp) > 1:
        raise NotImplementedError("We currently only cater for a single pipeline in BaseCRM")
    return base_api.parse(resp)

def get_stages_from_api(**kwargs):
    """
    This is the API method, called by the appConfig.instantiate method
    """
    resp = base_api.request(base_api.RETRIEVE, 'stages', kwargs)
    return base_api.parse(resp)

def get_users_from_api(**kwargs):
    """
    This is the API method, called by the appConfig.instantiate method
    """
    resp = base_api.request(base_api.RETRIEVE, 'users', kwargs)
    return base_api.parse(resp)
