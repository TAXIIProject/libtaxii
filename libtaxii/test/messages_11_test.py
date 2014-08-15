# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# This file has two purposes:
# 1. To provide a rough unit test of libtaxii.messages
# 2. To provide examples of how to use libtaxii.messages

# Contributors:
# * Mark Davidson - mdavidson@mitre.org

import datetime
import StringIO
import sys
import unittest

from dateutil.tz import tzutc
from lxml import etree

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq

# TODO: This is bad practice. Refactor this.
# Set up some things used across multiple tests.

#Note that the "*_old" tests are just to make sure that backward-compatible aliases exist
test1 = tdq.Test(capability_id=tdq.CM_CORE,  # Required
                 relationship='equals',  # Required
                 parameters={'value': 'Test value',
                             'match_type': 'case_sensitive_string'}  # Each relationship defines which params are and are not required
                 )

test1_old = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE,  # Required
                                        relationship='equals',  # Required
                                        parameters={'value': 'Test value',
                                                    'match_type': 'case_sensitive_string'}  # Each relationship defines which params are and are not required
                                        )

test2 = tdq.Test(capability_id=tdq.CM_REGEX,  # Required
                 relationship='matches',  # Required
                 parameters={'value': '[A-Z]*',
                             'case_sensitive': True})  # Each relationship defines which params are and are not required

test2_old = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_REGEX,  # Required
                                        relationship='matches',  # Required
                                        parameters={'value': '[A-Z]*',
                                                    'case_sensitive': True})  # Each relationship defines which params are and are not required

test3 = tdq.Test(capability_id=tdq.CM_TIMESTAMP,  # Required
                 relationship='greater_than',  # Required
                 parameters={'value': datetime.datetime.now()})  # Each relationship defines which params are and are not required

test3_old = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_TIMESTAMP,  # Required
                                        relationship='greater_than',  # Required
                                        parameters={'value': datetime.datetime.now()})  # Each relationship defines which params are and are not required

criterion1 = tdq.Criterion(target='**', test=test1)
criterion2 = tdq.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
criterion3 = tdq.Criterion(target='**/Description', test=test3)

criterion1_old = tdq.DefaultQuery.Criterion(target='**', test=test1)
criterion2_old = tdq.DefaultQuery.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
criterion3_old = tdq.DefaultQuery.Criterion(target='**/Description', test=test3)

criteria1 = tdq.Criteria(operator=tdq.OP_AND, criterion=[criterion1])
criteria2 = tdq.Criteria(operator=tdq.OP_OR, criterion=[criterion1, criterion2, criterion3])
criteria3 = tdq.Criteria(operator=tdq.OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

criteria1_old = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1])
criteria2_old = tdq.DefaultQuery.Criteria(operator=tdq.OP_OR, criterion=[criterion1, criterion2, criterion3])
criteria3_old = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

query1 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria1)
query2 = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria3)

subscription_parameters1 = tm11.SubscriptionParameters(
    response_type=tm11.RT_COUNT_ONLY,  # Optional, defaults to FULL
    content_bindings=[tm11.ContentBinding(t.CB_STIX_XML_11)],  # Optional. Absence means no restrictions on returned data
    query=query1)  # Optional. Absence means no query

push_parameters1 = tm11.PushParameters(
    inbox_protocol=t.VID_TAXII_HTTPS_10,  # Required
    inbox_address='https://example.com/inboxAddress/',  # Required
    delivery_message_binding=t.VID_TAXII_XML_11)  # Required

cb001 = tm11.ContentBlock(
    content_binding=tm11.ContentBinding(t.CB_STIX_XML_11, subtype_ids=['test1']),  # Required
    content='<STIX_Package/>',  # Required (This isn't real STIX)
    timestamp_label=datetime.datetime.now(tzutc()),  # Optional
    message='Hullo!',  # Optional
    padding='The quick brown fox jumped over the lazy dogs.')  # Optional

cb002 = tm11.ContentBlock(
    content_binding=tm11.ContentBinding(t.CB_STIX_XML_11),  # Required
    content='<STIX_Package/>')  # Required


def round_trip_message(taxii_message, print_xml=False):
    if not isinstance(taxii_message, tm11.TAXIIMessage):
        raise ValueError('taxii_message was not an instance of TAXIIMessage')

    # print '***** Message type = %s; id = %s' % (taxii_message.message_type, taxii_message.message_id)

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
    taxii_message.to_text()#to_text() returns a string, this just makes sure the call succeeds but doesn't validate the response
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

    # print '***** All tests completed!'


def round_trip_content_block(content_block):
    if not isinstance(content_block, tm11.ContentBlock):
        raise ValueError('content_block was not an instance of ContentBlock')

    # print '***** Starting Content Block tests'

    xml_string = content_block.to_xml()
    block_from_xml = tm11.ContentBlock.from_xml(xml_string)
    dictionary = content_block.to_dict()
    block_from_dict = tm11.ContentBlock.from_dict(dictionary)
    json_string = content_block.to_json()
    block_from_json = tm11.ContentBlock.from_json(json_string)
    content_block.to_text()

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

    # print '***** All tests completed!'


class StatusMessageTests(unittest.TestCase):

    def test_status_message_01(self):
        sm01 = tm11.StatusMessage(
            message_id='SM01',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=tm11.ST_SUCCESS,  # Required
            status_detail={'custom_status_detail_name': 'Custom status detail value',
                           'Custom_detail_2': ['this one has', 'multiple values']},  # Required depending on Status Type. See spec for details
            message='This is a test message'  # Optional
        )
        round_trip_message(sm01)

    def test_status_message_02(self):
        sm02 = tm11.StatusMessage(
                message_id='SM02',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_SUCCESS,  # Required
                status_detail=None,  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm02)

    def test_status_message_03(self):
        sm03 = tm11.StatusMessage(
                message_id='SM03',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_DESTINATION_COLLECTION_ERROR,  # Required
                status_detail={'ACCEPTABLE_DESTINATION': ['Collection1', 'Collection2']},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm03)

    def test_status_message_04(self):
        sm04 = tm11.StatusMessage(
                message_id='SM04',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_INVALID_RESPONSE_PART,  # Required
                status_detail={'MAX_PART_NUMBER': 4},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm04)

    def test_status_message_05(self):
        sm05 = tm11.StatusMessage(
                message_id='SM05',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_NOT_FOUND,  # Required
                status_detail={'ITEM': 'Collection1'},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm05)

    def test_status_message_06(self):
        sm06 = tm11.StatusMessage(
                message_id='SM06',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_PENDING,  # Required
                status_detail={'ESTIMATED_WAIT': 900, 'RESULT_ID': 'Result1', 'WILL_PUSH': False},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm06)

    def test_status_message_07(self):
        sm07 = tm11.StatusMessage(
                message_id='SM07',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_RETRY,  # Required
                status_detail={'ESTIMATED_WAIT': 900},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm07)

    def test_status_message_08(self):
        sm08 = tm11.StatusMessage(
                message_id='SM08',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_UNSUPPORTED_MESSAGE_BINDING,  # Required
                status_detail={'SUPPORTED_BINDING': [t.VID_TAXII_XML_10, t.VID_TAXII_XML_11]},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm08)

    def test_status_message_09(self):
        sm09 = tm11.StatusMessage(
                message_id='SM09',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_UNSUPPORTED_CONTENT_BINDING,  # Required
                status_detail={'SUPPORTED_CONTENT': tm11.ContentBinding(binding_id = t.CB_STIX_XML_101, subtype_ids = ['subtype1', 'subtype2'])},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm09)

    def test_status_message_10(self):
        sm09 = tm11.StatusMessage(
                message_id='SM10',  # Required
                in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
                status_type=tm11.ST_UNSUPPORTED_CONTENT_BINDING,  # Required
                status_detail={'SUPPORTED_CONTENT': [tm11.ContentBinding(binding_id = t.CB_STIX_XML_101, subtype_ids = ['subtype1', 'subtype2']), tm11.ContentBinding(binding_id = t.CB_STIX_XML_11)]},  # Required/optional depending on Status Type. See spec for details
                message=None  # Optional
        )
        round_trip_message(sm09)
    # TODO: TEst the query status types


class DiscoveryRequestTests(unittest.TestCase):

    def test_discovery_request(self):
        discovery_request1 = tm11.DiscoveryRequest(
                message_id=tm11.generate_message_id(),  # Required
                extended_headers={'ext_header1': 'value1', 'ext_header2': 'value2'})  # Optional.
                # Extended headers are optional for every message type, but demonstrated here
        round_trip_message(discovery_request1)


class DiscoveryResponseTests(unittest.TestCase):

    def setUp(self):
        # Create query information to use in the ServiceInstances
        tei_01 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
                    targeting_expression_id=t.CB_STIX_XML_10,  # Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
                    preferred_scope=[],  # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
                    allowed_scope=['**'])  # This example has no preferred scope, and allows any scope

        tei_02 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
                    targeting_expression_id=t.CB_STIX_XML_11,  # required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
                    preferred_scope=['STIX_Package/Indicators/Indicator/**'],  # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
                    allowed_scope=[])  # This example prefers the Indicator scope and allows no other scope

        tdq1 = tdq.DefaultQueryInfo(
                    targeting_expression_infos=[tei_01, tei_02],  # Required, 1-n. Indicates what targeting expressions are supported
                    capability_modules=[tdq.CM_CORE])  # Required, 1-n. Indicates which capability modules can be used.

        tdq2 = tdq.DefaultQueryInfo(
                    targeting_expression_infos=[tei_02],  # Required, 1-n. Indicates what targeting expressions are supported
                    capability_modules=[tdq.CM_REGEX])  # Required, 1-n. Indicates which capability modules can be used.

        # Create ServiceInstances to use in tests
        self.si1 = tm11.ServiceInstance(
                service_type=tm11.SVC_POLL,  # Required
                services_version=t.VID_TAXII_SERVICES_11,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/poll/',  # Required
                message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
                available=True,  # Optional - defaults to None, which means 'Unknown'
                message='This is a message.',
                supported_query=[tdq1])  # Optional for service_type=POLL

        self.si2 = tm11.ServiceInstance(
                service_type=tm11.SVC_POLL,  # Required
                services_version=t.VID_TAXII_SERVICES_11,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/poll/',  # Required
                message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
                available=True,  # Optional - defaults to None, which means 'Unknown'
                message='This is a message.',
                supported_query=[tdq1, tdq2])  # Optional for service_type=POLL

        self.si3 = tm11.ServiceInstance(
                service_type=tm11.SVC_INBOX,  # Required
                services_version=t.VID_TAXII_SERVICES_11,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/inbox/',  # Required
                message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
                inbox_service_accepted_content=[tm11.ContentBinding(t.CB_STIX_XML_11),
                                                tm11.ContentBinding(t.CB_STIX_XML_101),
                                                tm11.ContentBinding(t.CB_STIX_XML_10)],  # Optional. Defaults to "accepts all content"
                available=False,  # Optional - defaults to None, which means 'Unknown'
                message='This is a message. Yipee!')  # optional

        self.si4 = tm11.ServiceInstance(
                service_type=tm11.SVC_DISCOVERY,  # Required
                services_version=t.VID_TAXII_SERVICES_11,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/discovery/',  # Required
                message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
                message='This is a message. Yipee!')  # optional

        self.si5 = tm11.ServiceInstance(
                service_type=tm11.SVC_COLLECTION_MANAGEMENT,  # Required
                services_version=t.VID_TAXII_SERVICES_11,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/collection_management/',  # Required
                message_bindings=[t.VID_TAXII_XML_11],  # Required, must have at least one value in the list
                message='This is a message. Yipee!')  # optional

    def test_discovery_response_01(self):
        # Create and test various discovery responses
        discovery_response01 = tm11.DiscoveryResponse(
                message_id='DR01',  # Required
                in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
                service_instances=None)  # Optional.
        round_trip_message(discovery_response01)

    def test_discovery_response_02(self):
        discovery_response02 = tm11.DiscoveryResponse(
                message_id='DR02',  # Required
                in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
                service_instances=[self.si1, self.si3, self.si5])  # Optional.
        round_trip_message(discovery_response02)

    def test_discovery_response_03(self):
        discovery_response03 = tm11.DiscoveryResponse(
                message_id='DR03',  # Required
                in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
                service_instances=[self.si2, self.si4])  # Optional.
        round_trip_message(discovery_response03)

    def test_discovery_response_04(self):
        discovery_response04 = tm11.DiscoveryResponse(
                message_id='DR04',  # Required
                in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
                service_instances=[self.si1, self.si2, self.si4])  # Optional.
        round_trip_message(discovery_response04)

    def test_discovery_response_05(self):
        discovery_response05 = tm11.DiscoveryResponse(
                message_id='DR05',  # Required
                in_response_to='TheSecondIdentifier',  # Required. This should be the ID of the corresponding request
                service_instances=[self.si1, self.si2, self.si3, self.si4, self.si5])  # Optional.
        round_trip_message(discovery_response05)

    def test_discovery_response_deprecated(self):
        # Test deprecated nested form:
        #   DiscoveryResponse.ServiceInstance
        service = tm11.DiscoveryResponse.ServiceInstance(
                service_type=tm11.SVC_COLLECTION_MANAGEMENT,
                services_version=t.VID_TAXII_SERVICES_11,
                protocol_binding=t.VID_TAXII_HTTP_10,
                service_address='http://example.com/collection_management/',
                message_bindings=[t.VID_TAXII_XML_11])

        response = tm11.DiscoveryResponse(
                message_id='DR05',
                in_response_to='TheSecondIdentifier',
                service_instances=[service])

        round_trip_message(response)


class CollectionInformationRequestTests(unittest.TestCase):

    def test_collection_information_request_01(self):
        cir01 = tm11.CollectionInformationRequest(
                message_id='CIReq01'  # Required
        )
        round_trip_message(cir01)


class CollectionInformationResponseTests(unittest.TestCase):

    def setUp(self):
        # Instantiate a push methods
        push_method1 = tm11.PushMethod(
                push_protocol=t.VID_TAXII_HTTP_10,  # Required
                push_message_bindings=[t.VID_TAXII_XML_11])  # Required

        # Instantiate Poll Services
        poll_service1 = tm11.PollingServiceInstance(
                poll_protocol=t.VID_TAXII_HTTPS_10,  # Required
                poll_address='https://example.com/TheGreatestPollService',  # Required
                poll_message_bindings=[t.VID_TAXII_XML_11])  # Required, at least one item must be present in the list

        poll_service2 = tm11.PollingServiceInstance(
                poll_protocol=t.VID_TAXII_HTTP_10,  # Required
                poll_address='http://example.com/TheOtherPollService',  # Required
                poll_message_bindings=[t.VID_TAXII_XML_11])  # Required, at least one item must be present in the list

        # Instantiate Subscription Methods
        subs_method1 = tm11.SubscriptionMethod(
                subscription_protocol=t.VID_TAXII_HTTPS_10,  # Required
                subscription_address='https://example.com/TheSubscriptionService/',  # Required
                subscription_message_bindings=[t.VID_TAXII_XML_11])  # Required - at least one item must be present in the list

        subs_method2 = tm11.SubscriptionMethod(
                subscription_protocol=t.VID_TAXII_HTTP_10,  # Required
                subscription_address='http://example.com/TheSubscriptionService/',  # Required
                subscription_message_bindings=[t.VID_TAXII_XML_11])  # Required - at least one item must be present in the list

        # Instantiate Inbox Services
        inbox_service1 = tm11.ReceivingInboxService(
                inbox_protocol=t.VID_TAXII_HTTPS_10,  # required
                inbox_address='https://example.com/inbox/',  # Required
                inbox_message_bindings=[t.VID_TAXII_XML_11],  # Required
                supported_contents=None)  # Optional - None means "all are supported"

        inbox_service2 = tm11.ReceivingInboxService(
                inbox_protocol=t.VID_TAXII_HTTPS_10,  # required
                inbox_address='https://example.com/inbox/',  # Required
                inbox_message_bindings=[t.VID_TAXII_XML_11],  # Required
                supported_contents=[tm11.ContentBinding(t.CB_STIX_XML_11, subtype_ids=['exmaple1', 'example2'])])  # Optional - None means "all are supported"

        # Instantiate collections
        self.collection1 = tm11.CollectionInformation(
                collection_name='collection1',  # Required
                collection_type=tm11.CT_DATA_FEED,  # Optional. Defaults to 'Data Feed'
                available=False,  # Optional. Defaults to None, which means "unknown"
                collection_description='This is a collection',  # Required
                collection_volume=4,  # Optional - indicates typical number of messages per day
                supported_contents=[tm11.ContentBinding(t.CB_STIX_XML_101)],  # Optional, absence indicates all content bindings
                push_methods=[push_method1],  # Optional - absence indicates no push methods
                polling_service_instances=[poll_service1, poll_service2],  # Optional - absence indicates no polling services
                subscription_methods=[subs_method1, subs_method2],  # optional - absence means no subscription services
                receiving_inbox_services=[inbox_service1, inbox_service2])  # Optional - absence indicates no receiving inbox services

        self.collection2 = tm11.CollectionInformation(
                collection_name='collection2',  # Required
                collection_type=tm11.CT_DATA_SET,  # Optional. Defaults to 'Data Feed'
                collection_description='Warrgghghglble.')  # Required

        self.collection3 = tm11.CollectionInformation(
                collection_name='collection3',  # Required
                collection_description='You must pay all the dollars to have this information.',  # Required
                supported_contents=[tm11.ContentBinding(t.CB_STIX_XML_10), tm11.ContentBinding(t.CB_STIX_XML_11)],  # Optional
                polling_service_instances=[poll_service2],  # Optional - absence indicates no polling services
                subscription_methods=[subs_method2],  # optional - absence means no subscription services
                receiving_inbox_services=[inbox_service2])  # Optional - absence indicates no receiving inbox services

        self.collection4 = tm11.CollectionInformation(
                collection_name='collection4',  # Required
                collection_description='So improve information. Much amaze.',  # Required
                supported_contents=[tm11.ContentBinding(t.CB_STIX_XML_101, subtype_ids=['ex1', 'ex2', 'ex3'])],  # Optional
                receiving_inbox_services=[inbox_service1, inbox_service2])  # Optional - absence indicates no receiving inbox services

    def test_collection_information_response_01(self):
        collection_response1 = tm11.CollectionInformationResponse(
                message_id='CIR01',  # Required
                in_response_to='0',  # Required - should be the ID of the message tha this message is a response to
                collection_informations=[self.collection1])  # Optional - absence means "no collections"
        round_trip_message(collection_response1)

    def test_collection_information_response_02(self):
        collection_response2 = tm11.CollectionInformationResponse(
                message_id='CIR02',  # Required
                in_response_to='0',  # Required - should be the ID of the message tha this message is a response to
                collection_informations=[self.collection1, self.collection2, self.collection3, self.collection4])  # Optional - absence means "no collections"
        round_trip_message(collection_response2)

    def test_collection_information_response_03(self):
        collection_response3 = tm11.CollectionInformationResponse(
                message_id='CIR03',  # Required
                in_response_to='0')  # Required - should be the ID of the message tha this message is a response to
        round_trip_message(collection_response3)

    def test_collection_information_response_04(self):
        collection_response4 = tm11.CollectionInformationResponse(
                message_id='CIR04',  # Required
                in_response_to='0',  # Required - should be the ID of the message tha this message is a response to
                collection_informations=[self.collection1, self.collection4])  # Optional - absence means "no collections"
        round_trip_message(collection_response4)

    def test_collection_information_response_05(self):
        collection_response5 = tm11.CollectionInformationResponse(
                message_id='CIR05',  # Required
                in_response_to='0',  # Required - should be the ID of the message tha this message is a response to
                collection_informations=[self.collection2, self.collection4])  # Optional - absence means "no collections"
        round_trip_message(collection_response5)

    def test_collection_information_response_deprecated(self):
        # Test deprecated nested forms:
        #   CollectionInformationResponse.CollectionInformation
        #   CollectionInformationResponse.CollectionInformation.PushMethod
        #   CollectionInformationResponse.CollectionInformation.PollingServiceInstance
        #   CollectionInformationResponse.CollectionInformation.SubscriptionMethod
        #   CollectionInformationResponse.CollectionInformation.ReceivingInboxService
        push_method = tm11.CollectionInformationResponse.CollectionInformation.PushMethod(
                push_protocol=t.VID_TAXII_HTTP_10,
                push_message_bindings=[t.VID_TAXII_XML_11])

        poll_service = tm11.CollectionInformationResponse.CollectionInformation.PollingServiceInstance(
                poll_protocol=t.VID_TAXII_HTTPS_10,
                poll_address='https://example.com/TheGreatestPollService',
                poll_message_bindings=[t.VID_TAXII_XML_11])

        subs_method = tm11.CollectionInformationResponse.CollectionInformation.SubscriptionMethod(
                subscription_protocol=t.VID_TAXII_HTTPS_10,
                subscription_address='https://example.com/TheSubscriptionService/',
                subscription_message_bindings=[t.VID_TAXII_XML_11])

        inbox_service = tm11.CollectionInformationResponse.CollectionInformation.ReceivingInboxService(
                inbox_protocol=t.VID_TAXII_HTTPS_10,
                inbox_address='https://example.com/inbox/',
                inbox_message_bindings=[t.VID_TAXII_XML_11])

        collection = tm11.CollectionInformationResponse.CollectionInformation(
                collection_name='collection1',
                collection_description='This is a collection',
                push_methods=[push_method],
                polling_service_instances=[poll_service],
                subscription_methods=[subs_method],
                receiving_inbox_services=[inbox_service])

        response = tm11.CollectionInformationResponse(
                message_id='CIR05',
                in_response_to='0',
                collection_informations=[collection])

        round_trip_message(response)


class ManageCollectionSubscriptionRequestTests(unittest.TestCase):

    def test_subs_req1(self):
        subs_req1 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq01',  # Required
                action=tm11.ACT_SUBSCRIBE,  # Required
                collection_name='collection1',  # Required
                # subscription_id = None, #Prohibited for action = SUBSCRIBE
                subscription_parameters=subscription_parameters1,  # optional - absence means there are not any subscription parameters
                push_parameters=push_parameters1)  # Optional - absence means push messaging not requested
        round_trip_message(subs_req1)

    def test_subs_req2(self):
        subscription_parameters2 = tm11.SubscriptionParameters(
            response_type=tm11.RT_FULL,  # Optional, defaults to FULL
            # content_bindings = [tm11.ContentBinding(t.CB_STIX_XML_11)],#Optional. Absence means no restrictions on returned data
            query=query2)  # Optional. Absence means no query
        subs_req2 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq02',  # Required
                action=tm11.ACT_SUBSCRIBE,  # Required
                collection_name='collection2',  # Required
                # subscription_id = None, #Prohibited for action = SUBSCRIBE
                subscription_parameters=subscription_parameters2)  # optional - absence means there are not any subscription parameters
                # delivery_parameters = None)#Optional - absence means push messaging not requested
        round_trip_message(subs_req2)

    def test_subs_req3(self):
        subscription_parameters3 = tm11.SubscriptionParameters()  # Use all the defaults
        subs_req3 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq03',  # Required
                action=tm11.ACT_SUBSCRIBE,  # Required
                collection_name='collection213',  # Required
                # subscription_id = None, #Prohibited for action = SUBSCRIBE
                subscription_parameters=subscription_parameters3)  # optional - absence means there are not any subscription parameters
                # delivery_parameters = None)#Optional - absence means push messaging not requested
        round_trip_message(subs_req3)

    def test_subs_req4(self):
        subs_req4 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq04',  # Required
                action=tm11.ACT_SUBSCRIBE,  # Required
                collection_name='collection2')  # Required
                # subscription_id = None, #Prohibited for action = SUBSCRIBE
                # subscription_parameters = subscription_parameters2,#optional - absence means there are not any subscription parameters
                # delivery_parameters = None)#Optional - absence means push messaging not requested
        round_trip_message(subs_req4)

    def test_subs_req5(self):
        subs_req5 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq05',  # Required
                action=tm11.ACT_STATUS,  # Required
                collection_name='collection2',  # Required
                subscription_id='id1')  # Optional for ACT_STATUS
                # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
        round_trip_message(subs_req5)

    def test_subs_req6(self):
        subs_req6 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq06',  # Required
                action=tm11.ACT_STATUS,  # Required
                collection_name='collection2')  # Required
                # subscription_id = 'id1') #Optional for ACT_STATUS
                # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
        round_trip_message(subs_req6)

    def test_subs_req7(self):
        subs_req7 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq07',  # Required
                action=tm11.ACT_PAUSE,  # Required
                collection_name='collection2',  # Required
                subscription_id='id1')  # Optional for ACT_STATUS
                # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
        round_trip_message(subs_req7)

    def test_subs_req8(self):
        subs_req8 = tm11.ManageCollectionSubscriptionRequest(
                message_id='SubsReq08',  # Required
                action=tm11.ACT_RESUME,  # Required
                collection_name='collection2',  # Required
                subscription_id='id1')  # Optional for ACT_STATUS
                # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE
        round_trip_message(subs_req8)


class ManageCollectionSubscriptionResponseTests(unittest.TestCase):

    def setUp(self):
        poll_instance1 = tm11.PollInstance(
                            poll_protocol=t.VID_TAXII_HTTPS_10,
                            poll_address='https://example.com/poll1/',
                            poll_message_bindings=[t.VID_TAXII_XML_11])

        poll_instance2 = tm11.PollInstance(
                            poll_protocol=t.VID_TAXII_HTTPS_10,
                            poll_address='https://example.com/poll2/',
                            poll_message_bindings=[t.VID_TAXII_XML_11])
        poll_instance3 = tm11.PollInstance(
                            poll_protocol=t.VID_TAXII_HTTPS_10,
                            poll_address='https://example.com/poll3/',
                            poll_message_bindings=[t.VID_TAXII_XML_11])

        self.subs1 = tm11.SubscriptionInstance(
                    status=tm11.SS_ACTIVE,  # Optional, defaults to ACTIVE
                    subscription_id='Subs001',  # Required
                    subscription_parameters=subscription_parameters1,  # Optional - should be an echo of the request
                    push_parameters=push_parameters1,  # Optional - should be an echo of the request
                    poll_instances=[poll_instance1, poll_instance2, poll_instance3],  # Optional
        )

    def test_subs_resp1(self):
        subs2 = tm11.SubscriptionInstance(
                status=tm11.SS_PAUSED,  # Optional, defaults to ACTIVE
                subscription_id='Subs001',  # Required
                subscription_parameters=subscription_parameters1,  # Optional - should be an echo of the request
                push_parameters=push_parameters1,  # Optional - should be an echo of the request
                # poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
        )
        subs3 = tm11.SubscriptionInstance(
                status=tm11.SS_PAUSED,  # Optional, defaults to ACTIVE
                subscription_id='Subs001',  # Required
                # subscription_parameters = subscription_parameters1,#Optional - should be an echo of the request
                # push_parameters = delivery_parameters1,#Optional - should be an echo of the request
                # poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
        )
        subs_resp1 = tm11.ManageCollectionSubscriptionResponse(
                message_id='SubsResp01',  # Required
                in_response_to='xyz',  # Required - should be the ID of the message that this is a response to
                collection_name='abc123',  # Required
                message='Hullo!',  # Optional
                subscription_instances=[self.subs1, subs2, subs3],  # Optional
        )
        round_trip_message(subs_resp1)

    def test_subs_resp2(self):
        subs_resp2 = tm11.ManageCollectionSubscriptionResponse(
                message_id='SubsResp02',  # Required
                in_response_to='xyz',  # Required - should be the ID of the message that this is a response to
                collection_name='abc123',  # Required
                # message = 'Hullo!', #Optional
                # subscription_instances = [subs1, subs2, subs3],#Optional
        )
        round_trip_message(subs_resp2)

    def test_subs_resp3(self):
        subs_resp3 = tm11.ManageCollectionSubscriptionResponse(
                message_id='SubsResp03',  # Required
                in_response_to='xyz',  # Required - should be the ID of the message that this is a response to
                collection_name='abc123',  # Required
                # message = 'Hullo!', #Optional
                subscription_instances=[self.subs1],  # Optional
        )
        round_trip_message(subs_resp3)

    def test_subs_resp4(self):
        subs_resp4 = tm11.ManageCollectionSubscriptionResponse(
                message_id='SubsResp04',  # Required
                in_response_to='xyz',  # Required - should be the ID of the message that this is a response to
                collection_name='abc123',  # Required
                message='Hullo!',  # Optional
                # subscription_instances = [subs1, subs2, subs3],#Optional
        )
        round_trip_message(subs_resp4)

    def test_subs_resp_deprecated(self):
        # Test deprecated nested forms:
        #   ManageCollectionSubscriptionResponse.PollInstance
        #   ManageCollectionSubscriptionResponse.SubscriptionInstance
        poll = tm11.ManageCollectionSubscriptionResponse.PollInstance(
                poll_protocol=t.VID_TAXII_HTTPS_10,
                poll_address='https://example.com/poll1/',
                poll_message_bindings=[t.VID_TAXII_XML_11])

        subscription = tm11.ManageCollectionSubscriptionResponse.SubscriptionInstance(
                    subscription_id='Subs001',
                    subscription_parameters=subscription_parameters1,
                    push_parameters=push_parameters1,
                    poll_instances=[poll])

        subs_resp = tm11.ManageCollectionSubscriptionResponse(
                message_id='SubsResp01',
                in_response_to='xyz',
                collection_name='abc123',
                subscription_instances=[subscription])

        round_trip_message(subs_resp)


class PollRequestTests(unittest.TestCase):

    def test_poll_req1(self):
        poll_req1 = tm11.PollRequest(
                message_id='PollReq01',  # Required
                collection_name='collection100',  # Required
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                subscription_id='12345',  # Optional - one of this or poll_parameters MUST be present.
                poll_parameters=None)  # Optional - one of this or subscription_id MUST be present
        round_trip_message(poll_req1)

    def test_poll_req2(self):
        poll_req2 = tm11.PollRequest(
                message_id='PollReq02',  # Required
                collection_name='collection100',  # Required
                subscription_id='Kenneth Coal Collection',  # Optional - one of this or poll_parameters MUST be present.
                poll_parameters=None)  # Optional - one of this or subscription_id MUST be present
        round_trip_message(poll_req2)

    def test_poll_req3(self):
        delivery_parameters1 = tm11.DeliveryParameters(
            inbox_protocol=t.VID_TAXII_HTTPS_10,  # Required
            inbox_address='https://example.com/inboxAddress/',  # Required
            delivery_message_binding=t.VID_TAXII_XML_11)  # Required

        poll_params1 = tm11.PollParameters(
                        allow_asynch=False,  # Optional, defaults to False
                        response_type=tm11.RT_COUNT_ONLY,  # Optional, defaults to RT_FULL
                        content_bindings=[tm11.ContentBinding(binding_id=t.CB_STIX_XML_11)],  # Optional, defaults to None, which means "all bindings are accepted in response"
                        query=query1,  # Optional - defaults to None
                        delivery_parameters=delivery_parameters1)  # Optional - defaults to None

        poll_req3 = tm11.PollRequest(
                message_id='PollReq03',  # Required
                collection_name='collection100',  # Required
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                poll_parameters=poll_params1)  # Optional - one of this or subscription_id MUST be present
        round_trip_message(poll_req3)

    def test_poll_req4(self):
        poll_params2 = tm11.PollParameters()
        poll_req4 = tm11.PollRequest(
                message_id='PollReq04',  # Required
                collection_name='collection100',  # Required
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                poll_parameters=poll_params2)  # Optional - one of this or subscription_id MUST be present
        round_trip_message(poll_req4)

    def test_poll_req5(self):
        poll_params3 = tm11.PollParameters(query=query1)  # Optional - defaults to None)#Optional - defaults to None
        poll_req5 = tm11.PollRequest(
                message_id='PollReq05',  # Required
                collection_name='collection100',  # Required
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for a Data Feed, prohibited for a Data Set
                poll_parameters=poll_params3)  # Optional - one of this or subscription_id MUST be present
        round_trip_message(poll_req5)

    def test_poll_req_deprecated(self):
        # Test deprecated nested form:
        #   PollRequest.PollParameters
        params = tm11.PollRequest.PollParameters()
        poll = tm11.PollRequest(
                message_id='PollReq05',
                collection_name='collection100',
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
                poll_parameters=params)
        round_trip_message(poll)


class PollResponseTests(unittest.TestCase):

    def test_poll_resp1(self):
        poll_resp1 = tm11.PollResponse(
                message_id='PollResp1',  # Required
                in_response_to='tmp',  # Required. Must be the message that this is a response to
                collection_name='blah',  # Required
                more=True,  # Optional - defaults to false
                result_id='123',  # Optional
                result_part_number=1,  # optional
                subscription_id='24',  # optional
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for data feeds, prohibited for data sets
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # required for data feeds, prohibited for data sets
                record_count=tm11.RecordCount(record_count=22, partial_count=False),
                message='Woooooooo',  # optional
                content_blocks=[])  # optional
        round_trip_message(poll_resp1)

    def test_poll_resp2(self):
        poll_resp2 = tm11.PollResponse(
                message_id='PollResp2',  # Required
                in_response_to='tmp',  # Required. Must be the message that this is a response to
                collection_name='blah')  # Required
        round_trip_message(poll_resp2)

    def test_poll_resp3(self):
        poll_resp3 = tm11.PollResponse(
                message_id='PollResp3',  # Required
                in_response_to='tmp',  # Required. Must be the message that this is a response to
                collection_name='blah',  # Required
                result_id='123',  # Optional
                subscription_id='24',  # optional
                record_count=tm11.RecordCount(record_count=22),
                content_blocks=[])  # optional
        round_trip_message(poll_resp3)

    def test_poll_resp4(self):
        poll_resp4 = tm11.PollResponse(
                message_id='PollResp4',  # Required
                in_response_to='tmp',  # Required. Must be the message that this is a response to
                collection_name='blah',  # Required
                # content_blocks = [cb001, cb002])#optional
                content_blocks=[])  # optional
        round_trip_message(poll_resp4)


class InboxMessageTests(unittest.TestCase):

    def test_inbox1(self):
        subs_info1 = tm11.SubscriptionInformation(
                collection_name='SomeCollectionName',  # Required
                subscription_id='SubsId021',  # Required
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional for data feeds, prohibited for data sets
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))  # Optional for data feeds, prohibited for data sets
        inbox1 = tm11.InboxMessage(
                message_id='Inbox1',  # Required
                result_id='123',  # Optional
                destination_collection_names=['collection1', 'collection2'],  # Optional
                message='Hello!',  # Optional
                subscription_information=subs_info1,  # Optional
                record_count=tm11.RecordCount(22, partial_count=True),  # Optional
                content_blocks=[cb001, cb002])
        round_trip_message(inbox1)

    def test_inbox2(self):
        inbox2 = tm11.InboxMessage(message_id='Inbox1')  # Required
        round_trip_message(inbox2)

    def test_inbox3(self):
        subs_info2 = tm11.SubscriptionInformation(
                collection_name='SomeCollectionName',  # Required
                subscription_id='SubsId021')  # Required

        inbox3 = tm11.InboxMessage(
                message_id='Inbox3',  # Required
                result_id='123',  # Optional
                destination_collection_names=['collection1', 'collection2'],  # Optional
                subscription_information=subs_info2,  # Optional
                content_blocks=[cb002])
        round_trip_message(inbox3)

    def test_inbox_deprecated(self):
        # Test deprecated nested form:
        #   InboxMessage.SubscriptionInformation
        subscription = tm11.InboxMessage.SubscriptionInformation(
                collection_name='SomeCollectionName',
                subscription_id='SubsId021')

        inbox = tm11.InboxMessage(
                message_id='InboxMsg0001',
                subscription_information=subscription,
                content_blocks=[cb002])
        round_trip_message(inbox)


class PollFulfillmentTests(unittest.TestCase):

    def test_poll_fulfillment1(self):
        pf1 = tm11.PollFulfillmentRequest(
                message_id='pf1',  # required
                collection_name='1-800-collection',  # required
                result_id='123',  # required
                result_part_number=1)  # required

        round_trip_message(pf1)


class ContentBlockTests(unittest.TestCase):

    def test_content_block01(self):
        cb1 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                            content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')
        round_trip_content_block(cb1)

    def test_content_block02(self):
        cb2 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                            content=StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
        round_trip_content_block(cb2)

    def test_content_block03(self):
        cb3 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                            content=etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')))
        round_trip_content_block(cb3)

    def test_content_block04(self):
        cb4 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                            content='<Something thats not XML')
        round_trip_content_block(cb4)

    def test_content_block05(self):
        cb5 = tm11.ContentBlock(content_binding=tm11.ContentBinding(t.CB_STIX_XML_10),
                            content='Something thats not XML <xml/>')
        round_trip_content_block(cb5)

    def test_content_block06(self):
        cb6 = tm11.ContentBlock(content_binding='RandomUnicodeString', content=unicode('abcdef'))
        round_trip_content_block(cb6)


if __name__ == "__main__":
    unittest.main()
