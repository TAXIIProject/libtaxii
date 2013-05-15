#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import uuid
import StringIO
import os
from lxml import etree
from M2Crypto import BIO, Rand, SMIME, X509

ns_dict = {'taxii': 'http://taxii.mitre.org/messages/taxii_xml_binding-1'}

#Define ease-of-use constants
STATUS_TYPE_BAD_MESSAGE = 'BAD_MESSAGE'
STATUS_TYPE_DENIED = 'DENIED'
STATUS_TYPE_FAILURE = 'FAILURE'
STATUS_TYPE_NOT_FOUND = 'NOT_FOUND'
STATUS_TYPE_POLLING_UNSUPPORTED = 'POLLING_UNSUPPORTED'
STATUS_TYPE_RETRY = 'RETRY'
STATUS_TYPE_SUCCESS = 'SUCCESS'
STATUS_TYPE_UNAUTHORIZED = 'UNAUTHORIZED'
STATUS_TYPE_UNSUPPORTED_MESSAGE = 'UNSUPPORTED_MESSAGE'
STATUS_TYPE_UNSUPPORTED_CONTENT = 'UNSUPPORTED_CONTENT'
STATUS_TYPE_UNSUPPORTED_PROTOCOL = 'UNSUPPORTED_PROTOCOL'

class TaxiiDecryptException(Exception):
    def __init__(self, value):
        self.value = value

# Take in a blob of data and a public key. Encrypts and
# returns the encrypted blob.
def encrypt_payload(blob, pubkey):
    # Make a MemoryBuffer of the message.
    inbuf = BIO.MemoryBuffer(blob)

    # Seed the PRNG.
    Rand.rand_seed(os.urandom(1024))

    # Instantiate an SMIME object.
    s = SMIME.SMIME()

    # Load target cert to encrypt to.
    x509 = X509.load_cert(pubkey)
    sk = X509.X509_Stack()
    sk.push(x509)
    s.set_x509_stack(sk)

    # Set cipher: AES 256 bit in CBC mode.
    s.set_cipher(SMIME.Cipher('aes_256_cbc'))

    # Encrypt the buffer.
    p7 = s.encrypt(inbuf)
    temp_buff = BIO.MemoryBuffer()
    s.write(temp_buff, p7)
    x = temp_buff.read()
    return x

def decrypt_payload(blob, privkey, pubkey):
    inbuf = BIO.MemoryBuffer(blob.read())
    s = SMIME.SMIME()
    s.load_key(privkey, pubkey)
    p7, data = SMIME.smime_load_pkcs7_bio(inbuf)
    try:
        buf = s.decrypt(p7)
    except SMIME.PKCS7_Error, e:
        raise TaxiiDecryptException(e)
    return buf

#Required dictionary keys:
# message_id - the id of the message
# in_response_to - the id of the message that this message is in response to
# status_type - the status type of this status message
#
#Optional dictionary keys:
# extended_headers - a dictionary of key/value pairs to become extended headers
# status_detail - a string containing the status detail
# message - a string containing the message
#
def dict2xmlStatusMessage(dictionary):
    status_msg = etree.Element('{%s}Status_Message' % ns_dict['taxii'])
    if 'in_response_to' not in dictionary: raise ValueError('in_response_to is a required field')
    __addHeadersDict2xml(status_msg, dictionary)
    if 'status_type' not in dictionary: raise ValueError('status_type is a required field')
    status_msg.attrib['status_type'] = dictionary['status_type']
    
    if 'status_detail' in dictionary:
        detail = etree.SubElement(status_msg, '{%s}Status_Detail' % ns_dict['taxii'])
        detail.text = dictionary['status_detail']
    
    if 'message' in dictionary:
        msg = etree.SubElement(status_msg, '{%s}Message' % ns_dict['taxii'])
        msg.text = dictionary['message']
    
    return status_msg

def xml2dictStatusMessage(xml):
    dictionary = __getHeadersXml2dict(xml)
    root = xml.getroot()
    
    return dictionary

#Required dictionary keys:
# message_id - the id of the message
#
#Optional dictionary keys:
# extended_headers - a dictionary of key/value pairs to become extended headers
def dict2xmlDiscoveryRequest(dictionary):
    disc_req = etree.Element('{%s}Discovery_Request' % ns_dict['taxii'])
    __addHeadersDict2xml(disc_req, dictionary)
    return disc_req

#Required dictionary keys:
# message_id - the id of the message
# in_response_to - the id of the message that this message is in response to
#
#Optional dictionary keys:
# extended_headers - a dictionary of key/value pairs to become extended headers
# service_instances - a list of service_instance dictionaries to be contained in the response
#
#Service Instance Dictionary:
#  required keys:
#    service_type - the type of service
#    service_version - a TAXII Services Version ID (from the Services Spec)
#    protocol_binding - the TAXII Protocol Version ID that this service supports
#    address - The address of the service being described
#    message_bindings - a list of TAXII Message Version IDs that this service supports
#
#  optional keys:
#    available - whether or not the service is available to the recipient.
#    content_bindings - Valid only when service_type = 'INBOX'. A list of Content Binding IDs this service supports.
#    message - a human readable message
def dict2xmlDiscoveryResponse(dictionary):
    disc_resp = etree.Element('{%s}Discovery_Request' % ns_dict['taxii'])
    if 'in_response_to' not in dictionary: raise ValueError('in_response_to is a required field')
    __addHeadersDict2xml(disc_resp, dictionary)
    
    if 'service_instances' in dictionary:
        for service_instance in dictionary['service_instances']:
            #TODO: Add checks for required keys
            serv_inst = etree.SubElement(disc_resp, '{%s}Service_Instance' % ns_dict['taxii'])
            
            serv_inst.attrib['service_type'] = service_instance['service_type']
            serv_inst.attrib['service_version'] = service_instance['service_version']
            
            if 'available' in service_instance:
                serv_inst.attrib['available'] = service_instance['available']
            
            proto_bind = etree.SubElement(serv_inst, '{%s}Protocol_Binding' % ns_dict['taxii'])
            proto_bind.text = service_instance['protocol_binding']
            
            addr = etree.SubElement(serv_inst, '{%s}Address' % ns_dict['taxii'])
            addr.text = service_instance['address']
            
            for message_binding in service_instance['message_bindings']:
                msg_bind = etree.SubElement(serv_inst, '{%s}Message_Binding' % ns_dict['taxii'])
                msg_bind.text = message_binding
            
            if 'content_bindings' in service_instance:
                for content_binding in service_instance['content_bindings']:
                    cont_bind = etree.SubElement(serv_inst, '{%s}Content_Binding' % ns_dict['taxii'])
                    cont_bind.text = content_binding
            
    return disc_resp

#Helper function for internal use. Shouldn't be called by external code.
#Adds TAXII headers for dict2xml functions
#Signatures are not supported in this version of libtaxii
def __addHeadersDict2xml(xml, dictionary):
    if 'message_id' not in dictionary: raise ValueError('message_id is a required field')
    xml.attrib['message_id'] = dictionary['message_id']
    
    if 'in_response_to' in dictionary:
        xml.attrib['in_response_to'] = dictionary['in_response_to']
    
    if 'extended_headers' in dictionary:
        extended_headers = dictionary['extended_headers']
        ext_headers_xml = etree.SubElement(xml, '{%s}Extended_Headers' % ns_dict['taxii'])
        for header in extended_headers:
            ext_header = etree.SubElement(ext_headers_xml, '{%s}Extended_Header' % ns_dict['taxii'])
            ext_header.attrib['name'] = header
            ext_header.text = extended_headers[header]

#Helper function for internal use. Shouldn't be called by external code.
#Gets TAXII headers fom the xml for xml2dict functions
#Signatures are not supported in this version of libtaxii
def __getHeadersXml2dict(xml):
    dictionary = {}
    root = xml.getroot()
    dictionary['message_id'] = root.attrib['message_id']
    if 'in_response_to' in root.attrib:
        dictionary['in_response_to'] = root.attrib['in_response_to']
    
    ext_headers = root.xpath('//taxii:Extended_Headers', namespaces=ns_dict)
    if len(ext_headers) > 0:
        extended_headers = {}
        for header in ext_headers[0]:
            key = header.attrib['name']
            value = header.text
            extended_headers[key] = value
        dictionary['extended_headers'] = extended_headers
    
    return dictionary

#############TODO: Refactor below here for TAXII 1.0

#Takes a dictionary and creates an etree that is a valid poll response
#message_id - Optional. If not supplied, one will be generated
#in_response_to - Optional, but you should have one.
#inclusive_begin_timestamp - Optional.
#inclusive_end_timestamp - Required
#subscription_id - Optional
#payload_block - Optional. If present, should be a list similar to the output of x2dPayloadBlock
def dict2xmlPollResponse(dict, privkey=None, pubkey=None):
    poll_resp = etree.Element('{%s}TAXII_Poll_Response' % ns_dict['taxii'])

    if 'message_id' not in dict: poll_resp.attrib['message_id'] = uuid.uuid1().hex
    else: poll_resp.attrib['message_id'] = dict['message_id']

    if 'in_response_to' not in dict: poll_resp.attrib['in_response_to'] = dict['in_response_to']

    if 'inclusive_begin_timestamp' in dict:
        ibt = etree.SubElement(poll_resp, '{%s}Inclusive_Begin_Timestamp' % ns_dict['taxii'])
        ibt.text = dict['inclusive_begin_timestamp']

    if 'inclusive_end_timestamp' not in dict: raise Exception('inclusive_end_timestamp is a required field')
    iet = etree.SubElement(poll_resp, '{%s}Inclusive_End_Timestamp' % ns_dict['taxii'])
    iet.text = dict['inclusive_end_timestamp']

    if 'subscription_id' in dict:
        s_id = etree.SubElement(poll_resp, '{%s}Subscription_ID' % ns_dict['taxii'])
        s_id.text = dict['subscription_id']

    if 'payload_block' in dict:
        for block in dict['payload_block']:
            pb = dict2xmlPayloadBlock(block, poll_resp, privkey=privkey, pubkey=pubkey)

    return poll_resp

#Takes an etree and creates an XML dict
#Etree should be a valid TAXII message. This code does not validate the message
#see dict2xml for dictionary items
#optional values not present in the XML will not exist in the resulting dict
def xml2dictPollResponse(xml):
    dict = {}
    root = xml.getroot()

    dict['message_id'] = root.attrib['message_id']
    if 'in_response_to' in root.attrib: dict['in_response_to'] = root.attrib['in_response_to']

    ibt = root.xpath('//taxii:TAXII_Poll_Response/taxii:Inclusive_Begin_Timestamp', namespaces=ns_dict)
    if len(ibt) > 0: dict['inclusive_begin_timestamp'] = ibt[0].text

    dict['inclusive_last_timestamp'] = root.xpath('//taxii:TAXII_Poll_Response/taxii:Inclusive_End_Timestamp', namespaces=ns_dict)[0].text

    subs_id = root.xpath('//taxii:TAXII_Poll_Response/taxii:Subscription_ID', namespaces=ns_dict)
    if len(subs_id) > 0: dict['subscription_id'] = subs_id[0].text

    payload_blocks = root.xpath('//taxii:TAXII_Poll_Response/taxii:Payload_Block', namespaces=ns_dict)
    if len(payload_blocks) > 0:
        dict['payload_blocks'] = []
        for block in payload_blocks:
            pb = xml2dictPayloadBlock(block)
            dict['payload_blocks'].append(pb)

    return dict

#payload_binding - Required
#payload - Required
#signature - Optional list of signatures
#padding - Optional
#destination_feed_name - Optional list of destination feeds
def dict2xmlPayloadBlock(dict, node, privkey=None, pubkey=None):
    pb = etree.SubElement(node, '{%s}Payload_Block' % ns_dict['taxii'])
    pb_bind = etree.SubElement(pb, '{%s}Payload_Binding' % ns_dict['taxii'])
    pb_bind.text = dict['payload_binding']
    pb_payload = etree.SubElement(pb, '{%s}Payload' % ns_dict['taxii'])
    if pubkey:
        if privkey:
            payload_structure = decrypt_payload(str2xml(dict['payload']), privkey, pubkey)
        else:
            payload_structure = encrypt_payload(str(dict['payload']), pubkey)
        pb_payload.text = payload_structure
    else:
        if dict['payload_binding'] == 'ENCRYPTED_PAYLOAD':
            pb_payload.text = dict['payload']
        else:
            payload_structure = str2xml(dict['payload'])
            pb_payload.append(payload_structure.getroot())
    #TODO: Signatures
    if 'destination_feed_name' in dict:
        for feed in dict['destination_feed_name']:
            f = etree.SubElement(pb, '{%s}Destination_Feed_Name' % ns_dict['taxii'])
            f.text = feed

    return pb

#TODO: Test this
def xml2dictPayloadBlock(xml):
    dict = {}

    binding = xml.xpath('./taxii:Payload_Binding', namespaces=ns_dict)
    if len(binding) != 1:#we have a problem
        raise Exception('Was expecting one binding. Got %s.' % len(binding))

    dict['payload_binding'] = binding[0].text
    if dict['payload_binding'] == 'ENCRYPTED_PAYLOAD':
        dict['payload'] = xml.xpath('./taxii:Payload', namespaces=ns_dict)[0].text
    else:
        #First [0] = first result of the xpath
        #Second [0] = first child of the first result of the xpath.
        payload = xml.xpath('./taxii:Payload', namespaces=ns_dict)[0][0]
        dict['payload'] = etree.tostring(payload)

    #TODO: This is not implemented yet
    #signatures = None

    padding = xml.xpath('./taxii:Padding', namespaces=ns_dict)
    if len(padding) > 0:
        dict['padding'] = padding[0].text

    feed_names = xml.xpath('./taxii:Destination_Feed_Name', namespaces=ns_dict)
    if len(feed_names) > 0:
        dict['destination_feed_name'] = []
        for feed in feed_names:
            dict['destination_feed_name'].append(feed.text)

    return dict

def dict2xmlPollRequest(dict):
    raise Exception('This function is not implemented - Use an HTTP GET!')

def xml2dictPollRequest(xml):
    raise Exception('This function is not implemented - Use an HTTP GET!')

#Takes a dictionary and creates an etree that is a valid Error message
#error_type - Required.
#message_id - Optional. If not supplied, one will be generated
#message - Optional, but you should have one.
#error_detail - Optional.
def dict2xmlErrorMessage(dict):
    error = etree.Element('{%s}TAXII_Error_Message' % ns_dict['taxii'])

    error.attrib['error_type'] = dict['error_type']

    if 'message_id' not in dict: error.attrib['message_id'] = uuid.uuid1().hex
    else: error.attrib['message_id'] = dict['message_id']

    if 'in_response_to' in dict: error.attrib['in_response_to'] = dict['in_response_to']

    if 'error_detail' in dict:
        ed = etree.SubElement(error, '{%s}Error_Detail' % ns_dict['taxii'])
        ed.text = dict['Error_Detail']

    if 'message' in dict:
        msg = etree.SubElement(error, '{%s}Message' % ns_dict['taxii'])
        msg.text = dict['message']

    return error

def xml2dictErrorMessage(xml):
    dict = {}
    root = xml.getroot()

    dict['message_id'] = root.attrib['message_id']
    if 'in_response_to' in root.attrib: dict['in_response_to'] = root.attrib['in_response_to']
    dict['error_type'] = root.attrib['error_type']

    error_detail = root.xpath('//taxii:TAXII_Error_Message/taxii:Error_Detail', namespaces=ns_dict)
    if len(error_detail) > 0: dict['error_detail'] = error_detail[0].text

    message = root.xpath('//taxii:TAXII_Error_Message/taxii:Message', namespaces=ns_dict)
    if len(message) > 0: dict['message'] = message[0].text

    return dict

#message_id - Optional. One will will be auto-genned if this is not provided.
#subscription_id - Optional.
#payload_block - Optional.
def dict2xmlInboxMessage(dict, pubkey=None):
    inbox = etree.Element('{%s}TAXII_Inbox_Message' % ns_dict['taxii'])

    if 'message_id' not in dict: inbox.attrib['message_id'] = uuid.uuid1().hex
    else: inbox.attrib['message_id'] = dict['message_id']

    if 'subscription_id' in dict:
        s_id = etree.SubElement(inbox, '{%s}Subscription_ID' % ns_dict['taxii'])
        s_id.text = dict['subscription_id']

    if 'payload_block' in dict:
        for block in dict['payload_block']:
            pb = dict2xmlPayloadBlock(block, inbox, pubkey=pubkey)
            #etree.SubElement(inbox, pb)

    return inbox

def xml2dictInboxMessage(xml):
    dict = {}
    root = xml.getroot()

    dict['message_id'] = root.attrib['message_id']
    if 'in_response_to' in root.attrib: dict['in_response_to'] = root.attrib['in_response_to']

    s_id = root.xpath('//taxii:TAXII_Inbox_Message/taxii:Subscription_ID', namespaces=ns_dict)
    if len(s_id) > 0: dict['subscription_id'] = s_id[0].text

    payload_blocks = root.xpath('//taxii:TAXII_Inbox_Message/taxii:Payload_Block', namespaces=ns_dict)
    if len(payload_blocks) > 0:
        dict['payload_blocks'] = []
        for block in payload_blocks:
            pb = xml2dictPayloadBlock(block)
            dict['payload_blocks'].append(pb)

    return dict

#Takes any string and turns it into an etree
def str2xml(s):
    stio = StringIO.StringIO(s)
    return file2xml(stio)

def file2xml(file_name):
    local_parser = etree.XMLParser(no_network=True)
    xml = etree.parse(file_name, parser=local_parser)
    return xml

def xml2str(xml):
    return etree.tostring(xml)

#validate any etree against the TAXII xml schema
#WARNING: This WILL NOT WORK with version of libxml2 less than 2.9.0
def validateXml(xml):
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "../xsd", "TAXII_XMLMessageBinding_Schema.xsd")
    taxii_schema_doc = etree.parse(schema_file)
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(xml)
    if not valid:
        raise Exception(xml_schema.error_log.last_error)
    return True
