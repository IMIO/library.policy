# -*- coding: utf-8 -*-
"""Setup tests for this package."""

from bibliotheca.policy.testing import BIBLIOTHECA_POLICY_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that bibliotheca.policy is properly installed."""

    layer = BIBLIOTHECA_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if bibliotheca.policy is installed."""
        self.assertTrue(self.installer.is_product_installed("bibliotheca.policy"))

    def test_browserlayer(self):
        """Test that IBibliothecaPolicyLayer is registered."""
        from bibliotheca.policy.interfaces import IBibliothecaPolicyLayer
        from plone.browserlayer import utils

        self.assertIn(IBibliothecaPolicyLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = BIBLIOTHECA_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("bibliotheca.policy")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if bibliotheca.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("bibliotheca.policy"))

    def test_browserlayer_removed(self):
        """Test that IBibliothecaPolicyLayer is removed."""
        from bibliotheca.policy.interfaces import IBibliothecaPolicyLayer
        from plone.browserlayer import utils

        self.assertNotIn(IBibliothecaPolicyLayer, utils.registered_layers())
