Scripts
=======

This page provides documentation on the scripts that are included with libtaxii. All 
clients are configured to use the TAXII Test Server (http://taxiitest.mitre.org) by
default; provide command line options for specifying most aspects of the script (e.g., 
host, port, client certs, username/password, HTTP or HTTPS, etc); and support TAXII 1.1
unless otherwise noted.

Note that the scripts *should* be callable from anywhere on the command line as long as you have
the python scripts directory on your path.

Script Listing
--------------

* **discovery_client** - Issues a Discovery Request to a Discovery Service
* **fulfillment_client** - Issues a Poll Fulfillment Request to a Poll Service and writes the resulting content to file
* **inbox_client** - Issues an Inbox Message with one Content Block to an Inbox Service
* **poll_client** - Issues a Poll Request to a Poll Service and writes the resulting content to file
* **poll_client_10** - Issues a Poll Request to a TAXII 1.0 Poll Service and writes the resulting content to file
* **query_client** - Issues a Query for an IP Address or Hash to a Poll Service and writes the resulting content to file

Common Command Line Arguments
-----------------------------
All scripts use these command line arguments:

* ``-h, --help`` - Shows help text
* ``--host`` - Specifies the host to connect to (e.g., ``taxiitext.mitre.org``)
* ``--port`` - Specifies the port to connect on (e.g., ``80``)
* ``--path`` - Specifies the path portion of the URL to connect to
  (e.g., ``/services/discovery``)
* ``--https`` - Specifies whether to use HTTPS or not (e.g., True or False)
* ``--cert`` - Specifies the file location of the certificate to use for
  authentication. If provided, ``--key`` must also be provided.
* ``--key`` - Specifies the file location of the key to use for authentication.
* ``--username`` - Specifies the username to use for authentication. If
  provided, ``--pass`` must also be provided.
* ``--pass`` - Specifies the password to use for authentication.
* ``--proxy`` - Specifies proxy settings (e.g. ``http://proxy.example.com:80/``,
  or ``noproxy`` to not use any proxy). If omitted, the system's proxy settings
  will be used.
* ``--xml-output`` - Specifies that the XML messages should be printed instead of the default textual representation

For example, to call the discovery_client using all these arguments, you would do: 
``discovery_client --host taxiitest.mitre.org --port 80 --path /services/discovery/ --https False --cert MyCert.crt --key MyKey.key --username foo --pass bar --proxy http://myproxy.example.com:80``

Additional Discovery Client Command Line Arguments
--------------------------------------------------
The Discovery Client does not use any additional command line arguments.

Additional Poll Fulfillment Client Command Line Arguments
---------------------------------------------------------
In addition to the command line arguments listed above, the Poll Fulfillment Client uses these:

* ``--collection`` - The collection being requested
* ``--result_id`` - The result id being requested (required)
* ``--result_part_number`` - The result part number being requested (defaults to 1)

Example: ``fulfillment_client --collection MyCollection --result_id someId --result_part_number 1``

Additional Inbox Client Command Line Arguments
----------------------------------------------
In addition to the command line arguments listed above, the Inbox Client uses these:

* ``--content-binding`` - The Content Binding ID to use for the Content Block (Defaults to STIX XML 1.1)
* ``--subtype`` - The Content Binding ID subtype to use for the Content Block (Optional; Defaults to None)
* ``--content-file`` - The file location (e.g., /tmp/mydata) containing the data to send in the Content Block. Defaults to a built-in STIX 1.1 XML document.
* ``--dcn`` - The Destination Collection Name that is specified in the Inbox Message, requesting that the recipient
  make the sent content available on the specified Destination Collection Name. TAXII supports multiple DCNs, but
  this script only supports one.

Example: ``inbox_client --content-binding urn:stix.mitre.org:xml:1.1 --content-file stix_file.xml``

Additional Poll Client Command Line Arguments
---------------------------------------------
In addition to the command line arguments listed above, the Poll Client uses these:

* ``--collection`` - The Collection Name to Poll. Defaults to 'default'
* ``--begin_timestamp`` - The Begin Timestamp Label to used bound the Poll Request. Defaults to None.
* ``--end_timestamp`` - The End Timestamp Label to used bound the Poll Request. Defaults to None.
* ``--subscription-id`` - The Subscription ID for this Poll Request
* ``--dest-dir`` - The directory to save Content Blocks to. Defaults to the current directory.

Example: ``poll_client --collection MyCollection``

Additional Poll Client 1.0 Command Line Arguments
-------------------------------------------------
In addition to the command line arguments listed above, the Poll Client 1.0 uses these:

* ``--feed`` - The Data Feed to Poll. Defaults to 'default'
* ``--begin_timestamp`` - The Begin Timestamp Label to used bound the Poll Request. Defaults to None.
* ``--end_timestamp`` - The End Timestamp Label to used bound the Poll Request. Defaults to None.
* ``--subscription-id`` - The Subscription ID to use when polling
* ``--dest-dir`` - The directory to save Content Blocks to. Defaults to the current directory.

Example: ``poll_client_10 --feed MyFeedName --subscription-id SomeSubscriptionId``

Additional Query Client Command Line Arguments
----------------------------------------------
In addition to the command line arguments listed above, the Query Client uses these:

* ``--collection`` - The collection to Poll (recall that a query is part of a Poll Request). Defaults to 'default_queryable'.
* ``--allow_asynch`` - Whether asynchronous Polling is supported. Defaults to True (Use the Poll Fulfillment client to request asynchronous results!)
* ``--ip`` - The IP to query on. One of --ip or --hash must be specified.
* ``--hash`` - The file hash to query on. One of --ip or --hash must be specified.
* ``--dest-dir`` - The directory to save Content Blocks to. Defaults to the current directory.

Example: ``query_client --collection MyQueryCollection --ip 10.0.0.0``
