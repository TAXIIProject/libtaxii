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

#Version IDs
VID_TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
VID_TAXII_XML_10 = 'urn:taxii.mitre.org:message:xml:1.0'
VID_TAXII_HTTP_10 = 'urn:taxii.mitre.org:protocol:http:1.0'
VID_TAXII_HTTPS_10 = 'urn:taxii.mitre.org:protocol:https:1.0'

#Content Bindings
CB_STIX_XML_10 = 'urn:stix.mitre.org:xml:1.0'
CB_CAP_11 = 'urn:oasis:names:tc:emergency:cap:1.1'
CB_XENC_122002 = 'http://www.w3.org/2001/04/xmlenc#'

ns_map = {'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1'}#, 
          #TODO: figure out what to do with the digital signature namespace
          #'ds': 'http://www.w3.org/2000/09/xmldsig#'}

### General purpose helper methods ###

#Generate a TAXII Message ID
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

def get_message_from_xml(xml_string):
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string
    
    etree_xml = etree.parse(f).getroot()
    message_type = etree_xml.tag[53:]
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
    if message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_etree(etree_xml)
    
    raise ValueError('Unknown message_type: %s' % message_type)

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
    if message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_dict(d)
    
    raise ValueError('Unknown message_type: %s' % message_type)

#TODO: find a better way of parsing a string into a datetime object
def _str2datetime(date_string):
    if '.' in date_string:
        return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
    
    return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

#Allows for code reuse in non-TAXII Message objects
class BaseNonMessage(object):
    
    
    def to_etree(self):#Implemented by child classes
        pass
    
    def to_dict(self):#Implemented by child classes
        pass
    
    def to_xml(self):
        return etree.tostring(self.to_etree)
    
    @classmethod
    def from_etree(cls, src_etree):#Implemented by child classes
        pass
    
    @classmethod
    def from_dict(cls, src_etree):#Implemented by child classes
        pass
    
    @classmethod
    def from_xml(cls, xml):
        
        if isinstance(xml, basestring):
            f = StringIO.StringIO(xml)
        else:
            f = xml
        
        etree_xml = etree.parse(f).getroot()
        return cls.from_etree(etree_xml)
    
    def __eq__(self, other, debug=False):
        pass
    
    def _checkPropertiesEq(self, other, arglist, debug=False):
        if debug: print 'rararararara'
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

#The TAXIIMessage class keeps track of properties common to all TAXII Messages (i.e., headers).
#The TAXIIMessage class is extended by each Message Type (e.g., DiscoveryRequest), with each
#Subclass containing subclass-specific information
class TAXIIMessage(BaseNonMessage):
    message_type = 'TAXIIMessage'
    def __init__(self, message_id, in_response_to=None, extended_headers={}):
        self.message_id = message_id
        self.in_response_to = in_response_to
        self.extended_headers = extended_headers
    
    #Creates the base etree for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to XML,
    #Subclasses should call this method first, then create their specific XML constructs
    def to_etree(self):
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii'], self.message_type))
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
    def __init__(self, content_binding, content, timestamp_label = None, padding = None):
        self.content_binding = content_binding
        self.content = content
        self.timestamp_label = timestamp_label
        self.padding = padding
    
    def to_etree(self):
        block = etree.Element('{%s}Content_Block' % ns_map['taxii'])
        cb = etree.SubElement(block, '{%s}Content_Binding' % ns_map['taxii'])
        cb.text = self.content_binding
        c = etree.SubElement(block, '{%s}Content' % ns_map['taxii'])
        
        if isinstance(self.content, etree._Element):#For XML
            c.append(self.content)
        else:#Assume it is a string
            c.text = self.content
        
        if self.timestamp_label is not None:
            tl = etree.SubElement(block, '{%s}Timestamp_Label' % ns_map['taxii'])
            tl.text = self.timestamp_label.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        if self.padding is not None:
            p = etree.SubElement(block, '{%s}Timestamp_Label' % ns_map['taxii'])
            p.text = self.padding
        
        return block
    
    def to_dict(self):
        block = {}
        block['content_binding'] = self.content_binding
        
        if isinstance(self.content, etree._Element):#For XML
            block['content'] = etree.tostring(self.content)
        else:#Assume string
            block['content'] = self.content
        
        if self.timestamp_label is not None:
            block['timestamp_label'] = self.timestamp_label
        
        if self.padding is not None:
            block['padding'] = self.padding
        
        return block
    
    def __eq__(self, other, debug=False):
        if not self._checkPropertiesEq(other, ['content_binding','timestamp_label','padding'], debug):
            return False
        
        if isinstance(self.content, etree) and isinstance(other.content, etree):
            #TODO: Implement comparison for etrees
            pass
        elif isinstance(self.content, basestring) and isinstance(other.content, basestring):
            if self.content != other.content:
                if debug:
                    print 'contents not equal: %s != %s' % (self.content, other.content)
                return False
        else:
            if debug:
                print 'content not of same type: %s != %s' % (self.content.__class__.__name__, other.content.__class__.name__)
            return False
        
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
        
        content = etree_xml.xpath('./taxii:Content', namespaces=ns_map)
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
            kwargs['timestamp_label'] = d['timestamp_label']
        
        if d['content'].startswith('<'):
            kwargs['content'] = etree.parse(StringIO.StringIO(d['content']))
        else:
            kwargs['content'] = d['content']
        
        return ContentBlock(**kwargs)

class ServiceContactInfo(BaseNonMessage):
    NAME = 'ServiceContactInfo'
    def __init__(self, protocol_binding, address, message_bindings):
        self.protocol_binding=protocol_binding
        self.address = address
        self.message_bindings = message_bindings
    
    def to_etree(self):
        x = etree.Element('{%s}%s' % (ns_map['taxii'], self.NAME))
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
        proto_bind.text = self.protocol_binding
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
        address.text = self.address
        for binding in self.message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
            b.text = binding
        return x
    
    def to_dict(self):
        d = {}
        d['protocol_binding'] = self.protocol_binding
        d['address'] = self.address
        d['message_bindings'] = []
        for binding in self.message_bindings:
            d['message_bindings'].append(binding)
        return d
    
    def __eq__(self, other, debug=False):
        pass#TODO: Implement this
    
    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['protocol_binding'] = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
        kwargs['address'] = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
        kwargs['message_bindings'] = []
        message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            kwargs['message_bindings'].append(message_binding)
        return cls(**kwargs)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)
        

#### TAXII Message Classes ####

class DiscoveryRequest(TAXIIMessage):
    message_type = MSG_DISCOVERY_REQUEST

class DiscoveryResponse(TAXIIMessage):
    message_type = MSG_DISCOVERY_RESPONSE
    def __init__(self, message_id, in_response_to, extended_headers={}, service_instances=[]):
        super(DiscoveryResponse, self).__init__(message_id, in_response_to, extended_headers)
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
        def __init__(self, service_type, service_version, protocol_binding, address, message_bindings, available=None, content_bindings=[], message=None):
            self.service_type = service_type
            self.service_version = service_version
            self.protocol_binding = protocol_binding
            self.address = address
            self.message_bindings = message_bindings
            self.content_bindings = content_bindings
            self.available = available
            self.message = message
        
        def to_etree(self):
            si = etree.Element('{%s}Service_Instance' % ns_map['taxii'])
            si.attrib['service_type'] = self.service_type
            si.attrib['service_version'] = self.service_version
            if self.available is not None: 
                si.attrib['available'] = self.available
            
            protocol_binding = etree.SubElement(si, '{%s}Protocol_Binding' % ns_map['taxii'])
            protocol_binding.text = self.protocol_binding
            
            address = etree.SubElement(si, '{%s}Address' % ns_map['taxii'])
            address.text = self.address
            
            for mb in self.message_bindings:
                message_binding = etree.SubElement(si, '{%s}Message_Binding' % ns_map['taxii'])
                message_binding.text = mb
            
            for cb in self.content_bindings:
                content_binding = etree.SubElement(si, '{%s}Content_Binding' % ns_map['taxii'])
                content_binding.text = cb
            
            if self.message is not None:
                message = etree.SubElement(si, '{%s}Message' % ns_map['taxii'])
                message.text = self.message
            
            return si
        
        def to_dict(self):
            d = {}
            d['service_type'] = self.service_type
            d['service_version'] = self.service_version
            d['protocol_binding'] = self.protocol_binding
            d['address'] = self.address
            d['message_bindings'] = self.message_bindings
            d['content_bindings'] = self.content_bindings
            d['available'] = self.available
            d['message'] = self.message
            return d
        
        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['service_type','service_version','protocol_binding','address','available','message'], debug):
                return False
            
            if set(self.message_bindings) != set(other.message_bindings):
                if debug: 
                    print 'message_bindings not equal'
                return False
            
            if set(self.content_bindings) != set(other.content_bindings):
                if debug: 
                    print 'content_bindings not equal'
                return False
            
            return True
        
        @staticmethod
        def from_etree(etree_xml):#Expects a taxii:Service_Instance element
            service_type = etree_xml.attrib['service_type']
            service_version = etree_xml.attrib['service_version']
            available = None
            if 'available' in etree_xml.attrib: 
                available = etree_xml.attrib['available']
            
            protocol_binding = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
            address = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
            
            message_bindings = []
            message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
            for mb in message_binding_set:
                message_bindings.append(mb.text)
            
            content_bindings = []
            content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for cb in content_binding_set:
                content_bindings.append(cb.text)
            
            message = None
            message_set = etree_xml.xpath('./taxii:Message', namespaces=ns_map)
            if len(message_set) > 0:
                message = message_set[0].text
            
            return DiscoveryResponse.ServiceInstance(service_type, service_version, protocol_binding, address, message_bindings, available, content_bindings, message)
        
        @staticmethod
        def from_dict(d):
            return DiscoveryResponse.ServiceInstance(**d)

class FeedInformationRequest(TAXIIMessage):
    message_type = MSG_FEED_INFORMATION_REQUEST

class FeedInformationResponse(TAXIIMessage):
    message_type = MSG_FEED_INFORMATION_RESPONSE
    def __init__(self, message_id, in_response_to, extended_headers={}, feeds=[]):
        super(FeedInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feeds = feeds
    
    def to_etree(self):
        xml = super(FeedInformationResponse, self).to_etree()
        for feed in self.feeds:
            xml.append(feed.to_etree())
        return xml
    
    def to_dict(self):
        d = super(FeedInformationResponse, self).to_dict()
        d['feeds'] = []
        for feed in self.feeds:
            d['feeds'].append(feed.to_dict())
        return d
    
    def __eq__(self, other, debug=False):
        if not super(FeedInformationResponse, self).__eq__(other, debug):
            return False
        
        #Who knows if this is a good way to compare the service instances or not...
        for item1, item2 in zip(sorted(self.feeds), sorted(other.feeds)):
            if item1 != item2:
                if debug: 
                    print 'feeds not equal: %s != %s' % (item1, item2)
                    item1.__eq__(item2, debug)#This will print why they are not equal
                return False
        
        return True
    
    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(FeedInformationResponse, cls).from_etree(etree_xml)
        msg.feeds = []
        feeds = etree_xml.xpath('./taxii:Feed', namespaces=ns_map)
        for feed in feeds:
            msg.feeds.append(FeedInformationResponse.Feed.from_etree(feed))
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(FeedInformationResponse, cls).from_dict(d)
        msg.feeds = []
        for feed in d['feeds']:
            msg.feeds.append(FeedInformationResponse.Feed.from_dict(feed))
        return msg
    
    class Feed(BaseNonMessage):
        def __init__(self, feed_name, description, content_bindings, available=None, push_methods=[], polling_services=[], subscription_services=[]):
            self.feed_name = feed_name
            self.available = available
            self.description = description
            self.content_bindings = content_bindings
            self.push_methods = push_methods
            self.polling_services = polling_services
            self.subscription_services = subscription_services
        
        def to_etree(self):
            f = etree.Element('{%s}Feed' % ns_map['taxii'])
            f.attrib['feed_name'] = self.feed_name
            if self.available is not None:
                f.attrib['available'] = self.available
            description = etree.SubElement(f, '{%s}Description' % ns_map['taxii'])
            description.text = self.description
            
            for binding in self.content_bindings:
                cb = etree.SubElement(f, '{%s}Content_Binding' % ns_map['taxii'])
                cb.text = binding
            
            for push_method in self.push_methods:
                f.append(push_method.to_etree())
            
            for polling_service in self.polling_services:
                f.append(polling_service.to_etree())
            
            for subscription_service in self.subscription_services:
                f.append(subscription_service.to_etree())
            
            return f
        
        def to_dict(self):
            d = {}
            d['feed_name'] = self.feed_name
            if self.available is not None:
                d['available'] = self.available
            d['description'] = self.description
            d['content_bindings'] = self.content_bindings
            d['push_methods'] = []
            for push_method in self.push_methods:
                d['push_methods'].append(push_method.to_dict())
            d['polling_services'] = []
            for polling_service in self.polling_services:
                d['polling_services'].append(polling_service.to_dict())
            d['subscription_services'] = []
            for subscription_service in self.subscription_services:
                d['subscription_services'].append(subscription_service.to_dict())
            return d
        
        def __eq__(self, other, debug=False):
            if not self._checkPropertiesEq(other, ['feed_name','description','available'], debug):
                return False
            
            if set(self.content_bindings) != set(other.content_bindings):
                if debug: 
                    print 'content bindings not equal: %s != %s' % (self.content_bindings, other.content_bindings)
                return False
            
            #TODO: Test equality of: push_methods=[], polling_services=[], subscription_services=[]
            
            return True
        
        @staticmethod
        def from_etree(etree_xml):
            kwargs = {}
            kwargs['feed_name'] = etree_xml.attrib['feed_name']
            kwargs['available'] = None
            if 'available' in etree_xml.attrib:
                kwargs['available'] = etree_xml.attrib['available']
            
            kwargs['description'] = etree_xml.xpath('./taxii:Description', namespaces=ns_map)[0].text
            kwargs['content_bindings'] = []
            content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
            for binding_elt in content_binding_set:
                kwargs['content_bindings'].append(binding_elt.text)
            
            kwargs['push_methods'] = []
            push_method_set = etree_xml.xpath('./taxii:Push_Method', namespaces=ns_map)
            for push_method_elt in push_method_set:
                kwargs['push_methods'].append(FeedInformationResponse.Feed.PushMethod.from_etree(push_method_elt))
            
            kwargs['polling_services'] = []
            polling_service_set = etree_xml.xpath('./taxii:Polling_Service', namespaces=ns_map)
            for polling_elt in polling_service_set:
                kwargs['polling_services'].append(FeedInformationResponse.Feed.PollingService.from_etree(polling_elt))
            
            kwargs['subscription_services'] = []            
            subscription_service_set = etree_xml.xpath('./taxii:Subscription_Service', namespaces=ns_map)
            for subscription_elt in subscription_service_set:
                kwargs['subscription_services'].append(FeedInformationResponse.Feed.SubscriptionService.from_etree(subscription_elt))
            
            return FeedInformationResponse.Feed(**kwargs)
        
        @staticmethod
        def from_dict(d):
            kwargs = {}
            kwargs['feed_name'] = d['feed_name']
            kwargs['available'] = None
            if 'available' in d:
                kwargs['available'] = d['available']
            
            kwargs['description'] = d['description']
            kwargs['content_bindings'] = []
            if 'content_bindings' in d:
                for binding in d['content_bindings']:
                    kwargs['content_bindings'].append(binding)
            
            kwargs['push_methods'] = []
            if 'push_methods' in d:
                for push_method in d['push_methods']:
                    kwargs['push_methods'].append(FeedInformationResponse.Feed.PushMethod.from_dict(push_method))
            
            kwargs['polling_services'] = []
            if 'polling_services' in d:
                for polling in d['polling_services']:
                    kwargs['polling_services'].append(FeedInformationResponse.Feed.PollingService.from_dict(polling))
            
            kwargs['subscription_services'] = []
            if 'subscription_services' in d:
                for subscription_svc in d['subscription_services']:
                    kwargs['subscription_services'].append(FeedInformationResponse.Feed.SubscriptionService.from_dict(subscription_svc))
            
            return FeedInformationResponse.Feed(**kwargs)
        
        class PushMethod(BaseNonMessage):
            def __init__(self, protocol_binding, message_bindings):
                self.protocol_binding=protocol_binding
                self.message_bindings = message_bindings
            
            def to_etree(self):
                x = etree.Element('{%s}Push_Method' % ns_map['taxii'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
                proto_bind.text = self.protocol_binding
                for binding in self.message_bindings:
                    b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
                    b.text = binding
                return x
            
            def to_dict(self):
                d = {}
                d['protocol_binding'] = self.protocol_binding
                d['message_bindings'] = []
                for binding in self.message_bindings:
                    d['message_bindings'].append(binding)
                return d
            
            def __eq__(self, other, debug=False):
                pass#TODO: Implement this
            
            @staticmethod
            def from_etree(etree_xml):
                kwargs = {}
                kwargs['protocol_binding'] = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
                kwargs['message_bindings'] = []
                message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
                for message_binding in message_binding_set:
                    kwargs['message_bindings'].append(message_binding)
                return FeedInformationResponse.Feed.PushMethod(**kwargs)
            
            @staticmethod
            def from_dict(d):
                return FeedInformationResponse.Feed.PushMethod(**d)
        
        class PollingService(ServiceContactInfo):#TODO - maybe inherit from push method?
            NAME = 'Polling_Service'
        
        class SubscriptionService(ServiceContactInfo):#TODO - maybe inherit from push method?
            NAME = 'Subscription_Service'

class PollRequest(TAXIIMessage):
    message_type = MSG_POLL_REQUEST
    def __init__(self, 
                 message_id,
                 in_response_to=None,
                 extended_headers={},
                 feed_name=None,
                 subscription_id=None,
                 exclusive_begin_timestamp=None,
                 inclusive_end_timestamp=None,
                 content_bindings=[]
                 ):
        super(PollRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.exclusive_begin_timestamp = exclusive_begin_timestamp
        self.inclusive_end_timestamp = inclusive_end_timestamp
        self.subscription_id = subscription_id
        self.content_bindings = content_bindings
    
    def to_etree(self):
        xml = super(PollRequest, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id
        
        if self.exclusive_begin_timestamp is not None:
            ebt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii'])
            #TODO: Add TZ Info
            ebt.text = self.exclusive_begin_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        if self.inclusive_end_timestamp is not None:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
            #TODO: Add TZ Info
            iet.text = self.inclusive_end_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for binding in self.content_bindings:
            b = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii'])
            b.text = binding
        
        return xml
    
    def to_dict(self):
        d = super(PollRequest, self).to_dict()
        d['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.exclusive_begin_timestamp is not None:#TODO: Add TZ Info
            d['exclusive_begin_timestamp'] = self.exclusive_begin_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        if self.inclusive_end_timestamp is not None:#TODO: Add TZ Info
            d['inclusive_end_timestamp'] = self.inclusive_end_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        d['content_bindings'] = []
        for bind in self.content_bindings:
            d['content_bindings'].append(bind)
        return d
    
    def __eq__(self, other, debug=False):
        if not super(PollRequest, self).__eq__(other, debug):
            return False
        
        if not self._checkPropertiesEq(other, ['feed_name','subscription_id','exclusive_begin_timestamp','inclusive_end_timestamp'], debug):
                return False
        
        if set(self.content_bindings) != set(other.content_bindings):
            if debug: 
                print 'content_bindingss not equal: %s != %s' % (self.content_bindings, other.content_bindings)
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
        
        msg.exclusive_begin_timestamp = None
        begin_ts_set = etree_xml.xpath('./taxii:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if len(begin_ts_set) > 0:
            msg.exclusive_begin_timestamp = _str2datetime(begin_ts_set[0].text)
        
        msg.inclusive_end_timestamp = None
        end_ts_set = etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)
        if len(end_ts_set) > 0:
            msg.inclusive_end_timestamp = _str2datetime(end_ts_set[0].text)
        
        msg.content_bindings = []
        content_binding_set = etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map)
        for binding in content_binding_set:
            msg.content_bindings.append(binding)
        
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(PollRequest, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        
        msg.subscription_id = None
        if 'subscription_id' in d:
            msg.subscription_id = d['subscription_id']
        
        msg.exclusive_begin_timestamp = None
        if 'exclusive_begin_timestamp' in d:
            msg.exclusive_begin_timestamp = _str2datetime(d['exclusive_begin_timestamp'])
        
        msg.inclusive_end_timestamp = None
        if 'inclusive_end_timestamp' in d:
            msg.inclusive_end_timestamp = _str2datetime(d['inclusive_end_timestamp'])
        
        msg.content_bindings = []
        if 'content_bindings' in d:
            msg.content_bindings = d['content_bindings']
        
        return msg

class PollResponse(TAXIIMessage):
    message_type = MSG_POLL_RESPONSE
    
    def __init__(self, 
                 message_id, 
                 in_response_to,
                 extended_headers={},
                 feed_name = None,
                 inclusive_end_timestamp = None,
                 subscription_id = None,
                 message = None,
                 inclusive_begin_timestamp = None,
                 content_blocks=[]
                 ):
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.feed_name = feed_name
        self.inclusive_end_timestamp = inclusive_end_timestamp
        self.inclusive_begin_timestamp = inclusive_begin_timestamp
        self.subscription_id = subscription_id
        self.message = message
        self.content_blocks = content_blocks
    
    def to_etree(self):
        xml = super(PollResponse, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id
        
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message
        
        if self.inclusive_begin_timestamp is not None:
            ibt = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
            ibt.text = self.inclusive_begin_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
        iet.text = self.inclusive_end_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        
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
        if self.inclusive_begin_timestamp is not None:
            d['inclusive_begin_timestamp'] = self.inclusive_begin_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        d['inclusive_end_timestamp'] = self.inclusive_end_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())
        
        return d
    
    def __eq__(self, other, debug=False):
        if not super(PollResponse, self).__eq__(other, debug):
            return False
        
        if not self._checkPropertiesEq(other, ['feed_name','subscription_id','message','inclusive_begin_timestamp','inclusive_end_timestamp'], debug):
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
        
        msg.inclusive_begin_timestamp = None
        ibts = etree_xml.xpath('./taxii:Inclusive_Begin_Timestamp', namespaces=ns_map)
        if len(ibts) > 0:
            msg.inclusive_begin_timestamp = _str2datetime(ibts[0].text)
        
        msg.inclusive_end_timestamp = _str2datetime(etree_xml.xpath('./taxii:Inclusive_End_Timestamp', namespaces=ns_map)[0].text)
        
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
        
        msg.inclusive_begin_timestamp = None
        if 'inclusive_begin_timestamp' in d:
            msg.inclusive_begin_timestamp = _str2datetime(d['inclusive_begin_timestamp'])
        
        msg.inclusive_end_timestamp = _str2datetime(d['inclusive_end_timestamp'])
        
        msg.content_blocks = []
        for block in d['content_blocks']:
            msg.content_blocks.append(ContentBlock.from_dict(block))
        
        return msg

class StatusMessage(TAXIIMessage):
    message_type = MSG_STATUS_MESSAGE
    
    def __init__(self, message_id, in_response_to, extended_headers={}, status_type=None, status_detail=None, message=None):
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
    
    def __init__(self, message_id, in_response_to=None, extended_headers={}, content_blocks=[], message=None, subscription_information=None):
        super(InboxMessage, self).__init__(message_id, extended_headers=extended_headers)
        self.content_blocks = content_blocks
        self.subscription_information = subscription_information
        self.message = message
    
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
        
        #TODO: Check content blokcs
        
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
        
        content_blocks = etree_xml.xpath('./taxii:Content_Blocks', namespaces=ns_map)
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
        def __init__(self, feed_name, subscription_id, inclusive_begin_timestamp_label, inclusive_end_timestamp_label):
            self.feed_name = feed_name
            self.subscription_id = subscription_id
            self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
            self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        
        def to_etree(self):
            xml = etree.Element('{%s}Source_Subscription' % ns_map['taxii'])
            xml.attrib['feed_name'] = self.feed_name
            xml.attrib['subscription_id'] = self.subscription_id
            
            ibtl = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
            ibtl.text = self.inclusive_begin_timestamp_label.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            ietl = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
            ietl.text = self.inclusive_end_timestamp_label.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            return xml
        
        def to_dict(self):
            d = {}
            d['feed_name'] = self.feed_name
            d['subscription_id'] = self.subscription_id
            d['inclusive_begin_timestamp_label'] = self.inclusive_begin_timestamp_label.strftime('%Y-%m-%d %H:%M:%S.%f')
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.strftime('%Y-%m-%d %H:%M:%S.%f')
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
    
    def __init__(self, message_id, in_response_to=None, extended_headers={}, feed_name=None, action=None, subscription_id=None, delivery_parameters=None):
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
        msg.delivery_parameters = ManageFeedSubscriptionRequest.DeliveryParameters.from_etree(etree_xml.xpath('./taxii:Push_Parameters', namespaces=ns_map)[0])
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(ManageFeedSubscriptionRequest, cls).from_dict(d)
        msg.feed_name = d['feed_name']
        msg.action = d['action']
        msg.subscription_id = d['subscription_id']
        msg.delivery_parameters = ManageFeedSubscriptionRequest.DeliveryParameters.from_dict(d['delivery_parameters'])
        return msg
    
    class DeliveryParameters(BaseNonMessage):
        def __init__(self, inbox_protocol=None, inbox_address=None, delivery_message_binding=None, content_bindings=[]):
            self.inbox_protocol=inbox_protocol
            self.inbox_address=inbox_address
            self.delivery_message_binding = delivery_message_binding
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
            
            return ManageFeedSubscriptionRequest.DeliveryParameters(inbox_protocol, inbox_address, delivery_message_binding, content_bindings)
        
        @staticmethod
        def from_dict(d):
            return ManageFeedSubscriptionRequest.DeliveryParameters(**d)

class ManageFeedSubscriptionResponse(TAXIIMessage):
    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE
    
    def __init__(self, message_id, in_response_to, extended_headers={}, feed_name=None, message=None, subscription_instances=None)
        super(ManageFeedSubscriptionResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.message = message
        self.subscription_instances = subscription_instances
        raise Exception('Class not fully implemented yet!')
    
    #TODO: Fill out the rest of this





