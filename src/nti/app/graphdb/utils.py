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

from nti.dataserver.users import User
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.dataserver.metadata_index import IX_CREATOR
from nti.dataserver.metadata_index import IX_MIMETYPE
from nti.dataserver.metadata_index import IX_CREATEDTIME
from nti.dataserver.metadata_index import CATALOG_NAME as METADATA_CATALOG_NAME

from nti.zodb import isBroken

def all_user_ids(usernames=()):
	result = set()
	intids = component.getUtility(IIntIds)
	for name in usernames or ():
		user = User.get_user(name)
		if user is not None:
			result.add(intids.getId(user))
	return result

def all_cataloged_objects(users=()):
	intids = component.getUtility(IIntIds)
	catalog = component.getUtility(ICatalog, METADATA_CATALOG_NAME)
	usernames = {getattr(user, 'username', user).lower() for user in users or ()}
	if usernames:
		intids_created_by = catalog[IX_CREATOR].apply({'any_of': usernames})
		all_intids = intids.family.IF.union(all_user_ids(usernames), intids_created_by)
	else:
		all_intids = None
		for name in (IX_CREATOR, IX_MIMETYPE, IX_CREATEDTIME):
			if all_intids is None:
				all_intids = catalog[name].ids()
			else:
				all_intids = intids.family.IF.union(all_intids, catalog[name].ids())

	for uid in all_intids:
		obj = intids.queryObject(uid)
		if obj is None or isBroken(obj, uid) or IDeletedObjectPlaceholder.providedBy(obj):
			continue
		yield uid, obj
