# Copyright (C) 2014 - The MITRE Corporation
# For license information, see the LICENSE.txt file

#: Namespace map of namespaces libtaxii knows about
NS_MAP = {
    'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1',
    'taxii_11': 'http://taxii.mitre.org/messages/taxii_xml_binding-1.1',
    'tdq': 'http://taxii.mitre.org/query/taxii_default_query-1',
}

#: alias for NS_MAP for backward compatibility
ns_map = NS_MAP

#: Constant identifying a Status Message
MSG_STATUS_MESSAGE = 'Status_Message'
#: Constant identifying a Discovery Request Message
MSG_DISCOVERY_REQUEST = 'Discovery_Request'
#: Constant identifying a Discovery Response Message
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
#: Constant identifying a Feed Information Request Message
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
#: Constant identifying a Feed Information Response Message
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'
#: Constant identifying a Subscription Management Request Message
MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
#: Constant identifying a Subscription Management Response Message
MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'
#: Constant identifying a Poll Request Message
MSG_POLL_REQUEST = 'Poll_Request'
#: Constant identifying a Poll Response Message
MSG_POLL_RESPONSE = 'Poll_Response'
#: Constant identifying a Inbox Message
MSG_INBOX_MESSAGE = 'Inbox_Message'

#: TAXII 1.0 Message Types
MSG_TYPES_10 = (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE,
                MSG_FEED_INFORMATION_REQUEST, MSG_FEED_INFORMATION_RESPONSE,
                MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST,
                MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE, MSG_POLL_REQUEST,
                MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE)

# New Message Types in TAXII 1.1

#: Constant identifying a Status Message
MSG_POLL_FULFILLMENT_REQUEST = 'Poll_Fulfillment'
#: Constant identifying a Collection Information Request
MSG_COLLECTION_INFORMATION_REQUEST = 'Collection_Information_Request'
#: Constant identifying a Collection Information Response
MSG_COLLECTION_INFORMATION_RESPONSE = 'Collection_Information_Response'
#: Constant identifying a Subscription Request
MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
#: Constant identifying a Subscription Response
MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'

#: Tuple of all TAXII 1.1 Message Types
MSG_TYPES_11 = (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE,
                MSG_COLLECTION_INFORMATION_REQUEST, MSG_COLLECTION_INFORMATION_RESPONSE,
                MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST,
                MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE, MSG_POLL_REQUEST,
                MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE, MSG_POLL_FULFILLMENT_REQUEST)

# TAXII 1.0 Status Types

#: Constant identifying a Status Type of Bad Message
ST_BAD_MESSAGE = 'BAD_MESSAGE'
#: Constant identifying a Status Type of Denied
ST_DENIED = 'DENIED'
#: Constant identifying a Status Type of Failure
ST_FAILURE = 'FAILURE'
#: Constant identifying a Status Type of Not Found
ST_NOT_FOUND = 'NOT_FOUND'
#: Constant identifying a Status Type of Polling Unsupported
ST_POLLING_UNSUPPORTED = 'POLLING_UNSUPPORTED'
#: Constant identifying a Status Type of Retry
ST_RETRY = 'RETRY'
#: Constant identifying a Status Type of Success
ST_SUCCESS = 'SUCCESS'
#: Constant identifying a Status Type of Unauthorized
ST_UNAUTHORIZED = 'UNAUTHORIZED'
#: Constant identifying a Status Type of Unsupported Message Binding
ST_UNSUPPORTED_MESSAGE_BINDING = 'UNSUPPORTED_MESSAGE'
#: Constant identifying a Status Type of Unsupported Content Binding
ST_UNSUPPORTED_CONTENT_BINDING = 'UNSUPPORTED_CONTENT'
#: Constant identifying a Status Type of Unsupported Protocol Binding
ST_UNSUPPORTED_PROTOCOL = 'UNSUPPORTED_PROTOCOL'

#: Tuple of all TAXII 1.0 Status Types
ST_TYPES_10 = (ST_BAD_MESSAGE, ST_DENIED, ST_FAILURE, ST_NOT_FOUND,
               ST_POLLING_UNSUPPORTED, ST_RETRY, ST_SUCCESS, ST_UNAUTHORIZED,
               ST_UNSUPPORTED_MESSAGE_BINDING, ST_UNSUPPORTED_CONTENT_BINDING,
               ST_UNSUPPORTED_PROTOCOL)

# New Status Types in TAXII 1.1

#: Constant identifying a Status Type of Asynchronous Poll Error
ST_ASYNCHRONOUS_POLL_ERROR = 'ASYNCHRONOUS_POLL_ERROR'
#: Constant identifying a Status Type of Destination Collection Error
ST_DESTINATION_COLLECTION_ERROR = 'DESTINATION_COLLECTION_ERROR'
#: Constant identifying a Status Type of Invalid Response Part
ST_INVALID_RESPONSE_PART = 'INVALID_RESPONSE_PART'
#: Constant identifying a Status Type of Network Error
ST_NETWORK_ERROR = 'NETWORK_ERROR'
#: Constant identifying a Status Type of Pending
ST_PENDING = 'PENDING'
#: Constant identifying a Status Type of Unsupported Query Format
ST_UNSUPPORTED_QUERY = 'UNSUPPORTED_QUERY'

#: Tuple of all TAXII 1.1 Status types
ST_TYPES_11 = (ST_ASYNCHRONOUS_POLL_ERROR, ST_BAD_MESSAGE, ST_DENIED,
               ST_DESTINATION_COLLECTION_ERROR, ST_FAILURE, ST_INVALID_RESPONSE_PART,
               ST_NETWORK_ERROR, ST_NOT_FOUND, ST_PENDING, ST_POLLING_UNSUPPORTED,
               ST_RETRY, ST_SUCCESS, ST_UNAUTHORIZED, ST_UNSUPPORTED_MESSAGE_BINDING,
               ST_UNSUPPORTED_CONTENT_BINDING, ST_UNSUPPORTED_PROTOCOL,
               ST_UNSUPPORTED_QUERY)

# TAXII 1.0 Action Types

#: Constant identifying an Action of Subscribe
ACT_SUBSCRIBE = 'SUBSCRIBE'
#: Constant identifying an Action of Unsubscribe
ACT_UNSUBSCRIBE = 'UNSUBSCRIBE'
#: Constant identifying an Action of Status
ACT_STATUS = 'STATUS'

#: Tuple of all TAXII 1.0 Action Types
ACT_TYPES_10 = (ACT_SUBSCRIBE, ACT_UNSUBSCRIBE, ACT_STATUS)

#: Constant identifying an Action of Pause
ACT_PAUSE = 'PAUSE'
#: Constant identifying an Action of Resume
ACT_RESUME = 'RESUME'

#: Tuple of all TAXII 1.1 Action types
ACT_TYPES_11 = (ACT_SUBSCRIBE, ACT_PAUSE, ACT_RESUME, ACT_UNSUBSCRIBE, ACT_STATUS)

# TAXII 1.0 Service Types

#: Constant identifying a Service Type of Inbox
SVC_INBOX = 'INBOX'
#: Constant identifying a Service Type of Poll
SVC_POLL = 'POLL'
#: Constant identifying a Service Type of Feed Management
SVC_FEED_MANAGEMENT = 'FEED_MANAGEMENT'
#: Constant identifying a Service Type of Discovery
SVC_DISCOVERY = 'DISCOVERY'

#: Tuple of all TAXII 1.0 Service Types
SVC_TYPES_10 = (SVC_INBOX, SVC_POLL, SVC_FEED_MANAGEMENT, SVC_DISCOVERY)

# Renamed Status Types in TAXII 1.1
#: Constant identifying a Service Type of Collection Management.
#: "Feed Management" was renamed to "Collection Management" in TAXII 1.1.
SVC_COLLECTION_MANAGEMENT = 'COLLECTION_MANAGEMENT'

#: Tuple of all TAXII 1.1 Service Types
SVC_TYPES_11 = (SVC_INBOX, SVC_POLL, SVC_COLLECTION_MANAGEMENT, SVC_DISCOVERY)

# TAXII 1.1 Subscription Statuses

#: Subscription Status of Active
SS_ACTIVE = 'ACTIVE'
#: Subscription Status of Paused
SS_PAUSED = 'PAUSED'
#: Subscription Status of Unsubscribed
SS_UNSUBSCRIBED = 'UNSUBSCRIBED'

#: Tuple of all TAXII 1.1 Subscription Statues
SS_TYPES_11 = (SS_ACTIVE, SS_PAUSED, SS_UNSUBSCRIBED)

# TAXII 1.1 Response Types

#: Constant identifying a response type of Full
RT_FULL = 'FULL'
#: Constant identifying a response type of Count only
RT_COUNT_ONLY = 'COUNT_ONLY'

#: Tuple of all TAXII 1.1 Response Types
RT_TYPES_11 = (RT_FULL, RT_COUNT_ONLY)

# TAXII 1.1 Response Types

#: Constant identifying a collection type of Data Feed
CT_DATA_FEED = 'DATA_FEED'
#: Constant identifying a collection type of Data Set
CT_DATA_SET = 'DATA_SET'

#: Tuple of all TAXII 1.1 Collection Types
CT_TYPES_11 = (CT_DATA_FEED, CT_DATA_SET)

# TAXII 1.1 Status Detail Keys

#: Constant Identifying the Acceptable Destination Status Detail
SD_ACCEPTABLE_DESTINATION = 'ACCEPTABLE_DESTINATION'
#: Constant Identifying the Max Part Number Status Detail
SD_MAX_PART_NUMBER = 'MAX_PART_NUMBER'
#: Constant Identifying the Item Status Detail
SD_ITEM = 'ITEM'
#: Constant Identifying the Estimated Wait Status Detail
SD_ESTIMATED_WAIT = 'ESTIMATED_WAIT'
#: Constant Identifying the Result ID Status Detail
SD_RESULT_ID = 'RESULT_ID'
#: Constant Identifying the Will Push Status Detail
SD_WILL_PUSH = 'WILL_PUSH'
#: Constant Identifying the Supported Binding Status Detail
SD_SUPPORTED_BINDING = 'SUPPORTED_BINDING'
#: Constant Identifying the Supported Content Status Detail
SD_SUPPORTED_CONTENT = 'SUPPORTED_CONTENT'
#: Constant Identifying the Supported Protocol Status Detail
SD_SUPPORTED_PROTOCOL = 'SUPPORTED_PROTOCOL'
#: Constant Identifying the Supported Query Status Detail
SD_SUPPORTED_QUERY = 'SUPPORTED_QUERY'

#: Tuple of all TAXII 1.1 Status Detail Keys
SD_TYPES_11 = (SD_ACCEPTABLE_DESTINATION, SD_MAX_PART_NUMBER, SD_ITEM,
               SD_ESTIMATED_WAIT, SD_RESULT_ID, SD_WILL_PUSH,
               SD_SUPPORTED_BINDING, SD_SUPPORTED_CONTENT, SD_SUPPORTED_PROTOCOL,
               SD_SUPPORTED_QUERY)

#: (For TAXII Default Query) Constant identifying supported Capability Modules
SD_CAPABILITY_MODULE = 'CAPABILITY_MODULE'
#: (For TAXII Default Query) Constant identifying Preferred Scopes
SD_PREFERRED_SCOPE = 'PREFERRED_SCOPE'
#: (For TAXII Default Query) Constant identifying Allowed Scopes
SD_ALLOWED_SCOPE = 'ALLOWED_SCOPE'
#: (For TAXII Default Query) Constant identifying supported Targeting Expression IDs
SD_TARGETING_EXPRESSION_ID = 'TARGETING_EXPRESSION_ID'

#: Format ID for this version of TAXII Default Query
FID_TAXII_DEFAULT_QUERY_10 = 'urn:taxii.mitre.org:query:default:1.0'

# Capability Module IDs
#: Capability Module ID for Core
CM_CORE = 'urn:taxii.mitre.org:query:capability:core-1'
#: Capability Module ID for Regex
CM_REGEX = 'urn:taxii.mitre.org:query:capability:regex-1'
#: Capability Module ID for Timestamp
CM_TIMESTAMP = 'urn:taxii.mitre.org:query:capability:timestamp-1'

#: Tuple of all capability modules defined in TAXII Default Query 1.0
CM_IDS = (CM_CORE, CM_REGEX, CM_TIMESTAMP)

# Operators
#: Operator OR
OP_OR = 'OR'
#: Operator AND
OP_AND = 'AND'

#: Tuple of all operators
OP_TYPES = (OP_OR, OP_AND)


#: Status Type indicating an unsupported capability module
ST_UNSUPPORTED_CAPABILITY_MODULE = 'UNSUPPORTED_CAPABILITY_MODULE'
#: Status Type indicating an unsupported targeting expression
ST_UNSUPPORTED_TARGETING_EXPRESSION = 'UNSUPPORTED_TARGETING_EXPRESSION'
#: Status Type indicating an unsupported targeting expression id
ST_UNSUPPORTED_TARGETING_EXPRESSION_ID = 'UNSUPPORTED_TARGETING_EXPRESSION_ID'

#: Parameter name: value
P_VALUE = 'value'
#: Parameter name: match_type
P_MATCH_TYPE = 'match_type'
#: Parameter name: case_sensitive
P_CASE_SENSITIVE = 'case_sensitive'

#: Tuple of all parameter names
P_NAMES = (P_VALUE, P_MATCH_TYPE, P_CASE_SENSITIVE)

#: Relationship name: equals
R_EQUALS = 'equals'
#: Relationship name: not_requals
R_NOT_EQUALS = 'not_equals'
#: Relationship name: greater_than
R_GREATER_THAN = 'greater_than'
#: Relationship name: greater_than_or_equal
R_GREATER_THAN_OR_EQUAL = 'greater_than_or_equal'
#: Relationship name: less_than
R_LESS_THAN = 'less_than'
#: Relationship name: less_than_or_equal
R_LESS_THAN_OR_EQUAL = 'less_than_or_equal'
#: Relationship name: does_not_exist
R_DOES_NOT_EXIST = 'does_not_exist'
#: Relationship name: exists
R_EXISTS = 'exists'
#: Relationship name: begins_with
R_BEGINS_WITH = 'begins_with'
#: Relationship name: ends_with
R_ENDS_WITH = 'ends_with'
#: Relationship name: contains
R_CONTAINS = 'contains'
#: Relationship name: matches
R_MATCHES = 'matches'

#: Tuple of all relationship names
R_NAMES = (R_EQUALS, R_NOT_EQUALS, R_GREATER_THAN,
           R_GREATER_THAN_OR_EQUAL, R_LESS_THAN,
           R_LESS_THAN_OR_EQUAL, R_DOES_NOT_EXIST,
           R_EXISTS, R_BEGINS_WITH, R_ENDS_WITH,
           R_CONTAINS, R_MATCHES)

# TAXII Version IDs #

#: Version ID for the TAXII Services Specification 1.0
VID_TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
#: Version ID for the TAXII Services Specification 1.1
VID_TAXII_SERVICES_11 = 'urn:taxii.mitre.org:services:1.1'
#: Version ID for the TAXII XML Message Binding Specification 1.0
VID_TAXII_XML_10 = 'urn:taxii.mitre.org:message:xml:1.0'
#: Version ID for the TAXII XML Message Binding Specification 1.1
VID_TAXII_XML_11 = 'urn:taxii.mitre.org:message:xml:1.1'
#: Version ID for the TAXII HTTP Protocol Binding Specification 1.0
VID_TAXII_HTTP_10 = 'urn:taxii.mitre.org:protocol:http:1.0'
#: Version ID for the TAXII HTTPS Protocol Binding Specification 1.0
VID_TAXII_HTTPS_10 = 'urn:taxii.mitre.org:protocol:https:1.0'

# Third Party Version IDs
#: Version ID for the CERT EU JSON Message Binding
VID_CERT_EU_JSON_10 = 'urn:cert.europa.eu:message:json:1.0'


# TAXII Content Bindings #

#: Content Binding ID for STIX XML 1.0
CB_STIX_XML_10 = 'urn:stix.mitre.org:xml:1.0'
#: Content Binding ID for STIX XML 1.0.1
CB_STIX_XML_101 = 'urn:stix.mitre.org:xml:1.0.1'
#: Content Binding ID for STIX XML 1.1
CB_STIX_XML_11 = 'urn:stix.mitre.org:xml:1.1'
#: Content Binding ID for STIX XML 1.1.1
CB_STIX_XML_111 = 'urn:stix.mitre.org:xml:1.1.1'
#: Content Binding ID for CAP 1.1
CB_CAP_11 = 'urn:oasis:names:tc:emergency:cap:1.1'
#: Content Binding ID for XML Encryption
CB_XENC_122002 = 'http://www.w3.org/2001/04/xmlenc#'
#: Content Binding ID for SMIME
CB_SMIME = 'application/x-pks7-mime'

STD_INDENT = '  '  # A "Standard Indent" to use for to_text() methods
