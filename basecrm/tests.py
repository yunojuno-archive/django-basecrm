# -*- coding: utf-8 -*-
"""Tests for the basecrm library."""
import unittest
import os

# Base API token - available from
BASECRM_TOKEN = os.environ.get('BASECRM_TOKEN')


class TestAuth(unittest.TestCase):

    """Tests for the API authentication."""

    def test_basic_auth(self):
        """Check the auth request header is set."""
        self.fail("Write me")


class TestContacts(unittest.TestCase):

    """Tests for the Contacts API."""

    def test_create_contact(self):
        """Create a new contact."""
        self.fail("Write me")

    def test_update_contact(self):
        """Update an existing contact."""
        self.fail("Write me")

    def test_delete_contact(self):
        """Delete an existing contact."""
        self.fail("Write me")

    def test_delete_non_existant_contact(self):
        """Delete a non-existant contact."""
        self.fail("Write me")

    def test_create_duplicate_contact(self):
        """Create a duplicate contact."""
        self.fail("Write me")
