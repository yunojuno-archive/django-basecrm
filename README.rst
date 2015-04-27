Django-BaseCRM
==============

> A Django app that connects to the BaseCRM API (v2)

[![Build Status](https://travis-ci.org/yunojuno/django-basecrm.svg)](https://travis-ci.org/yunojuno/django-basecrm)

A lightweight Django app to wrap the [requests](http://docs.python-requests.org/en/latest/) library and provide easy endpoints for the BaseCRM API.

Note that this is not a __complete__ client SDK; it's a helper app that has the functionality we needed. Contributions gratefully accepted.

The `utils` module provides a `request()` method that allows less config-heavy calls to the BaseCRM API, relying on settings while still allowing all options to be passed and/or overridden, both for `requests` and for the API endpoint itself. There are also helpers to `parse()` and `count()` the results (`parse` strips the metadata, while `count` returns the server-side count pre pagination).

The `helpers` module also provides some higher level methods for interacting with the `contacts`, `deals`, `pipeline` and `stages` endpoints (and the top level `__init__` module exposes these). There's also a setting for retrieving and caching the stages for a pipeline (only 1 supported currently).

Features
--------

* Low configuration overhead, so it's easy to call API methods from anywhere in your code
* Pre-submission validation for `CREATE` and `UPDATE` calls will raise catchable custom exceptions
* Flexible serializers make creating BaseCRM objects from Django ORM objects trivial

Current Limitations
-------------------

* Currently only built to work with Django, but removing the Django dependencies should be trivial :)
* Only a single pipeline is currently supported.
* Stages and pipelines are, by default, cached at the app level (in memory), with no cachebusting method exposed.
* No `DELETE` calls are implemented
* `CREATE` and `UPDATE` are only implemented on `contacts` and `deals` endpoints
* `GET` is only implemented for `contacts`, `deals`, `notes`, `pipelines` and `stages`
* Serializers are only used one-way; they do not deserialize
* Probably many others...

Installation
------------
```python
pip install --upgrade django-basecrm
```

Setup
-----
At a minimum, you will need to add the following to your `settings.py`:
```python
BASECRM_API_URL=https://api.getbase.com/v2/
BASECRM_API_KEY=xxxx
BASECRM_INSTANTIATE_ON_START=False # If this is set to True, the pipeline ID and stage IDs will be retrieved when the app is started for the first time, and then held in memory
```
...putting your own API key instead of `xxx`, obv. Note that we're not using strings, and the API url is fully qualified, including __the protocol__ and __trailing slash__.

You'll also need to add this app to your `INSTALLED_APPS`; it doesn't really matter where (in terms of ordering):
```python
INSTALLED_APPS = [
    ...
    'django_basecrm',
    ...
]
```
Next, you'll probably want to extend the serializers to cater for your models.

For example, let's imagine you have an app called `people` that contains a your custom `User` profile model called `Person`, that represents the contacts you want to track in Base.

Let's also imagine that your model has an attribute for `info`, a `@property` for `phone` and a OneToOne relationship with `User`.

Create `people/serializers.py` and paste the following code:
```python
from django_basecrm import get_contacts, create_contact
from django_basecrm.serializers import ContactModelSerializer

class PersonSerializer(ContactModelSerializer):
    is_organization = False
    description = 'info'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = 'people.Person'
```
Things to note:

* We're extending `ContactModelSerializer`; there's also a `DealModelSerializer` that behaves identically but is set for the `deal` endpoint's fields
* We set the `is_organization` field to `False` explicitly; assuming your model doesn't have a field (or property) with the same name, this will never be automatically overridden.
* The `description` field is set to get the value of your object's `info` field at runtime
* The `phone` field will similarly get the value of your object's `phone` property at runtime; we don't need to specify it as the fields are identically named
* The `email` field, although not explicitly defined, will be populated by the return value of the `get_email` method. Any `get_*` method will always take priority in setting the serializer value for the related field.
* The Meta.model attribute is set to a string, __contianing both the app_name and the model_name__ -- any other string format will fail. It is however possible to specify a class directly (e.g. `model = Person`).
* Note that you can also specify `fields` as an attribute to the Meta subclass; this will override the serializer's list of fields

Once you've got this far, you really only need to call the functions, perhaps creating a module within your `people` app to offer `create_person_from_object` methods and the like.

An example `get_or_create` function for a BaseCRM contact, using the above models and serializers, might look like:
```python
def get_or_create_person(person_id):
    person = Person.objects.get(pk=person_id)
    base_contacts = django_basecrm.get_contacts(email=person.user.email))
    if len(base_contacts) > 1:
        # This shouldn't happen if we enforce email uniqueness in Django
        raise Exception()
    elif len(base_contacts) == 1:
        base_contact = base_contacts[0]
    else:
        serialized_person = PersonSerializer(person) # This is the serializer we defined above
        base_contact = django_basecrm.create_contact(serialized_person.to_dict())
    return base_contact
```

Contribute
----------

Contributions are very welcome. Please fork and submit pull requests, with all code covered by unit tests as per the existing code.
