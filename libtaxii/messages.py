""" 
| Copyright (C) 2013 - The MITRE Corporation
| For license information, see the LICENSE.txt file

| Contributors:
 
* Alex Ciobanu - calex@cert.europa.eu  
* Mark Davidson - mdavidson@mitre.org  
* Bryan Worrell - bworrell@mitre.org

"""

import random
import os
import StringIO
import datetime
import dateutil.parser
import re
import collections
from lxml import etree
try:
    import simplejson as json
except ImportError:
    import json

#Message Types
#:Constant identifying a Status Message
MSG_STATUS_MESSAGE = 'Status_Message'
#:Constant identifying a Discovery Request Message
MSG_DISCOVERY_REQUEST = 'Discovery_Request'
#:Constant identifying a Discovery Response Message
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
#:Constant identifying a Feed Information Request Message
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
#:Constant identifying a Feed Information Response Message
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'
#:Constant identifying a Subscription Management Request Message
MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
#:Constant identifying a Subscription Management Response Message
MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'
#:Constant identifying a Poll Request Message
MSG_POLL_REQUEST = 'Poll_Request'
#:Constant identifying a Poll Response Message
MSG_POLL_RESPONSE = 'Poll_Response'
#:Constant identifying a Inbox Message
MSG_INBOX_MESSAGE = 'Inbox_Message'
# Tuple of all message types
MSG_TYPES = (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE, MSG_FEED_INFORMATION_REQUEST, 
             MSG_FEED_INFORMATION_RESPONSE, MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST, MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE,
             MSG_POLL_REQUEST, MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE)

#Status Types
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
ST_UNSUPPORTED_PROTOCOL = 'UNSUPPORTED_PROTOCOL_BINDING'
# Tuple of all status types
ST_TYPES = (ST_BAD_MESSAGE, ST_DENIED, ST_FAILURE, ST_NOT_FOUND, ST_POLLING_UNSUPPORTED, ST_RETRY, ST_SUCCESS,
            ST_UNAUTHORIZED, ST_UNSUPPORTED_MESSAGE_BINDING, ST_UNSUPPORTED_CONTENT_BINDING, ST_UNSUPPORTED_PROTOCOL)

#: Constant identifying an Action of Subscribe
ACT_SUBSCRIBE = 'SUBSCRIBE'
#: Constant identifying an Action of Unsubscribe
ACT_UNSUBSCRIBE = 'UNSUBSCRIBE'
#: Constant identifying an Action of Status
ACT_STATUS = 'STATUS'
# Tuple of all actions
ACT_TYPES = (ACT_SUBSCRIBE, ACT_UNSUBSCRIBE, ACT_STATUS)

#Service types
#: Constant identifying a Service Type of Inbox
SVC_INBOX = 'INBOX'
#: Constant identifying a Service Type of Poll
SVC_POLL = 'POLL'
#: Constant identifying a Service Type of Feed Management
SVC_FEED_MANAGEMENT = 'FEED_MANAGEMENT'
#: Constant identifying a Service Type of Discovery
SVC_DISCOVERY = 'DISCOVERY'
# Tuple of all service types 
SVC_TYPES = (SVC_INBOX, SVC_POLL, SVC_FEED_MANAGEMENT, SVC_DISCOVERY)

ns_map = {
            'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1',
         }

### General purpose helper methods ###

_RegexTuple = collections.namedtuple('_RegexTuple', ['regex','title'])
#URI regex per http://tools.ietf.org/html/rfc3986
_uri_regex = _RegexTuple("(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", "URI Format")
_message_id_regex = _RegexTuple("[0-9]+", "Numbers only")

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

def generate_message_id(maxlen=5):
    """Generate a TAXII Message ID with a max length of `maxlen`."""
    message_id = random.randint(1, 10 ** maxlen)
    return str(message_id)

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
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XMLMessageBinding_Schema.xsd")
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
    if qn.namespace != ns_map['taxii']:
        raise ValueError('Unsupported namespace: %s' % qn.namespace)

    message_type = qn.localname

    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_etree(etree_xml)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_etree(etree_xml)
    if message_type == MSG_FEED_INFORMATION_REQUEST:
        return FeedInformationRequest.from_etree(etree_xml)
    if message_type == MSG_FEED_INFORMATION_RESPONSE:
        return FeedInformationResponse.from_etree(etree_xml)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_etree(etree_xml)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_etree(etree_xml)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_etree(etree_xml)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_etree(etree_xml)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST:
        return ManageFeedSubscriptionRequest.from_etree(etree_xml)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_etree(etree_xml)

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
    if message_type == MSG_FEED_INFORMATION_REQUEST:
        return FeedInformationRequest.from_dict(d)
    if message_type == MSG_FEED_INFORMATION_RESPONSE:
        return FeedInformationResponse.from_dict(d)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_dict(d)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_dict(d)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_dict(d)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_dict(d)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST:
        return ManageFeedSubscriptionRequest.from_dict(d)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_dict(d)

    raise ValueError('Unknown message_type: %s' % message_type)


def get_message_from_json(json_string):
    """Create a TAXII Message object from a json string.
    
    Note: This function auto-detects which TAXII Message should be created form
    the JSON string.
    """
    return get_message_from_dict(json.loads(json_string))


def _str2datetime(date_string):
    """ Users of libtaxii should not use this function.
    Takes a date string and creates a datetime object
    """
    return dateutil.parser.parse(date_string)


class BaseNonMessage(object):
    """This class should not be used directly by libtaxii users.  
    
    Base class for non-TAXII Message objects"""

    def to_etree(self):
        """Create an etree representation of this class.

        To be implemented by child classes.
        """
        raise Exception('Method not implemented by child class!')

    def to_dict(self):
        """Create a dictionary representation of this class.

        To be implemented by child classes.
        """
        raise Exception('Method not implemented by child class!')

    def to_xml(self):
        """Create an XML representation of this class."""
        return etree.tostring(self.to_etree())

    @classmethod
    def from_etree(cls, src_etree):
        """Create an instance of this class from an etree.

        To be implemented by child classes.
        """
        raise Exception('Method not implemented by child class!')

    @classmethod
    def from_dict(cls, d):
        """Create an instance of this class from a dictionary.

        To be implemented by child classes.
        """
        raise Exception('Method not implemented by child class!')

    @classmethod
    def from_xml(cls, xml):

        if isinstance(xml, basestring):
            f = StringIO.StringIO(xml)
        else:
            f = xml

        etree_xml = etree.parse(f, get_xml_parser()).getroot()
        return cls.from_etree(etree_xml)

    def __eq__(self, other, debug=False):
        raise Exception('Method not implemented by child class!')

    def _checkPropertiesEq(self, other, arglist, debug=False):
        for arg in arglist:
            #Check to see if the arg is in both objects
            in_self = arg in self.__dict__
            in_other = arg in other.__dict__
            if in_self != in_other:
                if debug:
                    print '%s presence not equal. in_self=%s, in_other=%s' % (arg, in_self, in_other)
                return False

            if in_self and in_other:
                if self.__dict__[arg] != other.__dict__[arg]:
                    if debug:
                        print '%s not equal %s != %s' % (arg, self.__dict__[arg], other.__dict__[arg])
                    return False

        return True

    def __ne__(self, other, debug=False):
        return not self.__eq__(other, debug)


class DeliveryParameters(BaseNonMessage):
        #TODO: Should the default arguments of these change? I'm not sure these are actually optional
        def __init__(self, inbox_protocol=None, inbox_address=None, delivery_message_binding=None, content_bindings=None):
            """Set up Delivery Parameters.

            Arguments
            - inbox_protocol (string) - identifies the protocol to be used when
                pushing TAXII Data Feed content to a Consumer's TAXII Inbox
                Service implementation.
            - inbox_address (string) - identifies the address of the TAXII
                Daemon hosting the Inbox Service to which the Consumer requests
                content  for this TAXII Data Feed to be delivered.
            - delivery_message_binding (string) - identifies the message
                binding to be used to send pushed content for this subscription.
            - content_bindings (list of strings) - contains Content Binding IDs
                indicating which types of contents the Consumer requests to
                receive for this TAXII  Data Feed
            """
            self.inbox_protocol = inbox_protocol
            self.inbox_address = inbox_address
            self.delivery_message_binding = delivery_message_binding
            if content_bindings is None:
                self.content_bindings = []
            else:
                self.content_bindings = content_bindings

        @property
        def inbox_protocol(self):
            return self._inbox_protocol
        
        @inbox_protocol.setter
        def inbox_protocol(self, value):
            _do_check(value, 'inbox_protocol', regex_tuple=_uri_regex)
            self._inbox_protocol = value
        
        @property
        def inbox_address(self):
            return self._inbox_address
        
        @inbox_address.setter
        def inbox_address(self, value):
            #TODO: Can inbox_address be validated?
            self._inbox_address = value
        
        @property
        def delivery_message_binding(self):
            return self._delivery_message_binding
        
        @delivery_message_binding.setter
        def delivery_message_binding(self, value):
            _do_check(value, 'delivery_message_binding', regex_tuple=_uri_regex)
            self._delivery_message_binding = value
        
        @property
        def content_bindings(self):
            return self._content_bindings
        
        @content_bindings.setter
        def content_bindings(self, value):
            _do_check(value, 'content_bindings', regex_tuple=_uri_regex)
            self._content_bindings = value

        def to_etree(self):
            xml = etree.Element('{%s}Push_Parameters' % ns_map['taxii'])

            if self.inbox_protocol is not None:
                pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii'])
                pb.text = self.inbox_protocol

            if self.inbox_address is not None:
                a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii'])
                a.text = self.inbox_address

            if self.delivery_message_binding is not None:
                mb = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii'])
                mb.text = self.delivery_message_binding

            for binding in self.content_bindings:
                cb = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii'])
                cb.text = binding

            return xml

        def to_dict(self):
            d = {}

            if self.inbox_protocol is not None:
                d['inbox_protocol'] = self.inbox_protocol

            if self.inbox_address is not None:
                d['inbox_address'] = self.inbox_address

            if self.delivery_message_binding is not None:
                d['delivery_message_binding'] = self.delivery_message_binding

            d['content_bindings'] = []
            for binding in self.content_bindings:
                d['content_bindings'].append(binding)

            return d

        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['inbox_protocol', 'address', 'deliver_message_binding'], debug):
                return False

            if set(self.content_bindings) != set(other.content_bindings):
                if debug:
                    print 'content_bindings not equal: %s != %s' % (self.content_bindings, other.content_bindings)
                return False

            return True

        @staticmethod
        def from_etree(etree_xml):
            inbox_protocol = None
            inbox_protocol_set = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)
            if len(inbox_protocol_set) > 0:
                inbox_protocol = inbox_protocol_set[0].text

            inbox_address = None
            inbox_address_set = etree_xml.xpath('./taxii:Address', namespaces=ns_map)
            if len(inbox_address_set) > 0:
                inbox_address = inbox_address_set[0].text

            delivery_message_binding = None
            delivery_message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
            if len(delivery_message_binding_set) > 0:
                delivery_message_binding = delivery_message_binding_set[0].text

            content_bindings = []
            content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for binding in content_binding_set:
                content_bindings.append(binding.text)

            return DeliveryParameters(inbox_protocol, inbox_address, delivery_message_binding, content_bindings)

        @staticmethod
        def from_dict(d):
            return DeliveryParameters(**d)


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
        if extended_headers is None:
            self.extended_headers = {}
        else:
            self.extended_headers = extended_headers

    
    @property
    def message_id(self):
        return self._message_id
    
    @message_id.setter
    def message_id(self, value):
        _do_check(value, 'message_id', regex_tuple=_message_id_regex)
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
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii'], self.message_type), nsmap=ns_map)
        root_elt.attrib['message_id'] = str(self.message_id)

        if self.in_response_to is not None:
            root_elt.attrib['in_response_to'] = str(self.in_response_to)

        if len(self.extended_headers) > 0:
            eh = etree.SubElement(root_elt, '{%s}Extended_Headers' % ns_map['taxii'])

            for name, value in self.extended_headers.items():
                h = etree.SubElement(eh, '{%s}Extended_Header' % ns_map['taxii'])
                h.attrib['name'] = name
                h.text = value
        return root_elt

    def to_xml(self):
        """Convert a message to XML.

        Subclasses shouldn't implement this method, as it is mainly a wrapper
        for cls.to_etree.
        """
        return etree.tostring(self.to_etree())

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
        message_type = src_etree.tag[53:]
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))

        #Get the message ID
        message_id = src_etree.xpath('/taxii:*/@message_id', namespaces=ns_map)[0]

        #Get in response to, if present
        in_response_to = None
        in_response_tos = src_etree.xpath('/taxii:*/@in_response_to', namespaces=ns_map)
        if len(in_response_tos) > 0:
            in_response_to = in_response_tos[0]

        #Get the Extended headers
        extended_header_list = src_etree.xpath('/taxii:*/taxii:Extended_Headers/taxii:Extended_Header', namespaces=ns_map)
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


class ContentBlock(BaseNonMessage):
    NAME = 'Content_Block'

    def __init__(self, content_binding, content, timestamp_label=None, padding=None):
        """Create a ContentBlock.

        Arguments:
        - content_binding (string) - a Content Binding ID or nesting expression
          indicating the type of content contained in the Content field of this
          Content Block
        - content (string or etree) - a piece of content of the type specified
          by the Content Binding.
        - timestamp_label (datetime) - the Timestamp Label associated with this
          Content Block.
        - padding (string) - an arbitrary amount of padding for this Content
          Block.
        """
        self.content_binding = content_binding
        self.content = self._stringify_content(content)
        self.timestamp_label = timestamp_label
        self.padding = padding

    @property
    def content_binding(self):
        return self._content_binding
    
    @content_binding.setter
    def content_binding(self, value):
        _do_check(value, 'content_binding', regex_tuple=_uri_regex)
        self._content_binding = value
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        _do_check(value, 'content')#Just check for not None
        if isinstance(value, str):
            value = value.decode('utf-8')
        elif not isinstance(value, unicode):
            value = unicode(value)
        self._content = value
    
    @property
    def timestamp_label(self):
        return self._timestamp_label
    
    @timestamp_label.setter
    def timestamp_label(self, value):
        _check_timestamplabel(value, 'timestamp_label', can_be_none=True)
        self._timestamp_label = value
    
    def _stringify_content(self, content):
        """Always a string or raises an error."""
        if isinstance(content, basestring):
            return content

        if isinstance(content, etree._ElementTree) or isinstance(content, etree._Element):
            return etree.tostring(content)

        return str(content)

    def to_etree(self):
        block = etree.Element('{%s}Content_Block' % ns_map['taxii'], nsmap=ns_map)
        cb = etree.SubElement(block, '{%s}Content_Binding' % ns_map['taxii'])
        cb.text = self.content_binding
        c = etree.SubElement(block, '{%s}Content' % ns_map['taxii'])

        if self.content.startswith('<'):  # It might be XML
            try:
                xml = etree.parse(StringIO.StringIO(self.content), get_xml_parser()).getroot()
                c.append(xml)
            except:
                c.text = self.content
        else:
            c.text = self.content

        if self.timestamp_label is not None:
            tl = etree.SubElement(block, '{%s}Timestamp_Label' % ns_map['taxii'])
            tl.text = self.timestamp_label.isoformat()

        if self.padding is not None:
            p = etree.SubElement(block, '{%s}Padding' % ns_map['taxii'])
            p.text = self.padding

        return block

    def to_dict(self):
        block = {}
        block['content_binding'] = self.content_binding

        if isinstance(self.content, etree._Element):  # For XML
            block['content'] = etree.tostring(self.content)
        else:
            block['content'] = self.content

        if self.timestamp_label is not None:
            block['timestamp_label'] = self.timestamp_label.isoformat()

        if self.padding is not None:
            block['padding'] = self.padding

        return block

    def to_json(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other, debug=False):
        if not self._checkPropertiesEq(other, ['content_binding', 'timestamp_label', 'padding'], debug):
            return False

        #TODO: It's pretty hard to check and see if content is equal....
        #if not self._checkPropertiesEq(other, ['content'], debug):
        #    return False

        return True

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['content_binding'] = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)[0].text
        padding_set = etree_xml.xpath('./taxii:Padding', namespaces=ns_map)
        if len(padding_set) > 0:
            kwargs['padding'] = padding_set[0].text

        ts_set = etree_xml.xpath('./taxii:Timestamp_Label', namespaces=ns_map)
        if len(ts_set) > 0:
            ts_string = ts_set[0].text
            kwargs['timestamp_label'] = _str2datetime(ts_string)

        content = etree_xml.xpath('./taxii:Content', namespaces=ns_map)[0]
        if len(content) == 0:  # This has string content
            kwargs['content'] = content.text
        else:  # This has XML content
            kwargs['content'] = content[0]

        return ContentBlock(**kwargs)

    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['content_binding'] = d['content_binding']
        kwargs['padding'] = d.get('padding')
        if 'timestamp_label' in d:
            kwargs['timestamp_label'] = _str2datetime(d['timestamp_label'])

        kwargs['content'] = d['content']

        return ContentBlock(**kwargs)

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))


#### TAXII Message Classes ####

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

    def to_json(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other, debug=False):
        if not super(DiscoveryResponse, self).__eq__(other, debug):
            return False

        if len(self.service_instances) != len(other.service_instances):
            if debug:
                print 'service_instance lengths not equal: %s != %s' % (len(self.service_instances), len(other.service_instances))
            return False

        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.service_instances), sorted(other.service_instances)):
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
        service_instance_set = etree_xml.xpath('./taxii:Service_Instance', namespaces=ns_map)
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

        def __init__(self, service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content=None, available=None, message=None):
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
            """
            self.service_type = service_type
            self.services_version = services_version
            self.protocol_binding = protocol_binding
            self.service_address = service_address
            self.message_bindings = message_bindings
            if inbox_service_accepted_content is None:
                self.inbox_service_accepted_content = []
            else:
                self.inbox_service_accepted_content = inbox_service_accepted_content
            self.available = available
            self.message = message

        
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
        def inbox_service_accepted_content(self):
            return self._inbox_service_accepted_content
        
        @inbox_service_accepted_content.setter
        def inbox_service_accepted_content(self, value):
            _do_check(value, 'inbox_service_accepted_content', regex_tuple=_uri_regex)
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
            si = etree.Element('{%s}Service_Instance' % ns_map['taxii'])
            si.attrib['service_type'] = self.service_type
            si.attrib['service_version'] = self.services_version
            if self.available is not None:
                si.attrib['available'] = str(self.available).lower()

            protocol_binding = etree.SubElement(si, '{%s}Protocol_Binding' % ns_map['taxii'])
            protocol_binding.text = self.protocol_binding

            service_address = etree.SubElement(si, '{%s}Address' % ns_map['taxii'])
            service_address.text = self.service_address

            for mb in self.message_bindings:
                message_binding = etree.SubElement(si, '{%s}Message_Binding' % ns_map['taxii'])
                message_binding.text = mb

            for cb in self.inbox_service_accepted_content:
                content_binding = etree.SubElement(si, '{%s}Content_Binding' % ns_map['taxii'])
                content_binding.text = cb

            if self.message is not None:
                message = etree.SubElement(si, '{%s}Message' % ns_map['taxii'])
                message.text = self.message

            return si

        def to_dict(self):
            d = {}
            d['service_type'] = self.service_type
            d['services_version'] = self.services_version
            d['protocol_binding'] = self.protocol_binding
            d['service_address'] = self.service_address
            d['message_bindings'] = self.message_bindings
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

            if set(self.inbox_service_accepted_content) != set(other.inbox_service_accepted_content):
                if debug:
                    print 'inbox_service_accepted_contents not equal'
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

            protocol_binding = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
            service_address = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text

            message_bindings = []
            message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
            for mb in message_binding_set:
                message_bindings.append(mb.text)

            inbox_service_accepted_contents = []
            inbox_service_accepted_content_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for cb in inbox_service_accepted_content_set:
                inbox_service_accepted_contents.append(cb.text)

            message = None
            message_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
            if len(message_set) > 0:
                message = message_set[0].text

            return DiscoveryResponse.ServiceInstance(service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_contents, available, message)

        @staticmethod
        def from_dict(d):
            return DiscoveryResponse.ServiceInstance(**d)


class FeedInformationRequest(TAXIIMessage):
    message_type = MSG_FEED_INFORMATION_REQUEST
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

class FeedInformationResponse(TAXIIMessage):
    message_type = MSG_FEED_INFORMATION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, feed_informations=None):
        """Create a new FeedInformationResponse.

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - the Message ID of the message to which this
          is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - feed_informations (list of FeedInformation objects) - A list of
          FeedInformation objects to be contained in this response
        """
        super(FeedInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        if feed_informations is None:
            self.feed_informations = []
        else:
            self.feed_informations = feed_informations
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_message_id_regex)
        self._in_response_to = value
    
    @property
    def feed_informations(self):
        return self._feed_informations
    
    @feed_informations.setter
    def feed_informations(self, value):
        _do_check(value, 'feed_informations', type=FeedInformationResponse.FeedInformation)
        self._feed_informations = value
    
    def to_etree(self):
        xml = super(FeedInformationResponse, self).to_etree()
        for feed in self.feed_informations:
            xml.append(feed.to_etree())
        return xml

    def to_dict(self):
        d = super(FeedInformationResponse, self).to_dict()
        d['feed_informations'] = []
        for feed in self.feed_informations:
            d['feed_informations'].append(feed.to_dict())
        return d

    def __eq__(self, other, debug=False):
        if not super(FeedInformationResponse, self).__eq__(other, debug):
            return False

        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.feed_informations), sorted(other.feed_informations)):
            if item1 != item2:
                if debug:
                    print 'feed_informations not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)  # This will print why they are not equal
                return False

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(FeedInformationResponse, cls).from_etree(etree_xml)
        msg.feed_informations = []
        feed_informations = etree_xml.xpath('./taxii:Feed', namespaces=ns_map)
        for feed in feed_informations:
            msg.feed_informations.append(FeedInformationResponse.FeedInformation.from_etree(feed))
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(FeedInformationResponse, cls).from_dict(d)
        msg.feed_informations = []
        for feed in d['feed_informations']:
            msg.feed_informations.append(FeedInformationResponse.FeedInformation.from_dict(feed))
        return msg

    class FeedInformation(BaseNonMessage):

        def __init__(self, feed_name, feed_description, supported_contents, available=None, push_methods=None, polling_service_instances=None, subscription_methods=None):
            """Create a new FeedInformation

            Arguments:
            - feed_name (string) - the name by which this TAXII Data Feed is
              identified.
            - feed_description (string) - a prose description of this TAXII
              Data Feed.
            - supported_contents (list of strings) - Content Binding IDs
              indicating which types of content are currently expressed in this
              TAXII Data Feed.
            - available (boolean) - whether the identity of the requester
              (authenticated or otherwise) is allowed to access this TAXII
              Service.
            - push_methods (list of PushMethod objects) - the protocols that
              can be used to push content via a subscription.
            - polling_service_instances (list of PollingServiceInstance
              objects) - the bindings and address a Consumer can use to
              interact with a Poll Service instance that supports this TAXII
              Data Feed.
            - subscription_methods (list of SubscriptionMethod objects) - the
              protocol and address of the TAXII Daemon hosting the Feed
              Management Service that can process subscriptions for this TAXII
              Data Feed.
            """
            self.feed_name = feed_name
            self.available = available
            self.feed_description = feed_description
            self.supported_contents = supported_contents
            if push_methods is None:
                self.push_methods = []
            else:
                self.push_methods = push_methods

            if polling_service_instances is None:
                self.polling_service_instances = []
            else:
                self.polling_service_instances = polling_service_instances

            if subscription_methods is None:
                self.subscription_methods = []
            else:
                self.subscription_methods = subscription_methods

        @property
        def feed_name(self):
            return self._feed_name
        
        @feed_name.setter
        def feed_name(self, value):
            _do_check(value, 'feed_name', regex_tuple=_uri_regex)
            self._feed_name = value
        
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
            _do_check(value, 'supported_contents', regex_tuple=_uri_regex)
            self._supported_contents = value
        
        @property
        def push_methods(self):
            return self._push_methods
        
        @push_methods.setter
        def push_methods(self, value):
            _do_check(value, 'push_methods', type=FeedInformationResponse.FeedInformation.PushMethod)
            self._push_methods = value
        
        @property
        def polling_service_instances(self):
            return self._polling_service_instances
        
        @polling_service_instances.setter
        def polling_service_instances(self, value):
            _do_check(value, 'polling_service_instances', type=FeedInformationResponse.FeedInformation.PollingServiceInstance)
            self._polling_service_instances = value
        
        @property
        def subscription_methods(self):
            return self._subscription_methods
        
        @subscription_methods.setter
        def subscription_methods(self, value):
            _do_check(value, 'subscription_methods', type=FeedInformationResponse.FeedInformation.SubscriptionMethod)
            self._subscription_methods = value
        
        def to_etree(self):
            f = etree.Element('{%s}Feed' % ns_map['taxii'])
            f.attrib['feed_name'] = self.feed_name
            if self.available is not None:
                f.attrib['available'] = str(self.available).lower()
            feed_description = etree.SubElement(f, '{%s}Description' % ns_map['taxii'])
            feed_description.text = self.feed_description

            for binding in self.supported_contents:
                cb = etree.SubElement(f, '{%s}Content_Binding' % ns_map['taxii'])
                cb.text = binding

            for push_method in self.push_methods:
                f.append(push_method.to_etree())

            for polling_service in self.polling_service_instances:
                f.append(polling_service.to_etree())

            for subscription_method in self.subscription_methods:
                f.append(subscription_method.to_etree())

            return f

        def to_dict(self):
            d = {}
            d['feed_name'] = self.feed_name
            if self.available is not None:
                d['available'] = self.available
            d['feed_description'] = self.feed_description
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
            if not self._checkPropertiesEq(other, ['feed_name', 'feed_description', 'available'], debug):
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
            kwargs['feed_name'] = etree_xml.attrib['feed_name']
            kwargs['available'] = None
            if 'available' in etree_xml.attrib:
                tmp = etree_xml.attrib['available']
                kwargs['available'] = tmp == 'True'

            kwargs['feed_description'] = etree_xml.xpath('./taxii:Description', namespaces=ns_map)[0].text
            kwargs['supported_contents'] = []
            supported_content_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for binding_elt in supported_content_set:
                kwargs['supported_contents'].append(binding_elt.text)

            kwargs['push_methods'] = []
            push_method_set = etree_xml.xpath('./taxii:Push_Method', namespaces=ns_map)
            for push_method_elt in push_method_set:
                kwargs['push_methods'].append(FeedInformationResponse.FeedInformation.PushMethod.from_etree(push_method_elt))

            kwargs['polling_service_instances'] = []
            polling_service_set = etree_xml.xpath('./taxii:Polling_Service', namespaces=ns_map)
            for polling_elt in polling_service_set:
                kwargs['polling_service_instances'].append(FeedInformationResponse.FeedInformation.PollingServiceInstance.from_etree(polling_elt))

            kwargs['subscription_methods'] = []
            subscription_method_set = etree_xml.xpath('./taxii:Subscription_Service', namespaces=ns_map)
            for subscription_elt in subscription_method_set:
                kwargs['subscription_methods'].append(FeedInformationResponse.FeedInformation.SubscriptionMethod.from_etree(subscription_elt))

            return FeedInformationResponse.FeedInformation(**kwargs)

        @staticmethod
        def from_dict(d):
            kwargs = {}
            kwargs['feed_name'] = d['feed_name']
            kwargs['available'] = d.get('available')

            kwargs['feed_description'] = d['feed_description']
            kwargs['supported_contents'] = []
            for binding in d.get('supported_contents', []):
                kwargs['supported_contents'].append(binding)

            kwargs['push_methods'] = []
            for push_method in d.get('push_methods', []):
                kwargs['push_methods'].append(FeedInformationResponse.FeedInformation.PushMethod.from_dict(push_method))

            kwargs['polling_service_instances'] = []
            for polling in d.get('polling_service_instances', []):
                kwargs['polling_service_instances'].append(FeedInformationResponse.FeedInformation.PollingServiceInstance.from_dict(polling))

            kwargs['subscription_methods'] = []
            for subscription_method in d.get('subscription_methods', []):
                kwargs['subscription_methods'].append(FeedInformationResponse.FeedInformation.SubscriptionMethod.from_dict(subscription_method))

            return FeedInformationResponse.FeedInformation(**kwargs)

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
                x = etree.Element('{%s}Push_Method' % ns_map['taxii'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
                proto_bind.text = self.push_protocol
                for binding in self.push_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
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
                return FeedInformationResponse.FeedInformation.PushMethod(**kwargs)

            @staticmethod
            def from_dict(d):
                return FeedInformationResponse.FeedInformation.PushMethod(**d)

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
                x = etree.Element('{%s}Polling_Service' % ns_map['taxii'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
                proto_bind.text = self.poll_protocol
                address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
                address.text = self.poll_address
                for binding in self.poll_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
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
                  supported by this Feed Management Service instance.
                - subscription_address (string) - the address of the TAXII
                  Daemon hosting this Feed Management Service instance.
                - subscription_message_bindings (list of strings) - the message
                  bindings supported by this Feed Management Service Instance
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
                x = etree.Element('{%s}%s' % (ns_map['taxii'], self.NAME))
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
                proto_bind.text = self.subscription_protocol
                address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
                address.text = self.subscription_address
                for binding in self.subscription_message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
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
                 feed_name=None,
                 exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None,
                 subscription_id=None,
                 content_bindings=None
                 ):
        """Create a new PollRequest.

        Arguments:
        - message_id (string) - A value identifying this message.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - feed_name (string) - the name of the TAXII Data Feed that is being
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
        self.feed_name = feed_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        if content_bindings is None:
            self.content_bindings = []
        else:
            self.content_bindings = content_bindings

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value
    
    @property
    def feed_name(self):
        return self._feed_name
    
    @feed_name.setter
    def feed_name(self, value):
        _do_check(value, 'feed_name', regex_tuple=_uri_regex)
        self._feed_name = value
    
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
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.exclusive_begin_timestamp_label is not None:
            ebt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii'])
            #TODO: Add TZ Info
            ebt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label is not None:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
            #TODO: Add TZ Info
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        for binding in self.content_bindings:
            b = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii'])
            b.text = binding

        return xml

    def to_dict(self):
        d = super(PollRequest, self).to_dict()
        d['feed_name'] = self.feed_name
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
                 feed_name=None,
                 inclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None,
                 subscription_id=None,
                 message=None,
                 content_blocks=None
                 ):
        """Create a new PollResponse:

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - feed_name (string) - the name of the TAXII Data Feed that was polled
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
        self.feed_name = feed_name
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
        self.subscription_id = subscription_id
        self.message = message
        if content_blocks is None:
            self.content_blocks = []
        else:
            self.content_blocks = content_blocks
    
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


class StatusMessage(TAXIIMessage):
    message_type = MSG_STATUS_MESSAGE

    def __init__(self, message_id, in_response_to, extended_headers=None, status_type=None, status_detail=None, message=None):
        """Create a new StatusMessage.

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - status_type (string) - One of the defined Status Types or a third
          partydefined Status Type.
        - status_detail (string) - A field for additional information about
          this status in a machine-readable format.
        - message (string) - Additional information for the status. There is no
          expectation that this field be interpretable by a machine; it is
          instead targeted to a human operator.
        """
        super(StatusMessage, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.status_type = status_type
        self.status_detail = status_detail
        self.message = message
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        _do_check(value, 'in_response_to', regex_tuple=_uri_regex)
        self._in_response_to = value
    
    @property
    def status_type(self):
        return self._status_type
    
    @status_type.setter
    def status_type(self, value):
        _do_check(value, 'status_type', value_tuple=ST_TYPES)
        self._status_type = value
    
    #TODO: is it possible to check the status detail?
    
    def to_etree(self):
        xml = super(StatusMessage, self).to_etree()
        xml.attrib['status_type'] = self.status_type

        if self.status_detail is not None:
            sd = etree.SubElement(xml, '{%s}Status_Detail' % ns_map['taxii'])
            sd.text = self.status_detail

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        return xml

    def to_dict(self):
        d = super(StatusMessage, self).to_dict()
        d['status_type'] = self.status_type
        if self.status_detail is not None:
            d['status_detail'] = self.status_detail
        if self.message is not None:
            d['message'] = self.message
            d['message'] = self.message
        return d

    def __eq__(self, other, debug=None):
        if not super(StatusMessage, self).__eq__(other, debug):
            return False

        return self._checkPropertiesEq(other, ['status_type', 'status_detail', 'status_message'], debug)

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        
        kwargs['status_type'] = etree_xml.attrib['status_type']

        kwargs['status_detail'] = None
        sd_set = etree_xml.xpath('./taxii:Status_Detail', namespaces=ns_map)
        if len(sd_set) > 0:
            kwargs['status_detail'] = sd_set[0].text

        kwargs['message'] = None
        m_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(m_set) > 0:
            kwargs['message'] = m_set[0].text
            
        msg = super(StatusMessage, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['status_type'] = d['status_type']
        kwargs['status_detail'] = d.get('status_detail')
        kwargs['message'] = d.get('message')
            
        msg = super(StatusMessage, cls).from_dict(d, **kwargs)
        return msg


class InboxMessage(TAXIIMessage):
    message_type = MSG_INBOX_MESSAGE

    def __init__(self, message_id, in_response_to=None, extended_headers=None, message=None, subscription_information=None, content_blocks=None):
        """Create a new InboxMessage.

        Arguments:
        - message_id (string) - A value identifying this message.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - message (string) - prose information for the message recipient.
        - subscription_information (a SubscriptionInformation object) - This
          field is only present if this message is being sent to provide
          content in accordance with an existing TAXII Data Feed subscription.
        - content_blocks (a list of ContentBlock objects)
        """
        super(InboxMessage, self).__init__(message_id, extended_headers=extended_headers)
        self.subscription_information = subscription_information
        self.message = message
        if content_blocks is None:
            self.content_blocks = []
        else:
            self.content_blocks = content_blocks
    
    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value
    
    @property
    def subscription_information(self):
        return self._subscription_information
    
    @subscription_information.setter
    def subscription_information(self, value):
        _do_check(value, 'subscription_information', type=InboxMessage.SubscriptionInformation, can_be_none=True)
        self._subscription_information = value
    
    @property
    def content_blocks(self):
        return self._content_blocks
    
    @content_blocks.setter
    def content_blocks(self, value):
        _do_check(value, 'content_blocks', type=ContentBlock)
        self._content_blocks = value
    
    def to_etree(self):
        xml = super(InboxMessage, self).to_etree()
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        if self.subscription_information is not None:
            xml.append(self.subscription_information.to_etree())

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(InboxMessage, self).to_dict()
        if self.message is not None:
            d['message'] = self.message

        if self.subscription_information is not None:
            d['subscription_information'] = self.subscription_information.to_dict()

        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def __eq__(self, other, debug=False):
        if not super(InboxMessage, self).__eq__(other, debug):
            return False

        if not self._checkPropertiesEq(other, ['message', 'subscription_information'], debug):
            return False

        if len(self.content_blocks) != len(other.content_blocks):
            if debug:
                print 'content block lengths not equal: %s != %s' % (len(self.content_blocks), len(other.content_blocks))
            return False

        #Who knows if this is a good way to compare the content blocks or not...
        for item1, item2 in zip(sorted(self.content_blocks), sorted(other.content_blocks)):
            if item1 != item2:
                if debug:
                    print 'content blocks not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)  # This will print why they are not equal
                return False

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(InboxMessage, cls).from_etree(etree_xml)

        msg_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(msg_set) > 0:
            msg.message = msg_set[0].text

        subs_infos = etree_xml.xpath('./taxii:Source_Subscription', namespaces=ns_map)
        if len(subs_infos) > 0:
            msg.subscription_information = InboxMessage.SubscriptionInformation.from_etree(subs_infos[0])

        content_blocks = etree_xml.xpath('./taxii:Content_Block', namespaces=ns_map)
        msg.content_blocks = []
        for block in content_blocks:
            msg.content_blocks.append(ContentBlock.from_etree(block))

        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(InboxMessage, cls).from_dict(d)

        msg.message = d.get('message')

        msg.subscription_information = None
        if 'subscription_information' in d:
            msg.subscription_information = InboxMessage.SubscriptionInformation.from_dict(d['subscription_information'])

        msg.content_blocks = []
        for block in d['content_blocks']:
            msg.content_blocks.append(ContentBlock.from_dict(block))

        return msg

    class SubscriptionInformation(BaseNonMessage):

        def __init__(self, feed_name, subscription_id, inclusive_begin_timestamp_label, inclusive_end_timestamp_label):
            """Create a new SubscriptionInformation.

            Arguments:
            - feed_name (string) - the name of the TAXII Data Feed from which
              this content is being provided.
            - subcription_id (string) - the Subscription ID for which this
              content is being provided.
            - inclusive_begin_timestamp_label (datetime) - a Timestamp Label
              indicating the beginning of the time range this Inbox Message
              covers.
            - inclusive_end_timestamp_label (datetime) - a Timestamp Label
              indicating the end of the time range this Inbox Message covers.
            """
            self.feed_name = feed_name
            self.subscription_id = subscription_id
            self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
            self.inclusive_end_timestamp_label = inclusive_end_timestamp_label

        
        @property
        def feed_name(self):
            return self._feed_name
        
        @feed_name.setter
        def feed_name(self, value):
            _do_check(value, 'feed_name', regex_tuple=_uri_regex)
            self._feed_name = value
        
        @property
        def subscription_id(self):
            return self._subscription_id
        
        @subscription_id.setter
        def subscription_id(self, value):
            _do_check(value, 'subscription_id', regex_tuple=_uri_regex)
            self._subscription_id = value
        
        @property
        def inclusive_begin_timestamp_label(self):
            return self._inclusive_begin_timestamp_label
        
        @inclusive_begin_timestamp_label.setter
        def inclusive_begin_timestamp_label(self, value):
            _check_timestamplabel(value, 'inclusive_begin_timestamp_label')
            self._inclusive_begin_timestamp_label = value
        
        @property
        def inclusive_end_timestamp_label(self):
            return self._inclusive_end_timestamp_label
        
        @inclusive_end_timestamp_label.setter
        def inclusive_end_timestamp_label(self, value):
            _check_timestamplabel(value, 'inclusive_end_timestamp_label')
            self._inclusive_end_timestamp_label = value
        
        def to_etree(self):
            xml = etree.Element('{%s}Source_Subscription' % ns_map['taxii'])
            xml.attrib['feed_name'] = self.feed_name
            xml.attrib['subscription_id'] = self.subscription_id

            ibtl = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
            ibtl.text = self.inclusive_begin_timestamp_label.isoformat()

            ietl = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
            ietl.text = self.inclusive_end_timestamp_label.isoformat()

            return xml

        def to_dict(self):
            d = {}
            d['feed_name'] = self.feed_name
            d['subscription_id'] = self.subscription_id
            d['inclusive_begin_timestamp_label'] = self.inclusive_begin_timestamp_label.isoformat()
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
            return d

        def __eq__(self, other, debug=False):
            return self._checkPropertiesEq(other, ['feed_name', 'subscription_id', 'inclusive_begin_timestamp_label', 'inclusive_end_timestamp_label'], debug)

        @staticmethod
        def from_etree(etree_xml):
            feed_name = etree_xml.attrib['feed_name']
            subscription_id = etree_xml.attrib['subscription_id']

            ibtl = _str2datetime(etree_xml.xpath('./taxii:Inclusive_Begin_Timestamp', namespaces=ns_map)[0].text)
            ietl = _str2datetime(etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)[0].text)

            return InboxMessage.SubscriptionInformation(feed_name, subscription_id, ibtl, ietl)

        @staticmethod
        def from_dict(d):
            feed_name = d['feed_name']
            subscription_id = d['subscription_id']

            ibtl = _str2datetime(d['inclusive_begin_timestamp_label'])
            ietl = _str2datetime(d['inclusive_end_timestamp_label'])

            return InboxMessage.SubscriptionInformation(feed_name, subscription_id, ibtl, ietl)


class ManageFeedSubscriptionRequest(TAXIIMessage):
    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST

    def __init__(self, message_id, in_response_to=None, extended_headers=None, feed_name=None, action=None, subscription_id=None, delivery_parameters=None):
        """Create a new ManageFeedSubscriptionRequest

        Arguments:
        - message_id (string) - A value identifying this message.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - feed_name (string) - the name of the TAXII Data Feed to which the
          action applies.
        - action (string) - the requested action to take.
        - subscription_id (string) - the ID of a previously created
          subscription
        - delivery_parameters (a list of DeliveryParameter objects) - the
          delivery parameters for this request.
        """
        super(ManageFeedSubscriptionRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.action = action
        self.subscription_id = subscription_id
        self.delivery_parameters = delivery_parameters

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value
    
    @property
    def feed_name(self):
        return self._feed_name
    
    @feed_name.setter
    def feed_name(self, value):
        _do_check(value, 'feed_name', regex_tuple=_uri_regex)
        self._feed_name = value
    
    @property
    def action(self):
        return self._action
    
    @action.setter
    def action(self, value):
        _do_check(value, 'action', value_tuple=ACT_TYPES)
        self._action = value
    
    @property
    def subscription_id(self):
        return self._subscription_id
    
    @subscription_id.setter
    def subscription_id(self, value):
        _do_check(value, 'subscription_id', regex_tuple=_uri_regex)
        self._subscription_id = value
    
    @property
    def delivery_parameters(self):
        return self._delivery_parameters
    
    @delivery_parameters.setter
    def delivery_parameters(self, value):
        _do_check(value, 'delivery_parameters', type=DeliveryParameters)
        self._delivery_parameters = value
    
    def to_etree(self):
        xml = super(ManageFeedSubscriptionRequest, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        xml.attrib['action'] = self.action
        xml.attrib['subscription_id'] = self.subscription_id
        xml.append(self.delivery_parameters.to_etree())
        return xml

    def to_dict(self):
        d = super(ManageFeedSubscriptionRequest, self).to_dict()
        d['feed_name'] = self.feed_name
        d['action'] = self.action
        d['subscription_id'] = self.subscription_id
        d['delivery_parameters'] = self.delivery_parameters.to_dict()
        return d

    def __eq__(self, other, debug=False):
        if not super(ManageFeedSubscriptionRequest, self).__eq__(other, debug):
            return False

        return self._checkPropertiesEq(other, ['feed_name', 'subscription_id', 'action', 'delivery_parameters'], debug)

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['feed_name'] = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]
        kwargs['action'] = etree_xml.xpath('./@action', namespaces=ns_map)[0]
        kwargs['subscription_id'] = etree_xml.xpath('./@subscription_id', namespaces=ns_map)[0]
        kwargs['delivery_parameters'] = DeliveryParameters.from_etree(etree_xml.xpath('./taxii:Push_Parameters', namespaces=ns_map)[0])
        
        msg = super(ManageFeedSubscriptionRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']
        kwargs['action'] = d['action']
        kwargs['subscription_id'] = d['subscription_id']
        kwargs['delivery_parameters'] = DeliveryParameters.from_dict(d['delivery_parameters'])
        
        msg = super(ManageFeedSubscriptionRequest, cls).from_dict(d, **kwargs)
        return msg


class ManageFeedSubscriptionResponse(TAXIIMessage):
    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, feed_name=None, message=None, subscription_instances=None):
        """Create a new ManageFeedSubscriptionResponse.

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        - feed_name (string) - the name of the TAXII Data Feed to which the
          action applies.
        - message (string) - a message associated with the subscription
          response.
        - subscription_instances (a list of SubscriptionInstance objects)
        """
        super(ManageFeedSubscriptionResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.message = message
        if subscription_instances is None:
            self.subscription_instances = []
        else:
            self.subscription_instances = subscription_instances

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
    def subscription_instances(self):
        return self._subscription_instances
    
    @subscription_instances.setter
    def subscription_instances(self, value):
        _do_check(value, 'subscription_instances', type=ManageFeedSubscriptionResponse.SubscriptionInstance)
        self._subscription_instances = value
    
    def to_etree(self):
        xml = super(ManageFeedSubscriptionResponse, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        for subscription_instance in self.subscription_instances:
            xml.append(subscription_instance.to_etree())

        return xml

    def to_dict(self):
        d = super(ManageFeedSubscriptionResponse, self).to_dict()
        d['feed_name'] = self.feed_name
        if self.message is not None:
            d['message'] = self.message
        d['subscription_instances'] = []
        for subscription_instance in self.subscription_instances:
            d['subscription_instances'].append(subscription_instance.to_dict())

        return d

    def __eq__(self, other, debug=False):
        if not super(ManageFeedSubscriptionResponse, self).__eq__(other, debug):
            return False

        if not self._checkPropertiesEq(other, ['feed_name', 'message'], debug):
            return False

        if len(self.subscription_instances) != len(other.subscription_instances):
            if debug:
                print 'subscription instance lengths not equal'
            return False

        #TODO: Compare the subscription instances

        return True

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['feed_name'] = etree_xml.attrib['feed_name']

        message_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(message_set) > 0:
            kwargs['message'] = message_set[0].text

        subscription_instance_set = etree_xml.xpath('./taxii:Subscription', namespaces=ns_map)

        kwargs['subscription_instances'] = []
        for si in subscription_instance_set:
            kwargs['subscription_instances'].append(ManageFeedSubscriptionResponse.SubscriptionInstance.from_etree(si))
            
        msg = super(ManageFeedSubscriptionResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']

        kwargs['message'] = d.get('message')

        kwargs['subscription_instances'] = []
        for instance in d['subscription_instances']:
            kwargs['subscription_instances'].append(ManageFeedSubscriptionResponse.SubscriptionInstance.from_dict(instance))

        msg = super(ManageFeedSubscriptionResponse, cls).from_dict(d, **kwargs)
        return msg

    class SubscriptionInstance(BaseNonMessage):

        def __init__(self, subscription_id, delivery_parameters=None, poll_instances=None):
            """Create a new SubscriptionInstance.

            Arguments:
            - subscription_id (string) - an identifier that is used to
              reference the given subscription in subsequent exchanges.
            - delivery_parameters (list of DeliveryParameter objects) - a copy
              of the Delivery Parameters of the Manage Feed Subscription
              Request Message that established this subscription.
            - poll_instances (list of PollInstance objects) - Each Poll
              Instance represents an instance of a Poll Service that can be
              contacted to retrieve content associated with the new
              Subscription.
            """
            self.subscription_id = subscription_id
            if delivery_parameters is None:
                self.delivery_parameters = []
            else:
                self.delivery_parameters = delivery_parameters

            if poll_instances is None:
                self.poll_instances = []
            else:
                self.poll_instances = poll_instances
        
        @property
        def subscription_id(self):
            return self._subscription_id
        
        @subscription_id.setter
        def subscription_id(self, value):
            _do_check(value, 'subscription_id', regex_tuple=_uri_regex)
            self._subscription_id = value
        
        @property
        def delivery_parameters(self):
            return self._delivery_parameters
        
        @delivery_parameters.setter
        def delivery_parameters(self, value):
            _do_check(value, 'delivery_parameters', type=DeliveryParameters, can_be_none=False)
            self._delivery_parameters = value
        
        @property
        def poll_instances(self):
            return self._poll_instances
        
        @poll_instances.setter
        def poll_instances(self, value):
            _do_check(value, 'poll_instances', type=ManageFeedSubscriptionResponse.PollInstance, can_be_none=False)
            self._poll_instances = value
        
        def to_etree(self):
            xml = etree.Element('{%s}Subscription' % ns_map['taxii'])
            xml.attrib['subscription_id'] = self.subscription_id

            for delivery_parameter in self.delivery_parameters:
                xml.append(delivery_parameter.to_etree())

            for poll_instance in self.poll_instances:
                xml.append(poll_instance.to_etree())

            return xml

        def to_dict(self):
            d = {}
            d['subscription_id'] = self.subscription_id

            d['delivery_parameters'] = []
            for delivery_parameter in self.delivery_parameters:
                d['delivery_parameters'].append(delivery_parameter.to_dict())

            d['poll_instances'] = []
            for poll_instance in self.poll_instances:
                d['poll_instances'].append(poll_instance.to_dict())

            return d

        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['subscription_id'], debug):
                return False

            #TODO: Compare delivery parameters
            #TODO: Compare poll instances

            return True

        @staticmethod
        def from_etree(etree_xml):
            subscription_id = etree_xml.attrib['subscription_id']

            delivery_parameters = []
            delivery_parameter_set = etree_xml.xpath('./taxii:Push_Parameters', namespaces=ns_map)
            for delivery_parameter in delivery_parameter_set:
                delivery_parameters.append(DeliveryParameters.from_etree(delivery_parameter))

            poll_instances = []
            poll_instance_set = etree_xml.xpath('./taxii:Poll_Instance', namespaces=ns_map)
            for poll_instance in poll_instance_set:
                poll_instances.append(ManageFeedSubscriptionResponse.PollInstance.from_etree(poll_instance))

            return ManageFeedSubscriptionResponse.SubscriptionInstance(subscription_id, delivery_parameters, poll_instances)

        @staticmethod
        def from_dict(d):
            subscription_id = d['subscription_id']

            delivery_parameters = []
            for delivery_parameter in d['delivery_parameters']:
                delivery_parameters.append(DeliveryParameters.from_dict(delivery_parameter))

            poll_instances = []
            for poll_instance in d['poll_instances']:
                poll_instances.append(ManageFeedSubscriptionResponse.PollInstance.from_dict(poll_instance))

            return ManageFeedSubscriptionResponse.SubscriptionInstance(subscription_id, delivery_parameters, poll_instances)

    class PollInstance:

        def __init__(self, poll_protocol, poll_address, poll_message_bindings=None):
            """Create a new PollInstance.

            Arguments:
            - poll_protocol (string) - The protocol binding supported by this
              instance of a Polling Service.
            - poll_address (string) - the address of the TAXII Daemon hosting
              this Poll Service.
            - poll_message_bindings (list of strings) - one or more message
              bindings that can be used when interacting with this Poll Service
              instance.
            """
            self.poll_protocol = poll_protocol
            self.poll_address = poll_address
            if poll_message_bindings is None:
                self.poll_message_bindings = []
            else:
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
            xml = etree.Element('{%s}Poll_Instance' % ns_map['taxii'])

            pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii'])
            pb.text = self.poll_protocol

            a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii'])
            a.text = self.poll_address

            for binding in self.poll_message_bindings:
                b = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii'])
                b.text = binding

            return xml

        def to_dict(self):
            d = {}

            d['poll_protocol'] = self.poll_protocol
            d['poll_address'] = self.poll_address
            d['poll_message_bindings'] = []
            for binding in self.poll_message_bindings:
                d['poll_message_bindings'].append(binding)

            return d

        def __eq__(self, other, debug=True):
            if not self._checkPropertiesEq(other, ['poll_protocol', 'poll_address'], debug):
                return False

            if set(self.poll_message_bindings) != set(other.poll_message_bindings):
                if debug:
                    print 'poll message bindings not equal: %s != %s' % (self.poll_message_bindings, other.poll_message_bindings)
                    return False

            return True

        @staticmethod
        def from_etree(etree_xml):
            poll_protocol = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
            address = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
            poll_message_bindings = []
            for b in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
                poll_message_bindings.append(b.text)

            return ManageFeedSubscriptionResponse.PollInstance(poll_protocol, address, poll_message_bindings)

        @staticmethod
        def from_dict(d):
            return ManageFeedSubscriptionResponse.PollInstance(**d)
