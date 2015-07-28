#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
import simplejson as json

from zope import component

from pyramid.view import view_config

from nti.common.maps import CaseInsensitiveDict

from nti.dataserver import authorization as nauth
from nti.dataserver.interfaces import IDataserver
from nti.dataserver.interfaces import IShardLayout

from nti.graphdb.interfaces import IGraphDB
from nti.graphdb.interfaces import IObjectProcessor

from nti.externalization.interfaces import LocatedExternalDict

from .utils import all_cataloged_objects

from .views import GraphPathAdapter

def _make_min_max_btree_range(search_term):
	min_inclusive = search_term  # start here
	max_exclusive = search_term[0:-1] + unichr(ord(search_term[-1]) + 1)
	return min_inclusive, max_exclusive

def username_search(search_term):
	min_inclusive, max_exclusive = _make_min_max_btree_range(search_term)
	dataserver = component.getUtility(IDataserver)
	_users = IShardLayout(dataserver).users_folder
	usernames = list(_users.iterkeys(min_inclusive, max_exclusive, excludemax=True))
	return usernames

def init(db, obj):
	result = False
	for _, module in component.getUtilitiesFor(IObjectProcessor):
		result = module.init(db, obj) or result
	return result

def init_db(db, usernames=()):
	count = 0
	for _, obj in all_cataloged_objects(usernames):
		if init(db, obj):
			count += 1
	return count

@view_config(route_name='objects.generic.traversal',
			 name='init_graphdb',
			 renderer='rest',
			 request_method='POST',
			 context=GraphPathAdapter,
			 permission=nauth.ACT_NTI_ADMIN)
def init_graphdb(request):
	values = json.loads(unicode(request.body, request.charset)) if request.body else {}
	values = CaseInsensitiveDict(values)
	term = values.get('term') or values.get('search')
	usernames = values.get('usernames') or values.get('username')
	if term:
		usernames = username_search(term)
	elif usernames:
		usernames = usernames.split(',')
	else:
		usernames = ()

	now = time.time()
	db = component.getUtility(IGraphDB)
	total = init_db(db, usernames)
	elapsed = time.time() - now

	logger.info("Total objects processed %s(%s)", total, elapsed)

	result = LocatedExternalDict()
	result['Elapsed'] = elapsed
	result['Total'] = total
	return result
