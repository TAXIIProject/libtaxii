#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import random
import os
import StringIO
import datetime
import dateutil.parser
from lxml import etree

MSG_STATUS_MESSAGE = 'Status_Message'
MSG_DISCOVERY_REQUEST = 'Discovery_Request'
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'
MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'
MSG_POLL_REQUEST = 'Poll_Request'
MSG_POLL_RESPONSE = 'Poll_Response'
MSG_INBOX_MESSAGE = 'Inbox_Message'

#Status Types
ST_BAD_MESSAGE = 'BAD_MESSAGE'
ST_DENIED = 'DENIED'
ST_FAILURE = 'FAILURE'
ST_NOT_FOUND = 'NOT_FOUND'
ST_POLLING_UNSUPPORTED = 'POLLING_UNSUPPORTED'
ST_RETRY = 'RETRY'
ST_SUCCESS = 'SUCCESS'
ST_UNAUTHORIZED = 'UNAUTHORIZED'
ST_UNSUPPORTED_MESSAGE_BINDING = 'UNSUPPORTED_MESSAGE'
ST_UNSUPPORTED_CONTENT_BINDING = 'UNSUPPORTED_CONTENT'
ST_UNSUPPORTED_PROTOCOL = 'UNSUPPORTED_PROTOCOL_BINDING'

ACT_SUBSCRIBE = 'SUBSCRIBE'
ACT_UNSUBSCRIBE = 'UNSUBSCRIBE'
ACT_STATUS = 'STATUS'

#Service types
SVC_INBOX = 'INBOX'
SVC_POLL = 'POLL'
SVC_FEED_MANAGEMENT = 'FEED_MANAGEMENT'
SVC_DISCOVERY = 'DISCOVERY'

ns_map = {'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1'}#, 
          #TODO: figure out what to do with the digital signature namespace
          #'ds': 'http://www.w3.org/2000/09/xmldsig#'}

### General purpose helper methods ###

#Generate a TAXII Message ID with a max length of maxlen
def generate_message_id(maxlen=5):
    message_id = random.randint(1, 10 ** maxlen)
    return str(message_id)

#validate XML with the TAXII XML Schema 1.0
def validate_xml(xml_string):
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string
    
    etree_xml = etree.parse(f)
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "../xsd", "TAXII_XMLMessageBinding_Schema.xsd")
    taxii_schema_doc = etree.parse(schema_file)
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(etree_xml)
    if not valid:
        return xml_schema.error_log.last_error
    return valid

# Takes an XML String and attempts to create a TAXII Message object from it.
# This function auto-detects which TAXII Message should be created from the XML.
def get_message_from_xml(xml_string):
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string
    
    etree_xml = etree.parse(f).getroot()
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

# Takes a dictionary and attempts to create a TAXII Message object from it.
# This function auto-detects which TAXII Message should be created from the dictionary.
def get_message_from_dict(d):
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

def _str2datetime(date_string):
    return dateutil.parser.parse(date_string)

#Allows for code reuse in non-TAXII Message objects
class BaseNonMessage(object):
    
    #Creates an etree representation of this class
    def to_etree(self):#Implemented by child classes
        raise Exception('Method not implemented by child class!')
    
    #Creates a dictionary representation of this class
    def to_dict(self):#Implemented by child classes
        raise Exception('Method not implemented by child class!')
    
    #Creates an XML representation of this class
    def to_xml(self):
        return etree.tostring(self.to_etree())
    
    #Creates an instance of this class from an etree
    @classmethod
    def from_etree(cls, src_etree):#Implemented by child classes
        raise Exception('Method not implemented by child class!')
    
    #Creates an instance of this class from a dictionary
    @classmethod
    def from_dict(cls, d):#Implemented by child classes
        raise Exception('Method not implemented by child class!')
    
    #Creates an instance of this class from an XML String
    @classmethod
    def from_xml(cls, xml):
        
        if isinstance(xml, basestring):
            f = StringIO.StringIO(xml)
        else:
            f = xml
        
        etree_xml = etree.parse(f).getroot()
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
        # inbox_protocol (string) - This field identifies the protocol to be used when pushing TAXII Data Feed content to a Consumer's TAXII Inbox Service implementation.
        # inbox_address (string) - This field identifies the address of the TAXII Daemon hosting the Inbox Service to which the Consumer requests content  for this TAXII Data Feed to be delivered.
        # delivery_message_binding (string) - This field identifies the message binding to be used to send pushed content for this subscription.
        # content_bindings (list of strings) - This field contains Content Binding IDs indicating which types of contents the Consumer requests to receive for this TAXII  Data Feed
        def __init__(self, inbox_protocol=None, inbox_address=None, delivery_message_binding=None, content_bindings=None):
            self.inbox_protocol=inbox_protocol
            self.inbox_address=inbox_address
            self.delivery_message_binding = delivery_message_binding
            if content_bindings is None:
                self.content_bindings = []
            else:
                self.content_bindings = content_bindings
        
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
            if not self._checkPropertiesEq(other, ['inbox_protocol','address','deliver_message_binding'], debug):
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

#The TAXIIMessage class keeps track of properties common to all TAXII Messages (i.e., headers).
#The TAXIIMessage class is extended by each Message Type (e.g., DiscoveryRequest), with each
#Subclass containing subclass-specific information
class TAXIIMessage(BaseNonMessage):
    message_type = 'TAXIIMessage'
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    def __init__(self, message_id, in_response_to=None, extended_headers=None):
        self.message_id = message_id
        self.in_response_to = in_response_to
        if extended_headers is None:
            self.extended_headers = {}
        else:
            self.extended_headers = extended_headers
    
    #Creates the base etree for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to XML,
    #Subclasses should call this method first, then create their specific XML constructs
    def to_etree(self):
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii'], self.message_type), nsmap = ns_map)
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
    
    #Subclasses shouldn't implemnet this method, as it is mainly a wrapper for cls.to_etree.
    def to_xml(self):
        return etree.tostring(self.to_etree())
    
    #Creates the base dictionary for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to dictionary,
    #Subclasses should call this method first, then create their specific dictionary constructs
    def to_dict(self):
        d = {}
        d['message_type'] = self.message_type
        d['message_id'] = self.message_id
        if self.in_response_to is not None:
            d['in_response_to'] = self.in_response_to
        d['extended_headers'] = self.extended_headers
        
        return d
    
    def __eq__(self, other, debug=False):
        if not isinstance(other, TAXIIMessage):
            raise ValueError('Not comparing two TAXII Messages! (%s, %s)' % (self.__class__.__name__, other.__class__.__name__))
        
        return self._checkPropertiesEq(other, ['message_type','message_id','in_response_to','extended_headers'], debug)
    
    def __ne__(self, other, debug=False):
        return not self.__eq__(other, debug)
    
    #Pulls properties of a TAXII Message from an etree. Message-specific constructs must be pulled
    #by each Message class. In general, when converting from etree,
    #Subclasses should call this method first, then parse their specific XML constructs
    @classmethod
    def from_etree(cls, src_etree):
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
        
        return cls(message_id, in_response_to, extended_headers=extended_headers)
    
    
    #Subclasses shouldn't implemnet this method, as it is mainly a wrapper for cls.from_etree.
    @classmethod
    def from_xml(cls, xml):
        
        if isinstance(xml, basestring):
            f = StringIO.StringIO(xml)
        else:
            f = xml
        
        etree_xml = etree.parse(f).getroot()
        return cls.from_etree(etree_xml)
    
    #Pulls properties of a TAXII Message from a dictionary. Message-specific constructs must be pulled
    #by each Message class. In general, when converting from dictionary,
    #Subclasses should call this method first, then parse their specific dictionary constructs
    @classmethod
    def from_dict(cls, d):
        message_type = d['message_type']
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))
        message_id = d['message_id']
        extended_headers = d['extended_headers']
        in_response_to = None
        if 'in_response_to' in d:
            in_response_to = d['in_response_to']
        return cls(message_id, in_response_to, extended_headers=extended_headers)

class ContentBlock(BaseNonMessage):
    NAME = 'Content_Block'
    # content_binding (string) - This field contains a Content Binding ID or nesting expression indicating the type of content contained in the Content field of this Content Block
    # content (string or etree) - This field contains a piece of content of the type specified by the Content Binding.
    # timestamp_label (datetime) - This field contains the Timestamp Label associated with this Content Block.
    # padding (string) - This field contains an arbitrary amount of padding for this Content Block.
    def __init__(self, content_binding, content, timestamp_label = None, padding = None):
        self.content_binding = content_binding
        self.content = self._stringify_content(content)
        if timestamp_label is not None:
            if timestamp_label.tzinfo is None:
                raise ValueError('timestamp_label.tzinfo must not be None')
        self.timestamp_label = timestamp_label
        self.padding = padding
    
    #Always a string or raises an error
    def _stringify_content(self, content):
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
        
        if self.content.startswith('<'):#It might be XML
            try:
                xml = etree.parse(StringIO.StringIO(self.content)).getroot()
                c.append(xml)
            except:
                c.text = self.content
                pass#Keep calm and carry on
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
        
        if isinstance(self.content, etree._Element):#For XML
            block['content'] = etree.tostring(self.content)
        else:
            block['content'] = self.content
        
        if self.timestamp_label is not None:
            block['timestamp_label'] = self.timestamp_label.isoformat()
        
        if self.padding is not None:
            block['padding'] = self.padding
        
        return block
    
    def __eq__(self, other, debug=False):
        if not self._checkPropertiesEq(other, ['content_binding','timestamp_label','padding'], debug):
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
        if len(content) == 0:#This has string content
            kwargs['content'] = content.text
        else:#This has XML content
            kwargs['content'] = content[0]
        
        return ContentBlock(**kwargs)
    
    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['content_binding'] = d['content_binding']
        if 'padding' in d:
            kwargs['padding'] = d['padding']
        if 'timestamp_label' in d:
            kwargs['timestamp_label'] = _str2datetime(d['timestamp_label'])
        
        kwargs['content'] = d['content']
        
        return ContentBlock(**kwargs)

#### TAXII Message Classes ####

class DiscoveryRequest(TAXIIMessage):
    message_type = MSG_DISCOVERY_REQUEST

class DiscoveryResponse(TAXIIMessage):
    message_type = MSG_DISCOVERY_RESPONSE
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # service_instances (list of ServiceInstance objects) - a list of service instances that this response contains
    def __init__(self, message_id, in_response_to, extended_headers=None, service_instances=None):
        super(DiscoveryResponse, self).__init__(message_id, in_response_to, extended_headers)
        if service_instances is None:
            self.service_instances = []
        else:
            self.service_instances = service_instances
    
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
    
    def __eq__(self, other, debug=False):
        if not super(DiscoveryResponse, self).__eq__(other, debug):
            return False
        
        if len(self.service_instances) != len(other.service_instances):
            if debug: print 'service_instance lengths not equal: %s != %s' % (len(self.service_instances), len(other.service_instances))
            return False
        
        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.service_instances), sorted(other.service_instances)):
            if item1 != item2:
                if debug:
                    print 'service instances not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)#This will print why they are not equal
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
        # service_type (string) - This field identifies the Service Type of this Service Instance.
        # services_version (string) - This field identifies the TAXII Services Specification to which this Service conforms.
        # protocol_binding (string) - This field identifies the protocol binding supported by this Service
        # service_address (string) - This field identifies the network address of the TAXII Daemon that hosts this Service.
        # message_bindings (list of strings) - This field identifies the message bindings supported by this Service instance.
        # inbox_service_accepted_content (list of strings) - This field identifies content bindings that this Inbox Service is willing to accept
        # available (boolean) - This field indicates whether the identity of the requester (authenticated or otherwise) is allowed to access this TAXII  Service.
        # message (string) - This field contains a message regarding this Service instance.
        def __init__(self, service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content=None, available=None, message=None):
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
        
        def to_etree(self):
            si = etree.Element('{%s}Service_Instance' % ns_map['taxii'])
            si.attrib['service_type'] = self.service_type
            si.attrib['service_version'] = self.services_version
            if self.available is not None: 
                si.attrib['available'] = str(self.available)
            
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
            if not self._checkPropertiesEq(other, ['service_type','services_version','protocol_binding','service_address','available','message'], debug):
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
        def from_etree(etree_xml):#Expects a taxii:Service_Instance element
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

class FeedInformationResponse(TAXIIMessage):
    message_type = MSG_FEED_INFORMATION_RESPONSE
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # feed_informations (list of FeedInformation objects) - A list of FeedInformation objects to be contained in this response
    def __init__(self, message_id, in_response_to, extended_headers=None, feed_informations=None):
        super(FeedInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        if feed_informations is None:
            self.feed_informations = []
        else:
            self.feed_informations = feed_informations
    
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
                    item1.__eq__(item2, debug)#This will print why they are not equal
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
        # feed_name (string) - This field contains the name by which this TAXII Data Feed is identified.
        # feed_description (string) - This field contains a prose description of this TAXII Data Feed.
        # supported_contents (list of strings) - This field contains Content Binding IDs indicating which types of content are currently expressed in this TAXII Data Feed.
        # available (boolean) - This field indicates whether the identity of the requester (authenticated or otherwise) is allowed to access this TAXII Service.
        # push_methods (list of PushMethod objects) - This field identifies the protocols that can be used to push content via a subscription.
        # polling_service_instances (list of PollingServiceInstance objects) - This field identifies the bindings and address a Consumer can use to interact with a Poll Service instance that supports this TAXII Data Feed.
        # subscription_methods (list of SubscriptionMethod objects) - This field identifies the protocol and address of the TAXII Daemon hosting the Feed Management Service that can process subscriptions for this TAXII Data Feed.
        def __init__(self, feed_name, feed_description, supported_contents, available=None, push_methods=None, polling_service_instances=None, subscription_methods=None):
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
        
        def to_etree(self):
            f = etree.Element('{%s}Feed' % ns_map['taxii'])
            f.attrib['feed_name'] = self.feed_name
            if self.available is not None:
                f.attrib['available'] = str(self.available)
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
            if not self._checkPropertiesEq(other, ['feed_name','feed_description','available'], debug):
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
            kwargs['available'] = None
            if 'available' in d:
                kwargs['available'] = d['available']
            
            kwargs['feed_description'] = d['feed_description']
            kwargs['supported_contents'] = []
            if 'supported_contents' in d:
                for binding in d['supported_contents']:
                    kwargs['supported_contents'].append(binding)
            
            kwargs['push_methods'] = []
            if 'push_methods' in d:
                for push_method in d['push_methods']:
                    kwargs['push_methods'].append(FeedInformationResponse.FeedInformation.PushMethod.from_dict(push_method))
            
            kwargs['polling_service_instances'] = []
            if 'polling_service_instances' in d:
                for polling in d['polling_service_instances']:
                    kwargs['polling_service_instances'].append(FeedInformationResponse.FeedInformation.PollingServiceInstance.from_dict(polling))
            
            kwargs['subscription_methods'] = []
            if 'subscription_methods' in d:
                for subscription_method in d['subscription_methods']:
                    kwargs['subscription_methods'].append(FeedInformationResponse.FeedInformation.SubscriptionMethod.from_dict(subscription_method))
            
            return FeedInformationResponse.FeedInformation(**kwargs)
        
        class PushMethod(BaseNonMessage):
            # push_protocol (string) - This field identifies a protocol binding that can be used to push content to an Inbox Service instance.
            # push_message_bindings (list of strings) - This field identifies the message bindings that can be used to push content to an Inbox Service instance using the protocol identified in the Push Protocol field.
            def __init__(self, push_protocol, push_message_bindings):
                self.push_protocol = push_protocol
                self.push_message_bindings = push_message_bindings
            
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
            # poll_protocol (string) - This field identifies the protocol binding supported by this Poll Service instance. 
            # poll_address (string) - This field identifies the address of the TAXII Daemon hosting this Poll Service instance.
            # poll_message_bindings (list of strings) - This field identifies the message bindings supported by this Poll Service instance
            def __init__(self, poll_protocol, poll_address, poll_message_bindings):
                self.poll_protocol = poll_protocol
                self.poll_address = poll_address
                self.poll_message_bindings = poll_message_bindings
    
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
                if not self._checkPropertiesEq(other, ['poll_protocol','poll_address'], debug):
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
            # subscription_protocol (string) - This field identifies the protocol binding supported by this Feed Management Service instance.
            # subscription_address (string) - This field identifies the address of the TAXII Daemon hosting this Feed Management Service instance.
            # subscription_message_bindings (list of strings) - This field identifies the message bindings supported by this Feed Management Service Instance
            def __init__(self, subscription_protocol, subscription_address, subscription_message_bindings):
                self.subscription_protocol = subscription_protocol
                self.subscription_address = subscription_address
                self.subscription_message_bindings = subscription_message_bindings
            
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
                if not self._checkPropertiesEq(other, ['subscription_protocol','subscription_address'], debug):
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
    # message_id (string) - A value identifying this message.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # feed_name (string) - This field identifies the name of the TAXII Data Feed that is being polled.
    # exclusive_begin_timestamp_label (datetime) - This field contains a Timestamp Label indicating the beginning of the range of TAXII Data Feed content the requester wishes to receive.
    # inclusive_end_timestamp_label (datetime) - This field contains a Timestamp Label indicating the end of the range of TAXII Data Feed content the requester wishes to receive.
    # subscription_id (string) - This field identifies the existing subscription the Consumer wishes to poll.
    # content_bindings (list of strings) - This field indicates the type of content that is requested in the response to this poll. 
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
        super(PollRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        if exclusive_begin_timestamp_label is not None:
            if exclusive_begin_timestamp_label.tzinfo is None:
                raise ValueError('exclusive_begin_timestamp_label.tzinfo must not be None')
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        if inclusive_end_timestamp_label is not None:
            if inclusive_end_timestamp_label.tzinfo is None:
                raise ValueError('inclusive_end_timestamp_label.tzinfo must not be None')
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        if content_bindings is None:
            self.content_bindings = []
        else:
            self.content_bindings = content_bindings
    
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
        if self.exclusive_begin_timestamp_label is not None:#TODO: Add TZ Info
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label is not None:#TODO: Add TZ Info
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_bindings'] = []
        for bind in self.content_bindings:
            d['content_bindings'].append(bind)
        return d
    
    def __eq__(self, other, debug=False):
        if not super(PollRequest, self).__eq__(other, debug):
            return False
        
        if not self._checkPropertiesEq(other, ['feed_name','subscription_id','exclusive_begin_timestamp_label','inclusive_end_timestamp_label'], debug):
                return False
        
        if set(self.content_bindings) != set(other.content_bindings):
            if debug: 
                print 'content_bindings not equal: %s != %s' % (self.content_bindings, other.content_bindings)
            return False
        
        return True
    
    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(PollRequest, cls).from_etree(etree_xml)
        msg.feed_name = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]
        msg.subscription_id = None
        subscription_id_set = etree_xml.xpath('./@subscription_id', namespaces=ns_map)
        if len(subscription_id_set) > 0:
            msg.subscription_id = subscription_id_set[0]
        
        msg.exclusive_begin_timestamp_label = None
        begin_ts_set = etree_xml.xpath('./taxii:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if len(begin_ts_set) > 0:
            msg.exclusive_begin_timestamp_label = _str2datetime(begin_ts_set[0].text)
        
        msg.inclusive_end_timestamp_label = None
        end_ts_set = etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)
        if len(end_ts_set) > 0:
            msg.inclusive_end_timestamp_label = _str2datetime(end_ts_set[0].text)
        
        msg.content_bindings = []
        content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
        for binding in content_binding_set:
            msg.content_bindings.append(binding.text)
        
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(PollRequest, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        
        msg.subscription_id = None
        if 'subscription_id' in d:
            msg.subscription_id = d['subscription_id']
        
        msg.exclusive_begin_timestamp_label = None
        if 'exclusive_begin_timestamp_label' in d:
            msg.exclusive_begin_timestamp_label = _str2datetime(d['exclusive_begin_timestamp_label'])
        
        msg.inclusive_end_timestamp_label = None
        if 'inclusive_end_timestamp_label' in d:
            msg.inclusive_end_timestamp_label = _str2datetime(d['inclusive_end_timestamp_label'])
        
        msg.content_bindings = []
        if 'content_bindings' in d:
            msg.content_bindings = d['content_bindings']
        
        return msg

class PollResponse(TAXIIMessage):
    message_type = MSG_POLL_RESPONSE
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # feed_name (string) - This field indicates the name of the TAXII Data Feed that was polled
    # inclusive_begin_timestamp_label (datetime) - This field contains a Timestamp Label indicating the beginning of the time range this Poll Response covers
    # inclusive_end_timestamp_label (datetime) - This field contains a Timestamp Label indicating the end of the time range this Poll Response covers.
    # subscription_id (string) - This field contains the Subscription ID for which this content is being provided.
    # message (string) - This field contains additional information for the message recipient
    # content_blocks (list of ContentBlock objects) - This field contains a piece of content and additional information related to the content.
    def __init__(self, 
                 message_id, 
                 in_response_to,
                 extended_headers=None,
                 feed_name = None,
                 inclusive_begin_timestamp_label = None,
                 inclusive_end_timestamp_label = None,
                 subscription_id = None,
                 message = None,
                 content_blocks=None
                 ):
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.feed_name = feed_name
        if inclusive_end_timestamp_label is not None:
            if inclusive_end_timestamp_label.tzinfo is None:
                raise ValueError('inclusive_end_timestamp_label.tzinfo must not be None')
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        if inclusive_begin_timestamp_label is not None:
            if inclusive_begin_timestamp_label.tzinfo is None:
                raise ValueError('inclusive_begin_timestamp_label.tzinfo must not be None')
        self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
        self.subscription_id = subscription_id
        self.message = message
        if content_blocks is None:
            self.content_blocks = []
        else:
            self.content_blocks = content_blocks
    
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
        
        if not self._checkPropertiesEq(other, ['feed_name','subscription_id','message','inclusive_begin_timestamp_label','inclusive_end_timestamp_label'], debug):
                return False
        
        #TODO: Check content blocks
        
        return True
    
    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(PollResponse, cls).from_etree(etree_xml)
        msg.feed_name = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]
        
        msg.subscription_id = None
        subs_ids = etree_xml.xpath('./@subscription_id', namespaces=ns_map)
        if len(subs_ids) > 0:
            msg.subscription_id = subs_ids[0]
        
        msg.message = None
        messages = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(messages) > 0:
            msg.message = messages[0].text
        
        msg.inclusive_begin_timestamp_label = None
        ibts = etree_xml.xpath('./taxii:Inclusive_Begin_Timestamp', namespaces=ns_map)
        if len(ibts) > 0:
            msg.inclusive_begin_timestamp_label = _str2datetime(ibts[0].text)
        
        msg.inclusive_end_timestamp_label = _str2datetime(etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)[0].text)
        
        msg.content_blocks = []
        blocks = etree_xml.xpath('./taxii:Content_Block', namespaces=ns_map)
        for block in blocks:
            msg.content_blocks.append(ContentBlock.from_etree(block))
        
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(PollResponse, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        
        msg.message = None
        if 'message' in d:
            msg.message = d['message']
        
        msg.subscription_id = None
        if 'subscription_id' in d:
            msg.subscription_id = d['subscription_id']
        
        msg.inclusive_begin_timestamp_label = None
        if 'inclusive_begin_timestamp_label' in d:
            msg.inclusive_begin_timestamp_label = _str2datetime(d['inclusive_begin_timestamp_label'])
        
        msg.inclusive_end_timestamp_label = _str2datetime(d['inclusive_end_timestamp_label'])
        
        msg.content_blocks = []
        for block in d['content_blocks']:
            msg.content_blocks.append(ContentBlock.from_dict(block))
        
        return msg

class StatusMessage(TAXIIMessage):
    message_type = MSG_STATUS_MESSAGE
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # status_type (string) - One of the defined Status Types or a third partydefined Status Type.
    # status_detail (string) - A field for additional information about this status in a machine-readable format.
    # message (string) - Additional information for the status. There is no expectation that this field be interpretable by a machine; it is instead targeted to a human operator. 
    def __init__(self, message_id, in_response_to, extended_headers=None, status_type=None, status_detail=None, message=None):
        super(StatusMessage, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.status_type = status_type
        self.status_detail = status_detail
        self.message = message
    
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
        msg = super(StatusMessage, cls).from_etree(etree_xml)
        msg.status_type = etree_xml.attrib['status_type']
        
        msg.status_detail = None
        sd_set = etree_xml.xpath('./taxii:Status_Detail', namespaces=ns_map)
        if len(sd_set) > 0:
            msg.status_detail = sd_set[0].text
        
        msg.message = None
        m_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(m_set) > 0:
            msg.message = m_set[0].text
        
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(StatusMessage, cls).from_dict(d)
        msg.status_type = d['status_type']
        msg.status_detail = None
        if 'status_detail' in d:
            msg.status_detail = d['status_detail']
        
        msg.message = None
        if 'message' in d:
            msg.message = d['message']
        
        return msg

class InboxMessage(TAXIIMessage):
    message_type = MSG_INBOX_MESSAGE
    # message_id (string) - A value identifying this message.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # message (string) - This field contains prose information for the message recipient.
    # subscription_information (a SubscriptionInformation object) - This field is only present if this message is being sent to provide content in accordance with an existing TAXII Data Feed subscription.
    # content_blocks (a list of ContentBlock objects) - 
    def __init__(self, message_id, in_response_to=None, extended_headers=None, message=None, subscription_information=None, content_blocks=None):
        super(InboxMessage, self).__init__(message_id, extended_headers=extended_headers)
        self.subscription_information = subscription_information
        self.message = message
        if content_blocks is None:
            self.content_blocks = []
        else:
            self.content_blocks = content_blocks
    
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
        
        if not self._checkPropertiesEq(other, ['message','subscription_information'], debug):
            return False
        
        if len(self.content_blocks) != len (other.content_blocks):
            if debug:
                print 'content block lengths not equal: %s != %s' % (len(self.content_blocks), len (other.content_blocks))
            return False
        
        #Who knows if this is a good way to compare the content blocks or not...
        for item1, item2 in zip(sorted(self.content_blocks), sorted(other.content_blocks)):
            if item1 != item2:
                if debug:
                    print 'content blocks not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)#This will print why they are not equal
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
        
        msg.message = None
        if 'message' in d:
            msg.message = d['message']
        
        msg.subscription_information = None
        if 'subscription_information' in d:
            msg.subscription_information = InboxMessage.SubscriptionInformation.from_dict(d['subscription_information'])
        
        msg.content_blocks = []
        for block in d['content_blocks']:
            msg.content_blocks.append(ContentBlock.from_dict(block))
        
        return msg
        
    class SubscriptionInformation(BaseNonMessage):
        # feed_name (string) - This field indicates the name of the TAXII Data Feed from which this content is being provided.
        # subcription_id (string) - This field contains the Subscription ID for which this content is being provided.
        # inclusive_begin_timestamp_label (datetime) - This field contains a Timestamp Label indicating the beginning of the time range this Inbox Message covers.
        # inclusive_end_timestamp_label (datetime) - This field contains a Timestamp Label indicating the end of the time range this Inbox Message covers.
        def __init__(self, feed_name, subscription_id, inclusive_begin_timestamp_label, inclusive_end_timestamp_label):
            self.feed_name = feed_name
            self.subscription_id = subscription_id
            if inclusive_begin_timestamp_label is not None:
                if inclusive_begin_timestamp_label.tzinfo is None:
                    raise ValueError('inclusive_begin_timestamp_label.tzinfo must not be None')
            self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
            if inclusive_end_timestamp_label is not None:
                if inclusive_end_timestamp_label.tzinfo is None:
                    raise ValueError('inclusive_end_timestamp_label.tzinfo must not be None')
            self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        
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
            return self._checkPropertiesEq(other, ['feed_name','subscription_id','inclusive_begin_timestamp_label','inclusive_end_timestamp_label'], debug)
        
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
    # message_id (string) - A value identifying this message.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # feed_name (string) - This field identifies the name of the TAXII Data Feed to which the action applies.
    # action (string) - This field identifies the requested action to take.
    # subscription_id (string) - This field contains the ID of a previously created subscription
    # delivery_parameters (a list of DeliveryParameter objects) - This field identifies the delivery parameters for this request. 
    def __init__(self, message_id, in_response_to=None, extended_headers=None, feed_name=None, action=None, subscription_id=None, delivery_parameters=None):
        super(ManageFeedSubscriptionRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.action = action
        self.subscription_id = subscription_id
        self.delivery_parameters = delivery_parameters
    
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
        
        return self._checkPropertiesEq(other, ['feed_name','subscription_id','action','delivery_parameters'], debug)
    
    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(ManageFeedSubscriptionRequest, cls).from_etree(etree_xml)
        msg.feed_name = etree_xml.xpath('./@feed_name', namespaces=ns_map)[0]
        msg.action = etree_xml.xpath('./@action', namespaces=ns_map)[0]
        msg.subscription_id = etree_xml.xpath('./@subscription_id', namespaces=ns_map)[0]
        msg.delivery_parameters = DeliveryParameters.from_etree(etree_xml.xpath('./taxii:Push_Parameters', namespaces=ns_map)[0])
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(ManageFeedSubscriptionRequest, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        msg.action = d['action']
        msg.subscription_id = d['subscription_id']
        msg.delivery_parameters = DeliveryParameters.from_dict(d['delivery_parameters'])
        return msg

class ManageFeedSubscriptionResponse(TAXIIMessage):
    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE
    # message_id (string) - A value identifying this message.
    # in_response_to (string) - Contains the Message ID of the message to which this is a response.
    # extended_headers (dictionary) - A dictionary of name/value pairs for use as Extended Headers
    # feed_name (string) - This field identifies the name of the TAXII Data Feed to which the action applies.
    # message (string) - This field contains a message associated with the subscription response.
    # subscription_instances (a list of SubscriptionInstance objects) - 
    def __init__(self, message_id, in_response_to, extended_headers=None, feed_name=None, message=None, subscription_instances=None):
        super(ManageFeedSubscriptionResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.message = message
        if subscription_instances is None:
            self.subscription_instances = []
        else:
            self.subscription_instances = subscription_instances
    
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
        
        if not self._checkPropertiesEq(other, ['feed_name','message'], debug):
            return False
        
        if len(self.subscription_instances) != len(other.subscription_instances):
            if debug:
                print 'subscription instance lengths not equal'
            return False
        
        #TODO: Compare the subscription instances
        
        return True
    
    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(ManageFeedSubscriptionResponse, cls).from_etree(etree_xml)
        msg.feed_name = etree_xml.attrib['feed_name']
        
        message_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
        if len(message_set) > 0:
            msg.message = message_set[0].text
        
        subscription_instance_set = etree_xml.xpath('./taxii:Subscription', namespaces=ns_map)
        
        msg.subscription_instances = []
        for si in subscription_instance_set:
            msg.subscription_instances.append(ManageFeedSubscriptionResponse.SubscriptionInstance.from_etree(si))
        
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(ManageFeedSubscriptionResponse, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        
        msg.message = None
        if 'message' in d:
            msg.message = d['message']
        
        msg.subscription_instances = []
        for instance in d['subscription_instances']:
            msg.subscription_instances.append(ManageFeedSubscriptionResponse.SubscriptionInstance.from_dict(instance))
        
        return msg
    
    class SubscriptionInstance(BaseNonMessage):
        # subscription_id (string) - This field contains an identifier that is used to reference the given subscription in subsequent exchanges.
        # delivery_parameters (a list of DeliveryParameter objects) - This field contains a copy of the Delivery Parameters of the Manage Feed Subscription Request Message that established this subscription.
        # poll_instances (a list of PollInstance objects) - Each Poll Instance represents an instance of a Poll Service that can be contacted to retrieve content associated with the new Subscription.
        def __init__(self, subscription_id, delivery_parameters=None, poll_instances=None):
            self.subscription_id = subscription_id
            if delivery_parameters is None:
                self.delivery_parameters = []
            else:
                self.delivery_parameters = delivery_parameters
            
            if poll_instances is None:
                self.poll_instances = []
            else:
                self.poll_instances = poll_instances
        
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
        
        # poll_protocol (string) - The protocol binding supported by this instance of a Polling Service.
        # poll_address (string) - This field identifies the address of the TAXII Daemon hosting this Poll Service.
        # poll_message_bindings (list of strings) - This field identifies one or more message bindings that can be used when interacting with this Poll Service instance.
        def __init__(self, poll_protocol, poll_address, poll_message_bindings=None):
            self.poll_protocol = poll_protocol
            self.poll_address = poll_address
            if poll_message_bindings is None:
                self.poll_message_bindings = []
            else:
                self.poll_message_bindings = poll_message_bindings
        
        def to_etree(self):
            xml = etree.Element('{%s}Poll_Instance' % ns_map['taxii'])
            
            pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii'])
            pb.text = self.poll_protocol
            
            a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii'])
            a.text = self.poll_address
            
            for binding in self.poll_message_bindings:
                b = etree.SubElement(xml, '{%s}Message_Bindingx' % ns_map['taxii'])
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
            if not self._checkPropertiesEq(other, ['poll_protocol','poll_address'], debug):
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



























