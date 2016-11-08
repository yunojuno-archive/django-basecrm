# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class BaseCRMAPIUnauthorized(Exception):
    default_detail = _(u'Required access token is missing, malformed, expired, or invalid.')

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail


class BaseCRMBadParameterFormat(Exception):
    default_detail = _(
        u'Parameter format was not as expected: a full dict from the requests.json() '
        u'method applied to the full BaseCRM API response'
    )

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail


class BaseCRMValidationError(Exception):
    default_detail = _(
        u'Parameters fail BaseCRM API requirements'
    )

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail


class BaseCRMConfigurationError(Exception):
    default_detail = _(
        u'Configuration is not valid'
    )

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail


class BaseCRMUnexpectedResult(Exception):
    default_detail = _(
        u'Expected a different result format'
    )

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail


class BaseCRMNoResult(Exception):
    default_detail = _(
        u'No results exist for the given query'
    )

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

    def __str__(self):
        return self.detail
