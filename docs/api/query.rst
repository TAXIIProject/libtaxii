:mod:`libtaxii.taxii_default_query` Module
==========================================
.. automodule:: libtaxii.taxii_default_query

Classes
-------

Default Query
*************

.. autoclass:: DefaultQuery
	:show-inheritance:
	:members:
	
**Example**

.. code-block:: python

	import libtaxii.taxii_default_query as tdq
	from libtaxii.taxii_default_query import Test
	from libtaxii.taxii_default_query import Criterion
	from libtaxii.taxii_default_query import Criteria
	from libtaxii.constants import *
	import datetime
	
	##############################################################################
	# A Taxii Default Query *Test* gives the consumer granular control over the
	# Target of a Query by applying unambiguos relationship requirements specified
	# using a standardized vocabulary.
	
	# Each Relationship (e.g. equals, matches, greater_than, etc.) in a Capability
	# Module defines a set of paramater fields, capable of expressing that
	# relation.
	
	# The *equals* relationship, of the Core Capability Module,  returns True if
	# the target matches the value exactly. If the target merely contains the
	# value (but does not match exactly) the relationship Test returns False.
	test_equals = Test(capability_id=CM_CORE,
	                   relationship='equals',
	                   parameters={'value': 'Test value',
	                               'match_type': 'case_sensitive_string'})
	
	# The *matches* relationship, in the context of the Regular Expression
	# Capability Module, returns true if the target matches the regular expression
	# contained in the value.
	test_matches = Test(capability_id=CM_REGEX,
	                    relationship='matches',
	                    parameters={'value': '[A-Z]*',
	                                'case_sensitive': True})
	
	# The *greater than* relationship, in the context of the Timestamp Capability
	# Module returns True if the target's timestamp indicates a later time than
	# that specified by this value. This relationship is only valid for timestamp
	# comparisons.
	test_timestamp = Test(capability_id=CM_TIMESTAMP,
	                      relationship='greater_than',
	                      parameters={'value': datetime.datetime.now()})
	
	
	##############################################################################
	# A *Criterion* specifies how a Target is evaluated against a Test. Within a
	# Criterion, the Target is used to identify a specific region of a record to
	# which the Test should be applied. Slash Notation Targeting Expression syntax,
	# in conjunction with a Targeting Expression Vocabulary, are used to form a
	# Targeting Expression
	
	# A Multi-field Wildcard (**). This indicates any Node or series of Nodes,
	# specified by double asterisks.
	criterion1 = Criterion(target='**',
	                       test=test_equals)
	
	# Indicates that *id* fields in the STIX Indicator construct are in scope
	criterion2 = Criterion(target='STIX_Package/Indicators/Indicator/@id',
	                       test=test_matches)
	
	# Indicates that all STIX Description fields are in scope
	criterion3 = Criterion(target='**/Description',
	                       test=test_timestamp)
	
	
	##############################################################################
	# *Criteria* consist of a logical operator (and/or) that should be applied to
	# child Criteria and Criterion to determine whether content matches this query.
	
	criteria1 = Criteria(operator=OP_AND,
	                     criterion=[criterion1])
	
	criteria2 = Criteria(operator=OP_OR,
	                     criterion=[criterion1, criterion2, criterion3])
	
	criteria3 = Criteria(operator=OP_AND,
	                     criterion=[criterion1, criterion3],
	                     criteria=[criteria2])
	
	
	##############################################################################
	# query1 and query2 would be able to be used in TAXII requests that
	# contain queries (e.g., PollRequest Messages)
	query1 = tdq.DefaultQuery(CB_STIX_XML_11, criteria1)
	query2 = tdq.DefaultQuery(CB_STIX_XML_11, criteria3)


Default Query Info
******************
			
.. autoclass:: DefaultQueryInfo
	:show-inheritance:
	:members:
	
**Example**

.. code-block:: python
	
	import libtaxii as t
	import libtaxii.taxii_default_query as tdq
	from libtaxii.constants import *
	import datetime
	from dateutil.tz import tzutc
	
	tei_01 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
	            targeting_expression_id = CB_STIX_XML_10, # Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
	            preferred_scope=[], # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
	            allowed_scope=['**'])# This example has no preferred scope, and allows any scope

	tei_02 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
	            targeting_expression_id = CB_STIX_XML_11,  # Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
	            preferred_scope=['STIX_Package/Indicators/Indicator/**'], # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
	            allowed_scope=[]) # This example prefers the Indicator scope and allows no other scope

	tdqi1 = tdq.DefaultQueryInfo(
	            targeting_expression_infos = [tei_01, tei_02], # Required, 1-n. Indicates what targeting expressions are supported
	            capability_modules = [tdq.CM_CORE]) # Required, 1-n. Indicates which capability modules can be used.


