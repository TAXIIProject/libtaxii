:mod:`libtaxii.taxii_default_query` Module
==========================================
.. automodule:: libtaxii.taxii_default_query

Constants
---------

Capability Module IDs
*********************

.. autodata:: CM_CORE
.. autodata:: CM_REGEX
.. autodata:: CM_TIMESTAMP


Operators
*********

.. autodata:: OP_OR
.. autodata:: OP_AND


Format IDs
**********

.. autodata:: FID_TAXII_DEFAULT_QUERY_10

Namespace Map
*************

.. autodata:: ns_map

Classes
-------

Default Query
*************

.. autoclass:: DefaultQuery
	:show-inheritance:
	:members:
	
**Example**

.. code-block:: python

	import libtaxii as t
	import libtaxii.taxii_default_query as tdq
	import datetime
	from dateutil.tz import tzutc

	test1 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE, #Required
	                                        relationship='equals', #Required
	                                        parameters={'value': 'Test value',
	                                                    'match_type': 'case_sensitive_string'}#Each relationship defines which params are and are not required
		                                        )

		test2 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_REGEX, #Required
		                                        relationship='matches',#Required
		                                        parameters={'value': '[A-Z]*',
		                                                    'case_sensitive': True})#Each relationship defines which params are and are not required

		test3 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_TIMESTAMP,#Required
		                                        relationship='greater_than',#Required
		                                        parameters={'value': datetime.datetime.now()})#Each relationship defines which params are and are not required

		criterion1 = tdq.DefaultQuery.Criterion(target='**', test=test1)
		criterion2 = tdq.DefaultQuery.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
		criterion3 = tdq.DefaultQuery.Criterion(target='**/Description', test=test3)

		criteria1 = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1])
		criteria2 = tdq.DefaultQuery.Criteria(operator=tdq.OP_OR, criterion=[criterion1, criterion2, criterion3])
		criteria3 = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

		query1 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria1)
		query2 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria3)
		#query1 and query2 would be able to be used in TAXII requests that contain queries (e.g., PollRequest messages)

Default Query Info
******************
			
.. autoclass:: DefaultQueryInfo
	:show-inheritance:
	:members:
	
**Example**

.. code-block:: python
	
	import libtaxii as t
	import libtaxii.taxii_default_query as tdq
	import datetime
	from dateutil.tz import tzutc
	
	tei_01 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
	            targeting_expression_id = t.CB_STIX_XML_10, #Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
	            preferred_scope=[], #At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
	            allowed_scope=['**'])#This example has no preferred scope, and allows any scope

	tei_02 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
	            targeting_expression_id = t.CB_STIX_XML_11,  #required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
	            preferred_scope=['STIX_Package/Indicators/Indicator/**'], #At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
	            allowed_scope=[])#This example prefers the Indicator scope and allows no other scope

	tdqi1 = tdq.DefaultQueryInfo(
	            targeting_expression_infos = [tei_01, tei_02], #Required, 1-n. Indicates what targeting expressions are supported
	            capability_modules = [tdq.CM_CORE])#Required, 1-n. Indicates which capability modules can be used.
