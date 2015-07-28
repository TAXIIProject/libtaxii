

# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import argparse
import os
import sys
import traceback
import datetime
import libtaxii.clients as tc
import six
from six.moves.urllib.parse import urlparse

import libtaxii as t
from libtaxii.common import gen_filename
from libtaxii.constants import *


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

#: When writing content blocks, clobber any existing files
W_CLOBBER = 0
#: When writing content blocks, skip any existing files
W_SKIP = 1
#: When writing content blocks, prompt before clobbering any existing files
W_PROMPT = 2
#: Do not write any files
W_NONE = 3
W_CHOICES = (W_CLOBBER, W_PROMPT, W_SKIP, W_NONE)

MSG_FILE_OVERWRITTEN = "File overwritten: "
MSG_FILE_SKIPPED = "File write skipped: "
MSG_FILE_CREATED = "File created: "

def write_type(s):
    s = s.lower()
    if s == 'clobber':
        return W_CLOBBER
    elif s == 'skip':
        return W_SKIP
    elif s == 'prompt':
        return W_PROMPT
    elif s == 'none':
        return W_NONE
    else:
        raise ValueError('Argument must be one of \'clobber\', \'skip\', \'prompt\', or \'none\'')


def add_poll_response_args(parser):
    """
    Adds arguments to the parser that are commonly used for handling Poll Response messages:
    - --dest-dir
    - --write

    :param parser:
    :return:
    """
    parser.add_argument("--dest-dir",
                            dest="dest_dir",
                            default="",
                            help="The directory to save Content Blocks to. Defaults to the current directory.")

    parser.add_argument("--write",
                        dest="write_type",
                        default='clobber',
                        type=write_type,
                        help="The write type. Must be one of \'clobber\', \'skip\', \'prompt\', or \'none\'. Defaults "
                             "to \'clobber\'")


class ProxyAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Turns the 'None' string argument into the None object
        that the API expects.
        """
        if option_string == "--proxy" and values == "None":
            values = None

        setattr(namespace, self.dest, values)


class TaxiiScript(object):

    #: taxii version to put in the request headers. Defaults to TAXII 1.1
    taxii_version = VID_TAXII_XML_11
    #: parser description
    parser_description = ''
    #: default path
    path = '/'

    def get_arg_parser(self,
                       parser_description,
                       path="/services/discovery/",
                       host="taxiitest.mitre.org",
                       port="80",
                       https=False,
                       cert=None,
                       key=None,
                       username=None,
                       password=None,
                       proxy='noproxy',
                       xml_output=False):
        """
        Parser things common to all scripts. Parsers for specific TAXII Services should
        add their own arguments.
        """
        parser = argparse.ArgumentParser(description=parser_description)
        url = "https" if https else "http" + "://" + host + ":" + str(port) + path
        parser.add_argument("-u",
                            "--url",
                            dest="url",
                            default=url,
                            help="The URL to connect to. Defaults to %s." % url)
        parser.add_argument("--host",
                            dest="host",
                            default=host,
                            help=argparse.SUPPRESS
                            )
        parser.add_argument("--port",
                            dest="port",
                            default=port,
                            type=int,
                            help=argparse.SUPPRESS)
        parser.add_argument("--path",
                            dest="path",
                            default=path,
                            help=argparse.SUPPRESS)
        parser.add_argument("--https",
                            dest="https",
                            default=https,
                            type=bool,
                            help=argparse.SUPPRESS)
        parser.add_argument("--cert",
                            dest="cert",
                            default=cert,
                            help="The file location of the certificate to use. Defaults to %s." % cert)
        parser.add_argument("--key",
                            dest="key",
                            default=key,
                            help="The file location of the private key to use. Defaults to %s." % key)
        parser.add_argument("--username",
                            dest="username",
                            default=username,
                            help="The username to authenticate with. Defaults to %s." % username)
        parser.add_argument("--pass",
                            dest="password",
                            default=password,
                            help="The password to authenticate with. Defaults to %s." % password)
        parser.add_argument("--proxy",
                            dest="proxy",
                            action=ProxyAction, default=proxy,
                            help="The proxy to use (e.g., http://myproxy.example.com:80/), or 'noproxy' to not use "
                                 "any proxy. If omitted, the system's proxy settings will be used.")
        parser.add_argument("--xml-output",
                            dest="xml_output",
                            action='store_true',
                            default=xml_output,
                            help="If present, the raw XML of the response will be printed to standard out. "
                                 "Otherwise, a \"Rich\" output will be presented.")

        return parser

    def handle_response(self, response, args):
        """
        Default response handler. Just prints the response
        """
        print("Response:\n")
        if args.xml_output is False:
            print(response.to_text())
        else:
            print(response.to_xml(pretty_print=True))

    def create_client(self, use_https, proxy, cert=None, key=None, username=None, password=None):
        client = tc.HttpClient()
        client.set_use_https(use_https)
        client.set_proxy(proxy)
        tls = (cert is not None and key is not None)
        basic = (username is not None and password is not None)
        if tls and basic:
            client.set_auth_type(tc.HttpClient.AUTH_CERT_BASIC)
            client.set_auth_credentials({'key_file': key,
                                         'cert_file': cert,
                                         'username': username,
                                         'password': password})
        elif tls:
            client.set_auth_type(tc.HttpClient.AUTH_CERT)
            client.set_auth_credentials({'key_file': key, 'cert_file': cert})
        elif basic:
            client.set_auth_type(tc.HttpClient.AUTH_BASIC)
            client.set_auth_credentials({'username': username, 'password': password})

        return client

    @staticmethod
    def get_write_and_message(filename, write_type_):
        """
        Depending on whether the file exists and the write_type, decide whether the file should be created or not
        and provide a message to be printed out to the user.
        """
        file_exists = os.path.exists(filename)

        if file_exists and write_type_ == W_CLOBBER:
            write = True
            message = MSG_FILE_OVERWRITTEN
        elif file_exists and write_type_ == W_PROMPT:
            var = None
            while var not in ('y', 'n'):
                var = six.moves.input("Overwrite file (%s)? (y/n): " % filename)
            if var == 'y':
                write = True
                message = MSG_FILE_OVERWRITTEN
            else:
                write = False
                message = MSG_FILE_SKIPPED
        elif not file_exists and write_type_ in (W_CLOBBER, W_PROMPT):
            write = True
            message = MSG_FILE_CREATED
        elif write_type_ in (W_SKIP, W_NONE):  # This happens no matter if the file exists or not
            write = False
            message = MSG_FILE_SKIPPED
        else:
            raise ValueError("Unknown combination of file_exists (%s) and write_type (%s)" % (file_exists, write_type_))

        return write, message


    def write_cbs_from_poll_response_10(self, poll_response, dest_dir, write_type_=W_CLOBBER):
        """
        This function writes content blocks to file from a TAXII 1.0 Poll Response
        """

        for cb in poll_response.content_blocks:
            if cb.content_binding == CB_STIX_XML_10:
                format_ = '_STIX10_'
                ext = '.xml'
            elif cb.content_binding == CB_STIX_XML_101:
                format_ = '_STIX101_'
                ext = '.xml'
            elif cb.content_binding == CB_STIX_XML_11:
                format_ = '_STIX11_'
                ext = '.xml'
            elif cb.content_binding == CB_STIX_XML_111:
                format_ = '_STIX111_'
                ext = '.xml'
            else:  # Format and extension are unknown
                format_ = ''
                ext = ''

        if cb.timestamp_label:
                date_string = 't' + cb.timestamp_label.isoformat()
        else:
            date_string = 's' + datetime.datetime.now().isoformat()

        filename = gen_filename(poll_response.collection_name,
                                format_,
                                date_string,
                                ext)
        filename = os.path.join(dest_dir, filename)
        write, message = TaxiiScript.get_write_and_message(filename, write_type_)

        if write:
            with open(filename, 'w') as f:
                f.write(cb.content)

        print("%s%s" % (message, filename))

    def write_cbs_from_poll_response_11(self, poll_response, dest_dir, write_type_=W_CLOBBER):
        """
        This function writes content blocks to file from a TAXII 1.1 Poll Response
        """

        for cb in poll_response.content_blocks:
            if cb.content_binding.binding_id == CB_STIX_XML_10:
                format_ = '_STIX10_'
                ext = '.xml'
            elif cb.content_binding.binding_id == CB_STIX_XML_101:
                format_ = '_STIX101_'
                ext = '.xml'
            elif cb.content_binding.binding_id == CB_STIX_XML_11:
                format_ = '_STIX11_'
                ext = '.xml'
            elif cb.content_binding.binding_id == CB_STIX_XML_111:
                format_ = '_STIX111_'
                ext = '.xml'
            else:  # Format and extension are unknown
                format_ = ''
                ext = ''

            if cb.timestamp_label:
                date_string = 't' + cb.timestamp_label.isoformat()
            else:
                date_string = 's' + datetime.datetime.now().isoformat()

            filename = gen_filename(poll_response.collection_name,
                                    format_,
                                    date_string,
                                    ext)
            filename = os.path.join(dest_dir, filename)
            write, message = TaxiiScript.get_write_and_message(filename, write_type_)

            if write:
                with open(filename, 'w') as f:
                    f.write(cb.content)

            print("%s%s" % (message, filename))

    def create_request_message(self, args):
        """
        This function should create a request message.
        Should be implemented by child classes.
        """
        raise NotImplementedError

    @staticmethod
    def _parse_url_info(args, parser):
        """
        In libtaxii 1.1.106, the command line args --port, --path, --host, and --https were deprecated in favor of
        --url. This function performs the following actions:

        1. Print a warning if any deprecated arguments are used (i.e., not one of the defaults).
        2. Raise a ValueError if --url is used in combination with any deprecated argument
        3. If deprecated arguments were used, translate them into the --url argument
        """

        deprecated_args = ['port', 'path', 'host', 'https']
        deprecated_arg_used = False
        for arg in deprecated_args:
            if str(getattr(args, arg)) != str(parser._optionals.get_default(arg)):
                print("WARNING: use of deprecated argument: %s. Use --url instead!" % arg)
                deprecated_arg_used = True

        url_used = getattr(args, 'url') != parser._optionals.get_default('url')
        if url_used and deprecated_arg_used:
            raise ValueError("Error: Both --url and a deprecated argument was used. Please use one or the other!")

        if deprecated_arg_used:
            url = "https" if args.https else "http" + "://" + args.host + ":" + str(args.port) + args.path
            args.url = url
            print("Deprecated arguments transformed into: '--url %s'" % url)

    def __call__(self):
        """
        Invoke a TAXII Service based on the arguments
        """
        try:
            parser = self.get_arg_parser(parser_description=self.parser_description, path=self.path)
            args = parser.parse_args()
            TaxiiScript._parse_url_info(args, parser)
            request_message = self.create_request_message(args)
            url = urlparse(args.url)
            client = self.create_client(url.scheme == 'https',
                                        args.proxy,
                                        args.cert,
                                        args.key,
                                        args.username,
                                        args.password)

            print("Request:\n")
            if args.xml_output is False:
                print(request_message.to_text())
            else:
                print(request_message.to_xml(pretty_print=True))

            resp = client.call_taxii_service2(url.hostname,
                                              url.path,
                                              self.taxii_version,
                                              request_message.to_xml(pretty_print=True),
                                              url.port)
            r = t.get_message_from_http_response(resp, '0')

            self.handle_response(r, args)
        except Exception as ex:
            traceback.print_exc()
            sys.exit(EXIT_FAILURE)

        sys.exit(EXIT_SUCCESS)

# TODO: These are stubs that will eventually need to be moved out into their own files / scripts


class SubscriptionClient11Script(TaxiiScript):
    parser_description = 'TAXII 1.1 Subscription Management Client'
    path = '/services/collection-management/'


class SubscriptionClient10Script(TaxiiScript):
    taxii_version = VID_TAXII_XML_10
    parser_description = 'TAXII 1.0 Subscription Management Client'
    path = '/services/feed-management/'


# No poll fulfillment in TAXII 1.0
