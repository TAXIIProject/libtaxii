Release Notes
=============

1.1.106
-------
`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.105...1.1.106>`__

- Thank you to the multiple contributors for this release: @traut, @gtback, @wbolster, and @MarkDavidson, and thank you to those who filed issues that were fixed in this release.
- Timestamp labels can now be provided as a string or as a python datetime object. Previously, only datetime objects were permitted.
- Some big changes to TAXII Client command line args. Deprecated URL compenents (e.g., --host, --port) in favor of specifying a single url (--url)
- Added a TAXII Inbox 1.0 client
- Decreased the likelihood of future message ID collisions
- A variety of improvements in the following areas: data validation, typos, documentation, DRY-ness, overall repo quality (thanks @gtback)
- Multiple code cleanup changes (Thanks in part to @traut of IntelWorks)

1.1.105
-------
`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.104...1.1.105>`__

- Fixed multiple XML parsing related vulnerabilities (Thanks @guidovranken of IntelWorks for the vulnerability research!)

1.1.104
-------
`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.103...1.1.04>`__

- Fixed a bug where libtaxii did not properly handle XML values for Extended Headers
- Added checking for required status detail keys in Status Messages
- Improved data validation in various places, fixed various bugs, and improved documentation
- Improved filename generation in scripts (Thanks @guidovranken!)

1.1.103
-------
`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.102...1.1.103>`__

In terms of code organization, there are a few big changes beginning to
take place in this version of libtaxii. Constants and commonly used classes/functions
are being moved to common locations (libtaxii.constants and libtaxii.common, respectively).
Also, nested classes (e.g., messages_11.DiscoveryResponse.ServiceInstance) have been de-nested
(e.g., is now messages_11.ServiceInstance). All of these changes are intended to make
using libtaxii easier. For the time being, backward compatibility has been maintained, but
many of these changes may result in a backward compatibility breaking change in a future,
major release of libtaxii.

Major changes:

- libtaxii.constants, a new source file, was created. The definition for all constants in libtaxii have been moved to libtaxii.constants. Aliases to the previous definition locations have been retained for backward compatibility and may be removed in a future major release.
- libtaxii.common, a new source file for containing classes and methods common to TAXII, was created. Some common classes and functions have been moved into libtaxii.common, and more will be moved over time. Aliases to the previous classes and functions have been retained for backward compatibility and may be removed in a future major release. (Thanks, @gtback!)
- Promoted nested classes to module-level classes in messages_10, messages_11, and taxii_default_query.  Aliases to the previous, nested, classes have been retained for backward compatibility and may be removed in a future major release. (Thanks, @gtback!)
- A ‘to_text()’ method has been added to all TAXII Message classes. ‘to_text()’ provides a “nicely formatted” human readable representation of a TAXII Message and its components. The ‘to_text()’ method was added to support libtaxii’s scripts. There is no ‘from_text()’ method as this is not intended to be a serialization/deserialization feature, but a readability feature.
- Lowered the required version of lxml to 2.2.3, the latest available on RHEL 6. (Thanks to @mblayman for raising this)
- Lowered the required version of python-dateutil to 1.4.1, the latest available on RHEL 6. (Thanks to @mblayman for raising this)
- TAXII 1.1 StatusMessages now raise a ValueError when required a Status Detail is not set.
- TAXII XML Validation has a new methodology: See validation.SchemaValidator (http://libtaxii.readthedocs.org/en/latest/api/validation.html#libtaxii.validation.SchemaValidator)
- Related: validate_xml(…) has been deprecated and may be removed in a future major release.

Minor changes:

- Tons of PEP8 improvements (Thanks, @gtback!)
- TAXII Scripts have been entirely reorganized to be more DRY.
- Added two constants for Proxy Settings (SYSTEM_PROXY and NO_PROXY). These supersede the need to use either None or ‘noproxy’, which were not as clear to developers.
- Improved documentation, Tox usage, and Travis-CI usage. (Thanks, @gtback!)
- SMIME Content Binding added (application/x-pks7-mime)
- For Python 2.6, argparse is now a requirement
- Added constants for TAXII Default Query Parameters and Relationships

Bug fixes:

- In messages_11.PollResponse, the result_part_number parameter is now set by the constructor. 


1.1.102
-------
`(diff) <https://github.com/TAXIIProject/libtaxii/compare/1.1.101...1.1.102>`__

The biggest change was the addition of scripts to libtaxii. Now when you install libtaxii, you get
a number of scripts that are by default configured to hit the TAXII Test server (taxiitest.mitre.org).
You can specify a number of parameters on the command line to change where/how the scripts connect.
The scripts are:

-  discovery_client - Calls a TAXII 1.1 Discovery Service
-  fulfillment_client - Calls a TAXII 1.1 Poll Service for Poll Fulfillment
-  inbox_client - Calls a TAXII 1.1 Inbox Service. Comes packaged with a STIX document to use by default.
-  poll_client - Calls a TAXII 1.1 Poll Service
-  poll_client_10 - Calls a TAXII 1.0 Poll Service (Note: Does not work with taxiitest.mitre.org, as taxiitest.mitre.org is TAXII 1.1 only)
-  query_client - Calls a TAXII 1.1 Poll Service with a query on IP or File Hash (Note: As of 6/11/2014; Works with the master branch of YETI, and will work with YETI after the next release of YETI)

We also had a number of bug fixes and impprovements for this version of libtaxii:

-  Unicode strings work round trip (Hat tip to Ben Yates for reporting the issue)
-  Added TONS of documentation (http://libtaxii.readthedocs.org/en/latest/index.html). Big thanks to @gtback and @slsnow!
-  Fixed some issues in ContentBlock.content where certain data was not serializing/deserializing properly
-  Streamlined serialization of XML documents to avoid a double-parse in certain cases
-  Added a Content Binding ID for STIX XML 1.1.1
-  Added an optional pretty_print argument to all to_xml() functions. e.g., to_xml(pretty_print=True)
-  Added the three TAXII Default Query Status Type to libtaxii.taxii_default_query
-  Fixed a bug where custom Status Types were prohibited
-  Added Travis CI

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
