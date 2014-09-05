:mod:`libtaxii.constants` Module
================================
.. module:: libtaxii.constants

Constants
---------

Version IDs
***********

The following constants can be used as TAXII Version IDs

.. autodata:: VID_TAXII_SERVICES_10
.. autodata:: VID_TAXII_SERVICES_11
.. autodata:: VID_TAXII_XML_10
.. autodata:: VID_TAXII_XML_11
.. autodata:: VID_TAXII_HTTP_10
.. autodata:: VID_TAXII_HTTPS_10

The following are third-party Version IDs included in libtaxii for convenience.

.. autodata:: VID_CERT_EU_JSON_10


Content Binding IDs
*******************

The following constants should be used as the Content Binding ID for STIX XML.

.. autodata:: CB_STIX_XML_10
.. autodata:: CB_STIX_XML_101
.. autodata:: CB_STIX_XML_11
.. autodata:: CB_STIX_XML_111

These other Content Binding IDs are included for convenience as well.

.. autodata:: CB_CAP_11
.. autodata:: CB_XENC_122002
.. autodata:: CB_SMIME

Namespace Map
*************
This constant contains commonly namespaces and aliases in TAXII.

.. autodata:: NS_MAP

Message Types
*************

.. autodata:: MSG_STATUS_MESSAGE
.. autodata:: MSG_DISCOVERY_REQUEST
.. autodata:: MSG_DISCOVERY_RESPONSE
.. autodata:: MSG_FEED_INFORMATION_REQUEST
.. autodata:: MSG_FEED_INFORMATION_RESPONSE
.. autodata:: MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST
.. autodata:: MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE
.. autodata:: MSG_POLL_REQUEST
.. autodata:: MSG_POLL_RESPONSE
.. autodata:: MSG_INBOX_MESSAGE

.. autodata:: MSG_TYPES_10

.. autodata:: MSG_POLL_FULFILLMENT_REQUEST
.. autodata:: MSG_COLLECTION_INFORMATION_REQUEST
.. autodata:: MSG_COLLECTION_INFORMATION_RESPONSE
.. autodata:: MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST
.. autodata:: MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE

.. autodata:: MSG_TYPES_11


Status Types
************

These constants are used in :py:class:`StatusMessage`.

.. autodata:: ST_BAD_MESSAGE
.. autodata:: ST_DENIED
.. autodata:: ST_FAILURE
.. autodata:: ST_NOT_FOUND
.. autodata:: ST_POLLING_UNSUPPORTED
.. autodata:: ST_RETRY
.. autodata:: ST_SUCCESS
.. autodata:: ST_UNAUTHORIZED
.. autodata:: ST_UNSUPPORTED_MESSAGE_BINDING
.. autodata:: ST_UNSUPPORTED_CONTENT_BINDING
.. autodata:: ST_UNSUPPORTED_PROTOCOL

.. autodata:: ST_TYPES_10

.. autodata:: ST_ASYNCHRONOUS_POLL_ERROR
.. autodata:: ST_DESTINATION_COLLECTION_ERROR
.. autodata:: ST_INVALID_RESPONSE_PART
.. autodata:: ST_NETWORK_ERROR
.. autodata:: ST_PENDING
.. autodata:: ST_UNSUPPORTED_QUERY

.. autodata:: ST_TYPES_11


Subscription Actions
********************

These constants are used in :py:class:`ManageFeedSubscriptionRequest`

.. autodata:: ACT_SUBSCRIBE
.. autodata:: ACT_UNSUBSCRIBE
.. autodata:: ACT_STATUS

.. autodata:: ACT_TYPES_10

.. autodata:: ACT_PAUSE
.. autodata:: ACT_RESUME

.. autodata:: ACT_TYPES_11


Service Types
****************

These constants are used to indicate the type of service.

.. autodata:: SVC_INBOX
.. autodata:: SVC_POLL
.. autodata:: SVC_FEED_MANAGEMENT
.. autodata:: SVC_DISCOVERY

.. autodata:: SVC_TYPES_10

.. autodata:: SVC_COLLECTION_MANAGEMENT

.. autodata:: SVC_TYPES_11

Subscription Statuses
*********************

These constants are used in :py:class:`ManageCollectionSubscriptionResponse`

.. autodata:: SS_ACTIVE
.. autodata:: SS_PAUSED
.. autodata:: SS_UNSUBSCRIBED

.. autodata:: SS_TYPES_11


Response Types
**************

These constants are used to indicate the type of response returned.

.. autodata:: RT_FULL
.. autodata:: RT_COUNT_ONLY

.. autodata:: RT_TYPES_11


Collection Types
****************

These constants are used to indicate the type of collection.

.. autodata:: CT_DATA_FEED
.. autodata:: CT_DATA_SET

.. autodata:: CT_TYPES_11

Status Details
**************

These constants are used in :py:class:`StatusMessage`.

.. autodata:: SD_ACCEPTABLE_DESTINATION
.. autodata:: SD_MAX_PART_NUMBER
.. autodata:: SD_ITEM
.. autodata:: SD_ESTIMATED_WAIT
.. autodata:: SD_RESULT_ID
.. autodata:: SD_WILL_PUSH
.. autodata:: SD_SUPPORTED_BINDING
.. autodata:: SD_SUPPORTED_CONTENT
.. autodata:: SD_SUPPORTED_PROTOCOL
.. autodata:: SD_SUPPORTED_QUERY

.. autodata:: SD_TYPES_11

.. autodata:: SD_CAPABILITY_MODULE
.. autodata:: SD_PREFERRED_SCOPE
.. autodata:: SD_ALLOWED_SCOPE
.. autodata:: SD_TARGETING_EXPRESSION_ID

Query Formats
*************

These constants are used to indicate query format.

..autodata:: FID_TAXII_DEFAULT_QUERY_10

Query Capability Modules
************************

These constants are used to indicate TAXII Default Query Capability Modules

.. autodata:: CM_CORE
.. autodata:: CM_REGEX
.. autodata:: CM_TIMESTAMP

.. autodata:: CM_IDS

Query Operators
***************

These constants are used to identify the operator in :py:class`Criteria`

.. autodata:: OP_OR
.. autodata:: OP_AND

.. autodata:: OP_TYPES

Query Status Types
******************

TAXII Default Query 1.0 identifies three additional Status Types:

.. autodata:: ST_UNSUPPORTED_CAPABILITY_MODULE
.. autodata:: ST_UNSUPPORTED_TARGETING_EXPRESSION
.. autodata:: ST_UNSUPPORTED_TARGETING_EXPRESSION_ID


Query Parameters
****************

These constants are used to identify parameters.

.. autodata:: P_VALUE
.. autodata:: P_MATCH_TYPE
.. autodata:: P_CASE_SENSITIVE

.. autodata:: P_NAMES

Query Relationships
*******************

These constants are used to identify relationships

.. autodata:: R_EQUALS
.. autodata:: R_NOT_EQUALS
.. autodata:: R_GREATER_THAN
.. autodata:: R_GREATER_THAN_OR_EQUAL
.. autodata:: R_LESS_THAN
.. autodata:: R_LESS_THAN_OR_EQUAL
.. autodata:: R_DOES_NOT_EXIST
.. autodata:: R_EXISTS
.. autodata:: R_BEGINS_WITH
.. autodata:: R_ENDS_WITH
.. autodata:: R_CONTAINS
.. autodata:: R_MATCHES

.. autodata:: R_NAMES
