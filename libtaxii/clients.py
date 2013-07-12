#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import httplib
import urllib
import urllib2
import base64
import uuid
import libtaxii


class HttpClient:

    #Constants for authentication types
    AUTH_NONE = 0  # Do not offer any authentication credentials to the server
    AUTH_BASIC = 1  # Offer HTTP Basic authentication credentials to the server
    AUTH_CERT = 2  # Offer certificate based authentication credentials to the server
    AUTH_CERT_BASIC = 3  # Offer certificate based auth and HTTP Basic credentials

    #Proxy Constants
    PROXY_HTTP = 'http'
    PROXY_HTTPS = 'https'

    def __init__(self):
        self.auth_type = HttpClient.AUTH_NONE
        self.auth_credentials = {}
        self.use_https = False
        self.proxy_type = None
        self.proxy_string = None

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

    @property
    def basic_auth_header(self):
        """Returns a Base64-encoded HTTP Basic Authorization Header."""
        return "Basic " + base64.b64encode('%s:%s' % (
                                           self.auth_credentials['username'],
                                           self.auth_credentials['password']))

    def setProxy(self, proxy_string=None, proxy_type=PROXY_HTTP):
        """Set the proxy settings to use when making a connection.

        Arguments:
        - proxy_string - a string like 'http://proxy.example.com:80'
          If set to None, use the system proxy.
          If set to 'noproxy', don't use a proxy (even the system proxy)
        - proxy_type - either PROXY_HTTP or PROXY_HTTPS
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
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTPS_10
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
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTP_10
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

    def callTaxiiService2(self, host, path, message_binding, post_data, port=None, get_params_dict=None, **kwargs):
        """New method of calling a TAXII Service

        Note: this uses urllib2 instead of httplib, and therefore returns
        a different kind of object than callTaxiiService.
        """
        header_dict = {'Content-Type':         'application/xml',
                       'User-Agent':           'libtaxii.httpclient',
                       'X-TAXII-Content-Type': message_binding}
        if kwargs['content_type']:
            header_dict['Content-Type'] = kwargs['content_type']

        handler_list = []

        if self.use_https:
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTPS_10

            if self.auth_type == HttpClient.AUTH_NONE:
                handler_list.append(urllib2.HTTPSHandler())
            elif self.auth_type == HttpClient.AUTH_BASIC:
                header_dict['Authorization'] = self.basic_auth_header
            elif self.auth_type == HttpClient.AUTH_CERT:
                k = self.auth_credentials['key_file']
                c = self.auth_credentials['cert_file']
                handler_list.append(HTTPSClientAuthHandler(k, c))
            elif self.auth_type == HttpClient.AUTH_CERT_BASIC:
                header_dict['Authorization'] = self.basic_auth_header
                k = self.auth_credentials['key_file']
                c = self.auth_credentials['cert_file']
                handler_list.append(HTTPSClientAuthHandler(k, c))
        else:  # Not using https
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTP_10

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
class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=0):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)


class HTTPClientAuthHandler(urllib2.HTTPSHandler):  # TODO: Is this used / is this possible?
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=0):
        return httplib.HTTPConnection(host, key_file=self.key, cert_file=self.cert)
