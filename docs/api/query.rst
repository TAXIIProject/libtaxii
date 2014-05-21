:mod:`libtaxii.taxii_default_query` Module
==========================================
.. module:: libtaxii.taxii_default_query

Constants
---------

**Capability Module IDs**

.. autodata:: CM_CORE
.. autodata:: CM_REGEX
.. autodata:: CM_TIMESTAMP


**Operators**

.. autodata:: OP_OR
.. autodata:: OP_AND


**Format IDs**

.. autodata:: FID_TAXII_DEFAULT_QUERY_10

**Namespace Map**

.. autodata:: ns_map

Classes
-------

.. class:: DefaultQuery

	This class is a subclass of ``messages_11.Query``, and is used to convey a TAXII Default Query.
	
	.. method:: __init__(targeting_expression_id, criteria)
			
			:param string targeting_expression_id: The targeting_expression used in the query
			:param criteria: The criteria of the query
			:type criteria: :class:`DefaultQuery.Criteria`

.. class:: DefaultQuery.Criteria
	
	Represents criteria for a :class:`DefaultQuery`
		
	.. method:: __init__(operator, criteria=None, criterion=None)
			
		**Note**: At least one criterion OR criteria MUST be present
			
		:param string operator: The operator to use
		:param list criteria: List of Criteria objects for the query
		:param list criterion: List of Criterion objects for the query	
					
.. class:: DefaultQuery.Criterion
	
	Represents criterion for a :class:`DefaultQuery.Criteria`
		
	.. method:: __init__(target, test, negate=False)
			
		:param string target: A targeting expression identifying the target
		:param test: The test to be applied to the target
		:type test: :class:`DefaultQuery.Criterion.Test`
		:param bool negate: Whether the result of applying the test to the target should be negated
			
.. class:: DefaultQuery.Criterion.Test
		
	.. method:: __init__(capability_id, relationship, parameters=None)
	
		:param string capability_id: The ID of the capability module that defines the relationship & parameters
		:param string relationship: The relationship (e.g., equals)
		:param parameters: The parameters for the relationship.
		:type parameters: :class:`dict` of key/value pairs
		
.. class:: DefaultQueryInfo

	This class is a subclass of the messages_11.SupportedQuery Class, and is used to describe the TAXII Default Queries that are supported.
		
	.. method:: __init__(targeting_expression_infos, capability_modules):
	
		:param targeting_expression_infos: Describe the supported targeting expressions
		:type targeting_expression_infos: :class:`list` of :class:`TargetingExpressionInfo` objects
		:param capability_modules: Indicate the supported capability modules
		:type capability_modules: :class:`list` of :class:`str`
	
.. class:: DefaultQueryInfo.TargetingExpressionInfo
	
	This class describes supported Targeting Expressions
		
	.. method:: __init__(targeting_expression_id, preferred_scope = None, allowed_scope = None)
	
		:param string targeting_expression_id: The supported targeting expression ID
		:param preferred_scope: Indicates the preferred scope of queries
		:type preferred_scope: :class:`list` of :class:`str`
		:param allowed_scope: Indicates the allowed scope of queries
		:type allowed_scope: :class:`list` of :class:`str`
	
Examples
--------

**DefaultQueryInfo Example**

.. code:: python

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

**DefaultQuery Example**

.. code:: python

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