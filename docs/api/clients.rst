:mod:`libtaxii.clients` Module
==========================================
.. module:: libtaxii.clients


Classes
-------

.. autoclass:: HttpClient
    :members: set_auth_type, set_auth_credentials, set_proxy, set_use_https,
              set_verify_server, call_taxii_service, call_taxii_service2


Examples
--------

TAXII clients have three types of authentication credentials: None, HTTP Basic, and TLS Certificate. This section demonstrates usage of all three auth types.

All examples assume the following imports:

	.. code-block:: python
	
		import libtaxii as t
		import libtaxii.messages as tm
		import libtaxii.clients as tc
		from dateutil.tz import tzutc

Using No Credentials
********************

.. code-block:: python

	client = tc.HttpClient()
	client.set_auth_type(tc.AUTH_NONE)
	client.set_use_https(False)

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.call_taxii_service2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()

Using Basic HTTP Auth
*********************

.. code-block:: python

	client = tc.HttpClient()
	client.set_use_https(True)
	client.set_auth_type(tc.AUTH_BASIC)
	client.set_auth_credentials({'username': 'MyUsername', 'password': 'MyPassword'})

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.call_taxii_service2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()
	
Using TLS Certificate Auth
**************************

.. code-block:: python

	client = tc.HttpClient()
	client.set_use_https(True)
	client.set_auth_type(tc.AUTH_CERT)
	client.set_auth_credentials({'key_file': '../PATH_TO_KEY_FILE.key', 'cert_file': '../PATH_TO_CERT_FILE.crt'})

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.call_taxii_service2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()
