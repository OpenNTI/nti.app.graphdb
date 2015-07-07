#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.catalog.interfaces import ICatalog

from zope.intid import IIntIds

from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.dataserver.metadata_index import IX_CREATOR
from nti.dataserver.metadata_index import CATALOG_NAME as METADATA_CATALOG_NAME

from nti.zodb import isBroken

def all_cataloged_objects(users=()):
    intids = component.getUtility(IIntIds)
    catalog = component.getUtility(ICatalog, METADATA_CATALOG_NAME)
    usernames = {getattr(user, 'username', user).lower() for user in users or ()}
    if usernames:
        intids_created_by = catalog[IX_CREATOR].apply({'any_of': usernames})
    else:
        intids_created_by = catalog[IX_CREATOR].ids()

    def _validate(uid):
        obj = intids.queryObject(uid)
        if obj is None or isBroken(obj, uid) or IDeletedObjectPlaceholder.providedBy(obj):
            return None
        return obj

    for uid in intids_created_by:
        obj = _validate(uid)
        if obj is not None:
            yield uid, obj
