#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.traversal import find_interface

from nti.app.assessment.interfaces import IUsersCourseInquiryItem
from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItem
from nti.app.assessment.interfaces import IUsersCourseAssignmentMetadataItem
from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItemFeedback

from nti.dataserver.interfaces import IUser

from nti.graphdb.common import get_createdTime

from nti.graphdb.interfaces import ITakenInquiry
from nti.graphdb.interfaces import IPropertyAdapter
from nti.graphdb.interfaces import ITakenAssessment

from nti.graphdb.properties import add_oid
from nti.graphdb.properties import add_intid
from nti.graphdb.properties import ModeledContentPropertyAdpater


@interface.implementer(IPropertyAdapter)
@component.adapter(IUser, IUsersCourseAssignmentHistoryItem, ITakenAssessment)
def _AssignmentHistoryItemRelationshipPropertyAdpater(user, item, unused_rel):
    result = {'creator': user.username}
    result['assignmentId'] = item.assignmentId
    result['createdTime'] = get_createdTime(item)
    metadata = IUsersCourseAssignmentMetadataItem(item, None)
    if metadata is not None:
        result['duration'] = metadata.Duration
        result['startTime'] = metadata.StartTime
    add_oid(item, result)
    add_intid(item, result)
    return result


@interface.implementer(IPropertyAdapter)
@component.adapter(IUsersCourseAssignmentHistoryItemFeedback)
def _AssignmentFeedbackPropertyAdpater(feedback):
    result = ModeledContentPropertyAdpater(feedback)
    result['type'] = u'AssignmentFeedback'
    item = find_interface(feedback, IUsersCourseAssignmentHistoryItem)
    if item is not None:
        result['assignmentId'] = item.__name__
    return result


@interface.implementer(IPropertyAdapter)
@component.adapter(IUser, IUsersCourseInquiryItem, ITakenInquiry)
def _InquiryItemRelationshipPropertyAdpater(user, item, unused_rel):
    result = {'creator': user.username}
    result['inquiryId'] = item.inquiryId
    result['createdTime'] = get_createdTime(item)
    add_oid(item, result)
    add_intid(item, result)
    return result
