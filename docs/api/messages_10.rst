:mod:`libtaxii.messages_10` Module
==================================

.. automodule:: libtaxii.messages_10

.. note::

    The examples on this page assume that you have run the equivalent of

    .. code-block:: python

        import libtaxii.messages_10 as tm10


Status Message
--------------

.. autoclass:: StatusMessage

**Example:**

.. code-block:: python

    status_message1 = tm10.StatusMessage(
            message_id=tm10.generate_message_id(),
            in_response_to="12345",
            status_type=tm10.ST_SUCCESS,
            status_detail='Machine-processable info here!',
            message='This is a message.')


Discovery Request
-----------------

.. autoclass:: DiscoveryRequest

**Example:**

.. code-block:: python

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    discovery_request = tm10.DiscoveryRequest(
            message_id=tm10.generate_message_id(),
            extended_headers=ext_headers)


Discovery Response
------------------

.. autoclass:: DiscoveryResponse
.. autoclass:: libtaxii.messages_10::DiscoveryResponse.ServiceInstance

**Example:**

.. code-block:: python

    discovery_response = tm10.DiscoveryResponse(
            message_id=tm10.generate_message_id(),
            in_response_to=discovery_request.message_id)

    service_instance = tm10.DiscoveryResponse.ServiceInstance(
            service_type=tm10.SVC_INBOX,
            services_version=t.VID_TAXII_SERVICES_10,
            protocol_binding=t.VID_TAXII_HTTPS_10,
            service_address='https://example.com/inbox/'
            message_bindings=[t.VID_TAXII_XML_10],
            inbox_service_accepted_content=[t.CB_STIX_XML_10],
            available=True,
            message='This is a sample inbox service instance')

    discovery_response.service_instances.append(service_instance)

Alternatively, you could define the service instance(s) first and use the
following:

.. code-block:: python

    service_instance_list = [service_instance]
    discovery_response = tm10.DiscoveryResponse(
            message_id=tm10.generate_message_id(),
            in_response_to=discovery_request.message_id,
            service_instances=service_instance_list)


Feed Information Request
------------------------

.. autoclass:: FeedInformationRequest

**Example:**

.. code-block:: python

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    feed_information_request= tm10.FeedInformationRequest(
            message_id=tm10.generate_message_id(),
            extended_headers=ext_headers)


Feed Information Response
-------------------------

.. autoclass:: FeedInformationResponse
.. autoclass:: libtaxii.messages_10::FeedInformationResponse.FeedInformation
.. autoclass:: libtaxii.messages_10::FeedInformationResponse.FeedInformation.PushMethod
.. autoclass:: libtaxii.messages_10::FeedInformationResponse.FeedInformation.PollingServiceInstance
.. autoclass:: libtaxii.messages_10::FeedInformationResponse.FeedInformation.SubscriptionMethod

**Example:**

.. code-block:: python

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
            available=True,
            push_methods=[push_method1],
            polling_service_instances=[polling_service1],
            subscription_methods=[subscription_service1])

    feed_information_response1 = tm10.FeedInformationResponse(
            message_id=tm10.generate_message_id(),
            in_response_to=tm10.generate_message_id(),
            feed_informations=[feed1])


Manage Feed Subscription Request
--------------------------------

.. autoclass:: ManageFeedSubscriptionRequest

**Example:**

.. code-block:: python

    delivery_parameters1 = tm10.DeliveryParameters(
            inbox_protocol=t.VID_TAXII_HTTP_10,
            inbox_address='http://example.com/inbox',
            delivery_message_binding=t.VID_TAXII_XML_10,
            content_bindings=[t.CB_STIX_XML_10])

    manage_feed_subscription_request1 = tm10.ManageFeedSubscriptionRequest(
            message_id=tm10.generate_message_id(),
            feed_name='SomeFeedName',
            action=tm10.ACT_UNSUBSCRIBE,
            subscription_id='SubsId056',
            delivery_parameters=delivery_parameters1)


Manage Feed Subscription Response
---------------------------------

.. autoclass:: ManageFeedSubscriptionResponse
.. autoclass:: libtaxii.messages_10::ManageFeedSubscriptionResponse.SubscriptionInstance
.. autoclass:: libtaxii.messages_10::ManageFeedSubscriptionResponse.PollInstance

**Example:**

.. code-block:: python

    poll_instance1 = tm10.ManageFeedSubscriptionResponse.PollInstance(
            poll_protocol=t.VID_TAXII_HTTP_10,
            poll_address='http://example.com/poll',
            poll_message_bindings=[t.VID_TAXII_XML_10])

    subscription_instance1 = tm10.ManageFeedSubscriptionResponse.SubscriptionInstance(
            subscription_id='SubsId234',
            delivery_parameters=[delivery_parameters1],
            poll_instances=[poll_instance1])

    manage_feed_subscription_response1 = tm10.ManageFeedSubscriptionResponse(
            message_id=tm10.generate_message_id(),
            in_response_to="12345",
            feed_name='Feed001',
            message='This is a message',
            subscription_instances=[subscription_instance1])


Poll Request
------------

.. autoclass:: PollRequest

**Example:**

.. code-block:: python

    poll_request1 = tm10.PollRequest(
            message_id=tm10.generate_message_id(),
            feed_name='TheFeedToPoll',
            exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
            subscription_id='SubsId002',
            content_bindings=[t.CB_STIX_XML_10])


Poll Response
-------------

.. autoclass:: PollResponse

**Example:**

.. code-block:: python

    poll_response1 = tm10.PollResponse(
            message_id=tm10.generate_message_id(),
            in_response_to="12345",
            feed_name='FeedName',
            inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
            subscription_id='SubsId001',
            message='This is a message.',
            content_blocks=[])


Inbox Message
-------------

.. autoclass:: InboxMessage
.. autoclass:: libtaxii.messages_10::InboxMessage.SubscriptionInformation

**Example:**

.. code-block:: python

    subscription_information1 = tm10.InboxMessage.SubscriptionInformation(
            feed_name='SomeFeedName',
            subscription_id='SubsId021',
            inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))

    inbox_message1 = tm10.InboxMessage(
            message_id=tm10.generate_message_id(),
            message='This is a message.',
            subscription_information=subscription_information1,
            content_blocks=[xml_content_block1])


Other Classes
-------------

.. autoclass:: TAXIIMessage
.. autoclass:: BaseNonMessage

.. autoclass:: ContentBlock

**Example:**

.. code-block:: python

    cb1 = tm10.ContentBlock(
            content_binding=t.CB_STIX_XML_10,
            content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')

.. autoclass:: DeliveryParameters


Functions
---------

.. autofunction:: generate_message_id
.. autofunction:: get_xml_parser
.. autofunction:: set_xml_parser
.. autofunction:: validate_xml
.. autofunction:: get_message_from_xml
.. autofunction:: get_message_from_dict
.. autofunction:: get_message_from_json


Constants
---------

Message Types
*************

.. autodata:: MSG_STATUS_MESSAGE
.. autodata:: MSG_DISCOVERY_REQUEST
.. autodata:: MSG_DISCOVERY_RESPONSE
.. autodata:: MSG_FEED_INFORMATION_REQUEST
.. autodata:: MSG_FEED_INFORMATION_RESPONSE
.. autodata:: MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST
.. autodata:: MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE
.. autodata:: MSG_POLL_REQUEST
.. autodata:: MSG_POLL_RESPONSE
.. autodata:: MSG_INBOX_MESSAGE

.. autodata:: MSG_TYPES


Status Types
************

These constants are used in :py:class:`StatusMessage`.

.. autodata:: ST_BAD_MESSAGE
.. autodata:: ST_DENIED
.. autodata:: ST_FAILURE
.. autodata:: ST_NOT_FOUND
.. autodata:: ST_POLLING_UNSUPPORTED
.. autodata:: ST_RETRY
.. autodata:: ST_SUCCESS
.. autodata:: ST_UNAUTHORIZED
.. autodata:: ST_UNSUPPORTED_MESSAGE_BINDING
.. autodata:: ST_UNSUPPORTED_CONTENT_BINDING
.. autodata:: ST_UNSUPPORTED_PROTOCOL

.. autodata:: ST_TYPES


Subscription Actions
********************

These constants are used in :py:class:`ManageFeedSubscriptionRequest`

.. autodata:: ACT_SUBSCRIBE
.. autodata:: ACT_UNSUBSCRIBE
.. autodata:: ACT_STATUS

.. autodata:: ACT_TYPES


Service Types
****************

These constants are used to indicate the type of service.

.. autodata:: SVC_INBOX
.. autodata:: SVC_POLL
.. autodata:: SVC_FEED_MANAGEMENT
.. autodata:: SVC_DISCOVERY

.. autodata:: SVC_TYPES
