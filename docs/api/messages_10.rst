messages_10 Module
==================

.. automodule:: libtaxii.messages_10

.. note::

    The examples on this page assume that you have run the equivalent of

    .. code-block:: python

        import datetime
        from dateutil.tz import tzutc
        import libtaxii as t
        import libtaxii.messages_10 as tm10
        from libtaxii.constants import *

.. testsetup::

    import datetime
    from dateutil.tz import tzutc
    import libtaxii as t
    import libtaxii.messages_10 as tm10
    from libtaxii.constants import *

Status Message
--------------

.. autoclass:: StatusMessage

**Example:**

.. testcode::

    status_message1 = tm10.StatusMessage(
            message_id=tm10.generate_message_id(),
            in_response_to="12345",
            status_type=ST_SUCCESS,
            status_detail='Machine-processable info here!',
            message='This is a message.')


Discovery Request
-----------------

.. autoclass:: DiscoveryRequest

**Example:**

.. testcode::

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    discovery_request = tm10.DiscoveryRequest(
            message_id=tm10.generate_message_id(),
            extended_headers=ext_headers)


Discovery Response
------------------

.. autoclass:: DiscoveryResponse
.. autoclass:: ServiceInstance

**Example:**

.. testcode::

    discovery_response = tm10.DiscoveryResponse(
            message_id=tm10.generate_message_id(),
            in_response_to=discovery_request.message_id)

    service_instance = tm10.ServiceInstance(
            service_type=SVC_INBOX,
            services_version=VID_TAXII_SERVICES_10,
            protocol_binding=VID_TAXII_HTTPS_10,
            service_address='https://example.com/inbox/',
            message_bindings=[VID_TAXII_XML_10],
            inbox_service_accepted_content=[CB_STIX_XML_10],
            available=True,
            message='This is a sample inbox service instance')

    discovery_response.service_instances.append(service_instance)

    # Alternatively, you could define the service instance(s) first and use the
    # following:

    service_instance_list = [service_instance]
    discovery_response = tm10.DiscoveryResponse(
            message_id=tm10.generate_message_id(),
            in_response_to=discovery_request.message_id,
            service_instances=service_instance_list)


Feed Information Request
------------------------

.. autoclass:: FeedInformationRequest

**Example:**

.. testcode::

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    feed_information_request= tm10.FeedInformationRequest(
            message_id=tm10.generate_message_id(),
            extended_headers=ext_headers)


Feed Information Response
-------------------------

.. autoclass:: FeedInformationResponse
.. autoclass:: FeedInformation
.. autoclass:: PushMethod
.. autoclass:: PollingServiceInstance
.. autoclass:: SubscriptionMethod

**Example:**

.. testcode::

    push_method1 = tm10.PushMethod(
            push_protocol=VID_TAXII_HTTP_10,
            push_message_bindings=[VID_TAXII_XML_10])

    polling_service1 = tm10.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTP_10,
            poll_address='http://example.com/PollService/',
            poll_message_bindings=[VID_TAXII_XML_10])

    subscription_service1 = tm10.SubscriptionMethod(
            subscription_protocol=VID_TAXII_HTTP_10,
            subscription_address='http://example.com/SubsService/',
            subscription_message_bindings=[VID_TAXII_XML_10])

    feed1 = tm10.FeedInformation(
            feed_name='Feed1',
            feed_description='Description of a feed',
            supported_contents=[CB_STIX_XML_10],
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

.. testcode::

    delivery_parameters1 = tm10.DeliveryParameters(
            inbox_protocol=VID_TAXII_HTTP_10,
            inbox_address='http://example.com/inbox',
            delivery_message_binding=VID_TAXII_XML_10,
            content_bindings=[CB_STIX_XML_10])

    manage_feed_subscription_request1 = tm10.ManageFeedSubscriptionRequest(
            message_id=tm10.generate_message_id(),
            feed_name='SomeFeedName',
            action=ACT_UNSUBSCRIBE,
            subscription_id='SubsId056',
            delivery_parameters=delivery_parameters1)


Manage Feed Subscription Response
---------------------------------

.. autoclass:: ManageFeedSubscriptionResponse
.. autoclass:: SubscriptionInstance
.. autoclass:: PollInstance

**Example:**

.. testcode::

    poll_instance1 = tm10.PollInstance(
            poll_protocol=VID_TAXII_HTTP_10,
            poll_address='http://example.com/poll',
            poll_message_bindings=[VID_TAXII_XML_10])

    subscription_instance1 = tm10.SubscriptionInstance(
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

.. testcode::

    poll_request1 = tm10.PollRequest(
            message_id=tm10.generate_message_id(),
            feed_name='TheFeedToPoll',
            exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
            subscription_id='SubsId002',
            content_bindings=[CB_STIX_XML_10])


Poll Response
-------------

.. autoclass:: PollResponse

**Example:**

.. testcode::

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
.. autoclass:: SubscriptionInformation

**Example:**

.. testcode::

    cb1 = tm10.ContentBlock(CB_STIX_XML_11, "")

    subscription_information1 = tm10.SubscriptionInformation(
            feed_name='SomeFeedName',
            subscription_id='SubsId021',
            inclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))

    inbox_message1 = tm10.InboxMessage(
            message_id=tm10.generate_message_id(),
            message='This is a message.',
            subscription_information=subscription_information1,
            content_blocks=[cb1])


Other Classes
-------------

.. autoclass:: TAXIIMessage

.. autoclass:: ContentBlock

**Example:**

.. testcode::

    cb1 = tm10.ContentBlock(
            content_binding=CB_STIX_XML_10,
            content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>')

.. autoclass:: DeliveryParameters


Functions
---------

.. autofunction:: generate_message_id
.. autofunction:: validate_xml
.. autofunction:: get_message_from_xml
.. autofunction:: get_message_from_dict
.. autofunction:: get_message_from_json

