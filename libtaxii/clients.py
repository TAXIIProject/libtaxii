#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import httplib
import urllib
import base64
import uuid
import libtaxii

class HttpClient:

    #Constants for authentication types
    AUTH_NONE = 0#Do not offer any authentication credentials to the server
    AUTH_BASIC = 1#Offer HTTP Basic authentication credentials to the server
    AUTH_CERT = 2#Offer certificate based authentication credentials to the server

    def __init__(self):
        self.auth_type = HttpClient.AUTH_NONE
        self.auth_credentials = {}
        self.use_https = False

    #Set the authentication type. Must be one of AUTH_NONE, AUTH_BASIC, or AUTH_CERT
    def setAuthType(self, auth_type):
        #If this isn't a change, don't do anything
        if self.auth_type == auth_type:
            return
        
        if auth_type == HttpClient.AUTH_NONE:
            self.auth_type = HttpClient.AUTH_NONE
        elif auth_type == HttpClient.AUTH_BASIC:
            self.auth_type = HttpClient.AUTH_BASIC
        elif auth_type == HttpClient.AUTH_CERT:
            self.auth_type = HttpClient.AUTH_CERT
        else:
            raise Exception('Invalid auth_type specified. Must be one of HttpClient AUTH_NONE, AUTH_BASIC, or AUTH_CERT')

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
        if self.auth_type == HttpClient.AUTH_NONE:
            self.auth_credentials = auth_credentials_dict
        elif self.auth_type == HttpClient.AUTH_BASIC:
            if 'username' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'username\' is not present')
            if 'password' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'password\' is not present')
            self.auth_credentials = auth_credentials_dict
        elif self.auth_type == HttpClient.AUTH_CERT:
            if 'key_file' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'key_file\' is not present')
            if 'cert_file' not in auth_credentials_dict:
                raise Exception('Invalid auth credentials. Field \'cert_file\' is not present')
            self.auth_credentials = auth_credentials_dict
    
    def callTaxiiService(self, host, path, message_binding, post_data, port=None, get_params_dict=None):
        
        if port is None:#If the caller did not specify a port, use the default
            if self.use_https:
                port = 443
            else:
                port = 80
        
        if get_params_dict is not None:#Add the query params to the URL
            path += '?' + urllib.urlencode(get_params_dict)
        
        header_dict = {'Content-Type': 'application/xml',
                       'User-Agent': 'libtaxii.httpclient'}
        
        if self.use_https:
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTPS_10
            if self.auth_type == HttpClient.AUTH_NONE:
                conn = httplib.HTTPSConnection(host, port)
            elif self.auth_type == HttpClient.AUTH_BASIC:
                base64string = base64.encodestring('%s:%s' % (self.auth_credentials['username'], self.auth_credentials['password']))
                header_dict['Authorization'] = 'Basic %s' % base64string
                conn = httplib.HTTPSConnection(host, port)
            else:#AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPSConnection(host, port, key_file, cert_file)
        else:#Not using https
            header_dict['X-TAXII-Protocol'] = libtaxii.VID_TAXII_HTTP_10
            if self.auth_type == HttpClient.AUTH_NONE:
                conn = httplib.HTTPConnection(host, port)
            #TODO: Consider deleting because this is a terrible idea
            elif self.auth_type == HttpClient.AUTH_BASIC:#Sending credentials in cleartext.. tsk tsk
                base64string = base64.encodestring('%s:%s' % (self.auth_credentials['username'], self.auth_credentials['password']))
                header_dict['Authorization'] = 'Basic %s' % base64string
                conn = httplib.HTTPConnection(host, port)
            else:#AUTH_CERT
                key_file = self.auth_credentials['key_file']
                cert_file = self.auth_credentials['cert_file']
                conn = httplib.HTTPConnection(host, port, key_file, cert_file)
        
        header_dict['Content-Type'] = 'application/xml'
        header_dict['X-TAXII-Content-Type'] = message_binding
        
        req = conn.request('POST', path, post_data, headers=header_dict)
        response = conn.getresponse()
        
        return response
