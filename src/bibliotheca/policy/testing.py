# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.globalrequest import setRequest

import bibliotheca.policy


class BibliothecaPolicyLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=bibliotheca.policy)

    def setUpPloneSite(self, portal):
        request = portal.REQUEST
        setRequest(request)
        request["LANGUAGE"] = "en"
        applyProfile(portal, "bibliotheca.policy:default")


BIBLIOTHECA_POLICY_FIXTURE = BibliothecaPolicyLayer()


BIBLIOTHECA_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BIBLIOTHECA_POLICY_FIXTURE,),
    name="BibliothecaPolicyLayer:IntegrationTesting",
)


BIBLIOTHECA_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIBLIOTHECA_POLICY_FIXTURE,),
    name="BibliothecaPolicyLayer:FunctionalTesting",
)


BIBLIOTHECA_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        BIBLIOTHECA_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="BibliothecaPolicyLayer:AcceptanceTesting",
)
