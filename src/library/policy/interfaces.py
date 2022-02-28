# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from collective.faceted.map.interfaces import ICollectiveFacetedMapLayer
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable

class ILibraryPolicyLayer(ICollectiveFacetedMapLayer, IFacetedNavigable):
    """Marker interface that defines a browser layer."""
