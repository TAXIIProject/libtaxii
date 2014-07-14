# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# This file has two purposes:
# 1. To provide a rough unit test of libtaxii.messages
# 2. To provide examples of how to use libtaxii.messages


### Contributors ###
# Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import datetime
import StringIO
import unittest

from dateutil.tz import tzutc
from lxml import etree

import libtaxii as t
import libtaxii.messages_10 as tm10


# TODO: This is bad practice. Refactor this.
# Set up some things used across multiple tests.
stix_etree = etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')).getroot()

xml_content_block1 = tm10.ContentBlock(
        content_binding=t.CB_STIX_XML_10,  # Required
        content=stix_etree,  # Required. Can be etree or string
        padding='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',  # Optional
        timestamp_label=datetime.datetime.now(tzutc()))  # Optional

string_content_block1 = tm10.ContentBlock(
        content_binding='string',  # Required
        content='Sample content',  # Required
        padding='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',  # Optional
        timestamp_label=datetime.datetime.now(tzutc()))  # Optional

delivery_parameters1 = tm10.DeliveryParameters(
        inbox_protocol=t.VID_TAXII_HTTP_10,  # Required if requesting push messaging
        inbox_address='http://example.com/inbox',  # Yes, if requesting push messaging
        delivery_message_binding=t.VID_TAXII_XML_10,  # Required if requesting push messaging
        content_bindings=[t.CB_STIX_XML_10])  # Optional - absence means accept all content bindings


def round_trip_message(taxii_message):
    if not isinstance(taxii_message, tm10.TAXIIMessage):
        raise ValueError('taxii_message was not an instance of TAXIIMessage')

    print '***** Message type = %s; id = %s' % (taxii_message.message_type, taxii_message.message_id)

    xml_string = taxii_message.to_xml()
    valid = tm10.validate_xml(xml_string)
    if valid is not True:
        raise Exception('\tFailure of test #1 - XML not schema valid: %s' % valid)
    msg_from_xml = tm10.get_message_from_xml(xml_string)
    dictionary = taxii_message.to_dict()
    msg_from_dict = tm10.get_message_from_dict(dictionary)
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


def round_trip_content_block(content_block):
    if not isinstance(content_block, tm10.ContentBlock):
        raise ValueError('content_block was not an instance of ContentBlock')

    print '***** Starting Content Block tests'

    xml_string = content_block.to_xml()
    block_from_xml = tm10.ContentBlock.from_xml(xml_string)
    dictionary = content_block.to_dict()
    block_from_dict = tm10.ContentBlock.from_dict(dictionary)
    json_string = content_block.to_json()
    block_from_json = tm10.ContentBlock.from_json(json_string)

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
    if block_from_json != block_from_dict:
        print '\t Failure of test #3 - running equals w/ debug:'
        block_from_json.__eq__(block_from_dict, True)
        raise Exception('Test #3 failed - block_from_json != block_from_dict')

    print '***** All tests completed!'


class DiscoveryRequestTests(unittest.TestCase):

    def test_discovery_request(self):
        discovery_request1 = tm10.DiscoveryRequest(
                message_id=tm10.generate_message_id(),  # Required
                extended_headers={'ext_header1': 'value1', 'ext_header2': 'value2'})  # Optional.
                # Extended headers are optional for every message type, but only demonstrated here

        round_trip_message(discovery_request1)


class DiscoveryResponseTests(unittest.TestCase):

    def test_discovery_response(self):
        service_instance1 = tm10.ServiceInstance(
                service_type=tm10.SVC_INBOX,  # Required
                services_version=t.VID_TAXII_SERVICES_10,  # Required
                protocol_binding=t.VID_TAXII_HTTP_10,  # Required
                service_address='http://example.com/inboxservice/',  # Required
                message_bindings=[t.VID_TAXII_XML_10],  # Required, must have at least one value in the list
                inbox_service_accepted_content=[t.CB_STIX_XML_10],  # Optional for service_type=SVC_INBOX, prohibited otherwise
                                                    # If this is absent and service_type=SVC_INBOX,
                                                    # It means the inbox service accepts all content
                available=True,  # Optional - defaults to None, which means 'Unknown'
                message='This is a message.')  # Optional

        # Create the discovery response
        discovery_response1 = tm10.DiscoveryResponse(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required. This should be the ID of the corresponding request
                service_instances=[service_instance1])  # Optional.

        round_trip_message(discovery_response1)

    def test_discovery_response_deprecated(self):
        # Test nested-class form:
        #   DiscoveryResponse.ServiceInstance

        service_instance1 = tm10.DiscoveryResponse.ServiceInstance(
                service_type=tm10.SVC_INBOX,
                services_version=t.VID_TAXII_SERVICES_10,
                protocol_binding=t.VID_TAXII_HTTP_10,
                service_address='http://example.com/inboxservice/',
                message_bindings=[t.VID_TAXII_XML_10])

        discovery_response1 = tm10.DiscoveryResponse(
                message_id=tm10.generate_message_id(),
                in_response_to=tm10.generate_message_id(),
                service_instances=[service_instance1])

        round_trip_message(discovery_response1)


class FeedInformationRequestTests(unittest.TestCase):

    def test_feed_information_request1(self):
        feed_information_request1 = tm10.FeedInformationRequest(
                message_id=tm10.generate_message_id())  # Required

        round_trip_message(feed_information_request1)


class FeedInformationResponseTests(unittest.TestCase):

    def test_feed_information_response1(self):
        push_method1 = tm10.PushMethod(
                push_protocol=t.VID_TAXII_HTTP_10,  # Required
                push_message_bindings=[t.VID_TAXII_XML_10])  # Required

        polling_service1 = tm10.PollingServiceInstance(
                poll_protocol=t.VID_TAXII_HTTP_10,  # Required
                poll_address='http://example.com/PollService/',  # Required
                poll_message_bindings=[t.VID_TAXII_XML_10])  # Required

        subscription_service1 = tm10.SubscriptionMethod(
                subscription_protocol=t.VID_TAXII_HTTP_10,  # Required
                subscription_address='http://example.com/SubsService/',  # Required
                subscription_message_bindings=[t.VID_TAXII_XML_10])  # Required

        feed1 = tm10.FeedInformation(
                feed_name='Feed1',  # Required
                feed_description='Description of a feed',  # Required
                supported_contents=[t.CB_STIX_XML_10],  # Required. List of supported content binding IDs
                available=True,  # Optional. Defaults to None (aka Unknown)
                push_methods=[push_method1],  # Required if there are no polling_services. Optional otherwise
                polling_service_instances=[polling_service1],  # Required if there are no push_methods. Optional otherwise.
                subscription_methods=[subscription_service1])  # Optional

        feed_information_response1 = tm10.FeedInformationResponse(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required. This should be the ID of the corresponding request
                feed_informations=[feed1])  # Optional

        round_trip_message(feed_information_response1)

    def test_feed_information_response_deprecated(self):
        # Test nested-class forms:
        #   FeedInformationResponse.FeedInformation
        #   FeedInformationResponse.FeedInformation.PushMethod
        #   FeedInformationResponse.FeedInformation.PollingServiceInstance
        #   FeedInformationResponse.FeedInformation.SubscriptionMethod

        push_method1 = tm10.FeedInformationResponse.FeedInformation.PushMethod(
                push_protocol=t.VID_TAXII_HTTP_10,
                push_message_bindings=[t.VID_TAXII_XML_10])

        polling_service1 = tm10.FeedInformationResponse.FeedInformation.PollingServiceInstance(
                poll_protocol=t.VID_TAXII_HTTP_10,
                poll_address='http://example.com/PollService/',
                poll_message_bindings=[t.VID_TAXII_XML_10])

        subscription_service1 = tm10.FeedInformationResponse.FeedInformation.SubscriptionMethod(
                subscription_protocol=t.VID_TAXII_HTTP_10,
                subscription_address='http://example.com/SubsService/',
                subscription_message_bindings=[t.VID_TAXII_XML_10])

        feed1 = tm10.FeedInformationResponse.FeedInformation(
                feed_name='Feed1',
                feed_description='Description of a feed',
                supported_contents=[t.CB_STIX_XML_10],
                push_methods=[push_method1],
                polling_service_instances=[polling_service1],
                subscription_methods=[subscription_service1])

        feed_information_response1 = tm10.FeedInformationResponse(
                message_id=tm10.generate_message_id(),
                in_response_to=tm10.generate_message_id(),
                feed_informations=[feed1])

        round_trip_message(feed_information_response1)

class PollResponseTests(unittest.TestCase):

    def test_poll_request1(self):
        poll_request1 = tm10.PollRequest(
                message_id=tm10.generate_message_id(),  # Required
                feed_name='TheFeedToPoll',  # Required
                subscription_id='SubsId002',  # Optional
                exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional - Absence means 'no lower bound'
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Optional - Absence means 'no upper bound'
                content_bindings=[t.CB_STIX_XML_10])  # Optional - defaults to accepting all content bindings

        round_trip_message(poll_request1)


class PollResponseTests(unittest.TestCase):

    def test_poll_response1(self):
        poll_response1 = tm10.PollResponse(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required - this should be the ID of the corresponding request
                feed_name='FeedName',  # Required
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Required
                inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional
                subscription_id='SubsId001',  # Optional
                message='This is a message.',  # Optional
                content_blocks=[xml_content_block1])  # Optional

        round_trip_message(poll_response1)

    def test_poll_response1(self):
        poll_response2 = tm10.PollResponse(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required - this should be the ID of the corresponding request
                feed_name='FeedName',  # Required
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),  # Required
                inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional
                subscription_id='SubsId001',  # Optional
                message='This is a message.',  # Optional
                content_blocks=[string_content_block1])  # Optional

        round_trip_message(poll_response2)


class StatusMessageTests(unittest.TestCase):

    def test_status_message(self):
        status_message1 = tm10.StatusMessage(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required. Should be the ID of the corresponding request
                status_type=tm10.ST_SUCCESS,  # Required
                status_detail='Machine-processable info here!',  # May be optional or not allowed, depending on status_type
                message='This is a message.')  # Optional

        round_trip_message(status_message1)


class InboxMessageTests(unittest.TestCase):

    def setUp(self):
        self.subscription_information1 = tm10.SubscriptionInformation(
                feed_name='SomeFeedName',  # Required
                subscription_id='SubsId021',  # Required
                inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),  # Optional - Absence means 'no lower bound'
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))  # Optional - Absence means 'no upper bound'

    def test_inbox_message1(self):
        inbox_message1 = tm10.InboxMessage(
                message_id=tm10.generate_message_id(),  # Required
                message='This is a message.',  # Optional
                subscription_information=self.subscription_information1,  # Optional
                content_blocks=[xml_content_block1])  # Optional

        round_trip_message(inbox_message1)

    def test_inbox_message2(self):
        inbox_message2 = tm10.InboxMessage(
                message_id=tm10.generate_message_id(),  # Required
                message='This is a message.',  # Optional
                subscription_information=self.subscription_information1,  # Optional
                content_blocks=[string_content_block1])  # Optional

        round_trip_message(inbox_message2)

    def test_inbox_message_deprecated(self):
        # Test nested-class form:
        #   InboxMessage.SubscriptionInformation

        sub_info = tm10.InboxMessage.SubscriptionInformation(
                feed_name='SomeFeedName',
                subscription_id='SubsId021',
                inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
                inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))

        inbox_msg = tm10.InboxMessage(
                message_id=tm10.generate_message_id(),
                subscription_information=sub_info,
                content_blocks=[xml_content_block1])

        round_trip_message(inbox_msg)


class ManageFeedSubscriptionRequestTests(unittest.TestCase):

    def test_feed_subscription_request(self):
        manage_feed_subscription_request1 = tm10.ManageFeedSubscriptionRequest(
                message_id=tm10.generate_message_id(),  # Required
                feed_name='SomeFeedName',   # Required
                action=tm10.ACT_UNSUBSCRIBE,  # Required
                subscription_id='SubsId056',  # Required for unsubscribe, prohibited otherwise
                delivery_parameters=delivery_parameters1)  # Required

        round_trip_message(manage_feed_subscription_request1)


class ManageFeedSubscriptionResponseTests(unittest.TestCase):

    def test_manage_feed_subscription_response(self):
        poll_instance1 = tm10.PollInstance(
                poll_protocol=t.VID_TAXII_HTTP_10,  # Required
                poll_address='http://example.com/poll',  # Required
                poll_message_bindings=[t.VID_TAXII_XML_10])  # Required

        subscription_instance1 = tm10.SubscriptionInstance(
                subscription_id='SubsId234',  # required
                delivery_parameters=[delivery_parameters1],  # Required if message is responding to a status action. Optional otherwise
                poll_instances=[poll_instance1])  # Required if action was polling subscription. Optional otherwise

        manage_feed_subscription_response1 = tm10.ManageFeedSubscriptionResponse(
                message_id=tm10.generate_message_id(),  # Required
                in_response_to=tm10.generate_message_id(),  # Required - Should be the ID of the corresponding request
                feed_name='Feed001',  # Required
                message='This is a message',  # Optional
                subscription_instances=[subscription_instance1])  # Required

        round_trip_message(manage_feed_subscription_response1)

    def test_manage_feed_subscription_response_deprecated(self):
        # Test nested-class forms:
        #   ManageFeedSubscriptionResponse.PollInstance
        #   ManageFeedSubscriptionResponse.SubscriptionInstance

        poll = tm10.ManageFeedSubscriptionResponse.PollInstance(
                poll_protocol=t.VID_TAXII_HTTP_10,
                poll_address='http://example.com/poll',
                poll_message_bindings=[t.VID_TAXII_XML_10])

        subscription = tm10.ManageFeedSubscriptionResponse.SubscriptionInstance(
                subscription_id='SubsId234',
                delivery_parameters=[delivery_parameters1],
                poll_instances=[poll])

        response = tm10.ManageFeedSubscriptionResponse(
                message_id=tm10.generate_message_id(),
                in_response_to=tm10.generate_message_id(),
                feed_name='Feed001',
                subscription_instances=[subscription])

        round_trip_message(response)


class ContentBlockTests(unittest.TestCase):

    def test_content_block1(self):
        cb1 = tm10.ContentBlock(content_binding=t.CB_STIX_XML_10,
                            content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')
        round_trip_content_block(cb1)

    def test_content_block2(self):
        cb2 = tm10.ContentBlock(content_binding=t.CB_STIX_XML_10,
                            content=StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>'))
        round_trip_content_block(cb2)

    def test_content_block3(self):
        cb3 = tm10.ContentBlock(content_binding=t.CB_STIX_XML_10,
                            content=etree.parse(StringIO.StringIO('<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')))
        round_trip_content_block(cb3)

    def test_content_block4(self):
        cb4 = tm10.ContentBlock(content_binding=t.CB_STIX_XML_10,
                            content='<Something thats not XML')
        round_trip_content_block(cb4)

    def test_content_block5(self):
        cb5 = tm10.ContentBlock(content_binding=t.CB_STIX_XML_10,
                            content='Something thats not XML <xml/>')
        round_trip_content_block(cb5)

    def test_content_block6(self):
        cb6 = tm10.ContentBlock(content_binding='RandomUnicodeString', content=unicode('abcdef'))
        round_trip_content_block(cb6)


if __name__ == "__main__":
    unittest.main()
