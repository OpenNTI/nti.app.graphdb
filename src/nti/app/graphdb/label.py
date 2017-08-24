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

from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItemFeedback

from nti.graphdb.interfaces import ILabelAdapter


@interface.implementer(ILabelAdapter)
@component.adapter(IUsersCourseAssignmentHistoryItemFeedback)
def _AssignmentFeedbackLabelAdpater(unused_item):
    return u"AssignmentFeedback"
