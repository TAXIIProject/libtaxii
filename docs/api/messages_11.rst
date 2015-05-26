:mod:`libtaxii.messages_11` Module
==================================

.. automodule:: libtaxii.messages_11

.. note::

    The examples on this page assume that you have run the equivalent of

    .. code-block:: python

        import datetime
        from dateutil.tz import tzutc
        import libtaxii as t
        import libtaxii.messages_11 as tm11
	from libtaxii.constants import *

.. testsetup::

    import datetime
    from dateutil.tz import tzutc
    import libtaxii as t
    import libtaxii.messages_11 as tm11
    from libtaxii.constants import *

Status Message
--------------

.. autoclass:: StatusMessage

**Example:**

.. testcode::

    sm03 = tm11.StatusMessage(
            message_id='SM03',
            in_response_to=tm11.generate_message_id(),
            status_type=ST_DESTINATION_COLLECTION_ERROR,
            status_detail={'ACCEPTABLE_DESTINATION': ['Collection1','Collection2']})


Discovery Request
-----------------

.. autoclass:: DiscoveryRequest

**Example:**

.. testcode::

    headers={'ext_header1': 'value1', 'ext_header2': 'value2'}
    discovery_request = tm11.DiscoveryRequest(
            message_id=tm11.generate_message_id(),
            extended_headers=headers)


Discovery Response
------------------

.. autoclass:: DiscoveryResponse
.. autoclass:: ServiceInstance

**Example:**

.. testcode::

    discovery_response = tm11.DiscoveryResponse(
            message_id=tm11.generate_message_id(),
            in_response_to=discovery_request.message_id)

    service_instance = tm11.ServiceInstance(
            service_type=SVC_POLL,
            services_version=VID_TAXII_SERVICES_11,
            protocol_binding=VID_TAXII_HTTP_10,
            service_address='http://example.com/poll/',
            message_bindings=[VID_TAXII_XML_11],
            available=True,
            message='This is a message.',
            #supported_query=[tdq1],
            )

    discovery_response.service_instances.append(service_instance)

    # Alternatively, you could define the service instance(s) first and use the
    # following:

    service_instance_list = [service_instance]
    discovery_response = tm11.DiscoveryResponse(
            message_id=tm11.generate_message_id(),
            in_response_to=discovery_request.message_id,
            service_instances=service_instance_list)


Collection Information Request
------------------------------

.. autoclass:: CollectionInformationRequest

**Example:**

.. testcode::

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    collection_information_request = tm11.CollectionInformationRequest(
            message_id='CIReq01',
            extended_headers=ext_headers)


Collection Information Response
-------------------------------

.. autoclass:: CollectionInformationResponse
.. autoclass:: CollectionInformation
.. autoclass:: PushMethod
.. autoclass:: PollingServiceInstance
.. autoclass:: SubscriptionMethod
.. autoclass:: ReceivingInboxService

**Example:**

.. testcode::

    push_method1 = tm11.PushMethod(
            push_protocol=VID_TAXII_HTTP_10,
            push_message_bindings=[VID_TAXII_XML_11])

    poll_service1 = tm11.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/PollService1',
            poll_message_bindings=[VID_TAXII_XML_11])

    poll_service2 = tm11.PollingServiceInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/PollService2',
            poll_message_bindings=[VID_TAXII_XML_11])

    subs_method1 = tm11.SubscriptionMethod(
            subscription_protocol=VID_TAXII_HTTPS_10,
            subscription_address='https://example.com/SubscriptionService',
            subscription_message_bindings=[VID_TAXII_XML_11])

    inbox_service1 = tm11.ReceivingInboxService(
            inbox_protocol=VID_TAXII_HTTPS_10,
            inbox_address='https://example.com/InboxService',
            inbox_message_bindings=[VID_TAXII_XML_11],
            supported_contents=None)

    collection1 = tm11.CollectionInformation(
            collection_name='collection1',
            collection_description='This is a collection',
            supported_contents=[tm11.ContentBinding(CB_STIX_XML_101)],
            available=False,
            push_methods=[push_method1],
            polling_service_instances=[poll_service1, poll_service2],
            subscription_methods=[subs_method1],
            collection_volume=4,
            collection_type=CT_DATA_FEED,
            receiving_inbox_services=[inbox_service1])

    collection_response1 = tm11.CollectionInformationResponse(
            message_id='CIR01',
            in_response_to='0',
            collection_informations=[collection1])


Manage Collection Subscription Request
--------------------------------------

.. autoclass:: ManageCollectionSubscriptionRequest

**Example:**

.. testcode::

    subscription_parameters1 = tm11.SubscriptionParameters()
    push_parameters1 = tm11.PushParameters("", "", "")

    subs_req1 = tm11.ManageCollectionSubscriptionRequest(
            message_id='SubsReq01',
            action=ACT_SUBSCRIBE,
            collection_name='collection1',
            subscription_parameters=subscription_parameters1,
            push_parameters=push_parameters1)


Manage Collection Subscription Response
---------------------------------------

.. autoclass:: ManageCollectionSubscriptionResponse
.. autoclass:: SubscriptionInstance
.. autoclass:: PollInstance

**Example:**

.. testcode::

    subscription_parameters1 = tm11.SubscriptionParameters()
    push_parameters1 = tm11.PushParameters("", "", "")


    poll_instance1 = tm11.PollInstance(
            poll_protocol=VID_TAXII_HTTPS_10,
            poll_address='https://example.com/poll1/',
            poll_message_bindings=[VID_TAXII_XML_11])

    subs1 = tm11.SubscriptionInstance(
            subscription_id='Subs001',
            status=SS_ACTIVE,
            subscription_parameters=subscription_parameters1,
            push_parameters=push_parameters1,
            poll_instances=[poll_instance1])

    subs_resp1 = tm11.ManageCollectionSubscriptionResponse(
            message_id='SubsResp01',
            in_response_to='xyz',
            collection_name='abc123',
            message='Hullo!',
            subscription_instances=[subs1])


Poll Request
------------

.. autoclass:: PollRequest
.. autoclass:: PollParameters

**Example:**

.. testcode::

    delivery_parameters1 = tm11.DeliveryParameters(
            inbox_protocol=VID_TAXII_HTTPS_10,
            inbox_address='https://example.com/inboxAddress/',
            delivery_message_binding=VID_TAXII_XML_11)

    poll_params1 = tm11.PollParameters(
            allow_asynch=False,
            response_type=RT_COUNT_ONLY,
            content_bindings=[tm11.ContentBinding(binding_id=CB_STIX_XML_11)],
            #query=query1,
            delivery_parameters=delivery_parameters1)

    poll_req3 = tm11.PollRequest(
            message_id='PollReq03',
            collection_name='collection100',
            exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
            poll_parameters=poll_params1)


Poll Response
-------------

.. autoclass:: PollResponse

**Example:**

.. testcode::

    cb1 = tm11.ContentBlock(CB_STIX_XML_11, "")
    cb2 = tm11.ContentBlock(CB_STIX_XML_11, "")

    count = tm11.RecordCount(record_count=22, partial_count=False)

    poll_resp1 = tm11.PollResponse(
            message_id='PollResp1',
            in_response_to='tmp',
            collection_name='blah',
            exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
            subscription_id='24',
            message='This is a test message',
            content_blocks=[cb1, cb2],
            more=True,
            result_id='123',
            result_part_number=1,
            record_count=count)


Inbox Message
-------------

.. autoclass:: InboxMessage
.. autoclass:: SubscriptionInformation

**Example:**

.. testcode::

    cb1 = tm11.ContentBlock(CB_STIX_XML_11, "")
    cb2 = tm11.ContentBlock(CB_STIX_XML_11, "")

    subs_info1 = tm11.SubscriptionInformation(
            collection_name='SomeCollectionName',
            subscription_id='SubsId021',
            exclusive_begin_timestamp_label=datetime.datetime.now(tzutc()),
            inclusive_end_timestamp_label=datetime.datetime.now(tzutc()))

    inbox1 = tm11.InboxMessage(
            message_id='Inbox1',
            result_id='123',
            destination_collection_names=['collection1','collection2'],
            message='Hello!',
            subscription_information=subs_info1,
            record_count=tm11.RecordCount(22, partial_count=True),
            content_blocks=[cb1, cb2])


Poll Fulfillment Request
------------------------

.. autoclass:: PollFulfillmentRequest

**Example:**

.. testcode::

    pf1 = tm11.PollFulfillmentRequest(
            message_id='pf1',
            collection_name='1-800-collection',
            result_id='123',
            result_part_number=1)


Other Classes
-------------

.. autoclass:: TAXIIMessage

.. autoclass:: ContentBinding
.. autoclass:: ContentBlock

**Example:**

.. testcode::

    cb001 = tm11.ContentBlock(
            content_binding=tm11.ContentBinding(CB_STIX_XML_11),
            content='<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1"/>',
            timestamp_label=datetime.datetime.now(tzutc()),
            message='Hullo!',
            padding='The quick brown fox jumped over the lazy dogs.')

.. autoclass:: DeliveryParameters
.. autoclass:: PushParameters
.. autoclass:: RecordCount
.. autoclass:: SubscriptionParameters


Functions
---------

.. autofunction:: generate_message_id
.. autofunction:: validate_xml
.. autofunction:: get_message_from_xml
.. autofunction:: get_message_from_dict
.. autofunction:: get_message_from_json
