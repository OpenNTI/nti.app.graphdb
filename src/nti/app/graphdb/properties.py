#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.dataserver.interfaces import IUser

from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItem
from nti.app.assessment.interfaces import IUsersCourseAssignmentMetadataItem

from nti.graphdb.common import get_createdTime

from nti.graphdb.interfaces import ITakeAssessment
from nti.graphdb.interfaces import IPropertyAdapter

from nti.graphdb.properties import add_oid
from nti.graphdb.properties import add_intid

@interface.implementer(IPropertyAdapter)
@component.adapter(IUser, IUsersCourseAssignmentHistoryItem, ITakeAssessment)
def _AssignmentHistoryItemRelationshipPropertyAdpater(user, item, rel):
    result = {'creator' : user.username}
    result['assignmentId'] = item.assignmentId
    result['createdTime'] = get_createdTime(item)
    metadata = IUsersCourseAssignmentMetadataItem(item, None)
    if metadata is not None:
        result['duration'] = metadata.Duration
        result['startTime'] = metadata.StartTime
    add_oid(item, result)
    add_intid(item, result)
    return result
