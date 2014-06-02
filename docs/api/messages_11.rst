:mod:`libtaxii.messages_11` Module
==================================

.. module:: libtaxii.messages_11

.. note::

    The examples on this page assume that you have run the equivalent of

    .. code-block:: python

        import libtaxii.messages_11 as tm11


Discovery Request
-----------------

.. autoclass:: DiscoveryRequest

**Example:**

.. code-block:: python

    headers={'ext_header1': 'value1', 'ext_header2': 'value2'}
    discovery_request = tm11.DiscoveryRequest(
            message_id=tm11.generate_message_id(),
            extended_headers=headers)


Discovery Response
------------------

.. autoclass:: DiscoveryResponse
.. autoclass:: libtaxii.messages_11::DiscoveryResponse.ServiceInstance

**Example:**

.. code-block:: python

    discovery_request = tm11.DiscoveryResponse(
            message_id=tm11.generate_message_id(),
            in_response_to=discovery_request.message_id)

    service_instance= tm11.DiscoveryResponse.ServiceInstance(
            service_type=tm11.SVC_POLL,
            services_version=t.VID_TAXII_SERVICES_11,
            protocol_binding=t.VID_TAXII_HTTP_10,
            service_address='http://example.com/poll/',
            message_bindings=[t.VID_TAXII_XML_11],
            available=True,
            message='This is a message.',
            supported_query=[tdq1])

    discovery_response.service_instances.append(service_instance)

Alternatively, you could define the service instance(s) first and use the
following:

.. code-block:: python

    service_instance_list = [service_instance]
    discovery_response = tm11.DiscoveryResponse(
            message_id=tm11.generate_message_id(),
            in_response_to=discovery_request.message_id,
            service_instances=service_instance_list)


Collection Information Request
------------------------------

.. autoclass:: CollectionInformationRequest

**Example:**

.. code-block:: python

    ext_headers = {'name1': 'val1', 'name2': 'val2'}
    collection_information_request = tm11.CollectionInformationRequest(
            message_id='CIReq01',
            extended_headers=ext_headers)


Collection Information Response
-------------------------------

.. autoclass:: CollectionInformationResponse
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.PushMethod
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.PollingServiceInstance
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.SubscriptionMethod
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.ReceivingInboxService


Poll Request
------------

.. autoclass:: PollRequest
.. autoclass:: libtaxii.messages_11::PollRequest.PollParameters


Poll Response
-------------

.. autoclass:: PollResponse


Status Message
--------------

.. autoclass:: StatusMessage


Inbox Message
-------------

.. autoclass:: InboxMessage
.. autoclass:: libtaxii.messages_11::InboxMessage.SubscriptionInformation


Manage Collection Subscription Request
--------------------------------------

.. autoclass:: ManageCollectionSubscriptionRequest


Manage Collection Subscription Response
---------------------------------------

.. autoclass:: ManageCollectionSubscriptionResponse
.. autoclass:: libtaxii.messages_11::ManageCollectionSubscriptionResponse.SubscriptionInstance
.. autoclass:: libtaxii.messages_11::ManageCollectionSubscriptionResponse.PollInstance


Poll Fulfillment Request
------------------------

.. autoclass:: PollFulfillmentRequest


Other Classes
-------------

.. autoclass:: TAXIIMessage
.. autoclass:: BaseNonMessage

.. autoclass:: ContentBlock
.. autoclass:: DeliveryParameters
.. autoclass:: ContentBinding
.. autoclass:: RecordCount
.. autoclass:: SubscriptionParameters
.. autoclass:: PushParameters


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
.. autodata:: MSG_POLL_REQUEST
.. autodata:: MSG_POLL_RESPONSE
.. autodata:: MSG_INBOX_MESSAGE
.. autodata:: MSG_POLL_FULFILLMENT_REQUEST
.. autodata:: MSG_COLLECTION_INFORMATION_REQUEST
.. autodata:: MSG_COLLECTION_INFORMATION_RESPONSE
.. autodata:: MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST
.. autodata:: MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE

.. autodata:: MSG_TYPES


Status Types
************

These constants are used in :py:class:`StatusMessage`.

.. autodata:: ST_ASYNCHRONOUS_POLL_ERROR
.. autodata:: ST_BAD_MESSAGE
.. autodata:: ST_DENIED
.. autodata:: ST_DESTINATION_COLLECTION_ERROR
.. autodata:: ST_FAILURE
.. autodata:: ST_INVALID_RESPONSE_PART
.. autodata:: ST_NETWORK_ERROR
.. autodata:: ST_NOT_FOUND
.. autodata:: ST_PENDING
.. autodata:: ST_POLLING_UNSUPPORTED
.. autodata:: ST_RETRY
.. autodata:: ST_SUCCESS
.. autodata:: ST_UNAUTHORIZED
.. autodata:: ST_UNSUPPORTED_MESSAGE_BINDING
.. autodata:: ST_UNSUPPORTED_CONTENT_BINDING
.. autodata:: ST_UNSUPPORTED_PROTOCOL
.. autodata:: ST_UNSUPPORTED_QUERY

.. autodata:: ST_TYPES


Subscription Actions
********************

These constants are used in :py:class:`ManageCollectionSubscriptionRequest`

.. autodata:: ACT_SUBSCRIBE
.. autodata:: ACT_UNSUBSCRIBE
.. autodata:: ACT_STATUS
.. autodata:: ACT_PAUSE
.. autodata:: ACT_RESUME

.. autodata:: ACT_TYPES


Subscription Statuses
*********************

These constants are used in :py:class:`ManageCollectionSubscriptionResponse`

.. autodata:: SS_ACTIVE
.. autodata:: SS_PAUSED
.. autodata:: SS_UNSUBSCRIBED

.. autodata:: SS_TYPES


Response Types
**************

These constants are used to indicate the type of response returned.

.. autodata:: RT_FULL
.. autodata:: RT_COUNT_ONLY

.. autodata:: RT_TYPES


Collection Types
****************

These constants are used to indicate the type of collection.

.. autodata:: CT_DATA_FEED
.. autodata:: CT_DATA_SET

.. autodata:: CT_TYPES


Service Types
****************

These constants are used to indicate the type of service.

.. autodata:: SVC_INBOX
.. autodata:: SVC_POLL
.. autodata:: SVC_COLLECTION_MANAGEMENT
.. autodata:: SVC_DISCOVERY

.. autodata:: SVC_TYPES
