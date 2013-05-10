#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import random
import os
import StringIO
import datetime
from lxml import etree

#MSG_STATUS_MESSAGE = 'Status_Message'
MSG_DISCOVERY_REQUEST = 'Discovery_Request'
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'
#MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
#MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'
MSG_POLL_REQUEST = 'Poll_Request'
MSG_POLL_RESPONSE = 'Poll_Response'
#MSG_INBOX_MESSAGE = 'Inbox_Message'

SVC_INBOX = 'INBOX'
SVC_POLL = 'POLL'
SVC_FEED_MANAGEMENT = 'FEED_MANAGEMENT'
SVC_DISCOVERY = 'DISCOVERY'

VID_TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
VID_TAXII_XML_10 = 'urn:taxii.mitre.org:message:xml:1.0'
VID_TAXII_HTTP_10 = 'urn:taxii.mitre.org:protocol:http:1.0'
VID_TAXII_HTTPS_10 = 'urn:taxii.mitre.org:protocol:https:1.0'

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
    
    def __ne__(self, other, debug=False):
        return not self.__eq__(other, debug)

#The TAXIIMessage class keeps track of properties common to all TAXII Messages (i.e., headers).
#The TAXIIMessage class is extended by each Message Type (e.g., DiscoveryRequest), with each
#Subclass containing subclass-specific information
class TAXIIMessage(object):
    message_type = 'TAXIIMessage'
    def __init__(self, message_id, in_response_to=None, extended_headers={}):
        self.message_id = message_id
        self.in_response_to = in_response_to
        self.extended_headers = extended_headers
    
    #Creates the base etree for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to XML,
    #Subclasses should call this method first, then create their specific XML constructs
    def to_etree(self):
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
            raise ValueError('Not comparing two TAXII Messages!')
        if self.message_type != other.message_type:
            if debug: print 'message_type not equal: %s != %s' % (self.message_type, other.message_type)
            return False
        if self.message_id != other.message_id:
            if debug: print 'message_ids not equal: %s != %s' % (self.message_id, other.message_id)
            return False
        if self.in_response_to != other.in_response_to:
            if debug: print 'in_response_tos not equal: %s != %s' % (self.in_response_to, other.in_response_to)
            return False
        if self.extended_headers != other.extended_headers:
            if debug: print 'extended_headers not equal: %s != %s' % (self.extended_headers, other.extended_headers)
            return False
        return True
    
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
            if self.service_type != other.service_type:
                if debug: 
                    print 'service_types not equal: %s != %s' % (self.service_type, other.service_type)
                return False
            
            if self.service_version != other.service_version :
                if debug: 
                    print 'service_versions not equal: %s != %s' % (self.service_version, other.service_version)
                return False
            
            if self.protocol_binding != other.protocol_binding:
                if debug: 
                    print 'protocol_bindings not equal: %s != %s' % (self.protocol_binding, other.protocol_binding)
                return False
            
            if self.address != other.address:
                if debug: 
                    print 'addresses not equal: %s != %s' % (self.address, other.address)
                return False
            
            if self.available != other.available:
                if debug: 
                    print 'availables not equal: %s != %s' % (self.available, other.available)
                return False
            
            if self.message != other.message:
                if debug: 
                    print 'messages not equal: %s != %s' % (self.message, other.message)
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
            if self.feed_name != other.feed_name:
                if debug: 
                    print 'feed names not equal: %s != %s' % (self.feed_name, other.feed_name)
                return False
            
            if self.description != other.description:
                if debug: 
                    print 'descriptions not equal: %s != %s' % (self.description, other.description)
                return False
            
            if self.available != other.available:
                if debug: 
                    print 'availables not equal: %s != %s' % (self.available, other.available)
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
                 feed_name,
                 subscription_id=None,
                 exclusive_begin_timestamp=None,
                 inclusive_end_timestamp=None,
                 content_bindings=[],
                 extended_headers={}
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
        
        if self.feed_name != other.feed_name:
            if debug: 
                print 'feed names not equal: %s != %s' % (self.feed_name, other.feed_name)
            return False
        
        if self.subscription_id != other.subscription_id:
            if debug: 
                print 'subscription_ids not equal: %s != %s' % (self.subscription_id, other.subscription_id)
            return False
        
        if self.exclusive_begin_timestamp != other.exclusive_begin_timestamp:
            if debug: 
                print 'exclusive_begin_timestamps not equal: %s != %s' % (self.exclusive_begin_timestamp, other.exclusive_begin_timestamp)
            return False
        
        if self.inclusive_end_timestamp != other.inclusive_end_timestamp:
            if debug:
                print 'inclusive_end_timestamps not equal: %s != %s' % (self.inclusive_end_timestamp, other.inclusive_end_timestamp)
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
                 feed_name,
                 inclusive_end_timestamp,
                 subscription_id = None,
                 message = None,
                 inclusive_begin_timestamp = None,
                 content_blocks=[], 
                 extended_headers={}
                 ):
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.feed_name = feed_name
        self.inclusive_end_timestamp = inclusive_end_timestamp
        self.inclusive_begin_timestamp = inclusive_begin_timestamp
        self.subscription_id = subscription_id
        self.message = message
        self.content_blocks = content_blocks
    
    




















