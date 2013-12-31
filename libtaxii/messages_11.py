""" 
| Copyright (C) 2013 - The MITRE Corporation
| For license information, see the LICENSE.txt file

| Contributors:
 
* Alex Ciobanu - calex@cert.europa.eu  
* Mark Davidson - mdavidson@mitre.org  
* Bryan Worrell - bworrell@mitre.org

"""

import datetime
import dateutil.parser
import collections
import re
from lxml import etree
import StringIO
import os

from operator import attrgetter

#Import the message names that haven't changed
from libtaxii.messages_10 import (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE, MSG_POLL_REQUEST,
    MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE)

#Define the new message name
#:Constant identifying a Status Message
MSG_POLL_FULFILLMENT_REQUEST = 'Poll_Fulfillment'

#:Constant identifying a Collection Information Request
MSG_COLLECTION_INFORMATION_REQUEST = 'Collection_Information_Request'

#:Constant identifying a Collection Information Response
MSG_COLLECTION_INFORMATION_RESPONSE = 'Collection_Information_Response'

#:Constant identifying a Subscription Request
MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'

#:Constant identifying a Subscription Response
MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'

# Tuple of all message types
MSG_TYPES = (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE, MSG_COLLECTION_INFORMATION_REQUEST, 
             MSG_COLLECTION_INFORMATION_RESPONSE, MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST, MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE,
             MSG_POLL_REQUEST, MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE, MSG_POLL_FULFILLMENT_REQUEST)

#Import the status types that haven't changed
from libtaxii.messages_10 import (ST_BAD_MESSAGE, ST_DENIED, ST_FAILURE, ST_NOT_FOUND, ST_POLLING_UNSUPPORTED, ST_RETRY, 
            ST_SUCCESS, ST_UNAUTHORIZED, ST_UNSUPPORTED_MESSAGE_BINDING, ST_UNSUPPORTED_CONTENT_BINDING, ST_UNSUPPORTED_PROTOCOL)

#Define the new status types
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

#Tuple of all status types
ST_TYPES = (ST_ASYNCHRONOUS_POLL_ERROR, ST_BAD_MESSAGE, ST_DENIED, ST_DESTINATION_COLLECTION_ERROR, ST_FAILURE, 
            ST_INVALID_RESPONSE_PART, ST_NETWORK_ERROR, ST_NOT_FOUND, ST_PENDING, ST_POLLING_UNSUPPORTED, ST_RETRY, ST_SUCCESS,
            ST_UNAUTHORIZED, ST_UNSUPPORTED_MESSAGE_BINDING, ST_UNSUPPORTED_CONTENT_BINDING, ST_UNSUPPORTED_PROTOCOL,
            ST_UNSUPPORTED_QUERY)

#Import actions that haven't changed
from libtaxii.messages_10 import (ACT_SUBSCRIBE, ACT_UNSUBSCRIBE, ACT_STATUS)

#Define the new actions
#: Constant identifying an Action of Pause
ACT_PAUSE = 'PAUSE'
#: Constant identifying an Action of Resume
ACT_RESUME = 'RESUME'

# Tuple of all actions
ACT_TYPES = (ACT_SUBSCRIBE, ACT_PAUSE, ACT_RESUME, ACT_UNSUBSCRIBE, ACT_STATUS)

RT_FULL = 'FULL'
RT_COUNT_ONLY = 'COUNT_ONLY'

RT_TYPES = (RT_FULL, RT_COUNT_ONLY)

#Import service types that haven't changed
from libtaxii.messages_10 import (SVC_INBOX, SVC_POLL, SVC_DISCOVERY)
#No new services in TAXII 1.1
SVC_COLLECTION_MANAGEMENT = 'COLLECTION_MANAGEMENT'

#A tuple of all service types
SVC_TYPES = (SVC_INBOX, SVC_POLL, SVC_COLLECTION_MANAGEMENT, SVC_DISCOVERY)

ns_map = {
            'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1',
            'taxii_11': 'http://taxii.mitre.org/messages/taxii_xml_binding-1.1',
         }

### General purpose helper methods ###

_RegexTuple = collections.namedtuple('_RegexTuple', ['regex','title'])
#URI regex per http://tools.ietf.org/html/rfc3986
_uri_regex = _RegexTuple("(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", "URI Format")
#_message_id_regex = _RegexTuple("[0-9]+", "Numbers only")

_none_error = "%s is not allowed to be None and the provided value was None"
_type_error = "%s must be of type %s. The incorrect value was of type %s"
_regex_error = "%s must be a string conforming to %s. The incorrect value was: %s"
_tuple_error = "%s must be one of %s. The incorrect value was %s"

def _do_check(var, varname, type=None, regex_tuple=None, value_tuple=None, can_be_none=False):
    """
    Checks supplied var against all of the supplied checks using the following
    process:
    
    1. If var is iterable, call this function for every item in the iterable object
    2. If the var is none and can be none, return
    3. If the var is none and cannot be none, raise ValueError
    4. If a type is specified, and the var is not of the specified type, raise ValueError
    5. If a regex is specified, and the var doesn't match the regex, raise ValueError
    6. If a value_tuple is specified, and the var is not in the value_tuple, raise ValueError
    
    varname is used in the error messages
    
    """
    
    if isinstance(var, list) or isinstance(var, set) or isinstance(var, tuple):
        x = 0
        for item in var:
            _do_check(item, "%s[%s]" % (varname, x), type, regex_tuple, value_tuple, can_be_none)
            x = x+1
        return
    
    if var is None and can_be_none:
        return
    
    if var is None and not can_be_none:
        raise ValueError(_none_error % varname)
    
    if type is not None:
        if not isinstance(var, type):
            bad_type = var.__class__.__name__
            raise ValueError(_type_error % (varname, type, bad_type))
    
    if regex_tuple is not None:
        if re.match(regex_tuple.regex, var) is None:
            raise ValueError(_regex_error % (varname, regex_tuple.title, var))
    
    if value_tuple is not None:
        if var not in value_tuple:
            raise ValueError(_tuple_error % (varname, value_tuple, var))
    return

def _check_timestamplabel(timestamp_label, varname, can_be_none=False):
    """
    Checks the timestamp_label to see if it is a valid timestamp label
    using the following process:
    
    1. If the timestamp_label is None and is allowed to be None, Pass
    2. If the timestamp_label is None and is not allowed to be None, Fail
    3. If the timestamp_label does not have a tzinfo attribute, Fail
    4. Pass
    """
    
    if timestamp_label is None and can_be_none:
        return
    
    if timestamp_label is None and not can_be_none:
        raise ValueError(_none_error % varname)

    _do_check(timestamp_label, varname, type=datetime.datetime, can_be_none=can_be_none)
    
    if timestamp_label.tzinfo is None:
        raise ValueError('%s.tzinfo must not be None!' % varname)
    
    return

def _str2datetime(date_string):
    """ Users of libtaxii should not use this function.
    Takes a date string and creates a datetime object
    """
    return dateutil.parser.parse(date_string)

#Import helper methods from libtaxii.messages_10 that are still applicable
from libtaxii.messages_10 import (generate_message_id)

global_xml_parser = None
def get_xml_parser():
    """ Get the XML Parser being used by libtaxii.messages. 
    This method instantiates an XML Parser with no_network=True and
    huge_tree=True if the XML Parser has not already been set via 
    set_xml_parser() """
    global global_xml_parser
    if global_xml_parser is None:
        global_xml_parser = etree.XMLParser(no_network=True, huge_tree=True)
    return global_xml_parser

def set_xml_parser(xml_parser=None):
    """ Set the libtaxii.messages XML parser. """
    global global_xml_parser
    global_xml_parser = xml_parser

def validate_xml(xml_string):
    """Validate XML with the TAXII XML Schema 1.0."""
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string
    
    etree_xml = etree.parse(f, get_xml_parser())
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XMLMessageBinding_Schema_11.xsd")
    taxii_schema_doc = etree.parse(schema_file, get_xml_parser())
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(etree_xml)
    if not valid:
        return xml_schema.error_log.last_error
    return valid

def get_message_from_xml(xml_string):
    """Create a TAXII Message object from an XML string.

    Note: This function auto-detects which TAXII Message should be created from
    the XML.
    """
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string

    etree_xml = etree.parse(f, get_xml_parser()).getroot()
    qn = etree.QName(etree_xml)
    if qn.namespace != ns_map['taxii_11']:
        raise ValueError('Unsupported namespace: %s' % qn.namespace)

    message_type = qn.localname

    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_etree(etree_xml)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_etree(etree_xml)
    if message_type == MSG_COLLECTION_INFORMATION_REQUEST:
        return CollectionInformationRequest.from_etree(etree_xml)
    if message_type == MSG_COLLECTION_INFORMATION_RESPONSE:
        return CollectionInformationResponse.from_etree(etree_xml)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_etree(etree_xml)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_etree(etree_xml)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_etree(etree_xml)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_etree(etree_xml)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST:
        return ManageCollectionSubscriptionRequest.from_etree(etree_xml)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE:
        return ManageCollectionSubscriptionResponse.from_etree(etree_xml)

    raise ValueError('Unknown message_type: %s' % message_type)


def get_message_from_dict(d):
    """Create a TAXII Message object from a dictionary.

    Note: This function auto-detects which TAXII Message should be created from
    the dictionary.
    """
    if 'message_type' not in d:
        raise ValueError('message_type is a required field!')

    message_type = d['message_type']
    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_dict(d)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_dict(d)
    if message_type == MSG_COLLECTION_INFORMATION_REQUEST:
        return CollectionInformationRequest.from_dict(d)
    if message_type == MSG_COLLECTION_INFORMATION_RESPONSE:
        return CollectionInformationResponse.from_dict(d)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_dict(d)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_dict(d)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_dict(d)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_dict(d)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST:
        return ManageCollectionSubscriptionRequest.from_dict(d)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE:
        return ManageCollectionSubscriptionResponse.from_dict(d)

    raise ValueError('Unknown message_type: %s' % message_type)


def get_message_from_json(json_string):
    """Create a TAXII Message object from a json string.
    
    Note: This function auto-detects which TAXII Message should be created form
    the JSON string.
    """
    return get_message_from_dict(json.loads(json_string))


from libtaxii.messages_10 import BaseNonMessage

query_deserializers = {}

def register_deserializers(format_id, query, query_information):
    query_deserializers[format_id] = {'query': query, 'query_info': query_information}
    
def get_deserializer(format_id, type):
    if type not in ['query','query_info']:
        return None#TODO: Raise error
    
    if format_id not in query_deserializers:
        return None#TODO: Raise error
    
    return query_deserializers[format_id][type]

class SupportedQuery(BaseNonMessage):
    def __init__(self, format_id):
        self.format_id = format_id
    
    @property
    def format_id(self):
        return self._format_id
    
    @format_id.setter
    def format_id(self, value):
        #TODO: Check the value
        self._format_id = value
    
    def to_etree(self):
        q = etree.Element('{%s}Supported_Query' % ns_map['taxii_11'])
        q.attrib['format_id'] = self.format_id
        return q
    
    def to_dict(self):
        return {'format_id': self.format_id}
    
    def __eq__(self, other, debug=False):
        if self.format_id != other.format_id:
            if debug:
                print 'format ids not equal: %s != %s' % (self.format_id, other.format_id)
        return True
    
    @staticmethod
    def from_etree(etree_xml):
        format_id = etree_xml.xpath('./@format_id', ns_map = nsmap)[0]
        return SupportedQuery(format_id)
    
    @staticmethod
    def from_dict(d):
        return SupportedQuery(**d)

class Query(BaseNonMessage):
    def __init__(self, format_id):
        self.format_id = format_id
    
    @property
    def format_id(self):
        return self._format_id
    
    @format_id.setter
    def format_id(self, value):
        #TODO: Check the value
        self._format_id = value
    
    def to_etree(self):
        q = etree.Element('{%s}Query' % nsmap['taxii_11'])
        q.attrib['format_id'] = self.format_id
        return q
    
    def to_dict(self):
        return {'format_id': self.format_id}
    
    def __eq__(self, other, debug=False):
        if self.format_id != other.format_id:
            if debug:
                print 'format ids not equal: %s != %s' % (self.format_id, other.format_id)
        return True
    
    @classmethod
    def from_etree(etree_xml):
        format_id = etree_xml.xpath('./@format_id', ns_map = nsmap)[0]
        return SupportedQuery(format_id)
    
    @classmethod
    def from_dict(d):
        return SupportedQuery(**d)

#A value can be one of:
# - a dictionary, where each key is a content_binding_id and each value is a list of subtypes
#   (This is the default representation)
# - a "content_binding_id[>subtype]" structure
# - a list of "content_binding_id[>subtype]" structures

class ContentBinding(BaseNonMessage):
    def __init__(self, binding_id, subtype_ids = None):
        self.binding_id = binding_id
        self.subtype_ids = subtype_ids or []
    
    @property
    def binding_id(self):
        return self._binding_id
    
    @binding_id.setter
    def binding_id(self, value):
        #TODO: check the value
        self._binding_id = value
    
    @property
    def subtype_ids(self):
        return self._subtype_ids
    
    @subtype_ids.setter
    def subtype_ids(self, value):
        #TODO: Check the value
        self._subtype_ids = value
    
    def to_etree(self):
        cb = etree.Element('{%s}Content_Binding' % ns_map['taxii_11'])
        cb.attrib['binding_id'] = self.binding_id
        for subtype_id in self.subtype_ids:
            s = etree.SubElement(cb, '{%s}Subtype' % ns_map['taxii_11'])
            s.attrib['subtype_id'] = subtype_id
        return cb
    
    def to_dict(self):
        return {'binding_id': self.binding_id, 'subtype_ids': self.subtype_ids}
    
    def __eq__(self, other, debug=False):
        if self.binding_id != other.binding_id:
            if debug:
                print 'binding_ids not equal: %s != %s' % (self.binding_id, other.binding_id)
            return False
        
        if set(self.subtype_ids) != set(other.subtype_ids):
            if debug:
                print 'subtype_ids not equal: %s != %s' % (self.subtype_ids, other.subtype_ids)
            return False
        
        return True
    
    @classmethod
    def from_etree(self, etree_xml):
        binding_id = etree_xml.attrib['binding_id']
        subtype_ids = []
        subtype_elts = etree_xml.xpath('./taxii_11:Subtype', namespaces=ns_map)
        for elt in subtype_elts:
            subtype_ids.append(elt.attrib['subtype_id'])
        return ContentBinding(binding_id, subtype_ids)
    
    @classmethod
    def from_dict(self, d):
        return ContentBinding(**d)

class PollParameters(BaseNonMessage):
    def __init__(self, allow_asynch=None, response_type=None, content_bindings=None, query=None, delivery_parameters=None):
        self.allow_asynch = allow_asynch
        self.response_type = response_type
        self.content_bindings = content_bindings or []
        self.query = query or []
        self.delivery_parameters = delivery_parameters
    
    @property
    def allow_asynch(self):
        return self._allow_asynch
    
    @allow_asynch.setter
    def allow_asynch(self, value):
        _do_check(value, 'allow_asynch', value_tuple=(True,False))
        self._allow_asynch = value
    
    @property
    def response_type(self):
        return self._response_type
    
    @response_type.setter
    def response_type(self, value)
        _do_check(value, 'response_type', value_tuple=RT_TYPES)
        self._response_type = value
    
    @property
    def content_bindings(self):
        return self._content_bindings
    
    @content_bindings.setter
    def content_bindings(self, value):
        _do_check(value, 'content_bindings', type=ContentBinding)
        self._content_bindings = value
    
    @property
    def query(self):
        return self._query
    
    @query.setter
    def query(self, value):
        _do_check(query, 'query', type=Query, can_be_none=True)
        self._query = value
    
    @property
    def delivery_parameters(self):
        return self._delivery_parameters
    
    @delivery_parameters.setter
    def delivery_paramters(self, value):
        _do_check(delivery_parameters, 'delivery_parameters', type=DeliveryParameters, can_be_none=False)
        self._delivery_parameters = value
    
    def to_etree(self):
        pp = etree.Element('{%s}Poll_Parameters' % ns_map['taxii_11'], ns_map = ns_map)
        if self.allow_asynch is not None:
            pp.attrib['allow_asynch'] = str(self.allow_asynch).lower
        if self.response_type is not None:
            rt = etree.SubElement(pp, '{%s}Response_Type' % ns_map['taxii_11'], ns_map = ns_map)
            rt.text = self.response_type
        for cb in self.content_bindings:
            pp.append(cb.to_etree())
        if self.query is not None:
            pp.append(self.query.to_etree())
        if self.delivery_parameters is not None:
            pp.append(self.delivery_parameters.to_etree())
        return pp
    
    def to_dict(self):
        pass
    
    def __eq__(self, other, debug):
        pass
    
    @staticmethod
    def from_etree(etree_xml):
        pass
    
    @staticmethod
    def from_dict(d):
        pass
    

class TAXIIMessage(BaseNonMessage):
    """Encapsulate properties common to all TAXII Messages (such as headers).

    This class is extended by each Message Type (e.g., DiscoveryRequest), with
    each subclass containing subclass-specific information
    """

    message_type = 'TAXIIMessage'

    def __init__(self, message_id, in_response_to=None, extended_headers=None):
        """Create a new TAXIIMessage

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        """
        self.message_id = message_id
        self.in_response_to = in_response_to
        self.extended_headers = extended_headers or {}

    
    @property
    def message_id(self):
        return self._message_id
    
    @message_id.setter
    def message_id(self, value):
        _do_check(value, 'message_id', regex_tuple=_uri_regex)
        self._message_id = value
    
    @property
    def in_response_to(self):
        return self._in_response_to
    
    @in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_message_id_regex, can_be_none=True)
        self._in_response_to = value
    
    @property
    def extended_headers(self):
        return self._extended_headers
    
    @extended_headers.setter
    def extended_headers(self, value):
        _do_check(value.keys(), 'extended_headers.keys()', regex_tuple=_uri_regex)
        self._extended_headers = value
    
    
    def to_etree(self):
        """Creates the base etree for the TAXII Message.

        Message-specific constructs must be added by each Message class. In
        general, when converting to XML, subclasses should call this method
        first, then create their specific XML constructs.
        """
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.message_type), nsmap=ns_map)
        root_elt.attrib['message_id'] = str(self.message_id)

        if self.in_response_to is not None:
            root_elt.attrib['in_response_to'] = str(self.in_response_to)

        if len(self.extended_headers) > 0:
            eh = etree.SubElement(root_elt, '{%s}Extended_Headers' % ns_map['taxii_11'])

            for name, value in self.extended_headers.items():
                h = etree.SubElement(eh, '{%s}Extended_Header' % ns_map['taxii_11'])
                h.attrib['name'] = name
                h.text = value
        return root_elt

    def to_dict(self):
        """Create the base dictionary for the TAXII Message.

        Message-specific constructs must be added by each Message class. In
        general, when converting to dictionary, subclasses should call this
        method first, then create their specific dictionary constructs.
        """
        d = {}
        d['message_type'] = self.message_type
        d['message_id'] = self.message_id
        if self.in_response_to is not None:
            d['in_response_to'] = self.in_response_to
        d['extended_headers'] = self.extended_headers

        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other, debug=False):
        if not isinstance(other, TAXIIMessage):
            raise ValueError('Not comparing two TAXII Messages! (%s, %s)' % (self.__class__.__name__, other.__class__.__name__))

        return self._checkPropertiesEq(other, ['message_type', 'message_id', 'in_response_to', 'extended_headers'], debug)

    def __ne__(self, other, debug=False):
        return not self.__eq__(other, debug)

    @classmethod
    def from_etree(cls, src_etree, **kwargs):
        """Pulls properties of a TAXII Message from an etree.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from etree, subclasses should call this method
        first, then parse their specific XML constructs.
        """

        #Get the message type
        message_type = src_etree.tag[55:]
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))

        #Get the message ID
        message_id = src_etree.xpath('/taxii_11:*/@message_id', namespaces=ns_map)[0]

        #Get in response to, if present
        in_response_to = None
        in_response_tos = src_etree.xpath('/taxii_11:*/@in_response_to', namespaces=ns_map)
        if len(in_response_tos) > 0:
            in_response_to = in_response_tos[0]

        #Get the Extended headers
        extended_header_list = src_etree.xpath('/taxii_11:*/taxii:Extended_Headers/taxii:Extended_Header', namespaces=ns_map)
        extended_headers = {}
        for header in extended_header_list:
            eh_name = header.xpath('./@name')[0]
            eh_value = header.text
            extended_headers[eh_name] = eh_value
        
        return cls(message_id, 
                   in_response_to, 
                   extended_headers=extended_headers,
                   **kwargs)

    @classmethod
    def from_xml(cls, xml):
        """Parse a Message from XML.

        Subclasses shouldn't implemnet this method, as it is mainly a wrapper
        for cls.from_etree.
        """
        if isinstance(xml, basestring):
            f = StringIO.StringIO(xml)
        else:
            f = xml

        etree_xml = etree.parse(f, get_xml_parser()).getroot()
        return cls.from_etree(etree_xml)

    @classmethod
    def from_dict(cls, d, **kwargs):
        """Pulls properties of a TAXII Message from a dictionary.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from dictionary, subclasses should call this
        method first, then parse their specific dictionary constructs.
        """
        message_type = d['message_type']
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))
        message_id = d['message_id']
        extended_headers = d['extended_headers']
        in_response_to = d.get('in_response_to')
        
        return cls(message_id, 
                   in_response_to, 
                   extended_headers=extended_headers, 
                   **kwargs)

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))
    

class DiscoveryRequest(TAXIIMessage):
    message_type = MSG_DISCOVERY_REQUEST

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

class DiscoveryResponse(TAXIIMessage):
    message_type = MSG_DISCOVERY_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, service_instances=None):
        """Create a DiscoveryResponse

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - the Message ID of the message to which this
          is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - service_instances (list of ServiceInstance objects) - a list of
          service instances that this response contains
        """
        super(DiscoveryResponse, self).__init__(message_id, in_response_to, extended_headers)
        if service_instances is None:
            self.service_instances = []
        else:
            self.service_instances = service_instances
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_uri_regex)
        self._in_response_to = value
    
    @property
    def service_instances(self):
        return self._service_instances
    
    @service_instances.setter
    def service_instances(self, value):
        _do_check(value, 'service_instances', type=DiscoveryResponse.ServiceInstance)
        self._service_instances = value
    
    def to_etree(self):
        xml = super(DiscoveryResponse, self).to_etree()
        for service_instance in self.service_instances:
            xml.append(service_instance.to_etree())
        return xml

    def to_dict(self):
        d = super(DiscoveryResponse, self).to_dict()
        d['service_instances'] = []
        for service_instance in self.service_instances:
            d['service_instances'].append(service_instance.to_dict())
        return d

    def to_json(self):#TODO: Should this be a method of the parent object?
        return json.dumps(self.to_dict())

    def __eq__(self, other, debug=False):
        if not super(DiscoveryResponse, self).__eq__(other, debug):
            return False

        if len(self.service_instances) != len(other.service_instances):
            if debug:
                print 'service_instance lengths not equal: %s != %s' % (len(self.service_instances), len(other.service_instances))
            return False

        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.service_instances, key=attrgetter('service_address')), sorted(other.service_instances, key=attrgetter('service_address'))):
            if item1 != item2:
                if debug:
                    print 'service instances not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)  # This will print why they are not equal
                return False

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(DiscoveryResponse, cls).from_etree(etree_xml)
        msg.service_instances = []
        service_instance_set = etree_xml.xpath('./taxii_11:Service_Instance', namespaces=ns_map)
        for service_instance in service_instance_set:
            si = DiscoveryResponse.ServiceInstance.from_etree(service_instance)
            msg.service_instances.append(si)
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(DiscoveryResponse, cls).from_dict(d)
        msg.service_instances = []
        service_instance_set = d['service_instances']
        for service_instance in service_instance_set:
            si = DiscoveryResponse.ServiceInstance.from_dict(service_instance)
            msg.service_instances.append(si)
        return msg

    class ServiceInstance(BaseNonMessage):

        def __init__(self, service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content=None, available=None, message=None, supported_query=None):
            """Create a new ServiceInstance.

            Arguments:
            - service_type (string) - identifies the Service Type of this
              Service Instance.
            - services_version (string) - identifies the TAXII Services
              Specification to which this Service conforms.
            - protocol_binding (string) - identifies the protocol binding
              supported by this Service
            - service_address (string) - identifies the network address of the
              TAXII Daemon that hosts this Service.
            - message_bindings (list of strings) - identifies the message
              bindings supported by this Service instance.
            - inbox_service_accepted_content (list of strings) - identifies
              content bindings that this Inbox Service is willing to accept
            - available (boolean) - indicates whether the identity of the
              requester (authenticated or otherwise) is allowed to access this
              TAXII  Service.
            - message (string) - contains a message regarding this Service
              instance.
            - supported_query (SupportedQuery) - contains a structure indicating a supported query
            """
            self.service_type = service_type
            self.services_version = services_version
            self.protocol_binding = protocol_binding
            self.service_address = service_address
            self.message_bindings = message_bindings
            self.inbox_service_accepted_content = inbox_service_accepted_content or []
            self.available = available
            self.message = message
            self.supported_query = supported_query or []

        
        @property
        def service_type(self):
            return self._service_type
        
        @service_type.setter
        def service_type(self, value):
            _do_check(value, 'service_type', value_tuple=SVC_TYPES)
            self._service_type = value
        
        @property
        def services_version(self):
            return self._services_version
        
        @services_version.setter
        def services_version(self, value):
            _do_check(value, 'services_version', regex_tuple=_uri_regex)
            self._services_version = value
        
        @property
        def protocol_binding(self):
            return self._protocol_binding
        
        @protocol_binding.setter
        def protocol_binding(self, value):
            _do_check(value, 'protocol_binding', regex_tuple=_uri_regex)
            self._protocol_binding = value
        
        @property
        def service_address(self):
            return self._service_address
        
        @service_address.setter
        def service_address(self, value):
            self._service_address = value
        
        @property
        def message_bindings(self):
            return self._message_bindings
        
        @message_bindings.setter
        def message_bindings(self, value):
            _do_check(value, 'message_bindings', regex_tuple=_uri_regex)
            self._message_bindings = value
        
        @property
        def supported_query(self):
            return self._supported_query
        
        @supported_query.setter
        def supported_query(self, value):
            _do_check(value, 'supported_query', type=SupportedQuery)
            self._supported_query = value
        
        @property
        def inbox_service_accepted_content(self):
            return self._inbox_service_accepted_content
        
        @inbox_service_accepted_content.setter
        def inbox_service_accepted_content(self, value):
            _do_check(value, 'inbox_service_accepted_content', type=ContentBinding)
            self._inbox_service_accepted_content = value
        
        @property
        def available(self):
            return self._available
        
        @available.setter
        def available(self, value):
            _do_check(value, 'available', value_tuple=(True, False), can_be_none=True)
            self._available = value
        
        @property
        def service_type(self):
            return self._service_type
        
        @service_type.setter
        def service_type(self, value):
            _do_check(value, 'service_type', value_tuple=SVC_TYPES)
            self._service_type = value

        def to_etree(self):
            si = etree.Element('{%s}Service_Instance' % ns_map['taxii_11'])
            si.attrib['service_type'] = self.service_type
            si.attrib['service_version'] = self.services_version
            if self.available is not None:
                si.attrib['available'] = str(self.available).lower()

            protocol_binding = etree.SubElement(si, '{%s}Protocol_Binding' % ns_map['taxii_11'])
            protocol_binding.text = self.protocol_binding

            service_address = etree.SubElement(si, '{%s}Address' % ns_map['taxii_11'])
            service_address.text = self.service_address

            for mb in self.message_bindings:
                message_binding = etree.SubElement(si, '{%s}Message_Binding' % ns_map['taxii_11'])
                message_binding.text = mb
            
            for sq in self.supported_query:
                si.append(sq.to_etree())
            
            for cb in self.inbox_service_accepted_content:
                content_binding = cb.to_etree()
                si.append(content_binding)

            if self.message is not None:
                message = etree.SubElement(si, '{%s}Message' % ns_map['taxii_11'])
                message.text = self.message

            return si

        def to_dict(self):
            d = {}
            d['service_type'] = self.service_type
            d['services_version'] = self.services_version
            d['protocol_binding'] = self.protocol_binding
            d['service_address'] = self.service_address
            d['message_bindings'] = self.message_bindings
            d['supported_query'] = []
            for sq in self.supported_query:
                d['supported_query'].append(sq.to_dict())
            d['inbox_service_accepted_content'] = self.inbox_service_accepted_content
            d['available'] = self.available
            d['message'] = self.message
            return d

        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['service_type', 'services_version', 'protocol_binding', 'service_address', 'available', 'message'], debug):
                return False
            
            if set(self.message_bindings) != set(other.message_bindings):
                if debug:
                    print 'message_bindings not equal'
                return False

            if len(self.inbox_service_accepted_content) != len(other.inbox_service_accepted_content):
                if debug:
                    print 'inbox_service_accepted_contents lengths not equal: %s != %s' % (len(self.inbox_service_accepted_content),  len(other.inbox_service_accepted_content))
                return False
            
            #Who knows if this is a good way to compare the inbox_service_accepted_contents or not...
            for item1, item2 in zip(sorted(self.inbox_service_accepted_content), sorted(other.inbox_service_accepted_content)):
                if item1 != item2:
                    if debug:
                        print 'inbox_service_accepted_contents not equal: %s != %s' % (item1, item2)
                        item1.__eq__(item2, debug)  # This will print why they are not equal
                    return False
            
            if len(self.supported_query) != len(other.supported_query):
                if debug:
                    print 'supported_query lengths not equal: %s != %s' % (len(self.supported_query), len(other.supported_query))
                return False
            
            #Who knows if this is a good way to compare the supported_query or not...
            for item1, item2 in zip(sorted(self.supported_query), sorted(other.supported_query)):
                if item1 != item2:
                    if debug:
                        print ' supported_query not equal: %s != %s' % (item1, item2)
                        item1.__eq__(item2, debug)  # This will print why they are not equal
                    return False
            
            return True

        @staticmethod
        def from_etree(etree_xml):  # Expects a taxii:Service_Instance element
            service_type = etree_xml.attrib['service_type']
            services_version = etree_xml.attrib['service_version']
            available = None
            if 'available' in etree_xml.attrib:
                tmp_available = etree_xml.attrib['available']
                available = tmp_available == 'True'

            protocol_binding = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
            service_address = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text

            message_bindings = []
            message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
            for mb in message_binding_set:
                message_bindings.append(mb.text)

            inbox_service_accepted_content = []
            inbox_service_accepted_content_set = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)
            for cb in inbox_service_accepted_content_set:
                inbox_service_accepted_content.append(ContentBinding.from_etree(cb))
            
            supported_query = []
            supported_query_set = etree_xml.xpath('./taxii_11:Supported_Query', namespaces=ns_map)
            for sq in supported_query_set:
                format_id = sq.xpath('./@format_id')[0]
                if format_id in query_deserializers:
                    query_obj = get_deserializer(format_id, 'query_info').from_etree(sq)
                    supported_query.append(query_obj)
                else:
                    raise Error('No query deserializer registered for %s' % format_id)
            
            message = None
            message_set = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
            if len(message_set) > 0:
                message = message_set[0].text

            return DiscoveryResponse.ServiceInstance(service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content, available, message, supported_query)
        
        @staticmethod
        def from_dict(d):
            service_type = d['service_type']
            services_version = d['services_version']
            protocol_binding = d['protocol_binding']
            service_address = d['service_address']
            message_bindings = d['message_bindings']
            supported_query = []
            sq_list = d.get('supported_query')
            if sq_list is not None:
                for sq in sq_list:
                    format_id = sq['format_id']
                    if format_id in query_deserializers:
                        query_obj = get_deserializer(format_id, 'query_info').from_dict(sq)
                        supported_query.append(query_obj)
                    else:#The query format is unregistered
                        raise Error('No query deserializer registered for %s' % format_id)
            inbox_service_accepted_content = d.get('inbox_service_accepted_content')
            available = d.get('available')
            message = d.get('message')
            
            return DiscoveryResponse.ServiceInstance(service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content, available, message, supported_query)

class CollectionInformationRequest(TAXIIMessage):
    message_type = MSG_COLLECTION_INFORMATION_REQUEST
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

class CollectionInformationResponse(TAXIIMessage):
    message_type = MSG_COLLECTION_INFORMATION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, collection_informations=None):
        """Create a new CollectionInformationResponse.

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - the Message ID of the message to which this
          is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - collection_informations (list of CollectionInformation objects) - A list of
          CollectionInformation objects to be contained in this response
        """
        super(CollectionInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        if collection_informations is None:
            self.collection_informations = []
        else:
            self.collection_informations = collection_informations
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_uri_regex)
        self._in_response_to = value
    
    @property
    def collection_informations(self):
        return self._collection_informations
    
    @collection_informations.setter
    def collection_informations(self, value):
        _do_check(value, 'collection_informations', type=CollectionInformationResponse.CollectionInformation)
        self._collection_informations = value
    
    def to_etree(self):
        xml = super(CollectionInformationResponse, self).to_etree()
        for collection in self.collection_informations:
            xml.append(collection.to_etree())
        return xml

    def to_dict(self):
        d = super(CollectionInformationResponse, self).to_dict()
        d['collection_informations'] = []
        for collection in self.collection_informations:
            d['collection_informations'].append(collection.to_dict())
        return d

    def __eq__(self, other, debug=False):
        if not super(CollectionInformationResponse, self).__eq__(other, debug):
            return False

        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.collection_informations), sorted(other.collection_informations)):
            if item1 != item2:
                if debug:
                    print 'collection_informations not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)  # This will print why they are not equal
                return False

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(CollectionInformationResponse, cls).from_etree(etree_xml)
        msg.collection_informations = []
        collection_informations = etree_xml.xpath('./taxii:Collection', namespaces=ns_map)
        for collection in collection_informations:
            msg.collection_informations.append(CollectionInformationResponse.CollectionInformation.from_etree(collection))
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(CollectionInformationResponse, cls).from_dict(d)
        msg.collection_informations = []
        for collection in d['collection_informations']:
            msg.collection_informations.append(CollectionInformationResponse.CollectionInformation.from_dict(collection))
        return msg

    class CollectionInformation(BaseNonMessage):

        def __init__(self, collection_name, collection_description, supported_contents, available=None, push_methods=None, polling_service_instances=None, subscription_methods=None):
            """Create a new CollectionInformation

            Arguments:
            - collection_name (string) - the name by which this TAXII Data Collection is
              identified.
            - collection_description (string) - a prose description of this TAXII
              Data Collection.
            - supported_contents (list of strings) - Content Binding IDs
              indicating which types of content are currently expressed in this
              TAXII Data Collection.
            - available (boolean) - whether the identity of the requester
              (authenticated or otherwise) is allowed to access this TAXII
              Service.
            - push_methods (list of PushMethod objects) - the protocols that
              can be used to push content via a subscription.
            - polling_service_instances (list of PollingServiceInstance
              objects) - the bindings and address a Consumer can use to
              interact with a Poll Service instance that supports this TAXII
              Data Collection.
            - subscription_methods (list of SubscriptionMethod objects) - the
              protocol and address of the TAXII Daemon hosting the Collection
              Management Service that can process subscriptions for this TAXII
              Data Collection.
            """
            self.collection_name = collection_name
            self.available = available
            self.collection_description = collection_description
            self.supported_contents = supported_contents
            self.push_methods = push_methods or []
            self.polling_service_instances = polling_service_instances or []
            self.subscription_methods = subscription_methods or []

        @property
        def collection_name(self):
            return self._collection_name
        
        @collection_name.setter
        def collection_name(self, value):
            _do_check(value, 'collection_name', regex_tuple=_uri_regex)
            self._collection_name = value
        
        @property
        def available(self):
            return self._available
        
        @available.setter
        def available(self, value):
            _do_check(value, 'available', value_tuple=(True, False), can_be_none=True)
            self._available = value
        
        @property
        def supported_contents(self):
            return self._supported_contents
        
        @supported_contents.setter
        def supported_contents(self, value):
            _do_check(value, 'supported_contents', type=ContentBinding)
            self._supported_contents = value
        
        @property
        def push_methods(self):
            return self._push_methods
        
        @push_methods.setter
        def push_methods(self, value):
            _do_check(value, 'push_methods', type=CollectionInformationResponse.CollectionInformation.PushMethod)
            self._push_methods = value
        
        @property
        def polling_service_instances(self):
            return self._polling_service_instances
        
        @polling_service_instances.setter
        def polling_service_instances(self, value):
            _do_check(value, 'polling_service_instances', type=CollectionInformationResponse.CollectionInformation.PollingServiceInstance)
            self._polling_service_instances = value
        
        @property
        def subscription_methods(self):
            return self._subscription_methods
        
        @subscription_methods.setter
        def subscription_methods(self, value):
            _do_check(value, 'subscription_methods', type=CollectionInformationResponse.CollectionInformation.SubscriptionMethod)
            self._subscription_methods = value
        
        def to_etree(self):
            c = etree.Element('{%s}Collection' % ns_map['taxii_11'])
            c.attrib['collection_name'] = self.collection_name
            if self.available is not None:
                c.attrib['available'] = str(self.available).lower()
            collection_description = etree.SubElement(c, '{%s}Description' % ns_map['taxii_11'])
            collection_description.text = self.collection_description

            for binding in self.supported_contents:
                c.append(binding.to_etree())

            for push_method in self.push_methods:
                c.append(push_method.to_etree())

            for polling_service in self.polling_service_instances:
                c.append(polling_service.to_etree())

            for subscription_method in self.subscription_methods:
                c.append(subscription_method.to_etree())

            return c

        def to_dict(self):
            d = {}
            d['collection_name'] = self.collection_name
            if self.available is not None:
                d['available'] = self.available
            d['collection_description'] = self.collection_description
            d['supported_contents'] = self.supported_contents
            d['push_methods'] = []
            for push_method in self.push_methods:
                d['push_methods'].append(push_method.to_dict())
            d['polling_services'] = []
            for polling_service in self.polling_service_instances:
                d['polling_services'].append(polling_service.to_dict())
            d['subscription_methods'] = []
            for subscription_method in self.subscription_methods:
                d['subscription_methods'].append(subscription_method.to_dict())
            return d

        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['collection_name', 'collection_description', 'available'], debug):
                return False

            if set(self.supported_contents) != set(other.supported_contents):
                if debug:
                    print 'supported_contents not equal: %s != %s' % (self.supported_contents, other.supported_contents)
                return False

            #TODO: Test equality of: push_methods=[], polling_service_instances=[], subscription_methods=[]

            return True

        @staticmethod
        def from_etree(etree_xml):
            kwargs = {}
            kwargs['collection_name'] = etree_xml.attrib['collection_name']
            kwargs['available'] = None
            if 'available' in etree_xml.attrib:
                tmp = etree_xml.attrib['available']
                kwargs['available'] = tmp == 'True'

            kwargs['collection_description'] = etree_xml.xpath('./taxii:Description', namespaces=ns_map)[0].text
            kwargs['supported_contents'] = []
            supported_content_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for binding_elt in supported_content_set:
                kwargs['supported_contents'].append(binding_elt.text)

            kwargs['push_methods'] = []
            push_method_set = etree_xml.xpath('./taxii:Push_Method', namespaces=ns_map)
            for push_method_elt in push_method_set:
                kwargs['push_methods'].append(CollectionInformationResponse.CollectionInformation.PushMethod.from_etree(push_method_elt))

            kwargs['polling_service_instances'] = []
            polling_service_set = etree_xml.xpath('./taxii:Polling_Service', namespaces=ns_map)
            for polling_elt in polling_service_set:
                kwargs['polling_service_instances'].append(CollectionInformationResponse.CollectionInformation.PollingServiceInstance.from_etree(polling_elt))

            kwargs['subscription_methods'] = []
            subscription_method_set = etree_xml.xpath('./taxii:Subscription_Service', namespaces=ns_map)
            for subscription_elt in subscription_method_set:
                kwargs['subscription_methods'].append(CollectionInformationResponse.CollectionInformation.SubscriptionMethod.from_etree(subscription_elt))

            return CollectionInformationResponse.CollectionInformation(**kwargs)

        @staticmethod
        def from_dict(d):
            kwargs = {}
            kwargs['collection_name'] = d['collection_name']
            kwargs['available'] = d.get('available')

            kwargs['collection_description'] = d['collection_description']
            kwargs['supported_contents'] = []
            for binding in d.get('supported_contents', []):
                kwargs['supported_contents'].append(binding)

            kwargs['push_methods'] = []
            for push_method in d.get('push_methods', []):
                kwargs['push_methods'].append(CollectionInformationResponse.CollectionInformation.PushMethod.from_dict(push_method))

            kwargs['polling_service_instances'] = []
            for polling in d.get('polling_service_instances', []):
                kwargs['polling_service_instances'].append(CollectionInformationResponse.CollectionInformation.PollingServiceInstance.from_dict(polling))

            kwargs['subscription_methods'] = []
            for subscription_method in d.get('subscription_methods', []):
                kwargs['subscription_methods'].append(CollectionInformationResponse.CollectionInformation.SubscriptionMethod.from_dict(subscription_method))

            return CollectionInformationResponse.CollectionInformation(**kwargs)

        class PushMethod(BaseNonMessage):
            def __init__(self, push_protocol, push_message_bindings):
                """Create a new PushMethod.

                Arguments:
                - push_protocol (string) - a protocol binding that can be used
                  to push content to an Inbox Service instance.
                - push_message_bindings (list of strings) - the message
                  bindings that can be used to push content to an Inbox Service
                  instance using the protocol identified in the Push Protocol
                  field.
                """
                self.push_protocol = push_protocol
                self.push_message_bindings = push_message_bindings

            @property
            def push_protocol(self):
                return self._push_protocol
            
            @push_protocol.setter
            def push_protocol(self, value):
                _do_check(value, 'push_protocol', regex_tuple=_uri_regex)
                self._push_protocol = value
            
            @property
            def push_message_bindings(self):
                return self._push_message_bindings
            
            @push_message_bindings.setter
            def push_message_bindings(self, value):
                _do_check(value, 'push_message_bindings', regex_tuple=_uri_regex)
                self._push_message_bindings = value
            
            def to_etree(self):
                x = etree.Element('{%s}Push_Method' % ns_map['taxii_11'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'])
                proto_bind.text = self.push_protocol
                for binding in self.push_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'])
                    b.text = binding
                return x

            def to_dict(self):
                d = {}
                d['push_protocol'] = self.push_protocol
                d['push_message_bindings'] = []
                for binding in self.push_message_bindings:
                    d['push_message_bindings'].append(binding)
                return d

            def __eq__(self, other, debug=False):
                if not self._checkPropertiesEq(other, ['push_protocol'], debug):
                    return False

                if set(self.push_message_bindings) != set(other.push_message_bindings):
                    if debug:
                        print 'message bindings not equal: %s != %s' % (self.push_message_bindings, other.push_message_bindings)
                    return False

                return True

            @staticmethod
            def from_etree(etree_xml):
                kwargs = {}
                kwargs['push_protocol'] = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
                kwargs['push_message_bindings'] = []
                message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
                for message_binding in message_binding_set:
                    kwargs['push_message_bindings'].append(message_binding.text)
                return CollectionInformationResponse.CollectionInformation.PushMethod(**kwargs)

            @staticmethod
            def from_dict(d):
                return CollectionInformationResponse.CollectionInformation.PushMethod(**d)

        class PollingServiceInstance(BaseNonMessage):
            NAME = 'Polling_Service'

            def __init__(self, poll_protocol, poll_address, poll_message_bindings):
                """Create a new PollingServiceInstance.

                Arguments:
                - poll_protocol (string) - the protocol binding supported by
                  this Poll Service instance.
                - poll_address (string) - the address of the TAXII Daemon
                  hosting this Poll Service instance.
                - poll_message_bindings (list of strings) - the message
                  bindings supported by this Poll Service instance
                """
                self.poll_protocol = poll_protocol
                self.poll_address = poll_address
                self.poll_message_bindings = poll_message_bindings

            @property
            def poll_protocol(self):
                return self._poll_protocol
            
            @poll_protocol.setter
            def poll_protocol(self, value):
                _do_check(value, 'poll_protocol', regex_tuple=_uri_regex)
                self._poll_protocol = value
            
            @property
            def poll_message_bindings(self):
                return self._poll_message_bindings
            
            @poll_message_bindings.setter
            def poll_message_bindings(self, value):
                _do_check(value, 'poll_message_bindings', regex_tuple=_uri_regex)
                self._poll_message_bindings = value
            
            def to_etree(self):
                x = etree.Element('{%s}Polling_Service' % ns_map['taxii_11'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'])
                proto_bind.text = self.poll_protocol
                address = etree.SubElement(x, '{%s}Address' % ns_map['taxii_11'])
                address.text = self.poll_address
                for binding in self.poll_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'])
                    b.text = binding
                return x

            def to_dict(self):
                d = {}
                d['poll_protocol'] = self.poll_protocol
                d['poll_address'] = self.poll_address
                d['poll_message_bindings'] = []
                for binding in self.poll_message_bindings:
                    d['poll_message_bindings'].append(binding)
                return d

            def __eq__(self, other, debug=False):
                if not self._checkPropertiesEq(other, ['poll_protocol', 'poll_address'], debug):
                    return False

                if set(self.poll_message_bindings) != set(other.poll_message_bindings):
                    if debug:
                        print 'poll_message_bindings not equal %s != %s' % (self.poll_message_bindings, other.poll_message_bindings)
                    return False

                return True

            @classmethod
            def from_etree(cls, etree_xml):
                protocol = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
                addr = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
                bindings = []
                message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
                for message_binding in message_binding_set:
                    bindings.append(message_binding.text)
                return cls(protocol, addr, bindings)

            @classmethod
            def from_dict(cls, d):
                return cls(**d)

        class SubscriptionMethod(BaseNonMessage):
            NAME = 'Subscription_Service'

            def __init__(self, subscription_protocol, subscription_address, subscription_message_bindings):
                """Create a new SubscriptionMethod.

                Arguments:
                - subscription_protocol (string) - the protocol binding
                  supported by this Collection Management Service instance.
                - subscription_address (string) - the address of the TAXII
                  Daemon hosting this Collection Management Service instance.
                - subscription_message_bindings (list of strings) - the message
                  bindings supported by this Collection Management Service Instance
                """
                self.subscription_protocol = subscription_protocol
                self.subscription_address = subscription_address
                self.subscription_message_bindings = subscription_message_bindings
            
            @property
            def subscription_protocol(self):
                return self._subscription_protocol
            
            @subscription_protocol.setter
            def subscription_protocol(self, value):
                _do_check(value, 'subscription_protocol', regex_tuple=_uri_regex)
                self._subscription_protocol = value
            
            @property
            def subscription_message_bindings(self):
                return self._subscription_message_bindings
            
            @subscription_message_bindings.setter
            def subscription_message_bindings(self, value):
                _do_check(value, 'subscription_message_bindings', regex_tuple=_uri_regex)
                self._subscription_message_bindings = value
            
            def to_etree(self):
                x = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.NAME))
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'])
                proto_bind.text = self.subscription_protocol
                address = etree.SubElement(x, '{%s}Address' % ns_map['taxii_11'])
                address.text = self.subscription_address
                for binding in self.subscription_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'])
                    b.text = binding
                return x

            def to_dict(self):
                d = {}
                d['subscription_protocol'] = self.subscription_protocol
                d['subscription_address'] = self.subscription_address
                d['subscription_message_bindings'] = []
                for binding in self.subscription_message_bindings:
                    d['subscription_message_bindings'].append(binding)
                return d

            def __eq__(self, other, debug=False):
                if not self._checkPropertiesEq(other, ['subscription_protocol', 'subscription_address'], debug):
                    return False

                if set(self.subscription_message_bindings) != set(other.subscription_message_bindings):
                    if debug:
                        print 'subscription_message_bindings not equal: %s != %s' % (self.subscription_message_bindings, other.subscription_message_bindings)
                    return False

                return True

            @classmethod
            def from_etree(cls, etree_xml):
                protocol = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
                addr = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
                bindings = []
                message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
                for message_binding in message_binding_set:
                    bindings.append(message_binding.text)
                return cls(protocol, addr, bindings)

            @classmethod
            def from_dict(cls, d):
                return cls(**d)

class PollRequest(TAXIIMessage):
    message_type = MSG_POLL_REQUEST

    def __init__(self,
                 message_id,
                 in_response_to=None,
                 extended_headers=None,
                 collection_name=None,
                 exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None,
                 subscription_id=None,
                 poll_parameters=None
                 ):
        """Create a new PollRequest.

        Arguments:
        - message_id (string) - A value identifying this message.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - collection_name (string) - the name of the TAXII Data Collection that is being
          polled.
        - exclusive_begin_timestamp_label (datetime) - a Timestamp Label
          indicating the beginning of the range of TAXII Data Feed content the
          requester wishes to receive.
        - inclusive_end_timestamp_label (datetime) - a Timestamp Label
          indicating the end of the range of TAXII Data Feed content the
          requester wishes to receive.
        - subscription_id (string) - the existing subscription the Consumer
          wishes to poll.
        - content_bindings (list of strings) - the type of content that is
          requested in the response to this poll.
        """
        super(PollRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.collection_name = collection_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        self.content_bindings = content_bindings or []
        
        if subscription_id is None and poll_parameters is None:
            raise ValueError('One of subscription_id or poll_parameters must not be None')
        if subscription_id is not None and poll_parameters is not None:
            raise ValueError('Only one of subscription_id and poll_parameters can be present')

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:#TODO: do a call to _do_check
            raise ValueError('in_response_to must be None')
        self._in_response_to = value
    
    @property
    def collection_name(self):
        return self._collection_name
    
    @collection_name.setter
    def collection_name(self, value):
        _do_check(value, 'collection_name', regex_tuple=_uri_regex)
        self._collection_name = value
    
    @property
    def exclusive_begin_timestamp_label(self):
        return self._exclusive_begin_timestamp_label
    
    @exclusive_begin_timestamp_label.setter
    def exclusive_begin_timestamp_label(self, value):
        _check_timestamplabel(value, 'exclusive_begin_timestamp_label', can_be_none=True)
        self._exclusive_begin_timestamp_label = value
    
    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label
    
    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        _check_timestamplabel(value, 'inclusive_end_timestamp_label', can_be_none=True)
        self._inclusive_end_timestamp_label = value
    
    @property
    def subscription_id(self):
        return self._subscription_id
    
    @subscription_id.setter
    def subscription_id(self, value):
        _do_check(value, 'subscription_id', regex_tuple=_uri_regex, can_be_none=True)
        self._subscription_id = value
    
    @property
    def content_bindings(self):
        return self._content_bindings
    
    @content_bindings.setter
    def content_bindings(self, value):
        _do_check(value, 'content_bindings', regex_tuple=_uri_regex)
        self._content_bindings = value
    
    def to_etree(self):
        xml = super(PollRequest, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.exclusive_begin_timestamp_label is not None:
            ebt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'])
            #TODO: Add TZ Info
            ebt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label is not None:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii_11'])
            #TODO: Add TZ Info
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        for binding in self.content_bindings:
            b = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii_11'])
            b.text = binding

        return xml

    def to_dict(self):
        d = super(PollRequest, self).to_dict()
        d['collection_name'] = self.collection_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.exclusive_begin_timestamp_label is not None:  # TODO: Add TZ Info
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label is not None:  # TODO: Add TZ Info
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_bindings'] = []
        for bind in self.content_bindings:
            d['content_bindings'].append(bind)
        return d

    def __eq__(self, other, debug=False):
        if not super(PollRequest, self).__eq__(other, debug):
            return False

        if not self._checkPropertiesEq(other, ['feed_name', 'subscription_id', 'exclusive_begin_timestamp_label', 'inclusive_end_timestamp_label'], debug):
                return False

        if set(self.content_bindings) != set(other.content_bindings):
            if debug:
                print 'content_bindings not equal: %s != %s' % (self.content_bindings, other.content_bindings)
            return False

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['feed_name'] = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]
        kwargs['subscription_id'] = None
        subscription_id_set = etree_xml.xpath('./@subscription_id', namespaces=ns_map)
        if len(subscription_id_set) > 0:
            kwargs['subscription_id'] = subscription_id_set[0]

        kwargs['exclusive_begin_timestamp_label'] = None
        begin_ts_set = etree_xml.xpath('./taxii:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if len(begin_ts_set) > 0:
            kwargs['exclusive_begin_timestamp_label'] = _str2datetime(begin_ts_set[0].text)

        kwargs['inclusive_end_timestamp_label'] = None
        end_ts_set = etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)
        if len(end_ts_set) > 0:
            kwargs['inclusive_end_timestamp_label'] = _str2datetime(end_ts_set[0].text)

        kwargs['content_bindings'] = []
        content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
        for binding in content_binding_set:
            kwargs['content_bindings'].append(binding.text)

        msg = super(PollRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']

        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['exclusive_begin_timestamp_label'] = None
        if 'exclusive_begin_timestamp_label' in d:
            kwargs['exclusive_begin_timestamp_label'] = _str2datetime(d['exclusive_begin_timestamp_label'])

        kwargs['inclusive_end_timestamp_label'] = None
        if 'inclusive_end_timestamp_label' in d:
            kwargs['inclusive_end_timestamp_label'] = _str2datetime(d['inclusive_end_timestamp_label'])

        kwargs['content_bindings'] = d.get('content_bindings', [])

        msg = super(PollRequest, cls).from_dict(d, **kwargs)
        return msg


class PollResponse(TAXIIMessage):
    message_type = MSG_POLL_RESPONSE

    def __init__(self,
                 message_id,
                 in_response_to,
                 extended_headers=None,
                 collection_name=None,
                 exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None,
                 subscription_id=None,
                 message=None,
                 content_blocks=None,
                 more=False,
                 result_id=None,
                 result_part_number=1,
                 record_count=None
                 partial_count=False
                 ):
        """Create a new PollResponse:

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - collection_name (string) - the name of the TAXII Data Collection that was polled
        - inclusive_begin_timestamp_label (datetime) - a Timestamp Label
          indicating the beginning of the time range this Poll Response covers
        - inclusive_end_timestamp_label (datetime) - a Timestamp Label
          indicating the end of the time range this Poll Response covers.
        - subscription_id (string) - the Subscription ID for which this content
          is being provided.
        - message (string) - additional information for the message recipient
        - content_blocks (list of ContentBlock objects) - a piece of content
          and additional information related to the content.
        """
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.collection_name = collection_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        self.message = message
        self.content_blocks = content_blocks or []
        #TODO: Lots more
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_uri_regex)
        self._in_response_to = value
    
    @property
    def feed_name(self):
        return self._feed_name
    
    @feed_name.setter
    def feed_name(self, value):
        _do_check(value, 'feed_name', regex_tuple=_uri_regex)
        self._feed_name = value
    
    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label
    
    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        _check_timestamplabel(value, 'inclusive_end_timestamp_label')
        self._inclusive_end_timestamp_label = value
    
    @property
    def inclusive_begin_timestamp_label(self):
        return self._inclusive_begin_timestamp_label
    
    @inclusive_begin_timestamp_label.setter
    def inclusive_begin_timestamp_label(self, value):
        _check_timestamplabel(value, 'inclusive_begin_timestamp_label', can_be_none=True)
        self._inclusive_begin_timestamp_label = value
    
    @property
    def subscription_id(self):
        return self._subscription_id
    
    @subscription_id.setter
    def subscription_id(self, value):
        _do_check(value, 'subscription_id', regex_tuple=_uri_regex, can_be_none=True)
        self._subscription_id = value
    
    @property
    def content_blocks(self):
        return self._content_blocks
    
    @content_blocks.setter
    def content_blocks(self, value):
        _do_check(value, 'content_blocks', type=ContentBlock)
        self._content_blocks = value
    
    def to_etree(self):
        xml = super(PollResponse, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        if self.inclusive_begin_timestamp_label is not None:
            ibt = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
            ibt.text = self.inclusive_begin_timestamp_label.isoformat()

        iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
        iet.text = self.inclusive_end_timestamp_label.isoformat()

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(PollResponse, self).to_dict()

        d['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.message is not None:
            d['message'] = self.message
        if self.inclusive_begin_timestamp_label is not None:
            d['inclusive_begin_timestamp_label'] = self.inclusive_begin_timestamp_label.isoformat()
        d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def __eq__(self, other, debug=False):
        if not super(PollResponse, self).__eq__(other, debug):
            return False

        if not self._checkPropertiesEq(other, ['feed_name', 'subscription_id', 'message', 'inclusive_begin_timestamp_label', 'inclusive_end_timestamp_label'], debug):
                return False

        #TODO: Check content blocks

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        
        kwargs['feed_name'] = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]

        kwargs['subscription_id'] = None
        subs_ids = etree_xml.xpath('./@subscription_id', namespaces=ns_map)
        if len(subs_ids) > 0:
            kwargs['subscription_id'] = subs_ids[0]

        kwargs['message'] = None
        messages = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(messages) > 0:
            kwargs['message'] = messages[0].text

        kwargs['inclusive_begin_timestamp_label'] = None
        ibts = etree_xml.xpath('./taxii:Inclusive_Begin_Timestamp', namespaces=ns_map)
        if len(ibts) > 0:
            kwargs['inclusive_begin_timestamp_label'] = _str2datetime(ibts[0].text)

        kwargs['inclusive_end_timestamp_label'] = _str2datetime(etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)[0].text)

        kwargs['content_blocks'] = []
        blocks = etree_xml.xpath('./taxii:Content_Block', namespaces=ns_map)
        for block in blocks:
            kwargs['content_blocks'].append(ContentBlock.from_etree(block))

        msg = super(PollResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']

        kwargs['message'] = None
        if 'message' in d:
            kwargs['message'] = d['message']

        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['inclusive_begin_timestamp_label'] = None
        if 'inclusive_begin_timestamp_label' in d:
            kwargs['inclusive_begin_timestamp_label'] = _str2datetime(d['inclusive_begin_timestamp_label'])

        kwargs['inclusive_end_timestamp_label'] = _str2datetime(d['inclusive_end_timestamp_label'])

        kwargs['content_blocks'] = []
        for block in d['content_blocks']:
            kwargs['content_blocks'].append(ContentBlock.from_dict(block))
        msg = super(PollResponse, cls).from_dict(d, **kwargs)
        return msg
