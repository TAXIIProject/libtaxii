#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import httplib
import base64
import uuid

class TaxiiClient:

    #Constants for authentication types
    AUTH_NONE = 0#Do not offer any authentication credentials to the server
    AUTH_BASIC = 1#Offer basic authentication credentials to the server
    AUTH_CERT = 2#Offer certificate based authentication credentials to the server

    def __init__(self):
        self.auth_type = TaxiiClient.AUTH_NONE
        self.auth_credentials = {}
        self.use_https = False

    #Set the authentication type. Must be one of AUTH_NONE, AUTH_BASIC, or AUTH_CERT
    #Setting the authentication type clears any credentials that have been set
    def setAuthType(self, auth_type):
        #If this isn't a change, don't do anything
        if self.auth_type == auth_type:
            return

        if auth_type == TaxiiClient.AUTH_NONE:
            self.auth_type = TaxiiClient.AUTH_NONE
        elif auth_type == TaxiiClient.AUTH_BASIC:
            self.auth_type = TaxiiClient.AUTH_BASIC
        elif auth_type == TaxiiClient.AUTH_CERT:
            self.auth_type = TaxiiClient.AUTH_CERT
        else:
            raise Exception('Invalid auth_type specified. Must be one of TaxiiClient AUTH_NONE, AUTH_BASIC, or AUTH_CERT')

    def setUseHttps(self, bool):
        if bool == True:
            self.use_https = True
        elif bool == False:
            self.use_https = False
        else:
            raise('Invalid argument value. Must be a boolean value of \'True\' or \'False\'.')

    #This sets the authentication credentials to be used later when making a request.
    #note that it is possible to pass in one dict containing all credentials and swap between
    #auth types.
    def setAuthCredentials(self, auth_credentials_dict):
        if self.auth_type == TaxiiClient.AUTH_NONE:
            self.auth_credentials = auth_credentials_dict
        elif self.auth_type == TaxiiClient.AUTH_BASIC:
            if 'username' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'username\' is not present')
            if 'password' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'password\' is not present')
            self.auth_credentials = auth_credentials_dict
        elif self.auth_type == TaxiiClient.AUTH_CERT:
            if 'key_file' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'key_file\' is not present')
            if 'cert_file' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'cert_file\' is not present')
            self.auth_credentials = auth_credentials_dict

    #Wrapper method for callTaxiiService
    #Calls a Poll service, does some 'nice' things
    #Host is the hostname of the server
    #Path is the path portion of the URL.
    #Port is the port to connect to. Code will assume 80 for http, 443 for https if not specified
    #excl_begin_ts - begin timestamp of the range; exclusive
    #incl_end_ts - end timestamp of the range; inclusive
    #subs_id - subscription ID, if specified
    #payload_bindings - a list of payload bindings.
    def callPollService(self, host, path, feed_name, port=None, excl_begin_ts=None, incl_end_ts=None, subs_id=None, payload_bindings=None):
        params = {}
        params['message_id'] = uuid.uuid4().hex
        params['message_type'] = 'poll_request'
        params['feed_name'] = feed_name
        if excl_begin_ts is not None: params['exclusive_begin_timestamp'] = excl_begin_ts
        if incl_end_ts is not None: params['inclusive_end_timestamp'] = incl_end_ts
        if payload_bindings is not None: params['payload_binding'] = ','.join(payload_bindings)
        if subs_id is not None: params['subscription_id'] = subs_id
        return self.callTaxiiService(host, path, 'GET', port, None, params)

    #Wrapper method for callTaxiiService
    #Calls a discovery service, does some 'nice' things
    #Host is the hostname of the server
    #Path is the path portion of the URL.
    #Port is the port to connect to. Code will assume 80 for http, 443 for https if not specified
    def callDiscoveryService(self, host, path, port=None):
        params = {}
        params['message_id'] = uuid.uuid1().hex
        params['message_type'] = 'discovery_request'
        return self.callTaxiiService(host, path, 'GET', port, None, params)

    #Wrapper method for callTaxiiService
    #Calls an inbox service
    def callInboxService(self, host, path, inbox_xml, port=None):
        return self.callTaxiiService(host, path, 'POST', port, inbox_xml, None)

    #TODO: Implement the feed management stuff

    #url, hostname, post/get, xml, get params
    def callTaxiiService(self, host, path, method, port=None, post_data=None, get_params_dict=None):

        if port is None:#If the caller did not specify a port, use the default
            if self.use_https:
                port = 443
            else:
                port = 80

        if get_params_dict is not None:#Add the query params to the URL
            tmp = []
            for k, v in get_params_dict.iteritems():
                tmp += '&%s=%s' % (k, v)
            tmp[0] = '?'
            path += "".join(tmp)

        header_dict = {'Content-Type': 'application/xml',
                       'User-Agent': 'taxiilib.taxiiclient'}

        if self.use_https:
            header_dict['X-TAXII-Protocol'] = 'TAXII_HTTPS_1.0'
            if self.auth_type == TaxiiClient.AUTH_NONE:
                conn = httplib.HTTPSConnection(host, port)
            elif self.auth_type == TaxiiClient.AUTH_BASIC:
                base64string = base64.encodestring('%s:%s' % (self.auth_credentials['username'], self.auth_credentials['password']))
                header_dict['Authorization'] = 'Basic %s' % base64string
                conn = httplib.HTTPSConnection(host, port)
            else:#AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPSConnection(host, port, key_file, cert_file)
        else:#Not using https
            header_dict['X-TAXII-Protocol'] = 'TAXII_HTTP_1.0'
            if self.auth_type == TaxiiClient.AUTH_NONE:
                conn = httplib.HTTPConnection(host, port)
            #TODO: Consider deleting because this is a terrible idea
            elif self.auth_type == TaxiiClient.AUTH_BASIC:#Sending credentials in cleartext.. tsk tsk
                base64string = base64.encodestring('%s:%s' % (self.auth_credentials['username'], self.auth_credentials['password']))
                header_dict['Authorization'] = 'Basic %s' % base64string
                conn = httplib.HTTPConnection(host, port)
            else:#AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPConnection(host, port, key_file, cert_file)

        if method == 'POST':
            header_dict['Content-Type'] = 'application/xml'
            header_dict['X-TAXII-Content-Type'] = 'TAXII_1.0/TAXII_XML_1.0'
            req = conn.request('POST', path, post_data, headers=header_dict)
        elif method == 'GET':
            req = conn.request('GET', path, headers=header_dict)
        else:
            raise('HTTP Method was %s, rather than POST or GET. Must be POST or GET' % method)

        response = conn.getresponse()
        return response
