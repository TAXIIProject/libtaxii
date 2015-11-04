

# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# This file has two purposes:
# 1. To provide a rough unit test of libtaxii.messages
# 2. To provide examples of how to use libtaxii.messages

# Contributors:
# * Mark Davidson - mdavidson@mitre.org

import datetime
import io
import sys
import unittest
import warnings
import inspect

from dateutil.tz import tzutc
from lxml import etree

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
from libtaxii.validation import SchemaValidator
from libtaxii.constants import *
from libtaxii.common import *
import six

import sys

# TODO: This is bad practice. Refactor this.
# Set up some things used across multiple tests.

full_stix_doc = """<stix:STIX_Package
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:cybox="http://cybox.mitre.org/cybox-2"
    xmlns:DomainNameObj="http://cybox.mitre.org/objects#DomainNameObject-1"
    xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
    xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
    xmlns:example="http://example.com/"
    xsi:schemaLocation=
    "http://stix.mitre.org/stix-1 ../stix_core.xsd
    http://stix.mitre.org/Indicator-2 ../indicator.xsd
    http://cybox.mitre.org/default_vocabularies-2 ../cybox/cybox_default_vocabularies.xsd
    http://stix.mitre.org/default_vocabularies-1 ../stix_default_vocabularies.xsd
    http://cybox.mitre.org/objects#DomainNameObject-1 ../cybox/objects/Domain_Name_Object.xsd"
    id="example:STIXPackage-f61cd874-494d-4194-a3e6-6b487dbb6d6e"
    timestamp="2014-05-08T09:00:00.000000Z"
    version="1.1.1"
    >
    <stix:STIX_Header>
        <stix:Title>Example watchlist that contains domain information.</stix:Title>
        <stix:Package_Intent xsi:type="stixVocabs:PackageIntentVocab-1.0">Indicators - Watchlist</stix:Package_Intent>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator xsi:type="indicator:IndicatorType" id="example:Indicator-2e20c5b2-56fa-46cd-9662-8f199c69d2c9" timestamp="2014-05-08T09:00:00.000000Z">
            <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">Domain Watchlist</indicator:Type>
            <indicator:Description>Sample domain Indicator for this watchlist</indicator:Description>
            <indicator:Observable id="example:Observable-87c9a5bb-d005-4b3e-8081-99f720fad62b">
                <cybox:Object id="example:Object-12c760ba-cd2c-4f5d-a37d-18212eac7928">
                    <cybox:Properties xsi:type="DomainNameObj:DomainNameObjectType" type="FQDN">
                        <DomainNameObj:Value condition="Equals" apply_condition="ANY">malicious1.example.com##comma##malicious2.example.com##comma##malicious3.example.com</DomainNameObj:Value>
                    </cybox:Properties>
                </cybox:Object>
            </indicator:Observable>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>"""

xml_taxii_message_11 = '<taxii_11:Discovery_Request xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" message_id="1"/>'
json_taxii_message_11 = '{"extended_headers": {}, "message_type": "Discovery_Request", "message_id": "1"}'

# Note that the "*_old" tests are just to make sure that backward-compatible aliases exist
test1 = tdq.Test(capability_id=CM_CORE,  # Required
                 relationship='equals',  # Required
                 parameters={'value': 'Test value',
                             'match_type': 'case_sensitive_string'}  # Each relationship defines which params are and are not required
                 )

test1_old = tdq.DefaultQuery.Criterion.Test(capability_id=CM_CORE,  # Required
                                            relationship='equals',  # Required
                                            parameters={'value': 'Test value',
                                                        'match_type': 'case_sensitive_string'}  # Each relationship defines which params are and are not required
                                            )

test2 = tdq.Test(capability_id=CM_REGEX,  # Required
                 relationship='matches',  # Required
                 parameters={'value': '[A-Z]*',
                             'case_sensitive': True})  # Each relationship defines which params are and are not required

test2_old = tdq.DefaultQuery.Criterion.Test(capability_id=CM_REGEX,  # Required
                                            relationship='matches',  # Required
                                            parameters={'value': '[A-Z]*',
                                                        'case_sensitive': True})  # Each relationship defines which params are and are not required

test3 = tdq.Test(capability_id=CM_TIMESTAMP,  # Required
                 relationship='greater_than',  # Required
                 parameters={'value': datetime.datetime.now()})  # Each relationship defines which params are and are not required

test3_old = tdq.DefaultQuery.Criterion.Test(capability_id=CM_TIMESTAMP,  # Required
                                            relationship='greater_than',  # Required
                                            parameters={'value': datetime.datetime.now()})  # Each relationship defines which params are and are not required

criterion1 = tdq.Criterion(target='**', test=test1)
criterion2 = tdq.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
criterion3 = tdq.Criterion(target='**/Description', test=test3)

criterion1_old = tdq.DefaultQuery.Criterion(target='**', test=test1)
criterion2_old = tdq.DefaultQuery.Criterion(target='STIX_Package/Indicators/Indicator/@id', test=test2)
criterion3_old = tdq.DefaultQuery.Criterion(target='**/Description', test=test3)

criteria1 = tdq.Criteria(operator=OP_AND, criterion=[criterion1])
criteria2 = tdq.Criteria(operator=OP_OR, criterion=[criterion1, criterion2, criterion3])
criteria3 = tdq.Criteria(operator=OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

criteria1_old = tdq.DefaultQuery.Criteria(operator=OP_AND, criterion=[criterion1])
criteria2_old = tdq.DefaultQuery.Criteria(operator=OP_OR, criterion=[criterion1, criterion2, criterion3])
criteria3_old = tdq.DefaultQuery.Criteria(operator=OP_AND, criterion=[criterion1, criterion3], criteria=[criteria2])

query1 = tdq.DefaultQuery(CB_STIX_XML_11, criteria1)
query2 = tdq.DefaultQuery(CB_STIX_XML_11, criteria3)

subscription_parameters1 = tm11.SubscriptionParameters(
    response_type=RT_COUNT_ONLY,  # Optional, defaults to FULL
    content_bindings=[tm11.ContentBinding(CB_STIX_XML_11)],  # Optional. Absence means no restrictions on returned data
    query=query1)  # Optional. Absence means no query

push_parameters1 = tm11.PushParameters(
    inbox_protocol=VID_TAXII_HTTPS_10,  # Required
    inbox_address='https://example.com/inboxAddress/',  # Required
    delivery_message_binding=VID_TAXII_XML_11)  # Required

cb001 = tm11.ContentBlock(
    content_binding=tm11.ContentBinding(CB_STIX_XML_11, subtype_ids=['test1']),  # Required
    content='<STIX_Package/>',  # Required (This isn't real STIX)
    timestamp_label=datetime.datetime.now(tzutc()),  # Optional
    message='Hullo!',  # Optional
    padding='The quick brown fox jumped over the lazy dogs.')  # Optional

cb002 = tm11.ContentBlock(
    content_binding=tm11.ContentBinding(CB_STIX_XML_11),  # Required
    content=full_stix_doc)  # Required


def round_trip_message(taxii_message, print_xml=False):
    if not isinstance(taxii_message, tm11.TAXIIMessage):
        raise ValueError('taxii_message was not an instance of TAXIIMessage')

    # print '***** Message type = %s; id = %s' % (taxii_message.message_type, taxii_message.message_id)

    xml_string = taxii_message.to_xml()

    # The old way of validating
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        valid = tm11.validate_xml(xml_string)
    if valid is not True:
        print('Bad XML was:')
        try:
            print(etree.tostring(taxii_message.to_etree(), pretty_print=True))
        except Exception as e:
            print(xml_string)
        raise Exception('\tFailure of test #1 - XML not schema valid: %s' % valid)

    # The new way of validating
    sv = SchemaValidator(SchemaValidator.TAXII_11_SCHEMA)
    try:
        result = sv.validate_string(xml_string)
    except XMLSyntaxError:
        raise

    if not result.valid:
        errors = [item for item in result.error_log]
        raise Exception('\tFailure of test #1 - XML not schema valid: %s' % errors)

    if print_xml:
        print(etree.tostring(taxii_message.to_etree(), pretty_print=True))

    msg_from_xml = tm11.get_message_from_xml(xml_string)
    dictionary = taxii_message.to_dict()
    msg_from_dict = tm11.get_message_from_dict(dictionary)
    taxii_message.to_text()  # to_text() returns a string, this just makes sure the call succeeds but doesn't validate the response
    if taxii_message != msg_from_xml:
        print('\t Failure of test #2 - running equals w/ debug:')
        taxii_message.__eq__(msg_from_xml, True)
        raise Exception('Test #2 failed - taxii_message != msg_from_xml')

    if taxii_message != msg_from_dict:
        print('\t Failure of test #3 - running equals w/ debug:')
        taxii_message.__eq__(msg_from_dict, True)
        raise Exception('Test #3 failed - taxii_message != msg_from_dict')

    if msg_from_xml != msg_from_dict:
        print('\t Failure of test #4 - running equals w/ debug:')
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
        print('\t Failure of test #1 - running equals w/ debug:')
        content_block.__eq__(block_from_xml, True)
        raise Exception('Test #1 failed - content_block != block_from_xml')

    if content_block != block_from_dict:
        print('\t Failure of test #2 - running equals w/ debug:')
        content_block.__eq__(block_from_dict, True)
        raise Exception('Test #2 failed - content_block != block_from_dict')

    if block_from_xml != block_from_dict:
        print('\t Failure of test #3 - running equals w/ debug:')
        block_from_xml.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_xml != block_from_dict')
    if block_from_json != block_from_dict:
        print('\t Failure of test #3 - running equals w/ debug:')
        block_from_json.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_json != block_from_dict')

    # print '***** All tests completed!'


class GenericParametersTests(unittest.TestCase):

    # https://github.com/TAXIIProject/libtaxii/issues/165
    def test_typo_165(self):
        # Explicitly set `response_type` to None.
        sub_params = tm11.SubscriptionParameters(response_type=None)
        params_xml = sub_params.to_xml()

        # When parsing from XML, if no response_type is provided, it should be
        # set to RT_FULL.
        new_params = tm11.SubscriptionParameters.from_xml(params_xml)
        self.assertEqual(RT_FULL, new_params.response_type)


class StatusMessageTests(unittest.TestCase):

    def test_status_message_01(self):
        sm01 = tm11.StatusMessage(
            message_id='SM01',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_SUCCESS,  # Required
            status_detail={'custom_status_detail_name': 'Custom status detail value',
                           'Custom_detail_2': ['this one has', 'multiple values']},  # Required depending on Status Type. See spec for details
            message='This is a test message'  # Optional
        )
        round_trip_message(sm01)

    def test_status_message_02(self):
        sm02 = tm11.StatusMessage(
            message_id='SM02',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_SUCCESS,  # Required
            status_detail=None,  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm02)

    def test_status_message_03(self):
        sm03 = tm11.StatusMessage(
            message_id='SM03',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_DESTINATION_COLLECTION_ERROR,  # Required
            status_detail={'ACCEPTABLE_DESTINATION': ['Collection1', 'Collection2']},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm03)

    def test_status_message_04(self):
        sm04 = tm11.StatusMessage(
            message_id='SM04',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_INVALID_RESPONSE_PART,  # Required
            status_detail={'MAX_PART_NUMBER': 4},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm04)

    def test_status_message_05(self):
        sm05 = tm11.StatusMessage(
            message_id='SM05',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_NOT_FOUND,  # Required
            status_detail={'ITEM': 'Collection1'},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm05)

    def test_status_message_06(self):
        sm06 = tm11.StatusMessage(
            message_id='SM06',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_PENDING,  # Required
            status_detail={'ESTIMATED_WAIT': 900, 'RESULT_ID': 'Result1', 'WILL_PUSH': False},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm06)

    def test_status_message_07(self):
        sm07 = tm11.StatusMessage(
            message_id='SM07',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_RETRY,  # Required
            status_detail={'ESTIMATED_WAIT': 900},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm07)

    def test_status_message_08(self):
        sm08 = tm11.StatusMessage(
            message_id='SM08',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_UNSUPPORTED_MESSAGE_BINDING,  # Required
            status_detail={'SUPPORTED_BINDING': [VID_TAXII_XML_10, VID_TAXII_XML_11]},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm08)

    def test_status_message_09(self):
        sm09 = tm11.StatusMessage(
            message_id='SM09',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_UNSUPPORTED_CONTENT_BINDING,  # Required
            status_detail={'SUPPORTED_CONTENT': tm11.ContentBinding(binding_id=CB_STIX_XML_101, subtype_ids=['subtype1', 'subtype2'])},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm09)

    def test_status_message_10(self):
        sm09 = tm11.StatusMessage(
            message_id='SM10',  # Required
            in_response_to=tm11.generate_message_id(),  # Required, should be the ID of the message that this is in response to
            status_type=ST_UNSUPPORTED_CONTENT_BINDING,  # Required
            status_detail={'SUPPORTED_CONTENT': [tm11.ContentBinding(binding_id=CB_STIX_XML_101, subtype_ids=['subtype1', 'subtype2']), tm11.ContentBinding(binding_id=CB_STIX_XML_11)]},  # Required/optional depending on Status Type. See spec for details
            message=None  # Optional
        )
        round_trip_message(sm09)

    def test_status_message_11(self):
        # Per https://github.com/TAXIIProject/libtaxii/issues/111
        kwargs = {'message_id': '1', 'in_response_to': '2', 'status_type': ST_FAILURE, 'message': {}}
        self.assertRaises(ValueError, tm11.StatusMessage, **kwargs)

    # TODO: TEst the query status types

    def test_xml_ext_header(self):
        """
        Tests an XML extended header value of etree._Element

        :return:
        """

        eh = {'my_ext_header_1': parse('<x:element xmlns:x="#foo">'
                                       '<x:subelement attribute="something"/>'
                                       '</x:element>')}

        sm = tm11.StatusMessage(message_id='1',
                                in_response_to='2',
                                status_type=ST_SUCCESS,
                                extended_headers=eh)
        round_trip_message(sm)

    def test_xml_ext_header2(self):
        """
        Tests an XML extended header value of etree._Element

        :return:
        """

        eh = {'my_ext_header_1': parse('<x:element xmlns:x="#foo">'
                                       '<x:subelement attribute="something"/>'
                                       '</x:element>')}

        sm = tm11.StatusMessage(message_id='1',
                                in_response_to='2',
                                status_type=ST_SUCCESS,
                                extended_headers=eh)
        round_trip_message(sm)
        # print etree.tostring(etree.XML(sm.to_xml(pretty_print=True)), pretty_print=True)

    def test_xml_ext_header3(self):
        """
        Tests an XML extended header value of string

        :return:
        """

        eh = {'my_ext_header_1': '<x:element xmlns:x="#foo">'
                                 '<x:subelement attribute="something"/>'
                                 '</x:element>'}

        sm = tm11.StatusMessage(message_id='1',
                                in_response_to='2',
                                status_type=ST_SUCCESS,
                                extended_headers=eh)
        round_trip_message(sm)
        # print etree.tostring(etree.XML(sm.to_xml(pretty_print=True)), pretty_print=True)


class DiscoveryRequestTests(unittest.TestCase):

    def test_discovery_request(self):
        discovery_request1 = tm11.DiscoveryRequest(
            message_id=tm11.generate_message_id(),  # Required
            # Extended headers are optional for every message type, but demonstrated here
            extended_headers={'ext_header1': 'value1', 'ext_header2': 'value2'})  # Optional.
        round_trip_message(discovery_request1)


class DiscoveryResponseTests(unittest.TestCase):

    def setUp(self):
        # Create query information to use in the ServiceInstances
        tei_01 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
            targeting_expression_id=CB_STIX_XML_10,  # Required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
            preferred_scope=[],  # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
            allowed_scope=['**'])  # This example has no preferred scope, and allows any scope

        tei_02 = tdq.DefaultQueryInfo.TargetingExpressionInfo(
            targeting_expression_id=CB_STIX_XML_11,  # required. Indicates a supported targeting vocabulary (in this case STIX 1.1)
            preferred_scope=['STIX_Package/Indicators/Indicator/**'],  # At least one of Preferred/Allowed must be present. Indicates Preferred and allowed search scope.
            allowed_scope=[])  # This example prefers the Indicator scope and allows no other scope

        tdq1 = tdq.DefaultQueryInfo(
            targeting_expression_infos=[tei_01, tei_02],  # Required, 1-n. Indicates what targeting expressions are supported
            capability_modules=[CM_CORE])  # Required, 1-n. Indicates which capability modules can be used.

        tdq2 = tdq.DefaultQueryInfo(
            targeting_expression_infos=[tei_02],  # Required, 1-n. Indicates what targeting expressions are supported
            capability_modules=[CM_REGEX])  # Required, 1-n. Indicates which capability modules can be used.

        # Create ServiceInstances to use in tests
        self.si1 = tm11.ServiceInstance(
            service_type=SVC_POLL,  # Required
            services_version=VID_TAXII_SERVICES_11,  # Required
            protocol_binding=VID_TAXII_HTTP_10,  # Required
            service_address='http://example.com/poll/',  # Required
            message_bindings=[VID_TAXII_XML_11],  # Required, must have at least one value in the list
            available=True,  # Optional - defaults to None, which means 'Unknown'
            message='This is a message.',
            supported_query=[tdq1])  # Optional for service_type=POLL

        self.si2 = tm11.ServiceInstance(
            service_type=SVC_POLL,  # Required
            services_version=VID_TAXII_SERVICES_11,  # Required
            protocol_binding=VID_TAXII_HTTP_10,  # Required
            service_address='http://example.com/poll/',  # Required
            message_bindings=[VID_TAXII_XML_11],  # Required, must have at least one value in the list
            available=True,  # Optional - defaults to None, which means 'Unknown'
            message='This is a message.',
            supported_query=[tdq1, tdq2])  # Optional for service_type=POLL

        self.si3 = tm11.ServiceInstance(
            service_type=SVC_INBOX,  # Required
            services_version=VID_TAXII_SERVICES_11,  # Required
            protocol_binding=VID_TAXII_HTTP_10,  # Required
            service_address='http://example.com/inbox/',  # Required
            message_bindings=[VID_TAXII_XML_11],  # Required, must have at least one value in the list
            inbox_service_accepted_content=[tm11.ContentBinding(CB_STIX_XML_11),
                                            tm11.ContentBinding(CB_STIX_XML_101),
                                            tm11.ContentBinding(CB_STIX_XML_10)],  # Optional. Defaults to "accepts all content"
            available=False,  # Optional - defaults to None, which means 'Unknown'
            message='This is a message. Yipee!')  # optional

        self.si4 = tm11.ServiceInstance(
            service_type=SVC_DISCOVERY,  # Required
            services_version=VID_TAXII_SERVICES_11,  # Required
            protocol_binding=VID_TAXII_HTTP_10,  # Required
            service_address='http://example.com/discovery/',  # Required
            message_bindings=[VID_TAXII_XML_11],  # Required, must have at least one value in the list
            message='This is a message. Yipee!')  # optional

        self.si5 = tm11.ServiceInstance(
            service_type=SVC_COLLECTION_MANAGEMENT,  # Required
            services_version=VID_TAXII_SERVICES_11,  # Required
            protocol_binding=VID_TAXII_HTTP_10,  # Required
            service_address='http://example.com/collection_management/',  # Required
            message_bindings=[VID_TAXII_XML_11],  # Required, must have at least one value in the list
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
            service_type=SVC_COLLECTION_MANAGEMENT,
            services_version=VID_TAXII_SERVICES_11,
            protocol_binding=VID_TAXII_HTTP_10,
            service_address='http://example.com/collection_management/',
            message_bindings=[VID_TAXII_XML_11])

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
            push_protocol=VID_TAXII_HTTP_10,  # Required
            push_message_bindings=[VID_TAXII_XML_11])  # Required

        # Instantiate Poll Services
        poll_service1 = tm11.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTPS_10,  # Required
            poll_address='https://example.com/TheGreatestPollService',  # Required
            poll_message_bindings=[VID_TAXII_XML_11])  # Required, at least one item must be present in the list

        poll_service2 = tm11.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTP_10,  # Required
            poll_address='http://example.com/TheOtherPollService',  # Required
            poll_message_bindings=[VID_TAXII_XML_11])  # Required, at least one item must be present in the list

        # Instantiate Subscription Methods
        subs_method1 = tm11.SubscriptionMethod(
            subscription_protocol=VID_TAXII_HTTPS_10,  # Required
            subscription_address='https://example.com/TheSubscriptionService/',  # Required
            subscription_message_bindings=[VID_TAXII_XML_11])  # Required - at least one item must be present in the list

        subs_method2 = tm11.SubscriptionMethod(
            subscription_protocol=VID_TAXII_HTTP_10,  # Required
            subscription_address='http://example.com/TheSubscriptionService/',  # Required
            subscription_message_bindings=[VID_TAXII_XML_11])  # Required - at least one item must be present in the list

        # Instantiate Inbox Services
        inbox_service1 = tm11.ReceivingInboxService(
            inbox_protocol=VID_TAXII_HTTPS_10,  # required
            inbox_address='https://example.com/inbox/',  # Required
            inbox_message_bindings=[VID_TAXII_XML_11],  # Required
            supported_contents=None)  # Optional - None means "all are supported"

        inbox_service2 = tm11.ReceivingInboxService(
            inbox_protocol=VID_TAXII_HTTPS_10,  # required
            inbox_address='https://example.com/inbox/',  # Required
            inbox_message_bindings=[VID_TAXII_XML_11],  # Required
            supported_contents=[tm11.ContentBinding(CB_STIX_XML_11, subtype_ids=['exmaple1', 'example2'])])  # Optional - None means "all are supported"

        # Instantiate collections
        self.collection1 = tm11.CollectionInformation(
            collection_name='collection1',  # Required
            collection_type=CT_DATA_FEED,  # Optional. Defaults to 'Data Feed'
            available=False,  # Optional. Defaults to None, which means "unknown"
            collection_description='This is a collection',  # Required
            collection_volume=4,  # Optional - indicates typical number of messages per day
            supported_contents=[tm11.ContentBinding(CB_STIX_XML_101)],  # Optional, absence indicates all content bindings
            push_methods=[push_method1],  # Optional - absence indicates no push methods
            polling_service_instances=[poll_service1, poll_service2],  # Optional - absence indicates no polling services
            subscription_methods=[subs_method1, subs_method2],  # optional - absence means no subscription services
            receiving_inbox_services=[inbox_service1, inbox_service2])  # Optional - absence indicates no receiving inbox services

        self.collection2 = tm11.CollectionInformation(
            collection_name='collection2',  # Required
            collection_type=CT_DATA_SET,  # Optional. Defaults to 'Data Feed'
            collection_description='Warrgghghglble.')  # Required

        self.collection3 = tm11.CollectionInformation(
            collection_name='collection3',  # Required
            collection_description='You must pay all the dollars to have this information.',  # Required
            supported_contents=[tm11.ContentBinding(CB_STIX_XML_10), tm11.ContentBinding(CB_STIX_XML_11)],  # Optional
            polling_service_instances=[poll_service2],  # Optional - absence indicates no polling services
            subscription_methods=[subs_method2],  # optional - absence means no subscription services
            receiving_inbox_services=[inbox_service2])  # Optional - absence indicates no receiving inbox services

        self.collection4 = tm11.CollectionInformation(
            collection_name='collection4',  # Required
            collection_description='So improve information. Much amaze.',  # Required
            supported_contents=[tm11.ContentBinding(CB_STIX_XML_101, subtype_ids=['ex1', 'ex2', 'ex3'])],  # Optional
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
            push_protocol=VID_TAXII_HTTP_10,
            push_message_bindings=[VID_TAXII_XML_11])

        poll_service = tm11.CollectionInformationResponse.CollectionInformation.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/TheGreatestPollService',
            poll_message_bindings=[VID_TAXII_XML_11])

        subs_method = tm11.CollectionInformationResponse.CollectionInformation.SubscriptionMethod(
            subscription_protocol=VID_TAXII_HTTPS_10,
            subscription_address='https://example.com/TheSubscriptionService/',
            subscription_message_bindings=[VID_TAXII_XML_11])

        inbox_service = tm11.CollectionInformationResponse.CollectionInformation.ReceivingInboxService(
            inbox_protocol=VID_TAXII_HTTPS_10,
            inbox_address='https://example.com/inbox/',
            inbox_message_bindings=[VID_TAXII_XML_11])

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
            action=ACT_SUBSCRIBE,  # Required
            collection_name='collection1',  # Required
            # subscription_id = None, #Prohibited for action = SUBSCRIBE
            subscription_parameters=subscription_parameters1,  # optional - absence means there are not any subscription parameters
            push_parameters=push_parameters1)  # Optional - absence means push messaging not requested
        round_trip_message(subs_req1)

    def test_subs_req2(self):
        subscription_parameters2 = tm11.SubscriptionParameters(
            response_type=RT_FULL,  # Optional, defaults to FULL
            # content_bindings = [tm11.ContentBinding(CB_STIX_XML_11)],#Optional. Absence means no restrictions on returned data
            query=query2)  # Optional. Absence means no query
        subs_req2 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq02',  # Required
            action=ACT_SUBSCRIBE,  # Required
            collection_name='collection2',  # Required
            # subscription_id = None, #Prohibited for action = SUBSCRIBE
            subscription_parameters=subscription_parameters2)  # optional - absence means there are not any subscription parameters
        # delivery_parameters = None)#Optional - absence means push messaging not requested

        round_trip_message(subs_req2)

    def test_subs_req3(self):
        subscription_parameters3 = tm11.SubscriptionParameters()  # Use all the defaults
        subs_req3 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq03',  # Required
            action=ACT_SUBSCRIBE,  # Required
            collection_name='collection213',  # Required
            # subscription_id = None, #Prohibited for action = SUBSCRIBE
            subscription_parameters=subscription_parameters3)  # optional - absence means there are not any subscription parameters
        # delivery_parameters = None)#Optional - absence means push messaging not requested

        round_trip_message(subs_req3)

    def test_subs_req4(self):
        subs_req4 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq04',  # Required
            action=ACT_SUBSCRIBE,  # Required
            collection_name='collection2')  # Required
        # subscription_id = None, #Prohibited for action = SUBSCRIBE
        # subscription_parameters = subscription_parameters2,#optional - absence means there are not any subscription parameters
        # delivery_parameters = None)#Optional - absence means push messaging not requested

        round_trip_message(subs_req4)

    def test_subs_req5(self):
        subs_req5 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq05',  # Required
            action=ACT_STATUS,  # Required
            collection_name='collection2',  # Required
            subscription_id='id1')  # Optional for ACT_STATUS
        # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE

        round_trip_message(subs_req5)

    def test_subs_req6(self):
        subs_req6 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq06',  # Required
            action=ACT_STATUS,  # Required
            collection_name='collection2')  # Required
        # subscription_id = 'id1') #Optional for ACT_STATUS
        # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE

        round_trip_message(subs_req6)

    def test_subs_req7(self):
        subs_req7 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq07',  # Required
            action=ACT_PAUSE,  # Required
            collection_name='collection2',  # Required
            subscription_id='id1')  # Optional for ACT_STATUS
        # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE

        round_trip_message(subs_req7)

    def test_subs_req8(self):
        subs_req8 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq08',  # Required
            action=ACT_RESUME,  # Required
            collection_name='collection2',  # Required
            subscription_id='id1')  # Optional for ACT_STATUS
        # subscription_parameters, delivery_parameters prohibited if action != SUBSCRIBE

        round_trip_message(subs_req8)


class ManageCollectionSubscriptionResponseTests(unittest.TestCase):

    def setUp(self):
        poll_instance1 = tm11.PollInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/poll1/',
            poll_message_bindings=[VID_TAXII_XML_11])

        poll_instance2 = tm11.PollInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/poll2/',
            poll_message_bindings=[VID_TAXII_XML_11])
        poll_instance3 = tm11.PollInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/poll3/',
            poll_message_bindings=[VID_TAXII_XML_11])

        self.subs1 = tm11.SubscriptionInstance(
            status=SS_ACTIVE,  # Optional, defaults to ACTIVE
            subscription_id='Subs001',  # Required
            subscription_parameters=subscription_parameters1,  # Optional - should be an echo of the request
            push_parameters=push_parameters1,  # Optional - should be an echo of the request
            poll_instances=[poll_instance1, poll_instance2, poll_instance3],  # Optional
        )

    def test_subs_resp1(self):
        subs2 = tm11.SubscriptionInstance(
            status=SS_PAUSED,  # Optional, defaults to ACTIVE
            subscription_id='Subs001',  # Required
            subscription_parameters=subscription_parameters1,  # Optional - should be an echo of the request
            push_parameters=push_parameters1,  # Optional - should be an echo of the request
            # poll_instances = [poll_instance1, poll_instance2, poll_instance3],#Optional
        )
        subs3 = tm11.SubscriptionInstance(
            status=SS_PAUSED,  # Optional, defaults to ACTIVE
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
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/poll1/',
            poll_message_bindings=[VID_TAXII_XML_11])

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
            inbox_protocol=VID_TAXII_HTTPS_10,  # Required
            inbox_address='https://example.com/inboxAddress/',  # Required
            delivery_message_binding=VID_TAXII_XML_11)  # Required

        poll_params1 = tm11.PollParameters(
            allow_asynch=False,  # Optional, defaults to False
            response_type=RT_COUNT_ONLY,  # Optional, defaults to RT_FULL
            content_bindings=[tm11.ContentBinding(binding_id=CB_STIX_XML_11)],  # Optional, defaults to None, which means "all bindings are accepted in response"
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

    def test_poll_resp5(self):
        poll_resp5 = tm11.PollResponse(
            message_id='PollResp5',
            in_response_to='blah',
            collection_name='foo',
            result_part_number=10,
            content_blocks=[])
        round_trip_message(poll_resp5)


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


class SubscriptionInformationTests(unittest.TestCase):

    # See https://github.com/TAXIIProject/libtaxii/issues/110
    def test_exclusive_begin_timestamp_label_must_be_datetime(self):
        params = {
            'collection_name': 'foo',
            'subscription_id': 'baz',
            'exclusive_begin_timestamp_label': '100'
        }
        self.assertRaises(ValueError, tm11.SubscriptionInformation, **params)

    # See https://github.com/TAXIIProject/libtaxii/issues/110
    def test_110_2(self):
        """
        Test for https://github.com/TAXIIProject/libtaxii/issues/110
        :return:
        """
        params = {
            'collection_name': 'foo',
            'subscription_id': 'baz',
            'inclusive_end_timestamp_label': '100'
        }
        self.assertRaises(ValueError, tm11.SubscriptionInformation, **params)


class ContentBlockTests(unittest.TestCase):

    def test_content_block01(self):
        cb1 = tm11.ContentBlock(content_binding=tm11.ContentBinding(CB_STIX_XML_10),
                                content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')
        round_trip_content_block(cb1)

    def test_content_block02(self):
        cb2 = tm11.ContentBlock(content_binding=tm11.ContentBinding(CB_STIX_XML_10),
                                content=six.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
        round_trip_content_block(cb2)

    def test_content_block03(self):
        cb3 = tm11.ContentBlock(content_binding=tm11.ContentBinding(CB_STIX_XML_10),
                                content=parse('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
        round_trip_content_block(cb3)

    def test_content_block04(self):
        cb4 = tm11.ContentBlock(content_binding=tm11.ContentBinding(CB_STIX_XML_10),
                                content='<Something thats not XML')
        round_trip_content_block(cb4)

    def test_content_block05(self):
        cb5 = tm11.ContentBlock(content_binding=tm11.ContentBinding(CB_STIX_XML_10),
                                content='Something thats not XML <xml/>')
        round_trip_content_block(cb5)

    def test_content_block06(self):
        cb6 = tm11.ContentBlock(content_binding='RandomUnicodeString', content=six.text_type('abcdef'))
        round_trip_content_block(cb6)

    def test_content_block07(self):
        cb7 = tm11.ContentBlock(content_binding='something',
                                content='something',
                                message='a message',
                                padding='the padding!')
        round_trip_content_block(cb7)


class TestXmlAttacks(unittest.TestCase):
    """
    List of XML attacks can be found here: https://pypi.python.org/pypi/defusedxml#python-xml-libraries
    Thanks to @guidovranken for pointing these out

    """

    def test_billion_laughs(self):
        """
        Tests a "safe" variant of the "billion laughs" attack on libtaxii
        http://en.wikipedia.org/wiki/Billion_laughs
        :return:
        """

        billion_laughs = """<!DOCTYPE lolz [
                             <!ENTITY lol "lol">
                             <!ELEMENT lolz (#PCDATA)>
                             <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
                             <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
                           ]>
                           <lolz>&lol1;</lolz>"""

        e = parse(billion_laughs)

        if e.text is not None:
            raise ValueError("The text of e was not None, meaning a real attack would have succeeded!")

    def test_guadratic_blowup(self):
        """
        Tests a "safe" variant of the quadratic blowup attack
        http://msdn.microsoft.com/en-us/magazine/ee335713.aspx
        :return:
        """
        q_blowup = """<!DOCTYPE kaboom [
                        <!ENTITY a "aaaaaaaaaaaaaaaaaaa">
                      ]>
                      <kaboom>&a;</kaboom>
                   """

        e = parse(q_blowup)

        if e.text is not None:
            raise ValueError('The text of e was not None, meaning a real attack would have succeeded!')

    def test_xee_remote(self):
        """
        Tests a "safe" variant of the remote XEE attack
        https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing
        :return:
        """

        xee_remote = """<!DOCTYPE foo [
                          <!ELEMENT foo ANY >
                          <!ENTITY xxe SYSTEM "http://www.mitre.org" >]>
                        <foo>&xxe;</foo>
                      """

        # If an XML Syntax Error is received, an attack would have succeeded

        try:
            e = parse(xee_remote)
        except etree.XMLSyntaxError:
            raise ValueError("An XML Syntax Error was raised, meaning a real attack would have succeeded!")

    def test_xee_local(self):
        """
        Tests a "safe" variant of the local XEE attack
        https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing
        :return:
        """

        xee_local = """<!DOCTYPE foo [
                          <!ELEMENT foo ANY >
                          <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
                        <foo>&xxe;</foo>
                      """
        # If an XML Syntax Error is received, an attack would have succeeded

        try:
            e = parse(xee_local)
        except etree.XMLSyntaxError:
            raise ValueError("An XML Syntax Error was raised, meaning a real attack would have succeeded!")

    def test_dtd_retrieval(self):
        pass

    def test_gzip_bomb(self):
        pass

    def test_xpath(self):
        pass

    def test_xslt(self):
        pass

    def test_xinclude(self):
        pass

class VersionsTest(unittest.TestCase):

    def test_01(self):
        """
        Tests that all tm10 objects have a version attribute

        :return:
        """
        for name, obj in inspect.getmembers(tm11, inspect.isclass):
            # Certain classes are excluded from this test:
            if name in ('TAXIIBase', 'UnsupportedQueryException', '_StatusDetail'):
                continue
            obj.version


# Encodings pulled from: https://docs.python.org/2/library/codecs.html
PYTHON_ENCODINGS = ['ascii',
                     'big5',
                     'big5hkscs',
                     'cp037',
                     'cp424',
                     'cp437',
                     'cp500',
                     'cp720',
                     'cp737',
                     'cp775',
                     'cp850',
                     'cp852',
                     'cp855',
                     'cp856',
                     'cp857',
                     'cp858',
                     'cp860',
                     'cp861',
                     'cp862',
                     'cp863',
                     'cp864',
                     'cp865',
                     'cp866',
                     'cp869',
                     'cp874',
                     'cp875',
                     'cp932',
                     'cp949',
                     'cp950',
                     'cp1006',
                     'cp1026',
                     'cp1140',
                     'cp1250',
                     'cp1251',
                     'cp1252',
                     'cp1253',
                     'cp1254',
                     'cp1255',
                     'cp1256',
                     'cp1257',
                     'cp1258',
                     'euc_jp',
                     'euc_jis_2004',
                     'euc_jisx0213',
                     'euc_kr',
                     'gb2312',
                     'gbk',
                     'gb18030',
                     'hz',
                     'iso2022_jp',
                     'iso2022_jp_1',
                     'iso2022_jp_2',
                     'iso2022_jp_2004',
                     'iso2022_jp_3',
                     'iso2022_jp_ext',
                     'iso2022_kr',
                     'latin_1',
                     'iso8859_2',
                     'iso8859_3',
                     'iso8859_4',
                     'iso8859_5',
                     'iso8859_6',
                     'iso8859_7',
                     'iso8859_8',
                     'iso8859_9',
                     'iso8859_10',
                     'iso8859_13',
                     'iso8859_14',
                     'iso8859_15',
                     'iso8859_16',
                     'johab',
                     'koi8_r',
                     'koi8_u',
                     'mac_cyrillic',
                     'mac_greek',
                     'mac_iceland',
                     'mac_latin2',
                     'mac_roman',
                     'mac_turkish',
                     'ptcp154',
                     'shift_jis',
                     'shift_jis_2004',
                     'shift_jisx0213',
                     'utf_32',
                     'utf_32_be',
                     'utf_32_le',
                     'utf_16',
                     'utf_16_be',
                     'utf_16_le',
                     'utf_7',
                     'utf_8',
                     'utf_8_sig',
                     ]


class EncodingsTest(unittest.TestCase):

    def test_01(self):
        """
        Test all the encodings for TAXII 1.1 XML
        """

        for encoding in PYTHON_ENCODINGS:
            if encoding in ('cp720', 'cp858', 'iso8859_11') and (sys.version_info[0] == 2 and sys.version_info[1] == 6):
                continue  # This encoding is not supported in Python 2.6
                
            encoded_doc = xml_taxii_message_11.encode(encoding, 'strict')
            try:
                msg = tm11.get_message_from_xml(encoded_doc, encoding)
            except Exception as e:
                print('Bad codec was: %s' % encoding)
                raise

    def test_02(self):
        """
        Test all the encodings for TAXII 1.1 JSON
        """
        
        for encoding in PYTHON_ENCODINGS:
            if encoding in ('cp720', 'cp858', 'iso8859_11') and (sys.version_info[0] == 2 and sys.version_info[1] == 6):
                continue  # This encoding is not supported in Python 2.6
            encoded_doc = json_taxii_message_11.encode(encoding, 'strict')
            try:
                msg = tm11.get_message_from_json(encoded_doc, encoding)
            except Exception as e:
                print('Bad codec was: %s' % encoding)
                raise


if __name__ == "__main__":
    unittest.main()
