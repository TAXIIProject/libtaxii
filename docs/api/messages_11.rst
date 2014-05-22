:mod:`libtaxii.messages_11` Module
==================================

.. module:: libtaxii.messages_11

.. note::

    The examples on this page assume that you have run the equivalent of

    .. code-block:: python

        import libtaxii.messages_11 as tm11


Classes
-------

Message Classes
***************

.. autoclass:: TAXIIMessage

.. autoclass:: DiscoveryRequest
.. autoclass:: DiscoveryResponse
.. autoclass:: CollectionInformationRequest
.. autoclass:: CollectionInformationResponse
.. autoclass:: PollRequest
.. autoclass:: PollResponse
.. autoclass:: StatusMessage
.. autoclass:: InboxMessage
.. autoclass:: ManageCollectionSubscriptionRequest
.. autoclass:: ManageCollectionSubscriptionResponse
.. autoclass:: PollFulfillmentRequest


Message Nested Classes
*********************

.. autoclass:: libtaxii.messages_11::DiscoveryResponse.ServiceInstance
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.PushMethod
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.PollingServiceInstance
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.SubscriptionMethod
.. autoclass:: libtaxii.messages_11::CollectionInformationResponse.CollectionInformation.ReceivingInboxService
.. autoclass:: libtaxii.messages_11::PollRequest.PollParameters
.. autoclass:: libtaxii.messages_11::InboxMessage.SubscriptionInformation
.. autoclass:: libtaxii.messages_11::ManageCollectionSubscriptionResponse.SubscriptionInstance
.. autoclass:: libtaxii.messages_11::ManageCollectionSubscriptionResponse.PollInstance


Other Classes
*************

.. autoclass:: BaseNonMessage

.. autoclass:: ContentBlock
.. autoclass:: DeliveryParameters
.. autoclass:: ContentBinding
.. autoclass:: RecordCount
.. autoclass:: SubscriptionParameters
.. autoclass:: PushParameters


Functions
---------

.. TODO: Figure out why the parameter isn't being included.
.. autofunction:: generate_message_id
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
