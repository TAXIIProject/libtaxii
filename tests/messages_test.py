#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

#This file has two purposes:
# 1. To provide a rough unit test of libtaxii.messages
# 2. To provide examples of how to use libtaxii.messages



### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import libtaxii as t
import libtaxii.messages as tm
import datetime
from lxml import etree
from dateutil.tz import tzutc
import StringIO

def message_tests(taxii_message):
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

def contentblock_tests(content_block):
    if not isinstance(content_block, tm.ContentBlock):
        raise ValueError('content_block was not an instance of ContentBlock')
    
    print '***** Starting Content Block tests'
    
    xml_string = content_block.to_xml()
    block_from_xml = tm.ContentBlock.from_xml(xml_string)
    dictionary = content_block.to_dict()
    block_from_dict = tm.ContentBlock.from_dict(dictionary)
    
    if content_block != block_from_xml:
        print '\t Failure of test #1 - running equals w/ debug:'
        content_block.__equals(block_from_xml, True)
        raise Exception('Test #1 failed - content_block != block_from_xml')
    
    if content_block != block_from_dict:
        print '\t Failure of test #2 - running equals w/ debug:'
        content_block.__eq__(block_from_dict, True)
        raise Exception('Test #2 failed - content_block != block_from_dict')
    
    if block_from_xml != block_from_dict:
        print '\t Failure of test #3 - running equals w/ debug:'
        block_from_xml.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_xml != block_from_dict')
    
    print '***** All tests completed!'

## Discovery Request
discovery_request1 = tm.DiscoveryRequest(message_id = tm.generate_message_id(), #Required
                                         extended_headers={'ext_header1': 'value1', 'ext_header2': 'value2'})#Optional. 
                                         #Extended headers are optional for every message type, but only demonstrated here

message_tests(discovery_request1)

## Discovery Response

#Create a service instance
service_instance1 = tm.DiscoveryResponse.ServiceInstance(service_type = tm.SVC_INBOX,#Required
                                                         services_version = t.VID_TAXII_SERVICES_10,#Required
                                                         protocol_binding = t.VID_TAXII_HTTP_10,#Required
                                                         service_address = 'http://example.com/inboxservice/',#Required
                                                         message_bindings = [t.VID_TAXII_XML_10],#Required, must have at least one value in the list
                                                         inbox_service_accepted_content = [t.CB_STIX_XML_10],#Optional for service_type=SVC_INBOX, prohibited otherwise
                                                                                             #If this is absent and service_type=SVC_INBOX,
                                                                                             #It means the inbox service accepts all content
                                                         available = True,#Optional - defaults to None, which means 'Unknown'
                                                         message = 'This is a message.')#Optional

#Create the discovery response
discovery_response1 = tm.DiscoveryResponse(message_id = tm.generate_message_id(),#Required
                                           in_response_to = tm.generate_message_id(),#Required. This should be the ID of the corresponding request
                                           service_instances = [service_instance1])#Optional.

message_tests(discovery_response1)

##Feed Information Request
feed_information_request1 = tm.FeedInformationRequest(message_id = tm.generate_message_id())#Required

message_tests(feed_information_request1)

## Feed Information Response

push_method1 = tm.FeedInformationResponse.FeedInformation.PushMethod(push_protocol = t.VID_TAXII_HTTP_10, #Required
                                                                     push_message_bindings = [t.VID_TAXII_XML_10])#Required

polling_service1 = tm.FeedInformationResponse.FeedInformation.PollingServiceInstance(poll_protocol = t.VID_TAXII_HTTP_10,#Required
                                                                                     poll_address = 'http://example.com/PollService/',#Required
                                                                                     poll_message_bindings = [t.VID_TAXII_XML_10])#Required

subscription_service1 = tm.FeedInformationResponse.FeedInformation.SubscriptionMethod(subscription_protocol = t.VID_TAXII_HTTP_10,#Required
                                                                                      subscription_address = 'http://example.com/SubsService/',#Required
                                                                                      subscription_message_bindings = [t.VID_TAXII_XML_10])#Required

feed1 = tm.FeedInformationResponse.FeedInformation(feed_name = 'Feed1',#Required
                                                   feed_description = 'Description of a feed',#Required
                                                   supported_contents = [t.CB_STIX_XML_10],#Required. List of supported content binding IDs
                                                   available = True,#Optional. Defaults to None (aka Unknown)
                                                   push_methods = [push_method1],#Required if there are no polling_services. Optional otherwise
                                                   polling_service_instances = [polling_service1],#Required if there are no push_methods. Optional otherwise.
                                                   subscription_methods = [subscription_service1])#Optional

feed_information_response1 = tm.FeedInformationResponse(message_id = tm.generate_message_id(),#Required
                                                        in_response_to = tm.generate_message_id(),#Required. This should be the ID of the corresponding request
                                                        feed_informations=[feed1])#Optional

message_tests(feed_information_response1)

## Poll Request

poll_request1 = tm.PollRequest(message_id = tm.generate_message_id(),#Required
                               feed_name = 'TheFeedToPoll',#Required
                               subscription_id = 'SubsId002',#Optional
                               exclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional - Absence means 'no lower bound'
                               inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Optional - Absence means 'no upper bound'
                               content_bindings = [t.CB_STIX_XML_10])#Optional - defaults to accepting all content bindings

message_tests(poll_request1)

## Poll Response

stix_etree = etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')).getroot()

xml_content_block1 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10,#Required
                                     content = stix_etree,#Required. Can be etree or string
                                     padding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',#Optional
                                     timestamp_label = datetime.datetime.now(tzutc()))#Optional

string_content_block1 = tm.ContentBlock(content_binding = 'string',#Required
                                        content = 'Sample content',#Required
                                        padding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',#Optional
                                        timestamp_label = datetime.datetime.now(tzutc()))#Optional

poll_response1 = tm.PollResponse(message_id = tm.generate_message_id(),#Required
                                 in_response_to = tm.generate_message_id(),#Required - this should be the ID of the corresponding request
                                 feed_name = 'FeedName',#Required
                                 inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Required
                                 inclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional
                                 subscription_id = 'SubsId001',#Optional
                                 message = 'This is a message.',#Optional
                                 content_blocks = [xml_content_block1])#Optional

message_tests(poll_response1)

poll_response2 = tm.PollResponse(message_id = tm.generate_message_id(),#Required
                                 in_response_to = tm.generate_message_id(),#Required - this should be the ID of the corresponding request
                                 feed_name = 'FeedName',#Required
                                 inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Required
                                 inclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional
                                 subscription_id = 'SubsId001',#Optional
                                 message = 'This is a message.',#Optional
                                 content_blocks = [string_content_block1])#Optional

message_tests(poll_response2)

## Status Message

status_message1 = tm.StatusMessage(message_id = tm.generate_message_id(),#Required
                                   in_response_to = tm.generate_message_id(),#Required. Should be the ID of the corresponding request
                                   status_type = tm.ST_SUCCESS,#Required
                                   status_detail = 'Machine-processable info here!',#May be optional or not allowed, depending on status_type
                                   message = 'This is a message.')#Optional

message_tests(status_message1)

## Inbox Message

subscription_information1 = tm.InboxMessage.SubscriptionInformation(feed_name = 'SomeFeedName',#Required
                                                                    subscription_id = 'SubsId021',#Required
                                                                    inclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional - Absence means 'no lower bound'
                                                                    inclusive_end_timestamp_label = datetime.datetime.now(tzutc()))#Optional - Absence means 'no upper bound'

inbox_message1 = tm.InboxMessage(message_id = tm.generate_message_id(),#Required
                                 message = 'This is a message.',#Optional
                                 subscription_information = subscription_information1,#Optional
                                 content_blocks = [xml_content_block1])#Optional

message_tests(inbox_message1)

inbox_message2 = tm.InboxMessage(message_id = tm.generate_message_id(),#Required
                                 message = 'This is a message.',#Optional
                                 subscription_information = subscription_information1,#Optional
                                 content_blocks = [string_content_block1])#Optional

message_tests(inbox_message2)

## Manage Feed Subscription Request 

delivery_parameters1 = tm.DeliveryParameters(inbox_protocol = t.VID_TAXII_HTTP_10,#Required if requesting push messaging
                                             inbox_address = 'http://example.com/inbox',#Yes, if requesting push messaging
                                             delivery_message_binding = t.VID_TAXII_XML_10,#Required if requesting push messaging
                                             content_bindings = [t.CB_STIX_XML_10])#Optional - absence means accept all content bindings

manage_feed_subscription_request1 = tm.ManageFeedSubscriptionRequest(message_id = tm.generate_message_id(),#Required
                                                                     feed_name = 'SomeFeedName', #Required
                                                                     action = tm.ACT_UNSUBSCRIBE,#Required
                                                                     subscription_id = 'SubsId056',#Required for unsubscribe, prohibited otherwise
                                                                     delivery_parameters = delivery_parameters1)#Required

message_tests(manage_feed_subscription_request1)

## Manage Feed Subscription Response

poll_instance1 = tm.ManageFeedSubscriptionResponse.PollInstance(poll_protocol = t.VID_TAXII_HTTP_10,#Required
                                                                poll_address = 'http://example.com/poll',#Required
                                                                poll_message_bindings = [t.VID_TAXII_XML_10])#Required

subscription_instance1 = tm.ManageFeedSubscriptionResponse.SubscriptionInstance(subscription_id = 'SubsId234',#required
                                                                                delivery_parameters = [delivery_parameters1],#Required if message is responding to a status action. Optional otherwise
                                                                                poll_instances = [poll_instance1])#Required if action was polling subscription. Optional otherwise

manage_feed_subscription_response1 = tm.ManageFeedSubscriptionResponse(message_id = tm.generate_message_id(),#Required
                                                                       in_response_to = tm.generate_message_id(),#Required - Should be the ID of the corresponding request
                                                                       feed_name = 'Feed001',#Required
                                                                       message = 'This is a message',#Optional
                                                                       subscription_instances = [subscription_instance1])#Required

message_tests(manage_feed_subscription_response1)


### Test some Content Blocks ###
cb1 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10, content = '<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')
contentblock_tests(cb1)

cb2 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10, content = StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
contentblock_tests(cb2)

cb3 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10, content = etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')))
contentblock_tests(cb3)

cb4 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10, content = '<Something thats not XML')
contentblock_tests(cb4)

cb5 = tm.ContentBlock(content_binding = t.CB_STIX_XML_10, content = 'Something thats not XML <xml/>')
contentblock_tests(cb5)









