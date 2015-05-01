# -*- coding: utf-8 -*-
import types

from django.apps import apps
from django.db.models.base import ModelBase
from django.db.models.loading import get_model

from . import (
    utils as base_api,
    exceptions as base_exceptions,
    settings as base_settings
)


class AbstractModelSerializer(object):
    """
    A helper for defining which attributes and properties of Django ORM models map to which BaseCRM
    fields. This is extended and used by concrete serializers below.
    """
    instance = None
    base_fields = None
    read_only_fields = None

    def __init__(self, instance, *args, **kwargs):
        """
        Checks this (extended) class has set the basics correctly, and triggers the value assignment
        """
        if self.Meta.model is None:
            raise base_exceptions.BaseCRMConfigurationError(
                "ModelSerializer must be defined with the relevant model on the Meta inner class"
            )
        if isinstance(self.Meta.model, basestring):
            try:
                self.Meta.model = get_model ( *self.Meta.model.split('.',1) )
            except:
                raise base_exceptions.BaseCRMConfigurationError(
                    "The model on the Meta inner class could not be derived from the string given"
                )
        if not isinstance(instance, self.Meta.model):
            raise base_exceptions.BaseCRMConfigurationError(
                "Initialise serializer with an instance of type model (as defined in Meta class)"
            )
        self.instance = instance
        self._self_assign_values()

    def to_dict(self):
        """
        Creates a dict of the self-set values
        """
        output = {}
        for f in self._get_field_list():
            val = getattr(self, f, None)
            if val is not None:
                output[f] = val

        return output

    def _self_assign_values(self):
        """
        Assigns values to internal attributes, based on the instance values and falling back to
        values defined at class level. Will also call callables where appropriate.
        """
        for f in self._get_field_list():
            if (
                self.read_only_fields is None or
                (
                    self.read_only_fields is not None and
                    f not in self.read_only_fields
                )
            ):
                instance_val = self._get_value(f)
                if instance_val is not None:
                    setattr(self, f, instance_val)

    def _get_field_list(self):
        """
        If the Meta.fields list is not None we'll use that, otherwise we'll use the list defined
        at class level
        """
        if hasattr(self.Meta, 'fields') and self.Meta.fields is not None:
            fields = self.Meta.fields
        else:
            fields = self.base_fields
        return fields

    def _get_value(self, field_name):
        """
        Gets the value of the field to be assigned to this instance.

        First sees whether the field has a get_X function (where X is the BaseCRM field name) and if
        so, runs it to derive the value from there.

        If that doesn't exist, we check whether the value is specified on this class and if so,
        assign that (calling the method if applicable) -- if not, we see whether the instance has
        an identically-named field and we fall back to the value of that.
        """
        if hasattr(self, 'get_%s' % field_name):
            # we've got a custom method defined to return the value
            val_function = getattr(self, 'get_%s' % field_name)
            val = val_function(self.instance)
        else:
            val = getattr(self.instance, field_name, None)
            if val is not None:
                # it's specified on the instance
                if (
                    isinstance(val, types.FunctionType) or
                    isinstance(val, types.MethodType)
                ):
                    # it's a callable: assign the result
                    val = val()  # note this can easily raise errors - no params sent!
            else:
                # try to get one from the class level
                val = getattr(self, field_name, None)
                if val is not None and isinstance(val, basestring):
                    # it's a string - let's check if it's a field mapping
                    instance_val = getattr(self.instance, val, None)
                    if instance_val is not None:
                        # let's use the mapped value from the instance
                        val = instance_val

        # confirm that whatever we've ended up with is safe to set
        if self._validate_field(field_name, val):
            return val
        else:
            return None

    def _validate_field(self, field_name, field_value):
        """
        Ensures that e.g. owner_id value set is valid for this account; setting an invalid one can
        break the integration as BaseCRM API does not handle this gracefully.

        This abstract method exists to be overridden on concrete serializers
        """
        return True


    class Meta(object):
        model = None
        fields = None


class ContactModelSerializer(AbstractModelSerializer):
    """
    Extends AbstractSerializer. The list of BaseCRM fields for Contact objects exposed via the API
    is visible here: https://developers.getbase.com/docs/rest/reference/contacts
    """
    base_fields = [
        'id',  # BaseCRM ID, read-only
        'owner_id',  # BaseCRM user_id of staffmember assigned to this contact
        'is_organization',
        'contact_id',  # If individual, the ID of the associated organization
        'name',  # Required if is_organization = True
        'first_name',  # Required if is_organization = False
        'last_name',  # Required if is_organization = False
        'customer_status',  # can be 'none', 'current', 'past'
        'prospect_status',  # can be 'none', 'current', 'lost'
        'title',  # job title
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
        'address',  # this is a nested object (dict) with the following keys: 'city', 'country', 'line1', 'postal_code' and 'state'
        'tags',
        'custom_fields',
    ]
    read_only_fields = [
        'id'
    ]

    def _validate_field(self, field_name, field_value):
        if field_value is None:
            return True

        if field_name == 'owner_id' and field_value not in base_api.get_user_ids():
            return False

        return super(ContactModelSerializer, self)._validate_field(field_name, field_value)


class DealModelSerializer(AbstractModelSerializer):
    """
    Extends AbstractSerializer. The list of BaseCRM fields for Deal objects exposed via the API
    is visible here: https://developers.getbase.com/docs/rest/reference/deals
    """
    base_fields = [
        'id',  # BaseCRM ID, read-only
        'owner_id',  # BaseCRM user_id of staffmember assigned to this contact
        'name',  # Write-only
        'value',
        'currency',
        'hot',  # Boolean "is it hot?"
        'stage_id',
        'source_id',
        'loss_reason_id',
        'dropbox_email',
        'contact_id',
        'organization_id',  # read-only
        'tags',
        'custom_fields',
    ]
    read_only_fields = [
        'id',
        'organization_id'
    ]

    def _validate_field(self, field_name, field_value):
        if field_value is None:
            return True

        if field_name == 'owner_id' and field_value not in base_api.get_user_ids():
            return False

        if field_name == 'stage_id' and field_value not in base_api.get_stage_ids():
            return False

        return super(DealModelSerializer, self)._validate_field(field_name, field_value)
