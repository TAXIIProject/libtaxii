#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

#This file has two purposes:
# 1. To provide a rough unit test of libtaxii.messages
# 2. To provide examples of how to use libtaxii.messages
#
# Generally speaking, the tests are performed as follows:
# 
# 1. Create a kwargs dictionary. http://stackoverflow.com/questions/1769403/understanding-kwargs-in-python
#    The kwargs dictionary shows users which arguments the constructor takes
# 2. Create the TAXII Message (or related object) from kwargs
# (The following are done in perform_tests)
# 3. Convert the TAXII Message to xml
# 4. Validate the XML w/ the TAXII XML Schema
# 5. Convert the XML to a TAXII Message
# 6. Convert the TAXII Message to a python dictionary
# 7. Convert the dictionary to a TAXII Message
# 8. Compare all three messages for equality
#

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import libtaxii as t
import libtaxii.messages as tm
import datetime
from lxml import etree
import StringIO

def perform_tests(taxii_message):
    if not isinstance(taxii_message, tm.TAXIIMessage):
        raise ValueError('taxii_message was not an instance of TAXIIMessage')
    
    print '***** Message type = %s; id = %s' % (taxii_message.message_type, taxii_message.message_id)
    
    xml_string = taxii_message.to_xml()
    valid = tm.validate_xml(xml_string)
    if not valid:
        raise Exception('\tFailure of test #1 - XML not schema valid')
    msg_from_xml = tm.get_message_from_xml(xml_string)
    dictionary = taxii_message.to_dict()
    msg_from_dict = tm.get_message_from_dict(dictionary)
    if taxii_message != msg_from_xml:
        print '\t Failure of test #2 - running equals w/ debug:'
        taxii_message.__eq__(msg_from_xml, True)
        raise Exception('Test #2 failed - taxii_message != msg_from_xml')
    
    if taxii_message != msg_from_dict:
        print '\t Failure of test #3 - running equals w/ debug:'
        taxii_message.__eq__(msg_from_dict, True)
        raise Exception('Test #3 failed - taxii_message != msg_from_dict')
    
    if msg_from_xml != msg_from_dict:
        print '\t Failure of test #4 - running equals w/ debug:'
        msg_from_xml.__eq__(msg_from_dict, True)
        raise Exception('Test #4 failed - msg_from_xml != msg_from_dict')
    
    print '***** All tests completed!'

## Discovery Request
discovery_request_kwargs = {}
discovery_request_kwargs['message_id'] = tm.generate_message_id() #Required
discovery_request_kwargs['extended_headers'] = {'ext_header1': 'value1', 'ext_header2': 'value2'} #Optional

#TODO: Do it like the line below this.
#TODO: Say which args are optional
#tm.DiscoveryRequest(message_id=tm.generate_message_id(), ... )
discovery_request1 = tm.DiscoveryRequest(**discovery_request_kwargs)

perform_tests(discovery_request1)

## Discovery Response
service_kwargs = {}
service_kwargs['service_type'] = tm.SVC_INBOX
service_kwargs['service_version'] = t.VID_TAXII_SERVICES_10
service_kwargs['protocol_binding'] = t.VID_TAXII_HTTP_10
service_kwargs['address'] = 'http://example.com/inboxservice/'
service_kwargs['message_bindings'] = [t.VID_TAXII_XML_10, 'temporaryvalue']
service_kwargs['available'] = 'true'
service_kwargs['content_bindings'] = []
service_kwargs['message'] = 'This is a message.'
service_instance1 = tm.DiscoveryResponse.ServiceInstance(**service_kwargs)

discovery_response_kwargs = {}
discovery_response_kwargs['message_id'] = tm.generate_message_id()#Required
discovery_response_kwargs['in_response_to'] = tm.generate_message_id()#Required
discovery_response_kwargs['service_instances'] = [service_instance1]#Optional
discovery_response1 = tm.DiscoveryResponse(**discovery_response_kwargs)

perform_tests(discovery_response1)

##Feed Information Request
feed_information_request_kwargs = {}
feed_information_request_kwargs['message_id'] = tm.generate_message_id()
feed_information_request1 = tm.FeedInformationRequest(**feed_information_request_kwargs)

perform_tests(feed_information_request1)

## Feed Information Response

push_method_kwargs = {}
push_method_kwargs['protocol_binding'] = t.VID_TAXII_HTTP_10
push_method_kwargs['message_bindings'] = [t.VID_TAXII_XML_10]
push_method1 = tm.FeedInformationResponse.Feed.PushMethod(**push_method_kwargs)

polling_service_kwargs = {}
polling_service_kwargs['protocol_binding'] = t.VID_TAXII_HTTP_10
polling_service_kwargs['address'] = 'http://example.com/PollService/'
polling_service_kwargs['message_bindings'] = [t.VID_TAXII_XML_10]
polling_service1 = tm.FeedInformationResponse.Feed.PollingService(**polling_service_kwargs)

subscription_service_kwargs = {}
subscription_service_kwargs['protocol_binding'] = t.VID_TAXII_HTTP_10
subscription_service_kwargs['address'] = 'http://example.com/SubsService/'
subscription_service_kwargs['message_bindings'] = [t.VID_TAXII_XML_10]
subscription_service1 = tm.FeedInformationResponse.Feed.SubscriptionService(**subscription_service_kwargs)

feed_kwargs = {}
feed_kwargs['feed_name'] = 'Feed1'
feed_kwargs['description'] = 'Description of a feed'
feed_kwargs['available'] = 'true'
feed_kwargs['content_bindings'] = [t.CB_STIX_XML_10]
feed_kwargs['push_methods'] = [push_method1]
feed_kwargs['polling_services'] = [polling_service1]
feed_kwargs['subscription_services'] = [subscription_service1]
feed1 = tm.FeedInformationResponse.Feed(**feed_kwargs)

feed_information_response_kwargs = {}
feed_information_response_kwargs['message_id'] = tm.generate_message_id()
feed_information_response_kwargs['in_response_to'] = tm.generate_message_id()
feed_information_response_kwargs['extended_headers'] = {}
feed_information_response_kwargs['feeds'] = [feed1]
feed_information_response1 = tm.FeedInformationResponse(**feed_information_response_kwargs)

perform_tests(feed_information_response1)

## Poll Request
poll_request_kwargs = {}
poll_request_kwargs['message_id'] = tm.generate_message_id()
poll_request_kwargs['feed_name'] = 'TheFeedToPoll'
poll_request_kwargs['subscription_id'] = 'SomeID'
poll_request_kwargs['exclusive_begin_timestamp'] = datetime.datetime.now()
poll_request_kwargs['inclusive_end_timestamp'] = datetime.datetime.now()
poll_request_kwargs['content_bindings'] = []

poll_request1 = tm.PollRequest(**poll_request_kwargs)

perform_tests(poll_request1)

## Poll Response

xml_content_block_kwargs = {}
xml_content_block_kwargs['content_binding'] = t.CB_STIX_XML_10
xml_content_block_kwargs['content'] = etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')).getroot()
xml_content_block_kwargs['padding'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
xml_content_block_kwargs['timestamp_label'] = datetime.datetime.now()
xml_content_block1 = tm.ContentBlock(**xml_content_block_kwargs)

string_content_block_kwargs = {}
string_content_block_kwargs['content_binding'] = 'string'
string_content_block_kwargs['content'] = 'Sample content'
string_content_block_kwargs['padding'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
string_content_block_kwargs['timestamp_label'] = datetime.datetime.now()
string_content_block1 = tm.ContentBlock(**string_content_block_kwargs)

poll_response_kwargs = {}
poll_response_kwargs['message_id'] = tm.generate_message_id()
poll_response_kwargs['in_response_to'] = tm.generate_message_id()
poll_response_kwargs['feed_name'] = 'FeedName'
poll_response_kwargs['inclusive_end_timestamp'] = datetime.datetime.now()
poll_response_kwargs['subscription_id'] = 'SubsId001'
poll_response_kwargs['message'] = 'This is a message'
poll_response_kwargs['inclusive_begin_timestamp'] = datetime.datetime.now()
poll_response_kwargs['content_blocks'] = [xml_content_block1, string_content_block1]

poll_response1 = tm.PollResponse(**poll_response_kwargs)

perform_tests(poll_response1)

## Status Message
status_message_kwargs = {}
status_message_kwargs['message_id'] = tm.generate_message_id()
status_message_kwargs['in_response_to'] = tm.generate_message_id()
status_message_kwargs['status_type'] = tm.ST_SUCCESS
status_message_kwargs['status_detail'] = 'Real info should go here!'
status_message_kwargs['message'] = 'This is a message.'

status_message1 = tm.StatusMessage(**status_message_kwargs)

perform_tests(status_message1)

## Inbox Message
subscription_information_kwargs = {}
subscription_information_kwargs['feed_name'] = 'SomeFeedName'
subscription_information_kwargs['subscription_id'] = 'SubsId001'
subscription_information_kwargs['inclusive_begin_timestamp_label'] = datetime.datetime.now()
subscription_information_kwargs['inclusive_end_timestamp_label'] = datetime.datetime.now()

subscription_information1 = tm.InboxMessage.SubscriptionInformation(**subscription_information_kwargs)

inbox_message_kwargs = {}
inbox_message_kwargs['message_id'] = tm.generate_message_id()
inbox_message_kwargs['content_blocks'] = [xml_content_block1, string_content_block1]
inbox_message_kwargs['message'] = 'This is a message'
inbox_message_kwargs['subscription_information'] = subscription_information1

inbox_message1 = tm.InboxMessage(**inbox_message_kwargs)

perform_tests(inbox_message1)

## Manage Feed Subscription Request 

delivery_parameters_kwargs = {}
delivery_parameters_kwargs['inbox_protocol'] = t.VID_TAXII_HTTP_10
delivery_parameters_kwargs['inbox_address'] = 'http://example.com/inbox'
delivery_parameters_kwargs['delivery_message_binding'] = t.VID_TAXII_XML_10
delivery_parameters_kwargs['content_bindings'] = [t.CB_STIX_XML_10]

delivery_parameters1 = tm.DeliveryParameters(**delivery_parameters_kwargs)

manage_feed_subscription_request_kwargs = {}
manage_feed_subscription_request_kwargs['message_id'] = tm.generate_message_id()
manage_feed_subscription_request_kwargs['feed_name'] = 'SomeFeedName'
manage_feed_subscription_request_kwargs['action'] = tm.ACT_SUBSCRIBE
manage_feed_subscription_request_kwargs['subscription_id'] = 'SubsId002'
manage_feed_subscription_request_kwargs['delivery_parameters'] = delivery_parameters1

manage_feed_subscription_request1 = tm.ManageFeedSubscriptionRequest(**manage_feed_subscription_request_kwargs)

perform_tests(manage_feed_subscription_request1)

## Manage Feed Subscription Response

poll_instance_kwargs = {}
poll_instance_kwargs['protocol_binding'] = t.VID_TAXII_HTTP_10
poll_instance_kwargs['poll_address'] = 'http://example.com/poll'
poll_instance_kwargs['poll_message_bindings'] = [t.VID_TAXII_XML_10]

poll_instance1 = tm.ManageFeedSubscriptionResponse.PollInstance(**poll_instance_kwargs)

subscription_instance_kwargs = {}
subscription_instance_kwargs['subscription_id'] = 'SubsId005'
subscription_instance_kwargs['delivery_parameters'] = [delivery_parameters1]
subscription_instance_kwargs['poll_instances'] = [poll_instance1]

subscription_instance1 = tm.ManageFeedSubscriptionResponse.SubscriptionInstance(**subscription_instance_kwargs)

manage_feed_subscription_response_kwargs = {}
manage_feed_subscription_response_kwargs['message_id'] = tm.generate_message_id()
manage_feed_subscription_response_kwargs['in_response_to'] = tm.generate_message_id()
manage_feed_subscription_response_kwargs['feed_name'] = 'Feed001'
manage_feed_subscription_response_kwargs['message'] = 'This is a message.'
manage_feed_subscription_response_kwargs['subscription_instances'] = [subscription_instance1]

manage_feed_subscription_response1 = tm.ManageFeedSubscriptionResponse(**manage_feed_subscription_response_kwargs)

perform_tests(manage_feed_subscription_response1)














