""" 
| Copyright (C) 2013 - The MITRE Corporation
| For license information, see the LICENSE.txt file

| Contributors:
 
* Alex Ciobanu - calex@cert.europa.eu  
* Mark Davidson - mdavidson@mitre.org  

"""

import httplib
import urllib
import urllib2
import base64
import uuid
import socket
import ssl
import libtaxii as t

class HttpClient:

    #Constants for authentication types
    AUTH_NONE = 0  # Do not offer any authentication credentials to the server
    AUTH_BASIC = 1  # Offer HTTP Basic authentication credentials to the server
    AUTH_CERT = 2  # Offer certificate based authentication credentials to the server
    AUTH_CERT_BASIC = 3  # Offer certificate based auth and HTTP Basic credentials

    #Proxy Constants
    PROXY_HTTP = 'http'
    PROXY_HTTPS = 'https'
    
    #Header Constants
    HEADER_ACCEPT = 'accept'
    HEADER_CONTENT_TYPE = 'content-type'
    HEADER_X_TAXII_ACCEPT = 'x-taxii-accept'
    HEADER_X_TAXII_CONTENT_TYPE = 'x-taxii-content-type'
    HEDAER_X_TAXII_PROTOCOL = 'x-taxii-protocol'
    HEADER_X_TAXII_SERVICES = 'x-taxii-services'

    def __init__(self, auth_type=AUTH_NONE, auth_credentials=None, use_https=False):
        self.use_https = use_https
        self.auth_type = auth_type
        self.auth_credentials = {}
        if auth_credentials is not None:
            self.setAuthCredentials(auth_credentials)
        #These cannot currently be set in the constructor
        self.proxy_type = None
        self.proxy_string = None
        self.verify_server = False
        self.ca_file = None

    def setAuthType(self, auth_type):
        """Set the authentication type.

        Must be one of AUTH_NONE, AUTH_BASIC, or AUTH_CERT
        """
        #If this isn't a change, don't do anything
        if self.auth_type == auth_type:
            return

        if auth_type == HttpClient.AUTH_NONE:
            self.auth_type = HttpClient.AUTH_NONE
        elif auth_type == HttpClient.AUTH_BASIC:
            self.auth_type = HttpClient.AUTH_BASIC
        elif auth_type == HttpClient.AUTH_CERT:
            self.auth_type = HttpClient.AUTH_CERT
        elif auth_type == HttpClient.AUTH_CERT_BASIC:
            self.auth_type = HttpClient.AUTH_CERT_BASIC
        else:
            raise Exception('Invalid auth_type specified. Must be one of HttpClient AUTH_NONE, AUTH_BASIC, or AUTH_CERT')

    def setVerifyServer(self, verify_server=False, ca_file=None):
        """
        Tell libtaxii whether to verify the server's ssl certificate 
        using the provided ca_file.
        """
        if verify_server and ca_file is None:
            raise ValueError('If verify_server is True, ca_file must not be None.')
        
        self.verify_server=verify_server
        self.ca_file=ca_file

    @property
    def basic_auth_header(self):
        """Returns a Base64-encoded HTTP Basic Authorization Header."""
        return "Basic " + base64.b64encode('%s:%s' % (
                                           self.auth_credentials['username'],
                                           self.auth_credentials['password']))

    def setProxy(self, proxy_string=None, proxy_type=PROXY_HTTP):
        """
        Set the proxy settings to use when making a connection.

        Arguments:
        * proxy_string - a string like 'http://proxy.example.com:80'
          If set to None, use the system proxy.
          If set to 'noproxy', don't use a proxy (even the system proxy)
        * proxy_type - either PROXY_HTTP or PROXY_HTTPS
        """
        self.proxy_string = proxy_string
        self.proxy_type = proxy_type
    
    def setUseHttps(self, bool):
        if bool == True:
            self.use_https = True
        elif bool == False:
            self.use_https = False
        else:
            raise Exception('Invalid argument value. Must be a boolean value of \'True\' or \'False\'.')
    
    def setAuthCredentials(self, auth_credentials_dict):
        """Set the authentication credentials used later when making a request.

        Note that it is possible to pass in one dict containing credentials for
        different authentication types and swap between them later.
        """
        if self.auth_type == HttpClient.AUTH_NONE:
            req_fields = []
        elif self.auth_type == HttpClient.AUTH_BASIC:
            req_fields = ['username', 'password']
        elif self.auth_type == HttpClient.AUTH_CERT:
            req_fields = ['key_file', 'cert_file']
        elif self.auth_type == HttpClient.AUTH_CERT_BASIC:
            req_fields = ['key_file', 'cert_file', 'username', 'password']

        for k in req_fields:
            if k not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field %s is not present' % k)
        self.auth_credentials = auth_credentials_dict
    
    def callTaxiiService(self, host, path, message_binding, post_data, port=None, get_params_dict=None):
        if port is None:  # If the caller did not specify a port, use the default
            if self.use_https:
                port = 443
            else:
                port = 80

        if get_params_dict is not None:  # Add the query params to the URL
            path += '?' + urllib.urlencode(get_params_dict)

        header_dict = {'Content-Type': 'application/xml',
                       'User-Agent': 'libtaxii.httpclient'}

        if self.auth_type == HttpClient.AUTH_CERT_BASIC:
                raise Exception('AuthType AUTH_CERT_BASIC not supported by callTaxiiService. Use callTaxiiService2.')

        if self.use_https:
            header_dict['X-TAXII-Protocol'] = t.VID_TAXII_HTTPS_10
            if self.auth_type == HttpClient.AUTH_NONE:
                conn = httplib.HTTPSConnection(host, port)
            elif self.auth_type == HttpClient.AUTH_BASIC:
                header_dict['Authorization'] = self.basic_auth_header
                conn = httplib.HTTPSConnection(host, port)
            else:  # AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPSConnection(host, port, key_file, cert_file)
        else:  # Not using https
            header_dict['X-TAXII-Protocol'] = t.VID_TAXII_HTTP_10
            if self.auth_type == HttpClient.AUTH_NONE:
                conn = httplib.HTTPConnection(host, port)
            #TODO: Consider deleting because this is a terrible idea
            elif self.auth_type == HttpClient.AUTH_BASIC:  # Sending credentials in cleartext.. tsk tsk
                header_dict['Authorization'] = self.basic_auth_header
                conn = httplib.HTTPConnection(host, port)
            else:  # AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPConnection(host, port, key_file, cert_file)

        header_dict['Content-Type'] = 'application/xml'
        header_dict['X-TAXII-Content-Type'] = message_binding

        req = conn.request('POST', path, post_data, headers=header_dict)
        response = conn.getresponse()

        return response

    def callTaxiiService2(self, host, path, message_binding, post_data, port=None, get_params_dict=None,
                          content_type=None, headers=None):
        """New method of calling a TAXII Service

        Note: this uses urllib2 instead of httplib, and therefore returns
        a different kind of object than callTaxiiService.
        """
        
        header_dict = {}
        
        if headers is not None:
            for k, v in headers.iteritems():
                header_dict[k.lower()] = v
            
        
        header_dict['User-Agent'] = 'libtaxii.httpclient'
        header_dict[HttpClient.HEADER_X_TAXII_CONTENT_TYPE] = message_binding

        content_type_map = {t.VID_TAXII_XML_10: 'application/xml',
                            t.VID_TAXII_XML_11: 'application/xml',
                            t.VID_CERT_EU_JSON_10: 'application/json'}
        
        if content_type is not None:#Set the content type to the user-provided value
            header_dict[HttpClient.HEADER_CONTENT_TYPE] = content_type
        else:#If the user did not provide a value, attempt to find a known value
            if message_binding not in content_type_map:
                raise ValueError("content_type not specified, and the message_binding is unrecognized")
            header_dict[HttpClient.HEADER_CONTENT_TYPE] = content_type_map[message_binding]
        
        #States of Accept and X-TAXII-Accept headers:
        #
        # 1. Accept and X-TAXII-Accept headers both set.
        #    - Do nothing. Assume user knows what they are doing
        #
        # 2. Accept header set and X-TAXII-Accept header not set
        #    - Do nothing. Assume user knows what they are doing
        #
        # 3. Accept header not set and X-TAXII-Accept header set
        #    - Do nothing. Bad practice, but not invalid. 
        #      Assume user knows what they are doing.
        #
        # 4. Accept header not set and X-TAXII-Accept header not set
        #    - User hasn't specified anything. In this case, default behavior is: 
        #      Accept = Content-Type and
        #      X-TAXII-Accept = X-TAXII-Content-Type.
        #      This means that the client will only accept messages
        #      in the same format that was sent.
        #
        # 5. Users of libtaxii that wish to accept everything should set the 
        #    Accept header to '*/*'.
        
        accept_set = header_dict.get(HttpClient.HEADER_ACCEPT) is not None
        x_taxii_accept_set = header_dict.get(HttpClient.HEADER_X_TAXII_ACCEPT) is not None
        
        if not accept_set and not x_taxii_accept_set:
            header_dict[HttpClient.HEADER_ACCEPT] = header_dict[HttpClient.HEADER_CONTENT_TYPE]
            header_dict[HttpClient.HEADER_X_TAXII_ACCEPT] = header_dict[HttpClient.HEADER_X_TAXII_CONTENT_TYPE]
        
        #If the X-TAXII-Services header is not set by the user,
        #Attempt to use the library's default mapping
        services_map = {t.VID_TAXII_XML_10: t.VID_TAXII_SERVICES_10,
                        t.VID_TAXII_XML_10: t.VID_TAXII_SERVICES_11,
                        t.VID_CERT_EU_JSON_10: t.VID_TAXII_SERVICES_10}
        if header_dict.get(HttpClient.HEADER_X_TAXII_SERVICES) is None:#The X-TAXII-Services header was not set by the user
            if message_binding not in services_map:
                raise ValueError('x-taxii-services header not specified, and the message_binding is unrecognized')
            header_dict[HttpClient.HEADER_X_TAXII_SERVICES] = services_map[message_binding]
        
        handler_list = []

        if self.use_https:
            header_dict[HttpClient.HEADER_X_TAXII_PROTOCOL] = t.VID_TAXII_HTTPS_10
            
            if (self.auth_type == HttpClient.AUTH_CERT or
               self.auth_type == HttpClient.AUTH_CERT_BASIC):
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
            else:
                key_file = None
                cert_file = None
            
            if (self.auth_type == HttpClient.AUTH_BASIC or
               self.auth_type == HttpClient.AUTH_CERT_BASIC):
                header_dict['Authorization'] = self.basic_auth_header
            
            verify_server = self.verify_server
            ca_file = self.ca_file
            
            handler_list.append(LibtaxiiHTTPSHandler(key_file=key_file, 
                                                     cert_file=cert_file, 
                                                     verify_server=verify_server, 
                                                     ca_certs=ca_file))
            
        else:  # Not using https
            header_dict[HttpClient.HEADER_X_TAXII_PROTOCOL] = t.VID_TAXII_HTTP_10

            if self.auth_type == HttpClient.AUTH_NONE:
                handler_list.append(urllib2.HTTPHandler())
            elif self.auth_type == HttpClient.AUTH_BASIC:
                header_dict['Authorization'] = self.basic_auth_header
            elif self.auth_type == HttpClient.AUTH_CERT:
                k = self.auth_credentials['key_file']
                c = self.auth_credentials['cert_file']
                handler_list.append(HTTPClientAuthHandler(k, c))
            elif self.auth_type == HttpClient.AUTH_CERT_BASIC:
                header_dict['Authorization'] = self.basic_auth_header
                k = self.auth_credentials['key_file']
                c = self.auth_credentials['cert_file']
                handler_list.append(HTTPSClientAuthHandler(k, c))
            handler_list.append(urllib2.HTTPHandler())

        if self.proxy_string is not None:
            if self.proxy_string == 'noproxy':
                #Dont use any proxy, including the system-specified proxy
                handler_list.append(urllib2.ProxyHandler({}))
            else:  # Use a specific proxy
                handler_list.append(urllib2.ProxyHandler({self.proxy_type: self.proxy_string}))

        opener = urllib2.build_opener(*handler_list)
        urllib2.install_opener(opener)

        if port is None:  # If the caller did not specify a port, use the default
            if self.use_https:
                port = 443
            else:
                port = 80

        if self.use_https:
            scheme = 'https://'
        else:
            scheme = 'http://'

        url = scheme + host + ':' + str(port) + path
        if get_params_dict is not None:
            url += '?' + urllib.urlencode(get_params_dict)

        req = urllib2.Request(url, post_data, header_dict)
        try:
            response = urllib2.urlopen(req)
            return response
        except urllib2.HTTPError, error:
            return error

#http://stackoverflow.com/questions/5896380/https-connection-using-pem-certificate
class LibtaxiiHTTPSHandler(urllib2.HTTPSHandler):
    def __init__(self, key_file=None, cert_file=None, verify_server=False, ca_certs=None):
        urllib2.HTTPSHandler.__init__(self)
        self.key_file = key_file
        self.cert_file = cert_file
        self.verify_server = verify_server
        self.ca_certs = ca_certs

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=0):
        return VerifiableHTTPSConnection(host, 
                                       key_file=self.key_file, 
                                       cert_file=self.cert_file, 
                                       verify_server=self.verify_server, 
                                       ca_certs=self.ca_certs)

class HTTPClientAuthHandler(urllib2.HTTPSHandler):  # TODO: Is this used / is this possible?
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=0):
        return httplib.HTTPConnection(host, key_file=self.key, cert_file=self.cert)

class VerifiableHTTPSConnection(httplib.HTTPSConnection):
    """
    The default httplib HTTPSConnection does not verify certificates.
    This class extends HTTPSConnection and requires certificate verification.
    Borrowed from http://thejosephturner.com/blog/2011/03/19/https-certificate-verification-in-python-with-urllib2/
    """
    
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                     strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=None, verify_server=False, ca_certs=None):
        httplib.HTTPSConnection.__init__(self, host, port, key_file, 
                                         cert_file, strict, timeout, 
                                         source_address)
        
        if verify_server:
            self.cert_reqs = ssl.CERT_REQUIRED
        else:
            self.cert_reqs = ssl.CERT_NONE
        self.ca_certs = ca_certs
    
    def connect(self):
        #overrides the version in httplib so that we do 
        #certificate verification
        sock = socket.create_connection((self.host, self.port), 
                                         self.timeout,
                                         self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        
        self.sock = ssl.wrap_socket(sock,
                        keyfile=self.key_file,
                        certfile=self.cert_file,
                        cert_reqs=self.cert_reqs,
                        ca_certs=self.ca_certs)
