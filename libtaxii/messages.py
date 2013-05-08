#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import random
from lxml import etree

MSG_DISCOVERY_REQUEST = 'Discovery_Request'
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'

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
def GenerateMessageId(maxlen=5):
    message_id = random.randint(1, 10 ** maxlen)
    return message_id

def xml2str(etree_xml):
    return etree.tostring(etree_xml)

#The TAXIIMessage class keeps track of properties common to all TAXII Messages (i.e., headers).
#The TAXIIMessage class is extended by each Message Type (e.g., DiscoveryRequest), with each
#Subclass containing subclass-specific information
class TAXIIMessage(object):
    MSG_TYPE = 'TAXIIMessage'
    def __init__(self, message_id, in_response_to=None, extended_headers={}):
        self.message_id = message_id
        self.in_response_to = in_response_to
        self.extended_headers = extended_headers
    
    #Creates the base XML for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to XML,
    #Subclasses should call this method first, then create their specific XML constructs
    def to_xml(self):
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii'], self.MSG_TYPE), nsmap=ns_map)
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
    
    #Creates the base dictionary for the TAXII Message. Message-specific constructs must be added
    #by each Message class. In general, when converting to dictionary,
    #Subclasses should call this method first, then create their specific dictionary constructs
    def to_dict(self):
        d = {}
        d['message_type'] = self.MSG_TYPE
        d['message_id'] = self.message_id
        if self.in_response_to is not None:
            d['in_response_to'] = self.in_response_to
        d['extended_headers'] = self.extended_headers
        
        return d
    
    #Pulls properties of a TAXII Message from XML. Message-specific constructs must be pulled
    #by each Message class. In general, when converting from XML,
    #Subclasses should call this method first, then parse their specific XML constructs
    @classmethod
    def from_xml(cls, etree_xml):
        #Get the message type
        message_type = etree_xml.tag[53:]
        if message_type != cls.MSG_TYPE:
            raise ValueError('%s != %s' % (message_type, cls.MSG_TYPE))
        
        #Get the message ID
        message_id = etree_xml.xpath('/taxii:*/@message_id', namespaces=ns_map)[0]
        
        #Get in response to, if present
        in_response_to = None
        in_response_tos = etree_xml.xpath('/taxii:*/@message_id', namespaces=ns_map)
        if len(in_response_tos) > 0:
            in_response_to = in_response_tos[0]
        
        #Get the Extended headers
        extended_header_list = etree_xml.xpath('/taxii:*/taxii:Extended_Headers/taxii:Extended_Header', namespaces=ns_map)
        extended_headers = {}
        for header in extended_header_list:
            eh_name = header.xpath('./@name')[0]
            eh_value = header.text
            extended_headers[eh_name] = eh_value
            
        return cls(message_id, in_response_to, extended_headers=extended_headers)
    
    #Pulls properties of a TAXII Message from a dictionary. Message-specific constructs must be pulled
    #by each Message class. In general, when converting from dictionary,
    #Subclasses should call this method first, then parse their specific dictionary constructs
    @classmethod
    def from_dict(cls, d):
        message_type = d['message_type']
        if message_type != cls.MSG_TYPE:
            raise ValueError('%s != %s' % (message_type, cls.MSG_TYPE))
        message_id = d['message_id']
        extended_headers = d['extended_headers']
        in_response_to = None
        if 'in_response_to' in d:
            in_response_to = d['in_response_to']
        return cls(message_id, in_response_to, extended_headers=extended_headers)

class ServiceContactInfo():
    NAME = 'ServiceContactInfo'
    def __init__(self, protocol_binding, address, message_bindings):
        self.protocol_binding=protocol_binding
        self.address = address
        self.message_bindings = message_bindings
    
    def to_xml(self):
        x = etree.Element('{%s}%s' % (self.NAME, ns_map['taxii']))
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
        proto_bind.text = self.protocol_binding
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
        address.text = self.address
        for binding in message_bindings:
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
    def from_xml(cls, etree_xml):
        kwargs = {}
        kwargs['protocol_binding'] = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
        kwargs['address'] = etree_xml.xpath('./taxii:Address', namespaces=ns_map)[0].text
        kwargs['message_bindings'] = []
        message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            kwargs['message_bindings'].append(message_binding)
        return cls(**kwargs)
    
    @staticmethod
    def from_dict(cls, d):
        return cls(**d)
        

#### TAXII Message Classes ####

class DiscoveryRequest(TAXIIMessage):
    MSG_TYPE = MSG_DISCOVERY_REQUEST

class DiscoveryResponse(TAXIIMessage):
    MSG_TYPE = MSG_DISCOVERY_RESPONSE
    def __init__(self, message_id, in_response_to, extended_headers={}, service_instances=[]):
        super(DiscoveryResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.service_instances = service_instances
    
    def to_xml(self):
        xml = super(DiscoveryResponse, self).to_xml()
        for service_instance in self.service_instances:
            xml.append(service_instance.to_xml())
        return xml
    
    def to_dict(self):
        d = super(DiscoveryResponse, self).to_dict()
        d['service_instances'] = []
        for service_instance in self.service_instances:
            d['service_instances'].append(service_instance.to_dict())
        return d
    
    @classmethod
    def from_xml(cls, etree_xml):
        msg = super(DiscoveryResponse, cls).from_xml(etree_xml)
        msg.service_instances = []
        service_instance_set = etree_xml.xpath('./taxii:Service_Instance', namespaces=ns_map)
        for service_instance in service_instance_set:
            si = DiscoveryResponse.ServiceInstance.from_xml(service_instance)
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
    
    class ServiceInstance():
        def __init__(self, service_type, service_version, protocol_binding, address, message_bindings, available=None, content_bindings=[], message=None):
            self.service_type = service_type
            self.service_version = service_version
            self.protocol_binding = protocol_binding
            self.address = address
            self.message_bindings = message_bindings
            self.content_bindings = content_bindings
            self.available = available
            self.message = message
        
        def to_xml(self):
            si = etree.Element('{%s}Service_Instance' % ns_map['taxii'])
            si.attrib['service_type'] = self.service_type
            si.attrib['service_version'] = self.service_version
            if self.available is not None: si.attrib['available'] = self.available
            
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
        
        @staticmethod
        def from_xml(etree_xml):#Expects a taxii:Service_Instance element
            service_type = etree_xml.attrib['service_type']
            service_version = etree_xml.attrib['service_version']
            available = None
            if 'available' in etree_xml.attrib: available = etree_xml.attrib['available']
            
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
    MSG_TYPE = MSG_FEED_INFORMATION_REQUEST

class FeedInformationResponse(TAXIIMessage):
    MSG_TYPE = MSG_FEED_INFORMATION_RESPONSE
    def __init__(self, message_id, in_response_to, extended_headers={}, feeds=[]):
        super(FeedInformationResponse, self).__init__(MSG_FEED_INFORMATION_RESPONSE, message_id, in_response_to, extended_headers=extended_headers)
        self.feeds = feeds
    
    def to_xml(self):
        xml = super(FeedInformationResponse, self).to_xml()
        for feed in self.feeds:
            xml.append(feed.to_xml())
        return xml
    
    def to_dict(self):
        d = super(FeedInformationResponse, self).to_dict()
        for feed in self.feeds:
            d.append(feed.to_dict())
        return d
    
    @classmethod
    def from_xml(cls, etree_xml):
        msg = super(FeedInformationResponse, cls).from_xml(etree_xml)
        msg.feeds = []
        feeds = etree_xml.xpath('./taxii:Feed', namespaces=ns_map)
        for feed in feeds:
            msg.feeds.append(Feed.from_xml(feed))
        return msg
    
    @classmethod
    def from_dict(cls, d):
        msg = super(FeedInformationResponse, cls).from_dict(d)
        msg.feeds = []
        for feed in d['feeds']:
            msg.feeds.append(Feed.from_dict(feed))
        return msg
    
    class Feed():
        def __init__(self, description, content_bindings, push_methods=[], polling_services=[], subscription_services=[]):
            self.description = description
            self.content_bindings = content_bindings
            self.push_methods = push_methods
            self.polling_services = polling_services
            self.subscription_services = subscription_services
        
        def to_xml(self):
            f = etree.Element('{%s}Feed' % ns_map['taxii'])
            description = etree.SubElement('{%s}Description' % ns_map['taxii'])
            description.text = self.description
            
            for binding in self.content_bindings:
                cb = etree.Element('{%s}Content_Binding' % ns_map['taxii'])
                cb.text = binding
            
            for push_method in self.push_methods:
                f.append(push_method.to_xml())
            
            for polling_service in self.polling_services:
                f.append(polling_service.to_xml())
            
            for subscription_service in self.subscription_services:
                f.append(subscription_service.to_xml())
            
            return f
        
        def to_dict(self):
            d = {}
            d['description'] = self.description
            d['content_bindings'] = self.content_bindings
            d['push_methods'] = []
            for push_method in push_methods:
                d['push_methods'].append(push_method.to_dict())
            d['polling_services'] = []
            for polling_service in polling_services:
                d['polling_services'].append(polling_service.to_dict())
            d['subscription_services'] = []
            for subscription_service in subscription_services:
                d['subscription_services'].append(subscription_service.to_dict())
            return d
        
        @staticmethod
        def from_xml(etree_xml):
            pass
        
        @staticmethod
        def from_dict(d):
            pass
        
        class PushMethod():
            def __init__(self, protocol_binding, message_bindings):
                self.protocol_binding=protocol_binding
                self.message_bindings = message_bindings
            
            def to_xml(self):
                x = etree.Element('{%s}Push_Method' % ns_map['taxii'])
                proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
                proto_bind.text = self.protocol_binding
                for binding in message_bindings:
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
            
            @classmethod
            def from_xml(cls, etree_xml):
                kwargs = {}
                kwargs['protocol_binding'] = etree_xml.xpath('./taxii:Protocol_Binding', namespaces=ns_map)[0].text
                kwargs['message_bindings'] = []
                message_binding_set = etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map)
                for message_binding in message_binding_set:
                    kwargs['message_bindings'].append(message_binding)
                return cls(**kwargs)
            
            @staticmethod
            def from_dict(cls, d):
                return cls(**d)
        
        class PollingService(ServiceContactInfo):
            NAME = 'Polling_Service'
        
        class SubscriptionService():
            NAME = 'Subscription_Service'




