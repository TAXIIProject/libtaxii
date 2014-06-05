Release Notes
=============

1.1.101
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.100...1.1.101>`__

Lots of changes in this release, including some important bug fixes.

-  The equals method for all TAXII Messages was fixed (previous it would
   incorrectly return True in many cases).
-  Fixed various serialization/deserialization issues uncovered by the now
   correctly implemented equals methods.
-  Added a defined Content-Type for TAXII XML 1.1.
-  Corrected the value of ST\_UNSUPPORTED\_PROTOCOL.
-  Fixed a bug when parsing non-TAXII responses.
-  Fixed a bug where the Subscription ID was not allowed to be none in
   ManageFeedSubscriptionRequest (The Subscription ID must be None for
   subscription requests with an action of SUBSCRIBE).
-  Fixed a bug where DeliveryParameters were not permitted to be None in a
   ManageFeedSubscriptionRequest.
-  Added code to permit the setting of certain HTTP Headers (Accept,
   X-TAXII-Accept).
-  Improved libtaxii's handling of non-XML content that looks like XML
-  Added Constants for TAXII Headers (and updated the code to use them).
-  Improved handling of non-registered Query formats (now an exception is
   raised; previously None was returned).
-  libtaxii now provides an X-TAXII-Services header.


1.1.100
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.107...1.1.100>`__

*This version contains known bugs. Use a more recent version of libtaxii
when possible.*

-  First release that supports TAXII 1.1.
-  No changes to TAXII 1.0 code.
-  Added documentation for Messages 1.1 API and TAXII Default Query.


1.0.107
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.106...1.0.107>`__

-  Fixed an issue that was causing invalid TAXII XML to be generated
   (Thanks [@JamesNK](https://github.com/JamesNK)).
-  Fixed an issue in the messages test suite that caused the invalid XML
   to not be caught.


1.0.106
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.105...1.0.106>`__

-  Added validation to messages.py. This should not cause any backwards
   compatibility issues, but there may be things we didn't catch. Please
   report any instances of this via the issue tracker.
-  Modified the internals of ``from_dict()`` and ``from_xml()`` in many
   cases to support how validation now works.
-  Added constructor arguments to HttpClient. Default behavior is still
   the same.
-  Added the ability to specify whether or not an HTTP Server's SSL
   Certificate should be verified.
-  Prettified some of the documentation.
-  Added documentation in certain places where there was none previously.


1.0.105
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.104...1.0.105>`__

-  Added support for JSON (Thanks to [@ics](https://github.com/ics),
   Alex Ciobanu of CERT EU).
-  callTaxiiService2 now supports user-specified content\_types (Thanks
   to Alex Ciobanu of CERT EU).
-  Fixed `Issue #18 <https://github.com/TAXIIProject/libtaxii/issues/18>`__,
   libtaxii.messages now permits users to specify any lxml parser for
   parsing XML. A default parser is used when one is not specified,
   which is unchanged from previous usage.


1.0.104
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.103...1.0.104>`__

-  Many of the comments were aligned with PEP8 guidelines (thanks
   [@gtback](https://github.com/gtback)!)
-  Added a new authentication mechanism (AUTH\_CERT\_BASIC) to
   clients.py. This authentication mechanism supports Certificate
   Authentication plus HTTP Basic authentication.
-  Added clients.HttpClient.callTaxiiService2, which supersedes
   callTaxiiService. The previous version of callTaxiiService couldn't
   handle proxies well, which now have better support.
-  Added better proxy support to client.HttpClient via the setProxy()
   function.


1.0.103
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.102...1.0.103>`__

This version fixes a schema validation bug. Schema validation did not work
prior to this version.


1.0.102
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.101...1.0.102>`__

This version adds better proxy support to libtaxii in libtaxii.clients.  A
function to set a proxy (setProxy) was added as well as a new callTaxiiService2
function that can properly use proxies. The original callTaxiiService function
did not support proxies well. The APIs have the full documentation for
callTaxiiService, callTaxiiService2, and setProxy (`Client API
<https://github.com/TAXIIProject/libtaxii/wiki/Clients-API>`__).


1.0.101
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.100...1.0.101>`__

This version added missing source files for distribution on PyPI. No
functionality changes were made.


1.0.100
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.090...1.0.100>`__

Version 1.0.100 represents the first TAXII 1.0 compliant version of libtaxii.
This version removes all code not compliant with TAXII 1.0.


1.0.090
-------

`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.0.000draft...1.0.090>`__

This version of libtaxii has components that are TAXII 1.0 conformant and
experimental functionality that conforms to a draft version of TAXII. This
version should only be used to transition from 1.0.000draft to 1.0.100.


1.0.000draft
------------

This version of libtaxii represents experimental functionality that conforms to
a draft version of TAXII. This code should no longer be used. For those using
this code, you should upgrade to 1.0.090 and migrate your code to use the TAXII
1.0 components, then transition to 1.0.100.
