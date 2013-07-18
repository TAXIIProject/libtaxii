Getting Started
====================================

This page gives an introduction to libtaxii and how to use it. Please note that this page is being actively worked on and feedback is welcome.

libtaxii
========
libtaxii contains the following components:

* **libtaxii\\__init__.py** - Interface for methods that span messages.py and clients.py. Defines constants applicable to both TAXII Messages and TAXII Clients.
* **libtaxii\\messages.py** - Interface for handling TAXII Messages, creating the XML representation of a TAXII Message, and parsing the XML representation of a TAXII Message. Defines constants relevant to TAXII Messages.
* **libtaxii\\clients.py** - Interface for a TAXII HTTP and HTTPS client. Defines constants relevant to TAXII HTTP Clients

Messages Class Structure (messages.py)
--------------------------------------
In messages.py, each TAXII Message has a corresponding class (e.g., There is a DiscoveryRequest class for the Discovery Request message). In addition, other classes exist where appropriate. If a class can only exist with the context of a specific TAXII Message (e.g., a ServiceInstance can only exist in a DiscoveryResponse), that class (ServiceInstance) is a subclass of the message class (DiscoveryResponse). If a class can exist across multiple messages (e.g., ContentBlock can exist in both PollResponse and InboxMessage) it exists as a peer to TAXII Messages.

This example demonstrates how classes in messages.py are organized. This code won't work unless proper constructor arguments are used:

.. code:: python
    
    import libtaxii.messages as tm
    # Constructor arguments omitted for brevity. See tests/messages_test.py for real code examples
    discovery_request = tm.DiscoveryRequest( ... ) # Message classes are first-order
    service_instance = tm.DiscoveryRequest.ServiceInstance( ... ) # Message specific classes are 
                                                                  # a child class of the message class
    content_block = tm.ContentBlock( ... ) # Classes not specific to one message are peers to TAXII Messages

Messages Serialization and Deserialization (messages.py)
--------------------------------------------------------

Each class in messages.py has serialization/deserializatoin methods that support XML Strings, Python 
Dictionaries, and LXML Etrees. All ``from_<format>()`` (e.g., ``from_xml()``) methods are class methods 
and should be called on the class (e.g., ``tm.DiscoveryRequest.from_xml(xml_string)``). All 
``to_<format>()`` (e.g., ``to_xml()``) methods are instance methods and should be 
called on a particular instance of an object (e.g., ``discovery_request.to_xml()``)  

Each class in messages.py has the following:  

* ``from_xml(xml_string)`` - Creates an instance of the class from an XML String
* ``to_xml()`` - Creates the XML representation of an instance of a class
* ``from_dict(dictionary)`` - Creates an instance of the class from a Python dictionary
* ``to_dict()`` - Creates the Python dictionary representation of an instance of a class
* ``from_etree(lxml_etree)`` - Creates an instance of the class from an LXML Etree
* ``to_etree()`` - Creates the LXML Etree representation of an instance of a class

To create a TAXII Message from XML:  

.. code:: python

    xml_string = '<taxii:Discovery_Response ... />'#Not real XML
    discovery_response = tm.DiscoveryResponse.from_xml(xml_string)


To create an XML string from a TAXII Message:  

.. code:: python

    new_xml_string = discovery_response.to_xml()  

The same paradigm applies for Python dictionaries:

.. code:: python

    msg_dict = { ... }#Not a real dictionary
    discovery_response = tm.DiscoveryResponse.from_dict(msg_dict)
    new_dict = discovery_response.to_dict()

and lxml etrees:

.. code:: python

    msg_etree = etree.Element( ... ) #Not a real etree
    discovery_response = tm.DiscoveryResponse.from_etree(msg_etree)
    new_etree = discovery_response.to_etree()

Clients (clients.py)
--------------------
clients.py contains a single class, HttpClient. The HttpClient class is capable of invoking TAXII Services both over HTTP and HTTPS. Additionally, HttpClient provides a mechanism for using HTTP Basic and TLS Certificate authentication.  
The Clients portion of libtaxii is a fairly straightforward wrapper around httplib.

Example usage of clients:

.. code:: python

    import libtaxii as t
    import libtaxii.clients as tc
    import libtaxii.messages as tm

    client = tc.HttpClient()
    client.setAuthType(tc.AUTH_BASIC)
    client.setUseHttps(True)
    client.setAuthCredentials({'username': 'MyUsername', 'password': 'MyPassword'})

    discovery_request = tm.DiscoveryRequest(tm.generate_message_id())
    discovery_xml = discovery_request.to_xml()

    http_resp = client.callTaxiiService2('example.com', '/pollservice/', t.VID_TAXII_XML_10, discovery_xml)
    taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
    print taxii_message.to_xml()
