:mod:`libtaxii` Module
=======================
.. module:: libtaxii

Constants
---------

Version IDs
***********

The following constants can be used as TAXII Version IDs

.. autodata:: VID_TAXII_SERVICES_10
.. autodata:: VID_TAXII_SERVICES_11
.. autodata:: VID_TAXII_XML_10
.. autodata:: VID_TAXII_XML_11
.. autodata:: VID_TAXII_HTTP_10
.. autodata:: VID_TAXII_HTTPS_10

The following are third-party Version IDs included in libtaxii for convenience.

.. autodata:: VID_CERT_EU_JSON_10


Content Binding IDs
*******************

The following constants should be used as the Content Binding ID for STIX XML.

.. autodata:: CB_STIX_XML_10
.. autodata:: CB_STIX_XML_101
.. autodata:: CB_STIX_XML_11

These other Content Binding IDs are included for convenience as well.

.. autodata:: CB_CAP_11
.. autodata:: CB_XENC_122002


Functions
---------

.. autofunction:: get_message_from_http_response
