#!/usr/bin/env python
#
# This file exists because we don't have an actual Django app here, hence no manage.py
import os
import django
import nose

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
django.setup()
nose.main()