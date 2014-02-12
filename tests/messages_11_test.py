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

import datetime
import StringIO

from dateutil.tz import tzutc
from lxml import etree

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq

import sys

def message_tests(taxii_message, print_xml=False):
    if not isinstance(taxii_message, tm11.TAXIIMessage):
        raise ValueError('taxii_message was not an instance of TAXIIMessage')

    print '***** Message type = %s; id = %s' % (taxii_message.message_type, taxii_message.message_id)

    xml_string = taxii_message.to_xml()
    valid = tm11.validate_xml(xml_string)
    if valid is not True:
        print 'Bad XML was:'
        try:
            print etree.tostring(taxii_message.to_etree(), pretty_print=True)
        except Exception as e:
            print xml_string
        raise Exception('\tFailure of test #1 - XML not schema valid: %s' % valid)
    
    if print_xml:
        print etree.tostring(taxii_message.to_etree(), pretty_print=True)
    
    msg_from_xml = tm11.get_message_from_xml(xml_string)
    dictionary = taxii_message.to_dict()
    msg_from_dict = tm11.get_message_from_dict(dictionary)
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
    if not isinstance(content_block, tm11.ContentBlock):
        raise ValueError('content_block was not an instance of ContentBlock')

    print '***** Starting Content Block tests'

    xml_string = content_block.to_xml()
    block_from_xml = tm11.ContentBlock.from_xml(xml_string)
    dictionary = content_block.to_dict()
    block_from_dict = tm11.ContentBlock.from_dict(dictionary)
    json_string = content_block.to_json()
    block_from_json = tm11.ContentBlock.from_json(json_string)

    if content_block != block_from_xml:
        print '\t Failure of test #1 - running equals w/ debug:'
        content_block.__eq__(block_from_xml, True)
        raise Exception('Test #1 failed - content_block != block_from_xml')

    if content_block != block_from_dict:
        print '\t Failure of test #2 - running equals w/ debug:'
        content_block.__eq__(block_from_dict, True)
        raise Exception('Test #2 failed - content_block != block_from_dict')

    if block_from_xml != block_from_dict:
        print '\t Failure of test #3 - running equals w/ debug:'
        block_from_xml.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_xml != block_from_dict')
    if block_from_json != block_from_dict:
        print '\t Failure of test #3 - running equals w/ debug:'
        block_from_json.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_json != block_from_dict')

    print '***** All tests completed!'

## Begin 3.1 - TAXII Status Message Tests ##
sm01 = tm11.StatusMessage(
        message_id = 'SM01', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_SUCCESS, #Required
        status_detail = {'custom_status_detail_name': 'Custom status detail value', 
                         'Custom_detail_2': ['this one has', 'multiple values']}, #Required depending on Status Type. See spec for details
        message = 'This is a test message'#Optional
)
message_tests(sm01)

sm02 = tm11.StatusMessage(
        message_id = 'SM02', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_SUCCESS, #Required
        status_detail = None, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm02)

sm03 = tm11.StatusMessage(
        message_id = 'SM03', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_DESTINATION_COLLECTION_ERROR, #Required
        status_detail = {'ACCEPTABLE_DESTINATION': ['Collection1','Collection2']}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm03)

sm04 = tm11.StatusMessage(
        message_id = 'SM04', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_INVALID_RESPONSE_PART, #Required
        status_detail = {'MAX_PART_NUMBER': 4}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm04)

sm05 = tm11.StatusMessage(
        message_id = 'SM05', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_NOT_FOUND, #Required
        status_detail = {'ITEM': 'Collection1'}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm05)

sm06 = tm11.StatusMessage(
        message_id = 'SM06', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_PENDING, #Required
        status_detail = {'ESTIMATED_WAIT': 900, 'RESULT_ID': 'Result1', 'WILL_PUSH': False}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm06)

sm07 = tm11.StatusMessage(
        message_id = 'SM07', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_RETRY, #Required
        status_detail = {'ESTIMATED_WAIT': 900}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm07)

sm08 = tm11.StatusMessage(
        message_id = 'SM08', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_UNSUPPORTED_MESSAGE_BINDING, #Required
        status_detail = {'SUPPORTED_BINDING': [t.VID_TAXII_XML_10, t.VID_TAXII_XML_11]}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm08)

sm09 = tm11.StatusMessage(
        message_id = 'SM09', #Required
        in_response_to = tm11.generate_message_id(), #Required, should be the ID of the message that this is in response to
        status_type = tm11.ST_UNSUPPORTED_CONTENT_BINDING, #Required
        status_detail = {'SUPPORTED_CONTENT': [tm11.ContentBinding(t.CB_STIX_XML_10, subtype_ids=['subtype1','subtype2']), tm11.ContentBinding(t.CB_STIX_XML_101)]}, #Required/optional depending on Status Type. See spec for details
        message = None# Optional
)
message_tests(sm09)

#TODO: TEst the query status types

## End 3.1 - TAXII Status Message Tests ##

## Begin 3.2 - TAXII Discovery Request Tests ##

discovery_request1 = tm11.DiscoveryRequest(
        message_id=tm11.generate_message_id(),  # Required
        extended_headers={'ext_header1': 'value1', 'ext_header2': 'value2'})  # Optional.
        #Extended headers are optional for every message type, but demonstrated here
message_tests(discovery_request1)

## End 3.2 - TAXII Discovery Request Tests ##

## Begin 3.3 - TAXII Discovery Response Tests ##

#Create query information to use in the ServiceInstances
tei_01 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
            targeting_expression_id = t.CB_STIX_XML_10, #Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
            preferred_scope=[], #At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
            allowed_scope=['**'])#This example has no preferred scope, and allows any scope

tei_02 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
            targeting_expression_id = t.CB_STIX_XML_11,  #required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
            preferred_scope=['STIX_Package/Indicators/Indicator/**'], #At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
            allowed_scope=[])#This example prefers the Indicator scope and allows no other scope

tdq1 = tdq.DefaultQueryInfo(
            targeting_expression_infos = [tei_01, tei_02], #Required, 1-n. Indicates what targeting expressions are supported
            capability_modules = [tdq.CM_CORE])#Required, 1-n. Indicates which capability modules can be used.

tdq2 = tdq.DefaultQueryInfo(
            targeting_expression_infos = [tei_02], #Required, 1-n. Indicates what targeting expressions are supported
            capability_modules = [tdq.CM_REGEX])#Required, 1-n. Indicates which capability modules can be used.

#Create ServiceInstances to use in tests
si1 = tm11.DiscoveryResponse.ServiceInstance(
        service_type=tm11.SVC_POLL,  # Required
        services_version=t.VID_TAXII_SERVICES_11,  # Required
        protocol_binding=t.VID_TAXII_HTTP_10,  # Required
        service_address='http://example.com/poll/',  # Required
        message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
        available=True,  # Optional - defaults to None, which means 'Unknown'
        message='This is a message.',
        supported_query=[tdq1])  # Optional for service_type=POLL

si2 = tm11.DiscoveryResponse.ServiceInstance(
        service_type=tm11.SVC_POLL,  # Required
        services_version=t.VID_TAXII_SERVICES_11,  # Required
        protocol_binding=t.VID_TAXII_HTTP_10,  # Required
        service_address='http://example.com/poll/',  # Required
        message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
        available=True,  # Optional - defaults to None, which means 'Unknown'
        message='This is a message.',
        supported_query=[tdq1, tdq2])  # Optional for service_type=POLL

si3 = tm11.DiscoveryResponse.ServiceInstance(
        service_type=tm11.SVC_INBOX,  # Required
        services_version=t.VID_TAXII_SERVICES_11,  # Required
        protocol_binding=t.VID_TAXII_HTTP_10,  # Required
        service_address='http://example.com/inbox/',  # Required
        message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
        inbox_service_accepted_content = [tm11.ContentBinding(t.CB_STIX_XML_11), 
                                          tm11.ContentBinding(t.CB_STIX_XML_101), 
                                          tm11.ContentBinding(t.CB_STIX_XML_10)],#Optional. Defaults to "accepts all content"
        available=False,  # Optional - defaults to None, which means 'Unknown'
        message='This is a message. Yipee!')#optional

si4 = tm11.DiscoveryResponse.ServiceInstance(
        service_type=tm11.SVC_DISCOVERY,  # Required
        services_version=t.VID_TAXII_SERVICES_11,  # Required
        protocol_binding=t.VID_TAXII_HTTP_10,  # Required
        service_address='http://example.com/discovery/',  # Required
        message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
        message='This is a message. Yipee!')#optional

si5 = tm11.DiscoveryResponse.ServiceInstance(
        service_type=tm11.SVC_COLLECTION_MANAGEMENT,  # Required
        services_version=t.VID_TAXII_SERVICES_11,  # Required
        protocol_binding=t.VID_TAXII_HTTP_10,  # Required
        service_address='http://example.com/collection_management/',  # Required
        message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
        message='This is a message. Yipee!')#optional

#Create and test various discovery responses
discovery_response01 = tm11.DiscoveryResponse(
        message_id='DR01',  # Required
        in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
        service_instances=None)  # Optional.
message_tests(discovery_response01)

discovery_response02 = tm11.DiscoveryResponse(
        message_id='DR02',  # Required
        in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
        service_instances=[si1, si3, si5])  # Optional.
message_tests(discovery_response02)

discovery_response03 = tm11.DiscoveryResponse(
        message_id='DR03',  # Required
        in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
        service_instances=[si2, si4])  # Optional.
message_tests(discovery_response03)

discovery_response04 = tm11.DiscoveryResponse(
        message_id='DR04',  # Required
        in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
        service_instances=[si1, si2, si4])  # Optional.
message_tests(discovery_response04)

discovery_response05 = tm11.DiscoveryResponse(
        message_id='DR05',  # Required
        in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
        service_instances=[si1, si2, si3, si4, si5])  # Optional.
message_tests(discovery_response05)

## End 3.3 - TAXII Discovery Response Tests ##

## Begin 3.4 - TAXII Collection Information Request Tests ##
cir01 = tm11.CollectionInformationRequest(
        message_id = 'CIReq01'#Required
        )
message_tests(cir01)
## End 3.4 - TAXII Collection Information Request Tests ##

## Begin 3.5 - TAXII Collection Information Response Tests ##

#Instantiate a push methods
push_method1 = tm11.CollectionInformationResponse.CollectionInformation.PushMethod(
        push_protocol=t.VID_TAXII_HTTP_10,  # Required
        push_message_bindings=[t.VID_TAXII_XML_11])  # Required

#Instantiate Poll Services
poll_service1 = tm11.CollectionInformationResponse.CollectionInformation.PollingServiceInstance(
        poll_protocol=t.VID_TAXII_HTTPS_10,#Required
        poll_address = 'https://example.com/TheGreatestPollService',#Required
        poll_message_bindings=[t.VID_TAXII_XML_11])#Required, at least one item must be present in the list

poll_service2 = tm11.CollectionInformationResponse.CollectionInformation.PollingServiceInstance(
        poll_protocol=t.VID_TAXII_HTTP_10,#Required
        poll_address = 'http://example.com/TheOtherPollService',#Required
        poll_message_bindings=[t.VID_TAXII_XML_11])#Required, at least one item must be present in the list

#Instantiate Subscription Methods
subs_method1 = tm11.CollectionInformationResponse.CollectionInformation.SubscriptionMethod(
        subscription_protocol = t.VID_TAXII_HTTPS_10, #Required
        subscription_address = 'https://example.com/TheSubscriptionService/',#Required
        subscription_message_bindings = [t.VID_TAXII_XML_11])#Required - at least one item must be present in the list

subs_method2 = tm11.CollectionInformationResponse.CollectionInformation.SubscriptionMethod(
        subscription_protocol = t.VID_TAXII_HTTP_10, #Required
        subscription_address = 'http://example.com/TheSubscriptionService/',#Required
        subscription_message_bindings = [t.VID_TAXII_XML_11])#Required - at least one item must be present in the list

#Instantiate Inbox Services
inbox_service1 = tm11.CollectionInformationResponse.CollectionInformation.ReceivingInboxService(
        inbox_protocol = t.VID_TAXII_HTTPS_10,#required
        inbox_address = 'https://example.com/inbox/',#Required
        inbox_message_bindings = [t.VID_TAXII_XML_11],#Required
        supported_contents = None)#Optional - None means "all are supported"

inbox_service2 = tm11.CollectionInformationResponse.CollectionInformation.ReceivingInboxService(
        inbox_protocol = t.VID_TAXII_HTTPS_10,#required
        inbox_address = 'https://example.com/inbox/',#Required
        inbox_message_bindings = [t.VID_TAXII_XML_11],#Required
        supported_contents = [tm11.ContentBinding(t.CB_STIX_XML_11, subtype_ids=['exmaple1','example2'])])#Optional - None means "all are supported"

#Instantiate collections
collection1 = tm11.CollectionInformationResponse.CollectionInformation(
        collection_name = 'collection1',#Required
        collection_type = tm11.CT_DATA_FEED,#Optional. Defaults to 'Data Feed'
        available = False, #Optional. Defaults to None, which means "unknown"
        collection_description = 'This is a collection', #Required
        collection_volume = 4,#Optional - indicates typical number of messages per day
        supported_contents = [tm11.ContentBinding(t.CB_STIX_XML_101)],#Optional, absence indicates all content bindings
        push_methods = [push_method1],#Optional - absence indicates no push methods
        polling_service_instances = [poll_service1, poll_service2],#Optional - absence indicates no polling services
        subscription_methods = [subs_method1, subs_method2],#optional - absence means no subscription services
        receiving_inbox_services = [inbox_service1, inbox_service2])#Optional - absence indicates no receiving inbox services

collection2 = tm11.CollectionInformationResponse.CollectionInformation(
        collection_name = 'collection2', #Required
        collection_type = tm11.CT_DATA_SET,#Optional. Defaults to 'Data Feed'
        collection_description = 'Warrgghghglble.')#Required

collection3 = tm11.CollectionInformationResponse.CollectionInformation(
        collection_name = 'collection3', #Required
        collection_description = 'You must pay all the dollars to have this information.',#Required
        supported_contents = [tm11.ContentBinding(t.CB_STIX_XML_10), tm11.ContentBinding(t.CB_STIX_XML_11)],#Optional
        polling_service_instances = [poll_service2],#Optional - absence indicates no polling services
        subscription_methods = [subs_method2], #optional - absence means no subscription services
        receiving_inbox_services = [inbox_service2])#Optional - absence indicates no receiving inbox services

collection4 = tm11.CollectionInformationResponse.CollectionInformation(
        collection_name = 'collection4', #Required
        collection_description = 'So improve information. Much amaze.',#Required
        supported_contents = [tm11.ContentBinding(t.CB_STIX_XML_101, subtype_ids=['ex1','ex2','ex3'])],#Optional
        receiving_inbox_services = [inbox_service1, inbox_service2])#Optional - absence indicates no receiving inbox services

collection_response1 = tm11.CollectionInformationResponse(
        message_id = 'CIR01',#Required
        in_response_to = '0',#Required - should be the ID of the message tha this message is a response to
        collection_informations = [collection1])#Optional - absence means "no collections"
message_tests(collection_response1)

collection_response2 = tm11.CollectionInformationResponse(
        message_id = 'CIR02',#Required
        in_response_to = '0',#Required - should be the ID of the message tha this message is a response to
        collection_informations = [collection1, collection2, collection3, collection4])#Optional - absence means "no collections"
message_tests(collection_response2)

collection_response3 = tm11.CollectionInformationResponse(
        message_id = 'CIR03',#Required
        in_response_to = '0')#Required - should be the ID of the message tha this message is a response to
message_tests(collection_response3)

collection_response4 = tm11.CollectionInformationResponse(
        message_id = 'CIR04',#Required
        in_response_to = '0',#Required - should be the ID of the message tha this message is a response to
        collection_informations = [collection1, collection4])#Optional - absence means "no collections"
message_tests(collection_response4)

collection_response5 = tm11.CollectionInformationResponse(
        message_id = 'CIR05',#Required
        in_response_to = '0',#Required - should be the ID of the message tha this message is a response to
        collection_informations = [collection2, collection4])#Optional - absence means "no collections"
message_tests(collection_response5)

## End 3.5 - TAXII Collection Information Response Tests ##

## Begin 3.6 - TAXII Manage Collection Subscription Request Tests ##

#build up some queries
test1 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE, #Required
                                        relationship='equals', #Required
                                        parameters={'value': 'Test value',
                                                    'match_type': 'case_sensitive_string'}#Each relationship defines which params are and are not required
                                        )

test2 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_REGEX, #Required
                                        relationship='matches',#Required
                                        parameters={'value': '[A-Z]*',
                                                    'case_sensitive': True})#Each relationship defines which params are and are not required

test3 = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_TIMESTAMP,#Required
                                        relationship='greater_than',#Required
                                        parameters={'value': datetime.datetime.now()})#Each relationship defines which params are and are not required

criterion1 = tdq.DefaultQuery.Criterion(target='**', test=test1)
criterion2 = tdq.DefaultQuery.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
criterion3 = tdq.DefaultQuery.Criterion(target='**/Description', test=test3)

criteria1 = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1])
criteria2 = tdq.DefaultQuery.Criteria(operator=tdq.OP_OR, criterion=[criterion1, criterion2, criterion3])
criteria3 = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

query1 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria1)
query2 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria3)

#set up some subscription parameters

subscription_parameters1 = tm11.SubscriptionParameters(
    response_type = tm11.RT_COUNT_ONLY, #Optional, defaults to FULL
    content_bindings = [tm11.ContentBinding(t.CB_STIX_XML_11)],#Optional. Absence means no restrictions on returned data
    query = query1)#Optional. Absence means no query

subscription_parameters2 = tm11.SubscriptionParameters(
    response_type = tm11.RT_FULL, #Optional, defaults to FULL
    #content_bindings = [tm11.ContentBinding(t.CB_STIX_XML_11)],#Optional. Absence means no restrictions on returned data
    query = query2)#Optional. Absence means no query

subscription_parameters3 = tm11.SubscriptionParameters()#Use all the defaults

#set up some delivery parameters

push_parameters1 = tm11.PushParameters(
    inbox_protocol = t.VID_TAXII_HTTPS_10, #Required
    inbox_address = 'https://example.com/inboxAddress/',#Required
    delivery_message_binding = t.VID_TAXII_XML_11)#Required

#Now for the messages
subs_req1 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq01', #Required
        action = tm11.ACT_SUBSCRIBE, #Required
        collection_name = 'collection1', #Required
        #subscription_id = None, #Prohibited for action = SUBSCRIBE
        subscription_parameters = subscription_parameters1,#optional - absence means there are not any subscription parameters
        push_parameters = push_parameters1)#Optional - absence means push messaging not requested
message_tests(subs_req1)

subs_req2 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq02',#Required
        action = tm11.ACT_SUBSCRIBE, #Required
        collection_name = 'collection2',#Required
        #subscription_id = None, #Prohibited for action = SUBSCRIBE
        subscription_parameters = subscription_parameters2)#optional - absence means there are not any subscription parameters
        #delivery_parameters = None)#Optional - absence means push messaging not requested
message_tests(subs_req2)

subs_req3 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq03',#Required
        action = tm11.ACT_SUBSCRIBE, #Required
        collection_name = 'collection213',#Required
        #subscription_id = None, #Prohibited for action = SUBSCRIBE
        subscription_parameters = subscription_parameters3)#optional - absence means there are not any subscription parameters
        #delivery_parameters = None)#Optional - absence means push messaging not requested
message_tests(subs_req3)

subs_req4 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq04',#Required
        action = tm11.ACT_SUBSCRIBE, #Required
        collection_name = 'collection2')#Required
        #subscription_id = None, #Prohibited for action = SUBSCRIBE
        #subscription_parameters = subscription_parameters2,#optional - absence means there are not any subscription parameters
        #delivery_parameters = None)#Optional - absence means push messaging not requested
message_tests(subs_req4)

subs_req5 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq05', #Required
        action = tm11.ACT_STATUS, #Required
        collection_name = 'collection2', #Required
        subscription_id = 'id1') #Optional for ACT_STATUS
        #subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
message_tests(subs_req5)

subs_req6 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq06', #Required
        action = tm11.ACT_STATUS, #Required
        collection_name = 'collection2') #Required
        #subscription_id = 'id1') #Optional for ACT_STATUS
        #subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
message_tests(subs_req6)

subs_req7 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq07', #Required
        action = tm11.ACT_PAUSE, #Required
        collection_name = 'collection2', #Required
        subscription_id = 'id1') #Optional for ACT_STATUS
        #subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
message_tests(subs_req7)

subs_req8 = tm11.ManageCollectionSubscriptionRequest(
        message_id = 'SubsReq08', #Required
        action = tm11.ACT_RESUME, #Required
        collection_name = 'collection2', #Required
        subscription_id = 'id1') #Optional for ACT_STATUS
        #subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
message_tests(subs_req8)
## End 3.6 - TAXII Manage Collection Subscription Request Tests ##

## Begin 3.7 - TAXII Manage Collection Subscription Response Tests ##

poll_instance1 = tm11.ManageCollectionSubscriptionResponse.PollInstance(
                    poll_protocol = t.VID_TAXII_HTTPS_10,
                    poll_address = 'https://example.com/poll1/',
                    poll_message_bindings = [t.VID_TAXII_XML_11])

poll_instance2 = tm11.ManageCollectionSubscriptionResponse.PollInstance(
                    poll_protocol = t.VID_TAXII_HTTPS_10,
                    poll_address = 'https://example.com/poll2/',
                    poll_message_bindings = [t.VID_TAXII_XML_11])
poll_instance3 = tm11.ManageCollectionSubscriptionResponse.PollInstance(
                    poll_protocol = t.VID_TAXII_HTTPS_10,
                    poll_address = 'https://example.com/poll3/',
                    poll_message_bindings = [t.VID_TAXII_XML_11])

subs1 = tm11.ManageCollectionSubscriptionResponse.SubscriptionInstance(
            status = tm11.SS_ACTIVE,#Optional, defaults to ACTIVE
            subscription_id = 'Subs001',#Required
            subscription_parameters = subscription_parameters1,#Optional - should be an echo of the request
            push_parameters = push_parameters1,#Optional - should be an echo of the request
            poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
            )

subs2 = tm11.ManageCollectionSubscriptionResponse.SubscriptionInstance(
            status = tm11.SS_PAUSED,#Optional, defaults to ACTIVE
            subscription_id = 'Subs001',#Required
            subscription_parameters = subscription_parameters1,#Optional - should be an echo of the request
            push_parameters = push_parameters1,#Optional - should be an echo of the request
            #poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
            )

subs3 = tm11.ManageCollectionSubscriptionResponse.SubscriptionInstance(
            status = tm11.SS_PAUSED,#Optional, defaults to ACTIVE
            subscription_id = 'Subs001',#Required
            #subscription_parameters = subscription_parameters1,#Optional - should be an echo of the request
            #push_parameters = delivery_parameters1,#Optional - should be an echo of the request
            #poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
            )

subs_resp1 = tm11.ManageCollectionSubscriptionResponse(
        message_id = 'SubsResp01',#Required
        in_response_to = 'xyz', #Required - should be the ID of the message that this is a response to
        collection_name = 'abc123',#Required
        message = 'Hullo!', #Optional
        subscription_instances = [subs1, subs2, subs3],#Optional
        )
message_tests(subs_resp1)

subs_resp2 = tm11.ManageCollectionSubscriptionResponse(
        message_id = 'SubsResp02',#Required
        in_response_to = 'xyz', #Required - should be the ID of the message that this is a response to
        collection_name = 'abc123',#Required
        #message = 'Hullo!', #Optional
        #subscription_instances = [subs1, subs2, subs3],#Optional
        )
message_tests(subs_resp2)

subs_resp3 = tm11.ManageCollectionSubscriptionResponse(
        message_id = 'SubsResp03',#Required
        in_response_to = 'xyz', #Required - should be the ID of the message that this is a response to
        collection_name = 'abc123',#Required
        #message = 'Hullo!', #Optional
        subscription_instances = [subs1],#Optional
        )
message_tests(subs_resp3)

subs_resp4 = tm11.ManageCollectionSubscriptionResponse(
        message_id = 'SubsResp04',#Required
        in_response_to = 'xyz', #Required - should be the ID of the message that this is a response to
        collection_name = 'abc123',#Required
        message = 'Hullo!', #Optional
        #subscription_instances = [subs1, subs2, subs3],#Optional
        )
message_tests(subs_resp4)

## End 3.7 - TAXII Manage Collection Subscription Response Tests ##

## Begin 3.8 - TAXII Poll Request Tests ##

#Set up a delivery parameters
delivery_parameters1 = tm11.DeliveryParameters(
    inbox_protocol = t.VID_TAXII_HTTPS_10, #Required
    inbox_address = 'https://example.com/inboxAddress/',#Required
    delivery_message_binding = t.VID_TAXII_XML_11)#Required

#set up some PollParameters
poll_params1 = tm11.PollRequest.PollParameters(
                allow_asynch = False,#Optional, defaults to False
                response_type = tm11.RT_COUNT_ONLY,#Optional, defaults to RT_FULL
                content_bindings = [tm11.ContentBinding(binding_id=t.CB_STIX_XML_11)],#Optional, defaults to None, which means "all bindings are accepted in response"
                query = query1,#Optional - defaults to None
                delivery_parameters = delivery_parameters1)#Optional - defaults to None

#set up some PollParameters
poll_params2 = tm11.PollRequest.PollParameters()

#set up some PollParameters
poll_params3 = tm11.PollRequest.PollParameters(query = query1)#Optional - defaults to None)#Optional - defaults to None

#The actual tests

poll_req1 = tm11.PollRequest(
        message_id = 'PollReq01',#Required
        collection_name = 'collection100',#Required
        exclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        subscription_id = '12345',#Optional - one of this or poll_parameters MUST be present.
        poll_parameters = None)#Optional - one of this or subscription_id MUST be present
message_tests(poll_req1)

poll_req2 = tm11.PollRequest(
        message_id = 'PollReq02',#Required
        collection_name = 'collection100',#Required
        subscription_id = 'Kenneth Coal Collection',#Optional - one of this or poll_parameters MUST be present.
        poll_parameters = None)#Optional - one of this or subscription_id MUST be present
message_tests(poll_req2)

poll_req3 = tm11.PollRequest(
        message_id = 'PollReq03',#Required
        collection_name = 'collection100',#Required
        exclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        poll_parameters = poll_params1)#Optional - one of this or subscription_id MUST be present
message_tests(poll_req3)


poll_req4 = tm11.PollRequest(
        message_id = 'PollReq04',#Required
        collection_name = 'collection100',#Required
        inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        poll_parameters = poll_params2)#Optional - one of this or subscription_id MUST be present
message_tests(poll_req4)

poll_req5 = tm11.PollRequest(
        message_id = 'PollReq05',#Required
        collection_name = 'collection100',#Required
        exclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional for a Data Feed, prohibited for a Data Set
        poll_parameters = poll_params3)#Optional - one of this or subscription_id MUST be present
message_tests(poll_req5)
## End 3.8 - TAXII Poll Request Tests ##

## Begin 3.9 - TAXII Poll Response Tests ##

#build some content blocks

cb001 = tm11.ContentBlock(
        content_binding = tm11.ContentBinding(t.CB_STIX_XML_11, subtype_ids=['test1']),#Required
        content = '<STIX_Package/>',#Required (This isn't real STIX)
        timestamp_label = datetime.datetime.now(tzutc()),#Optional
        message = 'Hullo!',#Optional
        padding = 'The quick brown fox jumped over the lazy dogs.')#Optional

cb002 = tm11.ContentBlock(
        content_binding = tm11.ContentBinding(t.CB_STIX_XML_11),#Required
        content = '<STIX_Package/>')#Required
#now the tests

poll_resp1 = tm11.PollResponse(
        message_id = 'PollResp1',#Required
        in_response_to = 'tmp',#Required. Must be the message that this is a response to
        collection_name = 'blah',#Required
        more = True, #Optional - defaults to false
        result_id = '123',#Optional
        result_part_number = 1,#optional
        subscription_id = '24',#optional
        exclusive_begin_timestamp_label = datetime.datetime.now(tzutc()),#Optional for data feeds, prohibited for data sets
        inclusive_end_timestamp_label = datetime.datetime.now(tzutc()),#required for data feeds, prohibited for data sets
        record_count = tm11.RecordCount(record_count=22, partial_count=False),
        message = 'Woooooooo',#optional
        content_blocks = [])#optional
message_tests(poll_resp1)

poll_resp2 = tm11.PollResponse(
        message_id = 'PollResp2',#Required
        in_response_to = 'tmp',#Required. Must be the message that this is a response to
        collection_name = 'blah')#Required
        
message_tests(poll_resp2)

poll_resp3 = tm11.PollResponse(
        message_id = 'PollResp3',#Required
        in_response_to = 'tmp',#Required. Must be the message that this is a response to
        collection_name = 'blah',#Required
        result_id = '123',#Optional
        subscription_id = '24',#optional
        record_count = tm11.RecordCount(record_count=22),
        content_blocks = [])#optional
message_tests(poll_resp3)

poll_resp4 = tm11.PollResponse(
        message_id = 'PollResp4',#Required
        in_response_to = 'tmp',#Required. Must be the message that this is a response to
        collection_name = 'blah',#Required
        content_blocks = [cb001, cb002])#optional
message_tests(poll_resp4)

## End 3.9 - TAXII Poll Response Tests

## Begin 3.10 - TAXII Inbox Message Tests ##

#subscription information

subs_info1 = tm11.InboxMessage.SubscriptionInformation(
        collection_name='SomeCollectionName',  # Required
        subscription_id='SubsId021',  # Required
        exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for data feeds, prohibited for data sets
        inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))  # Optional for data feeds, prohibited for data sets

subs_info2 = tm11.InboxMessage.SubscriptionInformation(
        collection_name='SomeCollectionName',  # Required
        subscription_id='SubsId021') # Required
#the tests

inbox1 = tm11.InboxMessage(
        message_id = 'Inbox1',#Required
        result_id = '123',#Optional
        destination_collection_names=['collection1','collection2'],#Optional
        message = 'Hello!', #Optional
        subscription_information = subs_info1,#Optional
        record_count = tm11.RecordCount(22, partial_count=True),#Optional
        content_blocks = [cb001, cb002])
message_tests(inbox1)

inbox2 = tm11.InboxMessage(message_id = 'Inbox1')#Required
message_tests(inbox2)

inbox3 = tm11.InboxMessage(
        message_id = 'Inbox3',#Required
        result_id = '123',#Optional
        destination_collection_names=['collection1','collection2'],#Optional
        subscription_information = subs_info1,#Optional
        content_blocks = [cb002])
message_tests(inbox3)

## End 3.10 - TAXII Inbox Message Tests ##

## Begin 3.11 - Poll Fulfillment Request Tests ##

pf1 = tm11.PollFulfillmentRequest(
        message_id = 'pf1',#Required
        collection_name = '1-800-collection',#Required
        result_id = '123',#Required
        result_part_number = 1)#Required

message_tests(pf1)

## End 3.11 - Poll Fulfillment Request Tests ##

### Begin - Test some Content Blocks ###
cb1 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                      content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')
contentblock_tests(cb1)

cb2 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                      content=StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
contentblock_tests(cb2)

cb3 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                      content=etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')))
contentblock_tests(cb3)

cb4 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                      content='<Something thats not XML')
contentblock_tests(cb4)

cb5 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                      content='Something thats not XML <xml/>')
contentblock_tests(cb5)

### End - Test some Content Blocks ###
