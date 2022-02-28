# -*- coding: utf-8 -*-
from collective.faceted.map.browser.view import FacetedGeoJSON as fgj
from plone import api
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class FacetedGeoJSON(fgj):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.vocabulary = get_vocabulary("collective.taxonomy.dossiers")

    def _generate_point(self, brain):
        catalog = api.portal.get_tool(name="portal_catalog")
        data = catalog.getIndexDataForRID(brain.getRID())
        if data.get("longitude") and data.get("latitude"):
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [data["longitude"], data["latitude"]],
                },
                "id": brain.id,
                "properties": {
                    "popup": self._template(brain),
                    "color": self.color(brain),
                },
            }

    # https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css
    def color(self, brain):
        colors = {
            "01": "blue",
            "02": "orange",
            "03": "darkred",
            "04": "red",
            "05": "gray",
            "06": "white",
            "07": "beige",
            "08": "cadetblue",
            "09": "pink",
            "10": "lightgray",
            "11": "darkgreen",
            "12": "green",
            "13": "darkblue",
            "14": "lightred",
            "15": "lightgreen",
            "16": "purple",
            "17": "darkpurple",
        }
        obj = brain.getObject()
        if not obj.taxonomy_dossiers:
            return
        token = obj.taxonomy_dossiers[0]
        taxo_label = self.vocabulary.inv_data.get(token)
        lazy_chars = taxo_label[: taxo_label.find(".")][-2:]
        if lazy_chars in [c for c, v in colors.items()]:
            return colors[lazy_chars]
        return


def get_vocabulary(voc_name):
    factory = getUtility(IVocabularyFactory, voc_name)
    vocabulary = factory(api.portal.get())
    return vocabulary
