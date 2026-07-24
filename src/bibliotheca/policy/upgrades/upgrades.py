# -*- coding: utf-8 -*-

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.layout import FacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from bibliotheca.policy.setuphandlers import configure_login_modal
from bibliotheca.policy.utils import configure_faceted
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import get_installer

import logging
import os

logger = logging.getLogger("bibliotheca.policy")


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        "profile-bibliotheca.policy:default",
    )


# silly : default_language = fr
# root and folders are fr-be !
def change_language(context):
    pl = api.portal.get_tool("portal_languages")
    default_language = pl.getDefaultLanguage()
    root = api.portal.get()
    brains = api.content.find(root)
    for brain in brains:
        obj = brain.getObject()
        if obj.language != default_language:
            obj.language = default_language
    root.language = default_language


def configure_faceted(context):
    pass


def upgrade_1004_to_1005(context):
    setup_tool = getToolByName(context, "portal_setup")
    setup_tool.runAllImportStepsFromProfile("profile-collective.plausible:default")


def uninstall_z3cform_select2(context):
    installer = get_installer(context)
    installer.uninstall_product("collective.z3cform.select2")


def update_faceted_folders(context):
    brains = api.content.find(portal_type="Folder")
    for brain in brains:
        obj = brain.getObject()
        if not IFacetedNavigable.providedBy(obj):
            continue
        criteria_handler = ICriteria(obj)
        criteria = criteria_handler.criteria
        for criterion in criteria:
            if criterion.widget == "select2" or criterion.widget == "multiselect":
                criterion.update(widget="multiselect", placeholder=criterion.title)
        criteria_handler._update(criteria)


def update_faceted_layout(context):
    brains = api.content.find(object_provides=IFacetedNavigable)
    for brain in brains:
        obj = brain.getObject()
        layout = FacetedLayout(obj)
        layout.update_layout(layout="faceted-map")


def set_banner_scale(context=None):
    # Set the default scale for the banner
    api.portal.set_registry_record(
        "collective.behavior.banner.browser.controlpanel.IBannerSettingsSchema.banner_scale",
        "banner",
    )


def uninstall_plone_patternslib(context):
    installer = get_installer(context)
    installer.uninstall_product("plone.patternslib")


def uninstall_library_theme(context):
    installer = get_installer(context)
    installer.uninstall_product("library.theme")


def install_kimug(context):
    setup_tool = getToolByName(context, "portal_setup")
    setup_tool.runAllImportStepsFromProfile("profile-pas.plugins.kimug:default")


def set_login_modal(context):
    portal = api.portal.get()
    configure_login_modal(portal)


def fix_library_rename(context):
    """Clean up persisted references to the old ``library.*`` package names.

    The add-ons were renamed ``library.*`` -> ``bibliotheca.*``. Sites created
    before the rename still hold, in the ZODB, references to the now
    unimportable dotted names, which breaks:

    * the ``patrimoine`` FTI ``schema`` string
      (``library.core.content.patrimoine.IPatrimoine``) -> RecursionError on
      ``lookupSchema`` because the fallback dynamic schema lookup loops;
    * the ``plone.browserlayer`` local utilities registered for
      ``ILibraryCoreLayer`` / ``ILibraryPolicyLayer`` -> startup warnings.

    It also (re)registers the renamed ``IBibliothecaCoreLayer`` /
    ``IBibliothecaPolicyLayer`` browser layers, which were never installed in
    ``library.*``-era sites; without them every view/viewlet/tile bound to
    those layers (e.g. the ``existingcontent`` standard tile) 404s.
    """
    old_prefix = "library."
    new_prefix = "bibliotheca."
    portal = api.portal.get()
    setup_tool = api.portal.get_tool("portal_setup")

    # 1. Rewrite stale FTI schema / model_source strings.
    ptypes = api.portal.get_tool("portal_types")
    fixed_types = []
    for type_id in ptypes.objectIds():
        fti = ptypes[type_id]
        for attr in ("schema", "model_source"):
            value = getattr(fti, attr, None)
            if value and old_prefix in value:
                setattr(fti, attr, value.replace(old_prefix, new_prefix))
                fixed_types.append(type_id)

    # 2. Invalidate the Dexterity schema cache so corrected schemas re-resolve.
    try:
        from plone.dexterity.schema import SCHEMA_CACHE

        for type_id in fixed_types:
            SCHEMA_CACHE.invalidate(type_id)
        SCHEMA_CACHE.clear()
    except Exception:  # pragma: no cover - best effort
        logger.exception(
            "fix_library_rename: failed to invalidate the Dexterity "
            "schema cache for types %r; continuing upgrade.",
            fixed_types,
        )

    # 3. Purge the orphaned (Broken) browser-layer utilities.
    from plone.browserlayer.interfaces import ILocalBrowserLayerType

    sm = portal.getSiteManager()
    for reg in list(sm.registeredUtilities()):
        if reg.provided is not ILocalBrowserLayerType:
            continue
        iface = reg.component
        module = getattr(iface, "__module__", "") or ""
        name = getattr(iface, "__name__", "") or reg.name or ""
        if module.startswith(old_prefix) or name.startswith("ILibrary"):
            sm.unregisterUtility(
                component=iface,
                provided=ILocalBrowserLayerType,
                name=reg.name,
            )

    # 4. Register the renamed browser layers (never installed in library.*-era
    #    sites). Idempotent: re-importing browserlayer.xml is a no-op if present.
    for profile in (
        "profile-bibliotheca.core:default",
        "profile-bibliotheca.policy:default",
    ):
        setup_tool.runImportStepFromProfile(profile, "browserlayer")
