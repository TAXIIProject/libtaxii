#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import uuid
import StringIO
import os
from lxml import etree
from M2Crypto import BIO, Rand, SMIME, X509

ns_dict = {'taxii': 'http://taxii.mitre.org/messages/xml/1'}

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
    buf = s.decrypt(p7)
    return buf

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
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XML_10.xsd")
    taxii_schema_doc = etree.parse(schema_file)
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(xml)
    if not valid:
        raise Exception(xml_schema.error_log.last_error)
    return True
