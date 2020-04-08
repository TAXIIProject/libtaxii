ssl_verify_server
=====================

This git branch 'ssl_verify_server' aims to enable the verification of
the TAXII server's certification to the scripts such as poll_client and
discovery_client.

In order to do so,

### to be reviewed.
* new command line option '--verify-server' is added to TaxiiScript class.
* if this option exists, it means "do verification using its value as 
  ca_bundle.txt."
* this option passed to HttpClient instance through create_client().
* HTTPClient.call_taxii_service2 creates LibtaxiiHTTPSHandler.
* LibtaxiiHTTPSHandler creates ssl.SSLContext so that verify-server option 
  added to the context too.
* in VerifiableHTTPSConnection.connect() 
