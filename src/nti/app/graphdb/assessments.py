#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# from zope import component
# 
# from zope.intid.interfaces import IIntIdRemovedEvent
# 
# from zope.lifecycleevent.interfaces import IObjectAddedEvent
# 
# from pyramid.traversal import find_interface
# 
# from nti.app.assessment.interfaces import IUsersCourseInquiryItem
# from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItem
# from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItemFeedback
# 
# from nti.assessment.interfaces import IQInquiry
# from nti.assessment.interfaces import IQAssignment
# 
# from nti.contenttypes.courses.interfaces import ICourseInstance
# 
# from nti.dataserver.interfaces import IUser
# 
# from nti.graphdb import create_job
# from nti.graphdb import get_graph_db
# from nti.graphdb import get_job_queue
# 
# from nti.graphdb.common import get_oid
# from nti.graphdb.common import get_entity
# from nti.graphdb.common import get_creator
# 
# from nti.graphdb.interfaces import IObjectProcessor
# from nti.graphdb.interfaces import IPropertyAdapter
# from nti.graphdb.interfaces import IUniqueAttributeAdapter
# 
# from nti.graphdb.relationships import TakenInquiry
# from nti.graphdb.relationships import TakenAssessment 
# from nti.graphdb.relationships import AssigmentFeedback
# 
# from nti.ntiids.ntiids import find_object_with_ntiid
# 
# def get_assignment(name):
# 	return component.queryUtility(IQAssignment, name=name)
# 
# def get_assignment_history_item_properties(user, item):
# 	result = component.queryMultiAdapter((user, item, TakenAssessment()),
# 										 IPropertyAdapter)
# 	return result or {}
# 
# def _add_assignment_taken_relationship(db, username, oid):
# 	user = get_entity(username)
# 	item = find_object_with_ntiid(oid)  # find user history item
# 	if IUsersCourseAssignmentHistoryItem.providedBy(item):
# 		assignment = get_assignment(item.__name__)
# 	else:
# 		assignment = None
# 
# 	if  	assignment is not None \
# 		and user is not None \
# 		and not db.match(user, assignment, TakenAssessment()):
# 		properties = get_assignment_history_item_properties(user, item)
# 		rel = db.create_relationship(user, assignment, TakenAssessment(),
# 									 properties=properties)
# 		logger.debug("Assignment taken relationship %s created", rel)
# 		return rel
# 	return None
# 
# def _process_assignment_taken(db, item):
# 	oid = get_oid(item)
# 	queue = get_job_queue()
# 	username = IUser(item).username
# 	job = create_job(_add_assignment_taken_relationship, db=db,
# 					 username=username,
# 					 oid=oid)
# 	queue.put(job)
# 
# @component.adapter(IUsersCourseAssignmentHistoryItem, IObjectAddedEvent)
# def _assignment_history_item_added(item, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_assignment_taken(db, item)
# 
# def _remove_assignment_taken_relationship(db, username, assignmentId):
# 	user = get_entity(username)
# 	assignment = component.queryUtility(IQAssignment, assignmentId)
# 	if assignment is not None and user is not None:
# 		rels = db.match(user, assignment, TakenAssessment())
# 		if rels:
# 			db.delete_relationships(*rels)
# 		logger.debug("%s assignment taken relationship(s) deleted", len(rels))
# 		return rels
# 	return None
# 
# def _process_assignment_taken_removal(db, item):
# 	assignmentId = item.__name__
# 	queue = get_job_queue()
# 	user = IUser(item, None)
# 	if user is not None:
# 		username = user.username
# 		job = create_job(_remove_assignment_taken_relationship, db=db,
# 						 username=username,
# 						 assignmentId=assignmentId)
# 		queue.put(job)
# 
# @component.adapter(IUsersCourseAssignmentHistoryItem, IIntIdRemovedEvent)
# def _assignment_history_item_removed(item, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_assignment_taken_removal(db, item)
# 
# # feedback
# 
# def _pick_instructor(course):
# 	instructors = course.instructors if course is not None else None
# 	for instructor in instructors or ():
# 		entity = get_entity(instructor)
# 		if entity is not None:
# 			return entity
# 	return None
# 
# def _set_asm_feedback(db, oid):
# 	feedback = find_object_with_ntiid(oid)
# 	if feedback is not None:
# 		unique = IUniqueAttributeAdapter(feedback)
# 		if db.get_indexed_relationships(unique.key, unique.value):
# 			return
# 
# 		creator = get_creator(feedback)
# 		student = get_creator(feedback.__parent__)
# 		if student == creator:
# 			direction = 1  # feedback from student to professor
# 			item = find_interface(feedback, IUsersCourseAssignmentHistoryItem)
# 			course = ICourseInstance(item, None)
# 			instructor = _pick_instructor(course) if course is not None else None
# 		else:
# 			direction = 2
# 			instructor = creator  # feedback from professor to student
# 
# 		if not instructor or not student:
# 			return
# 
# 		rel_type = AssigmentFeedback()
# 		properties = IPropertyAdapter(feedback)
# 		if direction == 1:
# 			rel = db.create_relationship(student, instructor, rel_type,
# 										 properties=properties)
# 		else:
# 			rel = db.create_relationship(instructor, student, rel_type,
# 										 properties=properties)
# 
# 		# track relationship
# 		db.index_relationship(rel, unique.key, unique.value)
# 		logger.debug("Assignment feedback relationship %s created", rel)
# 		return rel
# 
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
# def _del_asm_feedback(db, key, value):
# 	rels = db.get_indexed_relationships(key, value)
# 	if rels:
# 		db.delete_relationships(*rels)
# 		logger.debug("%s assignment feedback relationship(s) deleted", len(rels))
# 		return True
# 	return False
# 
# def _process_feedback_removed(db, feedback):
# 	unique = IUniqueAttributeAdapter(feedback)
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
# # inquiry
# 
# def get_inquiry(name):
# 	return component.queryUtility(IQInquiry, name=name)
# 
# def get_inquiry_item_properties(user, item):
# 	result = component.queryMultiAdapter((user, item, TakenInquiry()),
# 										 IPropertyAdapter)
# 	return result or {}
# 
# def _add_inquiry_taken_relationship(db, username, oid):
# 	user = get_entity(username)
# 	item = find_object_with_ntiid(oid)  # find user inquiry item
# 	if IUsersCourseInquiryItem.providedBy(item):
# 		inquiry = get_inquiry(item.__name__)
# 	else:
# 		inquiry = None
# 
# 	if  inquiry is not None and user is not None and \
# 		not db.match(user, inquiry, TakenInquiry()):
# 		properties = get_inquiry_item_properties(user, item)
# 		rel = db.create_relationship(user, inquiry, TakenInquiry(),
# 									 properties=properties)
# 		logger.debug("Inquiry taken relationship %s created", rel)
# 		return rel
# 	return None
# 
# def _process_inquiry_taken(db, item):
# 	oid = get_oid(item)
# 	queue = get_job_queue()
# 	username = IUser(item).username
# 	job = create_job(_add_inquiry_taken_relationship, db=db,
# 					 username=username,
# 					 oid=oid)
# 	queue.put(job)
# 
# @component.adapter(IUsersCourseInquiryItem, IObjectAddedEvent)
# def _inquiry_item_added(item, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_inquiry_taken(db, item)
# 
# def _remove_inquiry_taken_relationship(db, username, assignmentId):
# 	user = get_entity(username)
# 	inquiry = component.queryUtility(IQInquiry, assignmentId)
# 	if inquiry is not None and user is not None:
# 		rels = db.match(user, inquiry, TakenInquiry())
# 		if rels:
# 			db.delete_relationships(*rels)
# 		logger.debug("%s inquiry taken relationship(s) deleted", len(rels))
# 		return rels
# 	return None
# 
# def _process_inquiry_taken_removal(db, item):
# 	inquiryId = item.__name__
# 	queue = get_job_queue()
# 	username = IUser(item).username
# 	job = create_job(_remove_inquiry_taken_relationship, db=db,
# 					 username=username,
# 					 assignmentId=inquiryId)
# 	queue.put(job)
# 
# @component.adapter(IUsersCourseInquiryItem, IIntIdRemovedEvent)
# def _inquiry_item_removed(item, event):
# 	db = get_graph_db()
# 	if db is not None:
# 		_process_inquiry_taken_removal(db, item)
# 
# # processor
# 
# component.moduleProvides(IObjectProcessor)
# 
# def init(db, obj):
# 	result = True
# 	if IUsersCourseAssignmentHistoryItem.providedBy(obj):
# 		_process_assignment_taken(db, obj)
# 	elif IUsersCourseAssignmentHistoryItemFeedback.providedBy(obj):
# 		_process_feedback_added(db, obj)
# 	elif IUsersCourseInquiryItem.providedBy(obj):
# 		_process_inquiry_taken(db, obj)
# 	else:
# 		result = False
# 	return result
