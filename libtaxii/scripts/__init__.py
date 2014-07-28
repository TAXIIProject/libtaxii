# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import argparse
import libtaxii.clients as tc
import libtaxii.messages_10 as tm10
import libtaxii.messages_11 as tm11

class ProxyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Turns the 'None' string argument into the None object
        that the API expects.
        """
        if option_string == "--proxy" and values == "None":
            values = None

        setattr(namespace, self.dest, values)


def create_client(args):
    client = tc.HttpClient()
    client.setUseHttps(args.https)
    client.setProxy(args.proxy)
    tls = (args.cert is not None and args.key is not None)
    basic = (args.username is not None and args.password is not None)
    if tls and basic:
        client.setAuthType(tc.HttpClient.AUTH_CERT_BASIC)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert, 'username': args.username, 'password': args.password})
    elif tls:
        client.setAuthType(tc.HttpClient.AUTH_CERT)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert})
    elif basic:
        client.setAuthType(tc.HttpClient.AUTH_BASIC)
        client.setAuthCredentials({'username': args.username, 'password': args.password})

    return client

# def tm11_base_rp(msg):
    # print "Message Type: %s" % msg.message_type
    # print "Message ID: %s; In Response To: %s" % (r.message_id, r.in_response_to)
    # for k, v in r.extended_headers.iteritems():
        # print "Extended Header: %s = %s" % (k, v)

# def tm11_status_message_rp(msg):
    # tm11_base_rp(msg)
    # print "Status Type: %s" % msg.status_type
    # print "Status Message: %s" % msg.message
    # for k, v in msg.status_details.iteritems():
        # print "Status Detail: %s = %s" % (k, v)

# def tm11_discovery_request_rp(msg):
    # tm11_base_rp(msg)

# def tm11_discovery_response_rp(msg):
    # tm11_base_rp(msg)
    # print "Response has %s Service Instances" % len(msg.service_instances)
    # for si in msg.service_instances:
        # print "=== Service Instance ==="
        # print "  Service Type: %s" % si.service_type
        # print "  Service Version: %s" % si.services_version
        # print "  Protocol Binding: %s" % si.protocol_binding
        # print "  Service Address: %s" % si.service_address
        # print "  Message Bindings: %s" % [mb for mb in si.message_bindings]
        # if si.service_type == tm11.SVC_INBOX:
            # print "  Inbox Service Ac: %s" % [ac.to_string() for ac in si.inbox_service_accepted_contents]
        # print "  Available: %s" % si.available
        # print "  Message: %s" % si.message
        # if len(si.supported_query) > 0:
            # print "  Supported Query: %s" % si.supported_query
        # else:
            # print "  Supported Query: %s" % None
        # print ""

# def tm11_collection_information_request_rp(msg):
    # tm11_base_rp(msg)    

# def tm11_collection_information_response_rp(msg):
    # tm11_base_rp(msg)
    # print "Response has %s Data Collections" % len(msg.collection_informations)
    # for ci in msg.collection_informations:
        # print "=== Data Collections ==="
        # print "  Collection Name: %s" % ci.collection_name
        # print "  Collection Description: %s" % ci.collection_description
        # print "  Supported Contents: %s" % [sc.to_string() for sc in ci.supported_contents]
        # print "  Available: %s" % ci.available
        
        # # TODO: Push Methods, PollingServiceInstances, and SubscriptionMethods are all objects that need to be Rich printed
        # print "  Push Methods: %s" % ci.push_methods
        # print "  Polling Service Instances: %s" % ci.polling_service_instances
        # print "  Subscription Methods: %s" % ci.subscription_methods
        
        # if ci.collection_volume:
            # print "  Collection Volume: %s" % ci.collection_volume
        # print "  Collection Type: %s" % ci.collection_type
        
        # if len(ci.receiving_inbox_services) > 0:
            # print "  Receiving Inbox Services: %s" % ci.receiving_inbox_services
        # else:
            # print "Receiving Inbox Services: None"

# def tm11_manage_collection_subscription_request_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm11_manage_collection_subscription_response_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm11_poll_request_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm11_poll_response_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm11_inbox_message_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm11_poll_fulfillment_request_rp(msg):
    # tm11_base_rp(msg)
    # pass

# def tm10_discovery_request_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_discovery_response_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_collection_information_request_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_collection_information_response_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_manage_collection_subscription_request_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_manage_collection_subscription_response_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_poll_request_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_poll_response_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def tm10_inbox_message_rp(msg):
    # tm10_base_rp(msg)
    # pass

# def do_rich_print(taxii_message):
    # if isinstance(taxii_message, tm11.StatusMessage):
        # tm11_status_message_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.DiscoveryRequest):
        # tm11_discovery_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.DiscoveryResponse):
        # tm11_discovery_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.CollectionInformationRequest):
        # tm11_collection_information_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.CollectionInformationResponse):
        # tm11_collection_information_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.ManageCollectionSubscriptionRequest):
        # tm11_manage_collection_subscription_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.ManageCollectionSubscriptionResponse):
        # tm11_manage_collection_subscription_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.PollRequest):
        # tm11_poll_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.PollResponse):
        # tm11_poll_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.InboxMessage):
        # tm11_inbox_message_rp(taxii_message)
    # elif isinstance(taxii_message, tm11.PollFulfillmentRequest):
        # tm11_poll_fulfillment_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.DiscoveryRequest):
        # tm10_discovery_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.DiscoveryResponse):
        # tm10_discovery_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.CollectionInformationRequest):
        # tm10_collection_information_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.CollectionInformationResponse):
        # tm10_collection_information_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.ManageCollectionSubscriptionRequest):
        # tm10_manage_collection_subscription_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.ManageCollectionSubscriptionResponse):
        # tm10_manage_collection_subscription_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.PollRequest):
        # tm10_poll_request_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.PollResponse):
        # tm10_poll_response_rp(taxii_message)
    # elif isinstance(taxii_message, tm10.InboxMessage):
        # tm10_inbox_message_rp(taxii_message)
    # else:
        # raise ValueError("Unknown TAXII Message Type: %s" % taxii_message.__class__.__name__)

def get_base_parser(parser_description, 
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
    parser.add_argument("--host", dest="host", default=host, help="Host where the Discovery Service is hosted. Defaults to %s." % host)
    parser.add_argument("--port", dest="port", default=port, type=int, help="Port where the Discovery Service is hosted. Defaults to %s." % port)
    parser.add_argument("--path", dest="path", default=path, help="Path where the Discovery Service is hosted. Defaults to %s" % path)
    parser.add_argument("--https", dest="https", default=https, type=bool, help="Whether or not to use HTTPS. Defaults to %s" % https)
    parser.add_argument("--cert", dest="cert", default=cert, help="The file location of the certificate to use. Defaults to %s." % cert)
    parser.add_argument("--key", dest="key", default=key, help="The file location of the private key to use. Defaults to %s." % key)
    parser.add_argument("--username", dest="username", default=username, help="The username to authenticate with. Defaults to %s." % username)
    parser.add_argument("--pass", dest="password", default=password, help="The password to authenticate with. Defaults to %s." % password)
    parser.add_argument("--proxy", dest="proxy", action=ProxyAction, default=proxy,
                        help="A proxy to use (e.g., http://example.com:80/), or None to not use any proxy. Omit this to use the system proxy.")
    parser.add_argument("--xml-output", dest="xml_output", action='store_true', default=xml_output,
                        help="If present, the raw XML of the response will be printed to standard out. Otherwise, a \"Rich\" output will be presented.")

    return parser
