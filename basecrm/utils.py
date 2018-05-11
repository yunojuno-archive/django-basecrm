import logging
import requests

from django.apps import apps as django_apps

from . import settings, exceptions

logger = logging.getLogger(__name__)

CREATE = '__create__'
UPDATE = '__update__'
RETRIEVE = '__retrieve__'
DELETE = '__delete__'
INFO = '__head__'
VERBS = {
    RETRIEVE: 'GET',
    CREATE: 'POST',
    UPDATE: 'PUT',
    DELETE: 'DELETE',
    INFO: 'HEAD'
}
REQUIRE_BODY_DATA = [
    CREATE,
    UPDATE
]


def request(action, endpoint, get_params=None, **kwargs):
    """
    Makes a request to the BaseCRM API and handles any errors thrown intelligently. See _request
    for more info on the parameters.
    """
    if action not in VERBS.keys():
        raise exceptions.BaseCRMBadParameterFormat(
            "Expecting one of INFO, RETRIEVE, CREATE, UPDATE or DELETE but got %s"
            % action
        )

    if action in REQUIRE_BODY_DATA:
        if 'data' not in kwargs:
            raise exceptions.BaseCRMBadParameterFormat(
                "API method '%s' requires a `data` parameter"
                % VERBS[action]
            )
        post_data = kwargs.pop('data')
        kwargs['json'] = {'data': post_data}

    if get_params is not None and 'id' in get_params:
        is_id_request = True
    else:
        is_id_request = False

    method = VERBS[action]
    r = _request(method, endpoint, get_params, **kwargs)
    if r.status_code != 200:
        json = r.json()
        logger.error(
            "BaseCRM API responded with status code: '%s'. %s" % (
                r.status_code,
                json['errors'][0]['error']['details'],
            )
        )
        if r.status_code == 401:
            raise exceptions.BaseCRMAPIUnauthorized()
        elif r.status_code == 404 and is_id_request:
            # no record with the given ID exists
            raise exceptions.BaseCRMNoResult()
        elif r.status_code == 422:
            raise exceptions.BaseCRMValidationError(json['errors'][0]['error']['details'])
        else:
            raise Exception(
                "BaseCRM API responded with status code '%s'. %s" % (
                    r.status_code,
                    json['errors'][0]['error']['details'],
                )
            )
    else:
        return r.json()


def parse(response_json):
    """
    Simple helper method to get into the data dicts for each item returned and ignore all the meta;
    just gives back a list of dicts.
    """
    if (
        not isinstance(response_json, dict) or  # wrong type of arg
        (  # ID type response
            'items' not in response_json and
            'data' not in response_json
        ) or
        (  # list endpoint type response
            'items' in response_json and
            (
                len(response_json['items']) > 0 and
                'data' not in response_json['items'][0]
            )
        )
    ):
        raise exceptions.BaseCRMBadParameterFormat()

    if 'items' in response_json:
        return [item['data'] for item in response_json['items']]
    else:
        return response_json['data']


def count(response_json):
    """
    Pulls and returns the count given by the BaseCRM API (which takes account of pagination)
    """
    if (
        not isinstance(response_json, dict) or
        'meta' not in response_json
    ):
        raise exceptions.BaseCRMBadParameterFormat(
            u'Parameter format was not as expected: a full dict from the requests.json() '
            u'method applied to the full BaseCRM API response. The parameter given was: %s' %
            repr(response_json)
        )

    if 'count' not in response_json['meta']:
        return 1  # we're assuming this is a response to an ID request
    return response_json['meta']['count']


def validate_contact_dict(operation, contact_dict, skip_id=False, suppress=False):
    if suppress is True:
        raise NotImplementedError("No validation suppression in place yet")
    valid = False
    msg = ""
    if operation == CREATE:
        if (
            (  # individual contact requirements
                (
                    'is_organization' not in contact_dict or
                    not contact_dict['is_organization']
                ) and
                (
                    'first_name' in contact_dict and
                    'last_name' in contact_dict
                )
            ) or
            (  # organization contact requirements
                (
                    'is_organization' in contact_dict and
                    contact_dict['is_organization'] is True
                ) and
                (
                    'name' in contact_dict
                )
            )
        ):
            valid = True
        else:
            msg = (
                "If 'is_organization'==True, 'first_name' and 'last_name' are all required, "
                "or if 'is_organization'==False, 'name' is required; "
                "fields supplied were: %s" % contact_dict.keys()
            )
    elif operation == UPDATE:
        if 'id' in contact_dict or skip_id is True:
            valid = True
        else:
            msg = (
                "'id' is required; fields supplied were: %s" % contact_dict.keys()
            )

    if not valid:
        msg = "Parameters fail BaseCRM API requirements for contact. %s" % msg
        raise exceptions.BaseCRMValidationError(msg)

    return True


def validate_deal_dict(operation, deal_dict, skip_id=False, suppress=False):
    if suppress is True:
        raise NotImplementedError("No validation suppression in place yet")
    valid = False
    msg = ""
    if operation == CREATE:
        if (
            'name' in deal_dict and
            'contact_id' in deal_dict and
            'custom_fields' in deal_dict
        ):
            valid = True
        else:
            msg = (
                "'name', 'contact_id' and 'custom_fields' are all required; "
                "fields supplied were: %s" % deal_dict.keys()
            )
    elif operation == UPDATE:
        if 'id' in deal_dict or skip_id is True:
            valid = True
        else:
            msg = (
                "'id' is required; fields supplied were: %s" % deal_dict.keys()
            )

    if not valid:
        msg = "Parameters fail BaseCRM API requirements for deal. %s" % msg
        raise exceptions.BaseCRMValidationError(msg)

    return True


def validate_lead_dict(operation, lead_dict, skip_id=False, suppress=False):
    if suppress is True:
        raise NotImplementedError("No validation suppression in place yet")
    valid = False
    msg = ""
    if operation == CREATE:
        if (
            'last_name' in lead_dict and
            'organization_name' in lead_dict
        ):
            valid = True
        else:
            msg = (
                "'last_name' and 'organization_name' are all required; "
                "fields supplied were: %s" % lead_dict.keys()
            )
    elif operation == UPDATE:
        if 'id' in lead_dict or skip_id is True:
            valid = True
        else:
            msg = (
                "'id' is required; fields supplied were: %s" % lead_dict.keys()
            )

    if not valid:
        msg = "Parameters fail BaseCRM API requirements for deal. %s" % msg
        raise exceptions.BaseCRMValidationError(msg)

    return True


def instantiate_if_necessary():
    base_app = django_apps.get_app_config('basecrm')
    base_app.instantiate_objects()


###########################################################################
#                                                                        ##
#    Don't call any of the following methods directly unless debugging   ##
#                                                                        ##
###########################################################################

def _request(method, endpoint, get_params=None, **kwargs):
    """
    Wraps requests.request with custom headers and api URL generation methods. Accepts just the last
    segment of the endpoint, rather than the whole URI; the rest comes from settings.

    The get_params param will be used to build GET get_params to append to the API call (e.g. for
    pagination and filtering). An ID can also be added in to the get_params param and will be used
    by _build_api_endpoint.

    Any extra kwargs will be passed along to `requests.request()`
    """
    url = _build_api_endpoint(endpoint, get_params)
    extra_headers = kwargs.pop('headers', None)
    kwargs['headers'] = _build_headers(extra_headers)
    kwargs['params'] = get_params

    response = requests.request(method, url, **kwargs)

    logger.debug(
        "'%s' request to BaseCRM API '%s' endpoint gave a '%s' response (url: %s)" % (
            method,
            endpoint,
            response.status_code,
            response.url,
        )
    )
    return response


def _build_headers(extra_headers=None):
    """
    Puts together the standard headers BaseCRM API requires. Accepts a dict that can add to or
    override these.
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % settings.BASECRM_API_KEY,
        'User-Agent': settings.BASECRM_USER_AGENT
    }
    if extra_headers is not None:
        if not isinstance(extra_headers, dict):
            raise exceptions.BaseCRMBadParameterFormat(
                u'Parameter format was not a dict as expected. The parameter given was: %s' %
                repr(extra_headers)
            )
        for k, v in extra_headers.items():
            headers[k] = v

    return headers


def _build_api_endpoint(endpoint, get_params=None):
    """
    We expect settings.BASECRM_API_URL to be e.g. https://api.getbase.com/v2/ -- note the protocol,
    the path and the trailing slash are all included and expected (i.e. not handled)
    """
    url = '%s%s' % (settings.BASECRM_API_URL, endpoint)
    if get_params is not None:
        if not isinstance(get_params, dict):
            raise exceptions.BaseCRMBadParameterFormat(
                u'Parameter format was not a dict as expected. The parameter given was: %s' %
                repr(get_params)
            )

        id = get_params.pop('id', None)
        if id is not None:
            url = "%s/%s" % (url, id)
    return url
