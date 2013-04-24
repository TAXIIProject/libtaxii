import uuid
import StringIO
import os
from lxml import etree
import warnings

ns_dict = {'taxii': 'http://taxii.mitre.org/messages/xml/1',
		   'ds'	  : 'http://www.w3.org/2000/09/xmldsig#'}

#Define dictionary constants
MESSAGE_TYPE = 'message_type'
MESSAGE_ID = 'message_id'
IN_RESPONSE_TO = 'in_response_to'
EXTENDED_HEADERS = 'extended_headers'
#TODO: Signatures

INCLUSIVE_BEGIN_TIMESTAMP = 'inclusive_begin_timestamp'
INCLUSIVE_END_TIMESTAMP = 'inclusive_end_timestamp'

PAYLOAD_BLOCKS = 'payload_blocks'
PAYLOAD_BINDING = 'payload_binding'
PAYLOAD = 'payload'

SUBSCRIPTION_ID = 'subscription_id'

#Message Types
MSG_DISCOVERY_REQUEST = 'discovery_request'
MSG_DISCOVERY_RESPONSE = 'discovery_response'
MSG_FEED_INFORMATION_REQUEST = 'feed_information_request'
MSG_FEED_INFORMATION_RESPONSE = 'feed_information_response'
MSG_INBOX = 'inbox'
MSG_POLL_RESPONSE = 'poll_response'
MSG_POLL_REQUEST = 'poll_request'
MSG_STATUS = 'status'
MSG_SUBSCRIPTION_MANAGEMENT_REQUEST = 'subscription_management_request'
MSG_SUBSCRIPTION_MANAGEMENT_RESPONSE = 'subscription_management_response'

#Deprecated message type
MSG_ERROR = 'error'

def __checkRequiredFields(required_fields, dictionary, msg_type):
	for field in required_fields:
		if field not in dictionary:
			raise Exception('%s is a required dictionary item for %.' % (field, msg_type))

def __assertMsgType(msg_type, dictionary):
	if dictionary[MESSAGE_TYPE] != msg_type:
		raise Exception ('%s must be %s' % (MESSAGE_TYPE, msg_type))

#Takes in an arbitrary block of XML and attempts to parse it into a 
#TAXII message dictionary. Returns a dictionary or raises an exception. The message type can be 
#discovered by inspecting the MESSAGE_TYPE dictionary item in the returned dictionary
def xml2dictTaxiiMessage(xml):
	validateXml(xml)
	root_tag = xml.getroot().tag
	if   root_tag == '{%s}TAXII_Discovery_Request' % ns_dict['taxii']: return xml2dictDiscoveryRequest(xml)
	elif root_tag == '{%s}TAXII_Discovery_Response' % ns_dict['taxii']: return xml2dictDiscoveryResponse(xml)
	elif root_tag == '{%s}TAXII_Feed_Information_Request' % ns_dict['taxii']: return xml2dictFeedInformationRequest(xml)
	elif root_tag == '{%s}TAXII_Feed_Information_Response' % ns_dict['taxii']: return xml2dictFeedInformationResponse(xml)
	elif root_tag == '{%s}TAXII_Inbox_Message' % ns_dict['taxii']: return xml2dictInboxMessage(xml)
	elif root_tag == '{%s}TAXII_Poll_Response' % ns_dict['taxii']: return xml2dictPollResponse(xml)
	elif root_tag == '{%s}TAXII_Poll_Request' % ns_dict['taxii']: return xml2dictPollRequest(xml)
	elif root_tag == '{%s}TAXII_Status_Message' % ns_dict['taxii']: return xml2dictStatusMessage(xml)
	elif root_tag == '{%s}TAXII_Subscription_Management_Request' % ns_dict['taxii']: return xml2dictSubscriptionManagementRequest(xml)
	elif root_tag == '{%s}TAXII_Subscription_Management_Response' % ns_dict['taxii']: return xml2dictSubscriptionManagementResponse(xml)
	else: raise Exception('Unknown tag % ' % root_tag)

#Takes in a dictionary and auto-detects the message type from the MESSAGE_TYPE dictionary entry.
#returns XML or raises an exception
def dict2xmlTaxiiMessage(dictionary):
	msg_type = dictionary[MESSAGE_TYPE]
	if   msg_type == MSG_DISCOVERY_REQUEST: return dict2xmlDiscoveryRequest(dictionary)
	elif msg_type == MSG_DISCOVERY_RESPONSE : return dict2xmlDiscoveryResponse(dictionary)
	elif msg_type == MSG_FEED_INFORMATION_REQUEST : return dict2xmlFeedInformationRequest(dictionary)
	elif msg_type == MSG_FEED_INFORMATION_RESPONSE : return dict2xmlFeedInformationResponse(dictionary)
	elif msg_type == MSG_INBOX : return dict2xmlInboxMessage(dictionary)
	elif msg_type == MSG_POLL_RESPONSE : return dict2xmlPollResponse(dictionary)
	elif msg_type == MSG_POLL_REQUEST : return dict2xmlPollRequest(dictionary)
	elif msg_type == MSG_STATUS : return dict2xmlStatusMessage(dictionary)
	elif msg_type == MSG_SUBSCRIPTION_MANAGEMENT_REQUEST : return dict2xmlSubscriptionManagementRequest(dictionary)
	elif msg_type == MSG_SUBSCRIPTION_MANAGEMENT_RESPONSE : return dict2xmlSubscriptionManagementResponse(dictionary)
	else: raise Exception('Unknown message_type: %s' % msg_type) 

def dict2xmlDiscoveryRequest(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlDiscoveryResponse(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlFeedInformationRequest(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlFeedInformationResponse(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlStatusMessage(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlSubscriptionManagementResponse(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlSubscriptionManagementRequest(dictionary):
	raise Exception('Function not implemented yet')

def dict2xmlPollRequest(dictionary):
	#warnings.warn('While an XML structure for this exists, this message type is cuse an HTTP Get!')
	raise Exception('Function not implemented yet')

#Takes a dictionary and creates an etree that is a valid poll response
#message_id - Optional. If not supplied, one will be generated
#in_response_to - Optional, but you should have one.
#inclusive_begin_timestamp - Optional.
#inclusive_end_timestamp - Required
#subscription_id - Optional
#payload_block - Optional. If present, should be a list similar to the output of x2dPayloadBlock
def dict2xmlPollResponse(dictionary):
	__checkRequiredFields([MESSAGE_TYPE, IN_RESPONSE_TO, INCLUSIVE_END_TIMESTAMP], dict, MSG_POLL_RESPONSE)
	__assertMsgType(MSG_POLL_RESPONSE, dictionary)
		
	poll_resp = etree.Element('{%s}TAXII_Poll_Response' % ns_dict['taxii'])
	
	if MESSAGE_ID not in dict: poll_resp.attrib[MESSAGE_ID] = uuid.uuid1().hex
	else: poll_resp.attrib[MESSAGE_ID] = dict[MESSAGE_ID]
	
	poll_resp.attrib[IN_RESPONSE_TO] = dict[IN_RESPONSE_TO]
	
	if INCLUSIVE_BEGIN_TIMESTAMP in dict:
		ibt = etree.SubElement(poll_resp, '{%s}Inclusive_Begin_Timestamp' % ns_dict['taxii'])
		ibt.text = dict[INCLUSIVE_BEGIN_TIMESTAMP]
	
	iet = etree.SubElement(poll_resp, '{%s}Inclusive_End_Timestamp' % ns_dict['taxii'])
	iet.text = dict[INCLUSIVE_END_TIMESTAMP]
	
	if SUBSCRIPTION_ID in dict:
		s_id = etree.SubElement(poll_resp, '{%s}Subscription_ID' % ns_dict['taxii'])
		s_id.text = dict[SUBSCRIPTION_ID]
	
	if PAYLOAD_BLOCKS in dict:
		for block in dict[PAYLOAD_BLOCKS]:
			pb = __dict2xmlPayloadBlock(block, poll_resp)
	
	return poll_resp

#Takes a dictionary and creates an etree that is a valid Error message
#error_type - Required.
#message_id - Optional. If not supplied, one will be generated
#message - Optional, but you should have one.
#error_detail - Optional.
def dict2xmlErrorMessage(dictionary):
	warnings.warn('Use of deprecated function: dict2xmlErrorMessage. Use dict2xmlStatusMessage instead!')
	error = etree.Element('{%s}TAXII_Error_Message' % ns_dict['taxii'])
	
	error.attrib['error_type'] = dict['error_type']
	
	if MESSAGE_ID not in dict: error.attrib[MESSAGE_ID] = uuid.uuid1().hex
	else: error.attrib[MESSAGE_ID] = dict[MESSAGE_ID]
	
	if IN_RESPONSE_TO in dict: error.attrib[IN_RESPONSE_TO] = dict[IN_RESPONSE_TO]
	
	if 'error_detail' in dict:
		ed = etree.SubElement(error, '{%s}Error_Detail' % ns_dict['taxii'])
		ed.text = dict['Error_Detail']
	
	if 'message' in dict:
		msg = etree.SubElement(error, '{%s}Message' % ns_dict['taxii'])
		msg.text = dict['message']
	
	return error

def xml2dictDiscoveryRequest(xml):
	raise Exception('Function not implemented yet')

def xml2dictDiscoveryResponse(xml):
	raise Exception('Function not implemented yet')

def xml2dictFeedInformationRequest(xml):
	raise Exception('Function not implemented yet')

def xml2dictFeedInformationResponse(xml):
	raise Exception('Function not implemented yet')

#message_id - Optional. One will will be auto-genned if this is not provided.
#subscription_id - Optional.
#payload_block - Optional.
def dict2xmlInboxMessage(dictionary):
	__checkRequiredFields([MESSAGE_TYPE], dictionary, MSG_INBOX)
	__assertMsgType(MSG_INBOX, dictionary)
	
	inbox = etree.Element('{%s}TAXII_Inbox_Message' % ns_dict['taxii'])
	
	if MESSAGE_ID not in dictionary: inbox.attrib[MESSAGE_ID] = uuid.uuid1().hex
	else: inbox.attrib[MESSAGE_ID] = dictionary[MESSAGE_ID]
	
	if SUBSCRIPTION_ID in dictionary:
		s_id = etree.SubElement(inbox, '{%s}Subscription_ID' % ns_dict['taxii'])
		s_id.text = dictionary[SUBSCRIPTION_ID]
	
	if PAYLOAD_BLOCKS in dictionary:
		for block in dictionary[PAYLOAD_BLOCKS]:
			pb = __dict2xmlPayloadBlock(block, inbox)
	
	return inbox

#payload_binding - Required
#payload - Required
#signature - Optional list of signatures
#padding - Optional
#destination_feed_name - Optional list of destination feeds
def __dict2xmlPayloadBlock(dictionary, node):
	pb = etree.SubElement(node, '{%s}Payload_Block' % ns_dict['taxii'])
	pb_bind = etree.SubElement(pb, '{%s}Payload_Binding' % ns_dict['taxii'])
	pb_bind.text = dictionary[PAYLOAD_BINDING]
	pb_payload = etree.SubElement(pb, '{%s}Payload' % ns_dict['taxii'])
	payload_structure = str2xml(dictionary[PAYLOAD])
	pb_payload.append(payload_structure.getroot())
	#TODO: Signatures
	#TODO: This field is going away.
	if 'destination_feed_name' in dict:
		for feed in dict['destination_feed_name']:
			f = etree.SubElement(pb, '{%s}Destination_Feed_Name' % ns_dict['taxii'])
			f.text = feed
	
	return pb

def xml2dictStatusMessage(xml):
	raise Exception('Function not implemented yet')

def xml2dictSubscriptionManagementRequest(xml):
	raise Exception('Function not implemented yet')

def xml2dictSubscriptionManagementResponse(xml):
	raise Exception('Function not implemented yet')

#Takes an etree and creates an XML dict
#Etree should be a valid TAXII message. This code does not validate the message
#see dict2xml for dictionary items
#optional values not present in the XML will not exist in the resulting dict
def xml2dictPollResponse(xml):
	dictionary = {MESSAGE_TYPE: MSG_POLL_RESPONSE}
	root = xml.getroot()
	
	dictionary[MESSAGE_ID] = root.attrib[MESSAGE_ID]
	if IN_RESPONSE_TO in root.attrib: dictionary[IN_RESPONSE_TO] = root.attrib[IN_RESPONSE_TO]
	
	ibt = root.xpath('//taxii:TAXII_Poll_Response/taxii:Inclusive_Begin_Timestamp', namespaces=ns_dict)
	if len(ibt) > 0: dictionary[INCLUSIVE_BEGIN_TIMESTAMP] = ibt[0].text
	
	dictionary[INCLUSIVE_END_TIMESTAMP] = root.xpath('//taxii:TAXII_Poll_Response/taxii:Inclusive_End_Timestamp', namespaces=ns_dict)[0].text
	
	subs_id = root.xpath('//taxii:TAXII_Poll_Response/taxii:Subscription_ID', namespaces=ns_dict)
	if len(subs_id) > 0: dictionary[SUBSCRIPTION_ID] = subs_id[0].text
	
	blocks = root.xpath('//taxii:TAXII_Poll_Response/taxii:Payload_Block', namespaces=ns_dict)
	if len(blocks) > 0:
		dictionary[PAYLOAD_BLOCKS] = []
		for block in blocks:
			pb = __xml2dictPayloadBlock(block)
			dictionary[PAYLOAD_BLOCKS].append(pb)
	
	return dict

#TODO: Test this
def __xml2dictPayloadBlock(xml):
	dictionary = {}
	
	binding = xml.xpath('./taxii:Payload_Binding', namespaces=ns_dict)
	if len(binding) != 1:#we have a problem
		raise Exception('Was expecting one binding. Got %s.' % len(binding))
	
	dictionary['payload_binding'] = binding[0].text
	#First [0] = first result of the xpath
	#Second [0] = first child of the first result of the xpath.
	payload = xml.xpath('./taxii:Payload', namespaces=ns_dict)[0][0]
	dictionary['payload'] = etree.tostring(payload)
	
	signatures = None#TODO: This is not implemented yet
	
	padding = xml.xpath('./taxii:Padding', namespaces=ns_dict)
	if len(padding) > 0:
		dict['padding'] = padding[0].text
	
	feed_names = xml.xpath('./taxii:Destination_Feed_Name', namespaces=ns_dict)
	if len(feed_names) > 0:
		dictionary['destination_feed_name'] = []
		for feed in feed_names:
			dictionary['destination_feed_name'].append(feed.text)
	
	return dict

def xml2dictPollRequest(xml):
	raise Exception('This function is not implemented - Use an HTTP GET!')

def xml2dictErrorMessage(xml):
	dictionary = {MESSAGE_TYPE: MSG_ERROR}
	root = xml.getroot()
	
	dictionary[MESSAGE_ID] = root.attrib[MESSAGE_ID]
	if IN_RESPONSE_TO in root.attrib: dict[IN_RESPONSE_TO] = root.attrib[IN_RESPONSE_TO]
	dictionary['error_type'] = root.attrib['error_type']
	
	error_detail = root.xpath('//taxii:TAXII_Error_Message/taxii:Error_Detail', namespaces=ns_dict)
	if len(error_detail) > 0: dictionary['error_detail'] = error_detail[0].text
	
	message = root.xpath('//taxii:TAXII_Error_Message/taxii:Message', namespaces=ns_dict)
	if len(message) > 0: dictionary['message'] = message[0].text
	
	return dict

def xml2dictInboxMessage(xml):
	dictionary = {MESSAGE_TYPE: MSG_INBOX}
	root = xml.getroot()
	
	dictionary[MESSAGE_ID] = root.attrib[MESSAGE_ID]
	if IN_RESPONSE_TO in root.attrib: dict[IN_RESPONSE_TO] = root.attrib[IN_RESPONSE_TO]
	
	s_id = root.xpath('//taxii:TAXII_Inbox_Message/taxii:Subscription_ID', namespaces=ns_dict)
	if len(s_id) > 0: dictionary[SUBSCRIPTION_ID] = s_id[0].text
	
	blocks = root.xpath('//taxii:TAXII_Inbox_Message/taxii:Payload_Block', namespaces=ns_dict)
	if len(blocks) > 0:
		dictionary[PAYLOAD_BLOCKS] = []
		for block in blocks:
			pb = __xml2dictPayloadBlock(block)
			dictionary[PAYLOAD_BLOCKS].append(pb)
	
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
def validateXml(xml):
	package_dir, package_filename = os.path.split(__file__)
	schema_file = os.path.join(package_dir, "xsd", "TAXII_XML_10.xsd")
	taxii_schema_doc = etree.parse(schema_file)
	xml_schema = etree.XMLSchema(taxii_schema_doc)
	valid = xml_schema.validate(xml)
	if not valid:
		raise Exception(xml_schema.error_log.last_error)
	return True










