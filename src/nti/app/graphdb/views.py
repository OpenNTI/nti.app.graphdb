#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.container.contained import Contained

from zope.location.interfaces import IContained

from zope.traversing.interfaces import IPathAdapter

@interface.implementer(IPathAdapter, IContained)
class GraphPathAdapter(Contained):

	__name__ = 'graphdb'

	def __init__(self, context, request=None):
		self.context = context
		self.request = request
		self.__parent__ = context
