Getting Started
===============

This page gives an introduction to **libtaxii** and how to use it.  Please note
that this page is being actively worked on and feedback is welcome.


Modules
-------

The libtaxii library contains the following modules:

* **libtaxii** - Contains version info and some methods for getting TAXII Messages
  from HTTP responses. (Implemented in ``libtaxii/__init__.py``)
* **libtaxii.clients.** - TAXII HTTP and HTTPS clients. (Implemented in
  ``libtaxii/clients.py``)
* **libtaxii.common** - Contains functions and classes useful for all versions of TAXII
* **libtaxii.constants** - Contains constants for TAXII
* **libtaxii.messages_10** - Creating, handling, and parsing TAXII 1.0
  messages. (Implemented in ``libtaxii/messages_10.py``)
* **libtaxii.messages_11** - Creating, handling, and parsing TAXII 1.1
  messages. (Implemented in ``libtaxii/messages_11.py``)
* **libtaxii.taxii_default_query** - Creating, handling and parsing TAXII
  Default Queries. (Implemented in ``libtaxii/taxii_default_query.py``) *New in
  libtaxii 1.1.100*.
* **libtaxii.validation** - Common data validation functions used across
  libtaxii. (Implemented in ``libtaxii/validation.py``)

TAXII Messages Module Structure
-------------------------------

In the TAXII message modules (:py:mod:`libtaxii.messages_10` and
:py:mod:`libtaxii.messages_11`), there is a class corresponding to each type of
TAXII message.  For example, there is a ``DiscoveryRequest`` class for the
Discovery Request message:

.. code:: python

    import libtaxii.messages_11 as tm11
    discovery_request = tm11.DiscoveryRequest( ... )

For types that can been used across multiple messages (e.g., a Content Block
can exist in both Poll Response and Inbox Message), the corresponding class
(``ContentBlock``) is (and always has always been) defined at the module level.

.. code:: python

    content_block = tm11.ContentBlock( ... )

Other types that are used exclusively within a particular TAXII message type
were previously defined as nested classes on the corresponding message class;
however, they are now defined at the top level of the module.  For example, a
Service Instance is only used in a Discovery Response message, so the class
representing a Service Instance, now just ``ServiceInstance``, was previously
``DiscoveryResponse.ServiceInstance``. The latter name still works for backward
compatibilty reasons, but is deprecated and may be removed in the future.

.. code:: python

    service_instance = tm11.ServiceInstance( ... )
    service_instance = tm11.DiscoveryRequest.ServiceInstance( ... )

See the :ref:`API Documentation <apidoc>` for proper constructor arguments for
each type above.


TAXII Message Serialization and Deserialization
-----------------------------------------------

Each class in the message modules has serialization and deserialization methods
for XML Strings, Python dictionaries, and LXML ElementTrees.  All serialization
methods (``to_*()``) are instance methods called on specific objects (e.g.,
``discovery_request.to_xml()``). Deserialization methods (``from_*()``) are
class methods and should be called on the class itself (e.g.,
``tm11.DiscoveryRequest.from_xml(xml_string)``).

Each class in messages.py defines the following:

* ``from_xml(xml_string)`` - Creates an instance of the class from an XML String.
* ``to_xml()`` - Creates the XML representation of an instance of a class.
* ``from_dict(dictionary)`` - Creates an instance of the class from a Python dictionary.
* ``to_dict()`` - Creates the Python dictionary representation of an instance of a class.
* ``from_etree(lxml_etree)`` - Creates an instance of the class from an LXML Etree.
* ``to_etree()`` - Creates the LXML Etree representation of an instance of a class.

To create a TAXII Message from XML:

.. code:: python

    xml_string = '<taxii:Discovery_Response ... />'  # Note: Invalid XML
    discovery_response = tm11.DiscoveryResponse.from_xml(xml_string)

To create an XML string from a TAXII Message:

.. code:: python

    new_xml_string = discovery_response.to_xml()

The same approach can be used for Python dictionaries:

.. code:: python

    msg_dict = { ... }  # Note: Invalid dictionary syntax
    discovery_response = tm11.DiscoveryResponse.from_dict(msg_dict)
    new_dict = discovery_response.to_dict()

and for LXML ElementTrees:

.. code:: python

    msg_etree = etree.Element( ... )  # Note: Invalid Element constructor
    discovery_response = tm11.DiscoveryResponse.from_etree(msg_etree)
    new_etree = discovery_response.to_etree()

Schema Validating TAXII Messages
--------------------------------
You can use libtaxii to Schema Validate XML, etree, and file representations of TAXII Messages.
XML Schema validation cannot be performed on a TAXII Message Python object, since XML Schema validation
can only be performed on XML.

A full code example of XML Schema validation can be found in :ref:`API Documentation <apivalidation>`


TAXII Clients
-------------

The **libtaxii.clients** module defines a single class ``HttpClient`` capable
of invoking TAXII services over both HTTP and HTTPS.  The client is a fairly
straighforward wrapper around Python's builtin ``httplib`` and supports the use
of of both HTTP Basic and TLS Certificate authentication.

Example usage of clients:

.. code:: python

    import libtaxii as t
    import libtaxii.clients as tc
    import libtaxii.messages_11 as tm11
    from libtaxii.constants import *

    client = tc.HttpClient()
    client.set_auth_type(tc.HttpClient.AUTH_BASIC)
    client.set_use_https(True)
    client.set_auth_credentials({'username': 'MyUsername', 'password': 'MyPassword'})

    discovery_request = tm11.DiscoveryRequest(tm11.generate_message_id())
    discovery_xml = discovery_request.to_xml()

    http_resp = client.call_taxii_service2('example.com', '/pollservice/', VID_TAXII_XML_11, discovery_xml)
    taxii_message = t.get_message_from_http_response(http_resp, discovery_request.message_id)
    print taxii_message.to_xml()
