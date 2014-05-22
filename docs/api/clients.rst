:mod:`libtaxii.clients` Module
==========================================
.. module:: libtaxii.clients


Classes
-------

.. autoclass:: HttpClient
	:show-inheritance:
	:members:
	
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
	client.setAuthType(tc.AUTH_NONE)
	client.setUseHttps(False)

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.callTaxiiService2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()

Using Basic HTTP Auth
*********************

.. code-block:: python

	client = tc.HttpClient()
	client.setUseHttps(True)
	client.setAuthType(tc.AUTH_BASIC)
	client.setAuthCredentials({'username': 'MyUsername', 'password': 'MyPassword'})

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.callTaxiiService2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()
	
Using TLS Certificate Auth
**************************

.. code-block:: python

	client = tc.HttpClient()
	client.setUseHttps(True)
	client.setAuthType(tc.AUTH_CERT)
	client.setAuthCredentials({'key_file': '../PATH_TO_KEY_FILE.key', 'cert_file': '../PATH_TO_CERT_FILE.crt'})

	discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
	discovery_xml = discovery_request.to_xml()

	http_resp = client.callTaxiiService2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
	taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
	print taxii_message.to_xml()