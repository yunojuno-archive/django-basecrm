# -*- coding: utf-8 -*-
import mock
import types

from django.apps import apps as django_apps
from django.test import TestCase
from django.db.models.base import ModelBase

from . import apps, exceptions, helpers, serializers, utils


class RequestWrapperTests(TestCase):

    @mock.patch('%s.utils.base_settings' % __name__)
    def test_build_api_endpoint(self, settings):
        # bad api_urls aren't handled - caveat emptor
        settings.BASECRM_API_URL = 'api.base.com'
        params = None
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'api.base.comcontacts')

        settings.BASECRM_API_URL = 'http://api.base.com/test'
        params = None
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/testcontacts')

        settings.BASECRM_API_URL = 'http://api.base.com/test/'

        params = None
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/test/contacts')

        params = {'id': 34}
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/test/contacts/34')

        # only id params are used, and then only to add to the endpoint
        params = {'hello': 'world'}
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/test/contacts')

        params = {'hello': 'world', 'id': 34}
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/test/contacts/34')

        # but they're also not inspected - caveat emptor
        params = {'hello': 'world', 'id': 'world'}
        endpoint = 'contacts'
        result = utils._build_api_endpoint(endpoint, params)
        self.assertEqual(result, 'http://api.base.com/test/contacts/world')

    @mock.patch('%s.utils.base_settings' % __name__)
    def test_build_headers(self, settings):
        settings.BASECRM_API_KEY = 'an-api_key/that1s4lphaNuMer1c'
        settings.BASECRM_USER_AGENT = 'yourApp/1.0'

        extras = None
        result = utils._build_headers(extras)
        self.assertEqual(
            result,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer an-api_key/that1s4lphaNuMer1c',
                'User-Agent': 'yourApp/1.0'
            }
        )

        extras = {
            'X-Custom-Header': 'test value'
        }
        result = utils._build_headers(extras)
        self.assertEqual(
            result,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer an-api_key/that1s4lphaNuMer1c',
                'User-Agent': 'yourApp/1.0',
                'X-Custom-Header': 'test value'
            }
        )

        extras = {
            'Accept': 'text/html'
        }
        result = utils._build_headers(extras)
        self.assertEqual(
            result,
            {
                'Accept': 'text/html',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer an-api_key/that1s4lphaNuMer1c',
                'User-Agent': 'yourApp/1.0'
            }
        )

        extras = {
            'Accept': 'text/html',
            'Content-Type': 'something',
            'Authorization': 'something else',
            'User-Agent': 'yourApp/2.0',
            'X-Custom-Header': 'test value'
        }
        result = utils._build_headers(extras)
        self.assertEqual(
            result,
            {
                'Accept': 'text/html',
                'Content-Type': 'something',
                'Authorization': 'something else',
                'User-Agent': 'yourApp/2.0',
                'X-Custom-Header': 'test value'
            }
        )

    @mock.patch('%s.utils.requests' % __name__)
    @mock.patch('%s.utils._build_api_endpoint' % __name__)
    @mock.patch('%s.utils._build_headers' % __name__)
    def test_request_wrapper(self, _b_headers, _b_endpoint, requests):
        response = mock.Mock()
        response.status_code = 200
        response.url = 'http://google.com/q=helloworld'
        requests.request.return_value = response
        _b_headers.return_value = {'Accept': 'application/json', 'User-Agent': 'Test'}
        _b_endpoint.return_value = 'http://google.com/'

        method = 'GET'
        endpoint = 'http://api.base.com/contacts'
        get_params = {}
        kwargs = {}
        result = utils._request(method, endpoint, get_params, **kwargs)
        self.assertEqual(result, response)
        _b_headers.assert_called_once_with(None)
        _b_endpoint.assert_called_once_with(endpoint, get_params)
        requests.request.assert_called_once_with(
            method,
            _b_endpoint.return_value,
            headers=_b_headers.return_value,
            params=get_params
        )

        _b_headers.reset_mock()
        _b_endpoint.reset_mock()
        requests.request.reset_mock()

        method = 'POST'
        endpoint = 'http://api.base.com/deals'
        get_params = {
            'test': True
        }
        kwargs = {
            'headers': {'Accept': 'plain/txt', 'User-Agent': 'BaseCRM Client'}
        }
        result = utils._request(method, endpoint, get_params, **kwargs)
        self.assertEqual(result, response)
        _b_headers.assert_called_once_with({'Accept': 'plain/txt', 'User-Agent': 'BaseCRM Client'})
        _b_endpoint.assert_called_once_with(endpoint, get_params)
        requests.request.assert_called_once_with(
            method,
            _b_endpoint.return_value,
            headers=_b_headers.return_value,
            params=get_params
        )

        _b_headers.reset_mock()
        _b_endpoint.reset_mock()
        requests.request.reset_mock()

        method = 'POST'
        endpoint = 'http://api.base.com/deals'
        get_params = {
            'test': True
        }
        kwargs = {
            'headers': {'Accept': 'plain/txt'},
            'some_other_requests_param': 87
        }
        result = utils._request(method, endpoint, get_params, **kwargs)
        self.assertEqual(result, response)
        _b_headers.assert_called_once_with({'Accept': 'plain/txt'})
        _b_endpoint.assert_called_once_with(endpoint, get_params)
        requests.request.assert_called_once_with(
            method,
            _b_endpoint.return_value,
            headers=_b_headers.return_value,
            params=get_params,
            some_other_requests_param=87
        )


class ValidationTests(TestCase):

    def test_validate_contact_dict(self):
        operation = utils.CREATE
        contact_dict = {}
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.UPDATE
        contact_dict = {}
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.CREATE
        contact_dict = {
            'is_organization': True,
            'name': 'Acme Carburretors Inc.'
        }
        result = utils.validate_contact_dict(operation, contact_dict)
        self.assertTrue(result)

        operation = utils.UPDATE
        contact_dict = {
            'is_organization': True,
            'name': 'Acme Carburretors Inc.'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.CREATE
        contact_dict = {
            'is_organization': True,
            'first_name': 'Albert',
            'last_name': 'Einstein'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.UPDATE
        contact_dict = {
            'is_organization': True,
            'first_name': 'Albert',
            'last_name': 'Einstein'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.CREATE
        contact_dict = {
            'is_organization': False,
            'name': 'Acme Carburretors Inc.'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.UPDATE
        contact_dict = {
            'is_organization': False,
            'name': 'Acme Carburretors Inc.'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.CREATE
        contact_dict = {
            'is_organization': False,
            'first_name': 'Albert',
            'last_name': 'Einstein'
        }
        result = utils.validate_contact_dict(operation, contact_dict)
        self.assertTrue(result)

        operation = utils.UPDATE
        contact_dict = {
            'is_organization': False,
            'first_name': 'Albert',
            'last_name': 'Einstein'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.CREATE
        contact_dict = {
            'id': 32
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict)

        operation = utils.UPDATE
        contact_dict = {
            'id': 32
        }
        result = utils.validate_contact_dict(operation, contact_dict)
        self.assertTrue(result)

        operation = utils.UPDATE
        contact_dict = {
            'id': 32
        }
        skip_id = False
        suppress = True
        with self.assertRaises(NotImplementedError):
            utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)

        operation = 'hello'
        contact_dict = {
            'id': 32
        }
        suppress = False
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)

        operation = 'GET'
        contact_dict = {
            'id': 32
        }
        suppress = False
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)

        operation = utils.UPDATE
        contact_dict = {
            'id': 32
        }
        suppress = 'hello'
        result = utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)
        self.assertTrue(result)

        operation = utils.UPDATE
        contact_dict = {
            'id': 32
        }
        suppress = False
        result = utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)
        self.assertTrue(result)

        operation = utils.UPDATE
        contact_dict = {}
        skip_id = True
        result = utils.validate_contact_dict(operation, contact_dict, skip_id, suppress)
        self.assertTrue(result)

    def test_validate_deal_dict(self):
        operation = utils.UPDATE
        deal_dict = {
            'id': 32
        }
        skip_id = False
        suppress = True
        with self.assertRaises(NotImplementedError):
            utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)

        operation = utils.UPDATE
        deal_dict = {
            'id': 32
        }
        suppress = False
        result = utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)
        self.assertTrue(result)

        operation = utils.UPDATE
        deal_dict = {
            'id': 32
        }
        suppress = 'hello'
        result = utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)
        self.assertTrue(result)

        skip_id = True
        deal_dict = {}
        result = utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)
        self.assertTrue(result)

        skip_id = False
        operation = utils.CREATE
        deal_dict = {
            'name': 'Manhattan Project',
            'contact_id': 23456,
            'custom_fields': {}
        }
        result = utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)
        self.assertTrue(result)

        operation = utils.CREATE
        deal_dict = {
            'name': True,
            'contact_id': 'not really an id',
            'custom_fields': 'not_a_dict'
        }
        result = utils.validate_deal_dict(operation, deal_dict, skip_id, suppress)
        self.assertTrue(result)

        operation = utils.CREATE
        deal_dict = {
            'id': 32
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        skip_id = True
        operation = utils.CREATE
        deal_dict = {
            'id': 32
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        skip_id = False
        operation = utils.CREATE
        deal_dict = {
            'name': 'Manhattan Project',
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        operation = utils.CREATE
        deal_dict = {
            'name': 'Manhattan Project',
            'contact_id': 23456,
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        operation = utils.CREATE
        deal_dict = {
            'name': 'Manhattan Project',
            'custom_fields': 'not_a_dict'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        operation = utils.UPDATE
        deal_dict = {
            'name': True,
            'contact_id': 'not really an id',
            'custom_fields': 'not_a_dict'
        }
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.validate_deal_dict(operation, deal_dict)

        operation = utils.UPDATE
        deal_dict = {
            'id': True
        }
        result = utils.validate_deal_dict(operation, deal_dict)
        self.assertTrue(result)


class UtilityMethodTests(TestCase):

    @mock.patch('%s.utils.django_apps' % __name__)
    def test_instantiate_if_necessary(self, _django_apps):
        _app = mock.Mock()
        _app.pipeline = None
        _app.stages = None
        _app.users = None
        _django_apps.get_app_config.return_value = _app

        utils.instantiate_if_necessary()
        _django_apps.get_app_config.assert_called_once_with('django_basecrm')
        _app.instantiate_stages.assert_called_once()

        _django_apps.get_app_config.reset_mock()
        _app.instantiate_stages.reset_mock()

        _app.pipeline = 9877556
        _app.stages = None
        _app.users = None

        utils.instantiate_if_necessary()
        _django_apps.get_app_config.assert_called_once_with('django_basecrm')
        _app.instantiate_stages.assert_called_once()

        _django_apps.get_app_config.reset_mock()
        _app.instantiate_stages.reset_mock()

        _app.pipeline = 9877556
        _app.stages = ['one', 'two']
        _app.users = None

        utils.instantiate_if_necessary()
        _django_apps.get_app_config.assert_called_once_with('django_basecrm')
        _app.instantiate_stages.assert_called_once()

        _django_apps.get_app_config.reset_mock()
        _app.instantiate_stages.reset_mock()

        _app.pipeline = 9877556
        _app.stages = ['one', 'two']
        _app.users = ['a', 'b', 'c']

        utils.instantiate_if_necessary()
        _django_apps.get_app_config.assert_called_once_with('django_basecrm')
        self.assertFalse(_app.instantiate_stages.called)

    def test_count(self):
        response_dict = {}
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.count(response_dict)

        response_dict = []
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.count(response_dict)

        response_dict = ('hello', )
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.count(response_dict)

        response_dict = {'name': 'hello'}
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.count(response_dict)

        response_dict = {'name': 'hello', 'meta': []}
        result = utils.count(response_dict)
        self.assertEqual(result, 1)

        response_dict = {'name': 'hello', 'meta': 'world'}
        result = utils.count(response_dict)
        self.assertEqual(result, 1)

        response_dict = {'name': 'hello', 'meta': {'count': 98}}
        result = utils.count(response_dict)
        self.assertEqual(result, 98)

    def test_parse(self):
        response_dict = {}
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.parse(response_dict)

        response_dict = []
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.parse(response_dict)

        response_dict = ('hello', )
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.parse(response_dict)

        response_dict = {'items': []}
        result = utils.parse(response_dict)
        self.assertEqual(result, [])

        response_dict = {'items': [{'name': 'hello'}]}
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.parse(response_dict)

        response_dict = {'items': [{'data': {'name': 'hello'}}], 'meta': {'count': 98}}
        result = utils.parse(response_dict)
        self.assertEqual(result, [{'name': 'hello'}])

        response_dict = {'items': [{'data': {'name': 'hello'}}, {'data': {'name': 'world'}}], 'meta': {'count': 98}}
        result = utils.parse(response_dict)
        self.assertEqual(result, [{'name': 'hello'}, {'name': 'world'}])

        response_dict = {'name': 'hello'}
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.parse(response_dict)

        response_dict = {'data': {'name': 'hello'}, 'meta': 'world'}
        result = utils.parse(response_dict)
        self.assertEqual(result, {'name': 'hello'})

    @mock.patch('%s.utils._request' % __name__)
    def test_request(self, _request):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = {'items': [], 'meta': {}}
        _request.return_value = response


        # test all the pre-send validation

        action = 'GET'
        endpoint = 'contacts'
        get_params = None
        kwargs = {}

        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.request(action, endpoint, get_params, **kwargs)

        action = 'hello'
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.request(action, endpoint, get_params, **kwargs)

        action = utils.RETRIEVE
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        response.json.assert_called_once()

        response.json.reset_mock()
        action = utils.INFO
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        response.json.assert_called_once()

        response.json.reset_mock()
        action = utils.DELETE
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        response.json.assert_called_once()

        response.json.reset_mock()
        action = utils.CREATE
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.request(action, endpoint, get_params, **kwargs)

        response.json.reset_mock()
        action = utils.UPDATE
        with self.assertRaises(exceptions.BaseCRMBadParameterFormat):
            utils.request(action, endpoint, get_params, **kwargs)

        kwargs['data'] = {}

        response.json.reset_mock()
        action = utils.CREATE
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        response.json.assert_called_once()

        response.json.reset_mock()
        action = utils.UPDATE
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        response.json.assert_called_once()

        # test the param logic

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.UPDATE
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        _request.assert_called_once_with(
            utils.VERBS[action],
            endpoint,
            get_params,
            json={'data': {}}
        )
        response.json.assert_called_once()

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.CREATE
        kwargs = {
            'data': {'serialized_id': 98},
            'headers': {'Accept': 'text/plain'},
            'other_param_for_requests_lib': True
        }
        result = utils.request(action, endpoint, get_params, **kwargs)
        self.assertEqual(result, response.json.return_value)
        _request.assert_called_once_with(
            utils.VERBS[action],
            endpoint,
            get_params,
            json={'data': {'serialized_id': 98}},
            headers={'Accept': 'text/plain'},
            other_param_for_requests_lib=True
        )
        response.json.assert_called_once()

        response.json.return_value = {'errors': [{'error': {'details': 'test error message'}}]}
        response.status_code = 401

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.RETRIEVE
        kwargs = {}
        with self.assertRaises(exceptions.BaseCRMAPIUnauthorized):
            utils.request(action, endpoint, get_params, **kwargs)

        response.status_code = 403

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.RETRIEVE
        kwargs = {}
        with self.assertRaises(Exception):
            utils.request(action, endpoint, get_params, **kwargs)

        response.status_code = 404

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.RETRIEVE
        kwargs = {}
        with self.assertRaises(Exception):
            utils.request(action, endpoint, get_params, **kwargs)

        response.status_code = 404
        get_params = {'id': 99}

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.RETRIEVE
        kwargs = {}
        with self.assertRaises(exceptions.BaseCRMNoResult):
            utils.request(action, endpoint, get_params, **kwargs)

        response.status_code = 422
        get_params = None

        _request.reset_mock()
        response.json.reset_mock()
        action = utils.RETRIEVE
        kwargs = {}
        with self.assertRaises(exceptions.BaseCRMValidationError):
            utils.request(action, endpoint, get_params, **kwargs)


class HelperMethodTests(TestCase):

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_contacts(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'hello'},{'id':99, 'name':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'hello'},{'id':99, 'name':'world'}]

        result = helpers.get_contacts()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'contacts', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_contacts(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'contacts', {'id': 456, 'hello': 'world'})
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.validate_contact_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_create_contact(self, parse, request, validate):
        request.return_value = {
            'data':{'id':23, 'name':'M deLaurentiis'},
            'meta': {'count': 1}
        }
        parse.return_value = {'id':23, 'name':'M deLaurentiis'}
        validate.return_value = True
        data = {'id': 999, 'name': 'M deLaurentiis'}

        result = helpers.create_contact(data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.CREATE, data)
        request.assert_called_once_with(utils.CREATE, 'contacts', None, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_contact(data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.create_contact(data)
        validate.assert_called_once_with(utils.CREATE, data)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)

    @mock.patch('%s.utils.validate_contact_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_update_contact(self, parse, request, validate):
        request.return_value = {
            'data':{'id':23, 'name':'G deLaurentiis'},
            'meta': {'count': 1}
        }
        parse.return_value = {'id':23, 'name':'G deLaurentiis'}
        validate.return_value = True
        data = {'name': 'G deLaurentiis'}
        id = 33

        result = helpers.update_contact(id, data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        request.assert_called_once_with(utils.UPDATE, 'contacts', {'id': id}, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.update_contact(id, data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.update_contact(id, data)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_deals(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'hello'},{'id':99, 'name':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'hello'},{'id':99, 'name':'world'}]

        result = helpers.get_deals()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'deals', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_deals(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'deals', {'id': 456, 'hello': 'world'})
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.validate_deal_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_create_deal(self, parse, request, validate):
        request.return_value = {
            'data':{'id':23, 'name':'Создание советской атомной бомбы'},
            'meta': {'count': 1}
        }
        parse.return_value = {'id':23, 'name':'Создание советской атомной бомбы'}
        validate.return_value = True
        data = {'id': 999, 'name': 'Создание советской атомной бомбы'}

        result = helpers.create_deal(data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.CREATE, data)
        request.assert_called_once_with(utils.CREATE, 'deals', None, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_deal(data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.create_deal(data)
        validate.assert_called_once_with(utils.CREATE, data)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)

    @mock.patch('%s.utils.validate_deal_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_update_deal(self, parse, request, validate):
        request.return_value = {
            'data':{'id':23, 'name':'Manhattan Project'},
            'meta': {'count': 1}
        }
        parse.return_value = {'id':23, 'name':'Manhattan Project'}
        validate.return_value = True
        data = {'id': 999, 'name': 'Manhattan Project'}
        id = 23

        result = helpers.update_deal(id, data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        request.assert_called_once_with(utils.UPDATE, 'deals', {'id': id}, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.update_deal(id, data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.update_deal(id, data)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)


    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_leads(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'hello'},{'id':99, 'name':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'hello'},{'id':99, 'name':'world'}]

        result = helpers.get_leads()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'leads', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_leads(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'leads', {'id': 456, 'hello': 'world'})
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.validate_lead_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_create_lead(self, parse, request, validate):
        request.return_value = {
            'data': {
                'id': 23,
                'last_name': 'Бортников',
                'organization_name': 'Федеральная Служба Безопасности Российской Федерации'
            },
            'meta': {
                'count': 1
             }
        }
        parse.return_value = {
            'id': 23,
            'last_name': 'Бортников',
            'organization_name': 'Федеральная Служба Безопасности Российской Федерации'
        }
        validate.return_value = True
        data = {
            'id': 999,
            'last_name': 'Бортников',
            'organization_name': 'Федеральная Служба Безопасности Российской Федерации'
        }

        result = helpers.create_lead(data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.CREATE, data)
        request.assert_called_once_with(utils.CREATE, 'leads', None, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_lead(data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.create_lead(data)
        validate.assert_called_once_with(utils.CREATE, data)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)

    @mock.patch('%s.utils.validate_lead_dict' % __name__)
    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_update_lead(self, parse, request, validate):
        request.return_value = {
            'data':{'id':23, 'name':'Manhattan Project'},
            'meta': {'count': 1}
        }
        parse.return_value = {'id':23, 'name':'Manhattan Project'}
        validate.return_value = True
        data = {'id': 999, 'name': 'Manhattan Project'}
        id = 23

        result = helpers.update_lead(id, data)
        self.assertEqual(result, parse.return_value)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        request.assert_called_once_with(utils.UPDATE, 'leads', {'id': id}, data=data)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = exceptions.BaseCRMValidationError()
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.update_lead(id, data)

        request.reset_mock()
        parse.reset_mock()
        validate.reset_mock()
        validate.side_effect = None
        validate.return_value = False
        result = helpers.update_lead(id, data)
        validate.assert_called_once_with(utils.UPDATE, data, skip_id=True)
        self.assertFalse(request.called)
        self.assertFalse(parse.called)

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_notes(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'content':'hello'},{'id':99, 'content':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'content':'hello'},{'id':99, 'content':'world'}]
        resource_type = 'contact'
        resource_id = 55

        result = helpers.get_notes()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'notes', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_notes(resource_type)
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'notes', {'resource_type': 'contact'})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        resource_type = 'lead'
        result = helpers.get_notes(resource_type, resource_id)
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'notes', {'resource_type': 'lead', 'resource_id': 55})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        resource_type = 'deal'
        result = helpers.get_notes(resource_type, resource_id, page=5)
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'notes', {'resource_type': 'deal', 'resource_id': 55, 'page': 5})
        parse.assert_called_once_with(request.return_value)

        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.get_notes(resource_id)

        resource_type = 'contacts'
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.get_notes(resource_type)

        resource_type = 56
        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.get_notes(resource_type)

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_create_note(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'content':'hello'},{'id':99, 'content':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'content':'hello'},{'id':99, 'content':'world'}]
        resource_type = 'contact'
        resource_id = 55
        content = "Hi, this is å t€st note"
        data = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'content': content
        }

        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_note(None, resource_id, content)

        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_note('foo', resource_id, content)

        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_note(5577, resource_id, content)

        with self.assertRaises(exceptions.BaseCRMValidationError):
            helpers.create_note(resource_type, None, content)

        result = helpers.create_note(resource_type, resource_id, content)
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.CREATE, 'notes', data=data)
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.instantiate_if_necessary' % __name__)
    @mock.patch('%s.helpers.django_apps' % __name__)
    def test_get_pipelines(self, _apps, instantiate):
        _app_conf = mock.Mock()
        _app_conf.pipeline = {'id': 6456, 'name': 'default'}
        _apps.get_app_config.return_value = _app_conf

        result = helpers.get_pipelines()
        self.assertEqual(result, _app_conf.pipeline)
        _apps.get_app_config.assert_called_once_with('django_basecrm')
        instantiate.assert_called_once()

    @mock.patch('%s.helpers.get_stages_from_api' % __name__)
    @mock.patch('%s.helpers.base_settings' % __name__)
    @mock.patch('%s.apps.BaseCRMConfig.instantiate_stages' % __name__)
    @mock.patch('%s.helpers.django_apps' % __name__)
    def test_get_stages(self, _apps, instantiate, settings, get_from_api):
        settings.BASECRM_CACHE_STAGES = True
        _app_conf = mock.Mock()
        _app_conf.stages = [{'id': 6456, 'name': 'new'}, {'id': 6577, 'name': 'updated'}]
        get_from_api.return_value = [{'id': 6993, 'name': 'won'}, {'id': 7004, 'name': 'lost'}]
        _apps.get_app_config.return_value = _app_conf

        result = helpers.get_stages()
        self.assertEqual(result, _app_conf.stages)
        _apps.get_app_config.assert_called_once_with('django_basecrm')
        instantiate.assert_called_once()
        self.assertFalse(get_from_api.called)

        settings.BASECRM_CACHE_STAGES = False
        instantiate.reset_mock()
        _apps.get_app_config.reset_mock()

        result = helpers.get_stages()
        self.assertEqual(result, get_from_api.return_value)
        self.assertFalse(_apps.get_app_config.called)
        self.assertFalse(instantiate.called)
        get_from_api.assert_called_once()

    @mock.patch('%s.helpers.get_users_from_api' % __name__)
    @mock.patch('%s.helpers.base_settings' % __name__)
    @mock.patch('%s.apps.BaseCRMConfig.instantiate_users' % __name__)
    @mock.patch('%s.helpers.django_apps' % __name__)
    def test_get_users(self, _apps, instantiate, settings, get_from_api):
        settings.BASECRM_CACHE_USERS = True
        _app_conf = mock.Mock()
        _app_conf.users = [{'id': 6456, 'name': 'Albert'}, {'id': 6577, 'name': 'Bertie'}]
        get_from_api.return_value = [{'id': 6993, 'name': 'Charlie'}, {'id': 7004, 'name': 'Davie'}]
        _apps.get_app_config.return_value = _app_conf

        result = helpers.get_users()
        self.assertEqual(result, _app_conf.users)
        _apps.get_app_config.assert_called_once_with('django_basecrm')
        instantiate.assert_called_once()
        self.assertFalse(get_from_api.called)

        settings.BASECRM_CACHE_USERS = False
        instantiate.reset_mock()
        _apps.get_app_config.reset_mock()

        result = helpers.get_users()
        self.assertEqual(result, get_from_api.return_value)
        self.assertFalse(_apps.get_app_config.called)
        self.assertFalse(instantiate.called)
        get_from_api.assert_called_once()

    @mock.patch('%s.helpers.get_stages' % __name__)
    def test_get_stage_ids(self, get_stages):
        get_stages.return_value = [{'id': 8888, 'name': 'New'}, {'id': 9999, 'name': 'In Progress'}]

        result = helpers.get_stage_ids()
        self.assertEqual(result, [8888, 9999])
        get_stages.assert_called_once()

    @mock.patch('%s.helpers.get_users' % __name__)
    def test_get_user_ids(self, get_users):
        get_users.return_value = [{'id': 8, 'name': 'Albert'}, {'id': 9, 'name': 'Berties'}]

        result = helpers.get_user_ids()
        self.assertEqual(result, [8, 9])
        get_users.assert_called_once()

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    @mock.patch('%s.utils.count' % __name__)
    def test_get_pipelines_from_api(self, count, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'hello'},{'id':99, 'name':'world'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'hello'},{'id':99, 'name':'world'}]
        count.return_value = 2

        with self.assertRaises(NotImplementedError):
            helpers.get_pipelines_from_api()
            request.assert_called_once_with(utils.RETRIEVE, 'pipelines', {})
            count.assert_called_once_with(request.return_value)

        request.reset_mock()
        count.reset_mock()
        parse.reset_mock()
        count.return_value = 1
        result = helpers.get_pipelines_from_api()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'pipelines', {})
        count.assert_called_once_with(request.return_value)
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        count.reset_mock()
        parse.reset_mock()
        result = helpers.get_pipelines_from_api(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'pipelines', {'id': 456, 'hello': 'world'})
        count.assert_called_once_with(request.return_value)
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_stages_from_api(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'new'},{'id':99, 'name':'called in'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'new'},{'id':99, 'name':'called in'}]

        result = helpers.get_stages_from_api()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'stages', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_stages_from_api(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'stages', {'id': 456, 'hello': 'world'})
        parse.assert_called_once_with(request.return_value)

    @mock.patch('%s.utils.request' % __name__)
    @mock.patch('%s.utils.parse' % __name__)
    def test_get_users_from_api(self, parse, request):
        request.return_value = {
            'items':[{'id':23, 'name':'Albert'},{'id':99, 'name':'Bertie'}],
            'meta': {'count': 2}
        }
        parse.return_value = [{'id':23, 'name':'Albert'},{'id':99, 'name':'Bertie'}]

        result = helpers.get_users_from_api()
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'users', {})
        parse.assert_called_once_with(request.return_value)

        request.reset_mock()
        parse.reset_mock()
        result = helpers.get_users_from_api(id=456, hello='world')
        self.assertEqual(result, parse.return_value)
        request.assert_called_once_with(utils.RETRIEVE, 'users', {'id': 456, 'hello': 'world'})
        parse.assert_called_once_with(request.return_value)


class SerializerTests(TestCase):

    def setUp(self):
        self.instance = mock.Mock(spec=ModelBase)
        class ExampleAbstractSerializer(serializers.AbstractModelSerializer):
            base_fields = []
            class Meta:
                model = self.instance.__class__
                fields = [
                    'dummy',
                    'another'
                ]
        class ExampleContactSerializer(serializers.ContactModelSerializer):
            class Meta:
                model = self.instance.__class__
        class ExampleDealSerializer(serializers.DealModelSerializer):
            class Meta:
                model = self.instance.__class__
        self.serialized_abstract_object = ExampleAbstractSerializer(self.instance)
        self.serialized_contact = ExampleContactSerializer(self.instance)
        self.serialized_deal = ExampleDealSerializer(self.instance)
        self.ExampleContactSerializer = ExampleContactSerializer
        self.ExampleDealSerializer = ExampleDealSerializer

    @mock.patch('%s.serializers.AbstractModelSerializer._self_assign_values' % __name__)
    def test_init(self, assign):
        self.assertTrue(hasattr(self.serialized_abstract_object, 'instance'))
        self.assertTrue(hasattr(self.serialized_abstract_object, 'base_fields'))
        self.assertTrue(hasattr(self.serialized_abstract_object, 'read_only_fields'))
        self.assertTrue(hasattr(self.serialized_abstract_object.Meta, 'model'))
        self.assertTrue(hasattr(self.serialized_abstract_object.Meta, 'fields'))

        self.assertEqual(self.serialized_abstract_object.instance, self.instance)
        self.assertEqual(self.serialized_abstract_object.base_fields, [])
        self.assertEqual(self.serialized_abstract_object.read_only_fields, None)
        self.assertEqual(self.serialized_abstract_object.Meta.model, self.instance.__class__)
        self.assertEqual(self.serialized_abstract_object.Meta.fields, ['dummy', 'another'])

        assign.assert_called_once()

    def test_to_dict(self):
        self.instance.name = 'Acme Enterprises Inc.'
        class ExampleOrganizationSerializer(self.ExampleContactSerializer):
            is_organization = False

        serialized_organization = ExampleOrganizationSerializer(self.instance)
        result = serialized_organization.to_dict()

        self.assertEqual(result, {
            'is_organization': False,
            'name': 'Acme Enterprises Inc.'
        })

    @mock.patch('%s.serializers.AbstractModelSerializer._get_field_list' % __name__)
    @mock.patch('%s.serializers.AbstractModelSerializer._get_value' % __name__)
    def test_self_assign_values(self, get_value, get_fields):
        get_fields.return_value = ['id', 'name']
        get_value.side_effect = ['Albert Einstein']
        self.assertEqual(self.ExampleContactSerializer.read_only_fields, ['id'])
        serialized_contact = self.ExampleContactSerializer(self.instance)

        self.assertFalse(hasattr(serialized_contact, 'id'))
        self.assertTrue(hasattr(serialized_contact, 'name'))
        self.assertEqual(serialized_contact.name, 'Albert Einstein')
        get_fields.assert_called_once()
        get_value.assert_called_once_with('name')

        get_fields.reset_mock()
        get_value.reset_mock()
        get_fields.return_value = ['id', 'name', 'is_organization', 'is_deceased']
        get_value.side_effect = ['John von Neumann', False, None]
        serialized_contact = self.ExampleContactSerializer(self.instance)

        self.assertFalse(hasattr(serialized_contact, 'id'))
        self.assertTrue(hasattr(serialized_contact, 'name'))
        self.assertEqual(serialized_contact.name, 'John von Neumann')
        self.assertTrue(hasattr(serialized_contact, 'is_organization'))
        self.assertEqual(serialized_contact.is_organization, False)
        self.assertFalse(hasattr(serialized_contact, 'is_deceased'))
        get_fields.assert_called_once()
        self.assertEqual(get_value.call_count, 3)

    def test_get_field_list(self):
        class BaseFieldAbstractSerializer(serializers.AbstractModelSerializer):
            base_fields = [
                'test',
                'another',
                'third'
            ]
            class Meta:
                model = self.instance.__class__
        class MetaFieldAbstractSerializer(serializers.AbstractModelSerializer):
            base_fields = [
                'test',
                'another',
                'third'
            ]
            class Meta:
                model = self.instance.__class__
                fields = [
                    'meta_test',
                    'test_meta',
                    'another_test'
                ]

        base_serialized = BaseFieldAbstractSerializer(self.instance)
        meta_serialized = MetaFieldAbstractSerializer(self.instance)
        results = base_serialized._get_field_list()
        self.assertEqual(
            results,
            [
                'test',
                'another',
                'third'
            ]
        )
        results = meta_serialized._get_field_list()
        self.assertEqual(
            results,
            [
                'meta_test',
                'test_meta',
                'another_test'
            ]
        )

    def test_get_value(self):
        class TestSerializer(self.ExampleContactSerializer):
            is_organization = False
            name = 'Test'
            phone = 'phone'
            email = 'email'
            description = 'desc'

            def get_hot(self, obj):
                return obj.am_i_hot_today

            class Meta:
                model = self.instance.__class__
                fields = [
                    'is_organization',
                    'name',
                    'phone',
                    'email',
                    'hot',
                    'description',
                    'custom_field',
                    'extra_field'
                ]

        self.instance.name = "Not Test"
        self.instance.desc = "Test description"
        self.instance.email = "test@domain.com"
        self.instance.am_i_hot_today = True
        self.instance.custom_field = 'test value'
        self.instance.phone = mock.Mock()
        self.instance.phone.return_value = "0208555888"
        self.instance.phone.__class__ = types.MethodType
        serialized = TestSerializer(self.instance)

        # Fields that don't exist
        with self.assertRaises(TypeError):
            serialized._get_value(87)

        result = serialized._get_value('not_existing')
        self.assertEqual(result, None)

        # fields that are configured but not on instance
        result = serialized._get_value('extra_field')
        self.assertEqual(result, None)

        # Instance attributes / properties
        result = serialized._get_value('email')
        self.assertEqual(result, "test@domain.com")

        # ... and one with a non-identically named field mapping
        result = serialized._get_value('description')
        self.assertEqual(result, "Test description")

        # ... and one that isn't specified
        result = serialized._get_value('custom_field')
        self.assertEqual(result, "test value")

        # Instance methods
        result = serialized._get_value('phone')
        self.assertEqual(result, "0208555888")
        self.instance.phone.assert_called_once()

        # Class level values
        result = serialized._get_value('is_organization')
        self.assertFalse(result)

        # ... overridden by instance values
        result = serialized._get_value('name')
        self.assertEqual(result, "Not Test")

        # Class level get_ methods
        result = serialized._get_value('hot')
        self.assertTrue(result)

    def test_contact_fields(self):
        self.assertTrue(hasattr(self.serialized_contact, 'instance'))
        self.assertTrue(hasattr(self.serialized_contact, 'base_fields'))
        self.assertTrue(hasattr(self.serialized_contact, 'read_only_fields'))
        self.assertTrue(hasattr(self.serialized_contact.Meta, 'model'))

        self.assertEqual(self.serialized_contact.instance, self.instance)
        self.assertEqual(self.serialized_contact.base_fields, [
            'id',
            'owner_id',
            'is_organization',
            'contact_id',
            'name',
            'first_name',
            'last_name',
            'customer_status',
            'prospect_status',
            'title',
            'description',
            'industry',
            'website',
            'email',
            'phone',
            'mobile',
            'fax',
            'twitter',
            'facebook',
            'linkedin',
            'skype',
            'address',
            'tags',
            'custom_fields',
        ])
        self.assertEqual(self.serialized_contact.read_only_fields, ['id'])
        self.assertEqual(self.serialized_contact.Meta.model, self.instance.__class__)

    def test_deal_fields(self):
        self.assertTrue(hasattr(self.serialized_deal, 'instance'))
        self.assertTrue(hasattr(self.serialized_deal, 'base_fields'))
        self.assertTrue(hasattr(self.serialized_deal, 'read_only_fields'))
        self.assertTrue(hasattr(self.serialized_deal.Meta, 'model'))

        self.assertEqual(self.serialized_deal.instance, self.instance)
        self.assertEqual(self.serialized_deal.base_fields, [
            'id',
            'owner_id',
            'name',
            'value',
            'currency',
            'hot',
            'stage_id',
            'source_id',
            'loss_reason_id',
            'dropbox_email',
            'contact_id',
            'organization_id',
            'tags',
            'custom_fields',
        ])
        self.assertEqual(self.serialized_deal.read_only_fields, ['id', 'organization_id'])
        self.assertEqual(self.serialized_deal.Meta.model, self.instance.__class__)

    def test_validate_field(self):
        result = self.serialized_abstract_object._validate_field('any', 'val')
        self.assertTrue(result)

    @mock.patch('%s.serializers.base_helpers' % __name__)
    def test_contact_validate_field(self, helpers):
        helpers.get_user_ids.return_value = [111, 222, 333, 444]

        result = self.serialized_contact._validate_field('any', True)
        self.assertTrue(result)

        result = self.serialized_contact._validate_field('owner_id', None)
        self.assertTrue(result)

        result = self.serialized_contact._validate_field('owner_id', True)
        self.assertFalse(result)

        result = self.serialized_contact._validate_field('owner_id', 777)
        self.assertFalse(result)

        result = self.serialized_contact._validate_field('owner_id', 444)
        self.assertTrue(result)

    @mock.patch('%s.serializers.base_helpers' % __name__)
    def test_deal_validate_field(self, helpers):
        helpers.get_user_ids.return_value = [111, 222, 333, 444]
        helpers.get_stage_ids.return_value = [666, 777, 888, 999]

        result = self.serialized_deal._validate_field('any', True)
        self.assertTrue(result)

        result = self.serialized_deal._validate_field('owner_id', None)
        self.assertTrue(result)

        result = self.serialized_deal._validate_field('owner_id', True)
        self.assertFalse(result)

        result = self.serialized_deal._validate_field('owner_id', 777)
        self.assertFalse(result)

        result = self.serialized_deal._validate_field('owner_id', 444)
        self.assertTrue(result)

        result = self.serialized_deal._validate_field('owner_id', None)
        self.assertTrue(result)

        result = self.serialized_deal._validate_field('stage_id', True)
        self.assertFalse(result)

        result = self.serialized_deal._validate_field('stage_id', 444)
        self.assertFalse(result)

        result = self.serialized_deal._validate_field('stage_id', 777)
        self.assertTrue(result)


class AppMethodTests(TestCase):

    def setUp(self):
        self.base_app = django_apps.get_app_config('django_basecrm')
        self.base_app.users = None
        self.base_app.stages = None
        self.base_app.pipeline = None

    @mock.patch('%s.apps.base_settings' % __name__)
    @mock.patch('%s.apps.BaseCRMConfig.instantiate_objects' % __name__)
    def test_ready(self, instantiate_objects, settings):
        settings.BASECRM_CACHE_AT_STARTUP = False
        result = self.base_app.ready()
        self.assertFalse(instantiate_objects.called)

        settings.BASECRM_CACHE_AT_STARTUP = True
        result = self.base_app.ready()
        instantiate_objects.assert_called_once()

    @mock.patch('%s.apps.get_pipelines_from_api' % __name__)
    def test_instantiate_pipeline(self, get_pipelines):
        get_pipelines.return_value = [{'id': 'one'}, {'id': 'two'}, {'id': 'three'}]
        self.assertEqual(self.base_app.pipeline, None)

        self.base_app.instantiate_pipeline()
        self.assertEqual(self.base_app.pipeline, {'id': 'one'})
        get_pipelines.assert_called_once()

        get_pipelines.return_value = {'id': 'two'}

        # get from cache
        self.base_app.instantiate_pipeline()
        self.assertEqual(self.base_app.pipeline, {'id': 'one'})
        self.assertEqual(get_pipelines.call_count, 1)

        # force get from API
        self.base_app.instantiate_pipeline(True)
        self.assertEqual(self.base_app.pipeline, {'id': 'two'})
        self.assertEqual(get_pipelines.call_count, 2)

        get_pipelines.return_value = [{'id': 'four'}, {'id': 'three'}]

        # confim only one pipeline kept
        self.base_app.instantiate_pipeline(True)
        self.assertEqual(self.base_app.pipeline, {'id': 'four'})

    @mock.patch('%s.apps.get_stages_from_api' % __name__)
    def test_instantiate_stages(self, get_stages):
        get_stages.return_value = ['A', 'B', 'C']
        self.assertEqual(self.base_app.stages, None)

        self.base_app.instantiate_stages()
        self.assertEqual(self.base_app.stages, ['A', 'B', 'C'])
        get_stages.assert_called_once()

        get_stages.return_value = ['D', 'E', 'F']

        # get from cache
        self.base_app.instantiate_stages()
        self.assertEqual(self.base_app.stages, ['A', 'B', 'C'])
        self.assertEqual(get_stages.call_count, 1)

        # force get from API
        self.base_app.instantiate_stages(True)
        self.assertEqual(self.base_app.stages, ['D', 'E', 'F'])
        self.assertEqual(get_stages.call_count, 2)

        get_stages.reset_mock()
        self.base_app.stages = None
        self.base_app.pipeline = {'id': 99999}
        self.base_app.instantiate_stages(True)
        get_stages.assert_called_once_with(pipeline_id=99999)

    @mock.patch('%s.apps.get_users_from_api' % __name__)
    def test_instantiate_users(self, get_users):
        get_users.return_value = [1, 2, 3]
        self.assertEqual(self.base_app.users, None)

        self.base_app.instantiate_users()
        self.assertEqual(self.base_app.users, [1, 2, 3])
        get_users.assert_called_once()

        get_users.return_value = [1, 55, 77]

        # get from cache
        self.base_app.instantiate_users()
        self.assertEqual(self.base_app.users, [1, 2, 3])
        self.assertEqual(get_users.call_count, 1)

        # force get from API
        self.base_app.instantiate_users(True)
        self.assertEqual(self.base_app.users, [1, 55, 77])
        self.assertEqual(get_users.call_count, 2)

    @mock.patch('%s.apps.BaseCRMConfig.instantiate_stages' % __name__)
    @mock.patch('%s.apps.BaseCRMConfig.instantiate_pipeline' % __name__)
    @mock.patch('%s.apps.BaseCRMConfig.instantiate_users' % __name__)
    def test_instantiate_objects(self, get_users, get_pipelines, get_stages):
        self.base_app.instantiate_objects()
        get_pipelines.assert_called_once()
        get_stages.assert_called_once()
        get_users.assert_called_once()

        get_pipelines.reset_mock()
        get_stages.reset_mock()
        get_users.reset_mock()

        self.base_app.instantiate_objects(True)
        get_pipelines.assert_called_once_with(True)
        get_stages.assert_called_once_with(True)
        get_users.assert_called_once_with(True)
