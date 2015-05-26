#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from pyramid.traversal import find_interface

from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItem
# from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItemFeedback
# 
# from nti.app.products.courseware import interfaces as cw_interfaces
# 
# from nti.app.products.gradebook import interfaces as gb_interfaces

from nti.assessment.interfaces import IQAssignment

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.interfaces import IUser

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.graphdb import create_job
from nti.graphdb import get_graph_db
from nti.graphdb import get_job_queue

from nti.graphdb.common import get_oid
from nti.graphdb.common import get_entity
from nti.graphdb.common import get_creator

from nti.graphdb.interfaces import IObjectProcessor
from nti.graphdb.interfaces import IPropertyAdapter

from nti.graphdb.relationships import TakeAssessment

def _add_assignment_taken_relationship(db, username, oid):
	user = get_entity(username)
	item = find_object_with_ntiid(oid)  # find user history item
	if IUsersCourseAssignmentHistoryItem.providedBy(item):
		assignment = component.queryUtility(IQAssignment, item.__name__)
	else:
		assignment = None

	if  assignment is not None and user is not None and \
		not db.match(user, assignment, TakeAssessment()):

		# get properties from the history item
		properties = component.queryMultiAdapter((user, item, TakeAssessment()),
												 IPropertyAdapter) or {}
		# create relationship
		rel = db.create_relationship(user, assignment, TakeAssessment(),
									 properties=properties)
		logger.debug("Assignment taken relationship %s created", rel)
		return rel
	return None

def _process_assignment_taken(db, item):
	oid = get_oid(item)
	queue = get_job_queue()
	username = IUser(item).username
	job = create_job(_add_assignment_taken_relationship, db=db,
					 username=username,
					 oid=oid)
	queue.put(job)

@component.adapter(IUsersCourseAssignmentHistoryItem, IObjectAddedEvent)
def _assignment_history_item_added(item, event):
	db = get_graph_db()
	if db is not None:
		_process_assignment_taken(db, item)

def _remove_assignment_taken_relationship(db, username, assignmentId):
	user = get_entity(username)
	assignment = component.queryUtility(IQAssignment, assignmentId)
	if assignment is not None and user is not None:
		rels = db.match(user, assignment, TakeAssessment())
		if rels:
			db.delete_relationships(*rels)
		logger.debug("%s assignment taken relationship(s) deleted", len(rels))
		return rels
	return None

def _process_assignment_taken_removal(db, item):
	assignmentId = item.__name__
	queue = get_job_queue()
	username = IUser(item).username
	job = create_job(_remove_assignment_taken_relationship, db=db,
					 username=username,
					 assignmentId=assignmentId)
	queue.put(job)

@component.adapter(IUsersCourseAssignmentHistoryItem, IIntIdRemovedEvent)
def _assignment_history_item_removed(item, event):
	db = get_graph_db()
	if db is not None:
		_process_assignment_taken_removal(db, item)

# feedback

def _pick_instructor(course):
	instructors = course.instructors if course is not None else None
	for instructor in instructors or ():
		entity = get_entity(instructor)
		if entity is not None:
			return entity
	return None

def _set_asm_feedback(db, oid):
	feedback = find_object_with_ntiid(oid)
	if feedback is not None:
		creator = get_creator(feedback)
		student = get_creator(feedback.__parent__)
		if student == creator:
			direction = 1  # feedback from student to professor
			item = find_interface(feedback, IUsersCourseAssignmentHistoryItem)
			course = ICourseInstance(item, None)
			instructor = _pick_instructor(course)  # pick first found
		else:
			direction = 2
			instructor = creator  # feedback from professor to student

		if not instructor or not student or direction:
			return

#		 rel_type = relationships.AssigmentFeedback()
#		 properties = graph_interfaces.IPropertyAdapter(feedback)
#		 unique = graph_interfaces.IUniqueAttributeAdapter(feedback)
#
#		 if direction == 1:
#			 rel = db.create_relationship(student, instructor, rel_type,
#										  properties=properties,
#										  key=unique.key, value=unique.value)
#		 else:
#			 rel = db.create_relationship(instructor, student, rel_type,
#										  properties=properties,
#										  key=unique.key, value=unique.value)
#		 logger.debug("assignment feedback relationship %s created", rel)
#		 return rel

# def _process_feedback_added(db, feedback):
# 	oid = get_oid(feedback)
# 	queue = get_job_queue()
# 	job = create_job(_set_asm_feedback, db=db, oid=oid)
# 	queue.put(job)
# 
# @component.adapter(IUsersCourseAssignmentHistoryItemFeedback, IObjectAddedEvent)
# def _feedback_added(feedback, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_feedback_added(db, feedback)
# 
# def _del_asm_feedback(db, label, key, value):
# 	rel = db.delete_indexed_relationship(key, value)
# 	if rel is not None:
# 		logger.debug("assignment feedback relationship %s deleted", rel)
# 		return True
# 	return False
# 
# def _process_feedback_removed(db, feedback):
# 	unique = graph_interfaces.IUniqueAttributeAdapter(feedback)
# 	queue = get_job_queue()
# 	job = create_job(_del_asm_feedback, db=db, key=unique.key, value=unique.value)
# 	queue.put(job)
# 
# @component.adapter(IUsersCourseAssignmentHistoryItemFeedback, IIntIdRemovedEvent)
# def _feedback_removed(feedback, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_feedback_removed(db, feedback)
# 
# # utils
# 
# def get_course_enrollments(user):
# 	container = []
# 	subs = component.subscribers((user,), cw_interfaces.IPrincipalEnrollmentCatalog)
# 	for catalog in subs:
# 		queried = catalog.iter_enrollments()
# 		container.extend(queried)
# 	container[:] = [cw_interfaces.ICourseInstanceEnrollment(x) for x in container]
# 	return container
# 
# def init_asssignments(db, user):
# 	enrollments = get_course_enrollments(user)
# 	for enrollment in enrollments:
# 		course = enrollment.CourseInstance
# 		history = component.getMultiAdapter(
# 									(course, user),
# 									IUsersCourseAssignmentHistory)
# 		for _, item in history.items():
# 			grade = gb_interfaces.IGrade(item, None)
# 			if grade is not None and grade.value is not None:
# 				process_grade_modified(db, grade)
# 			else:
# 				process_assignment_taken(db, item)

component.moduleProvides(IObjectProcessor)

def init(db, obj):
	result = True
# 	if IUser.providedBy(obj):
# 		init_asssignments(db, obj)
# 	elif IUsersCourseAssignmentHistoryItemFeedback.providedBy(obj):
# 		_process_feedback_added(db, obj)
# 	else:
# 		result = False
	return result
