
#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii.messages_11 as tm11
from libtaxii.constants import *

class InboxClient11Script(TaxiiScript):
    parser_description = 'The TAXII 1.1 Inbox Client sends an Inbox Message to a TAXII Server and prints the ' \
                         'Status Message response to standard out. The Inbox Client has a "built in" STIX document ' \
                         'that is sent by default.'
    path = '/services/inbox/'

    # http://stix.mitre.org/language/version1.1.1/#samples
    # http://stix.mitre.org/language/version1.1.1/stix_v1.0_samples_20130408.zip
    stix_watchlist = '''
<!--
    STIX Domain Watchlist Example

    Copyright (c) 2014, The MITRE Corporation. All rights reserved.
    The contents of this file are subject to the terms of the STIX License located at
    http://stix.mitre.org/about/termsofuse.html.

    This example demonstrates one method of representing a domain watchlist (list of malicious domains) in STIX and
    CybOX. It demonstrates several STIX/CybOX concepts and best practices including:

       * Indicators
       * CybOX within STIX
       * The CybOX Domain object
       * Controlled vocabularies

    Created by Mark Davidson
-->
<stix:STIX_Package
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:cybox="http://cybox.mitre.org/cybox-2"
    xmlns:DomainNameObj="http://cybox.mitre.org/objects#DomainNameObject-1"
    xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
    xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
    xmlns:example="http://example.com/"
    xsi:schemaLocation=
    "http://stix.mitre.org/stix-1 ../stix_core.xsd
    http://stix.mitre.org/Indicator-2 ../indicator.xsd
    http://cybox.mitre.org/default_vocabularies-2 ../cybox/cybox_default_vocabularies.xsd
    http://stix.mitre.org/default_vocabularies-1 ../stix_default_vocabularies.xsd
    http://cybox.mitre.org/objects#DomainNameObject-1 ../cybox/objects/Domain_Name_Object.xsd"
    id="example:STIXPackage-f61cd874-494d-4194-a3e6-6b487dbb6d6e"
    timestamp="2014-05-08T09:00:00.000000Z"
    version="1.1.1"
    >
    <stix:STIX_Header>
        <stix:Title>Example watchlist that contains domain information.</stix:Title>
        <stix:Package_Intent xsi:type="stixVocabs:PackageIntentVocab-1.0">Indicators - Watchlist</stix:Package_Intent>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator xsi:type="indicator:IndicatorType" id="example:Indicator-2e20c5b2-56fa-46cd-9662-8f199c69d2c9"
            timestamp="2014-05-08T09:00:00.000000Z">
            <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">Domain Watchlist</indicator:Type>
            <indicator:Description>Sample domain Indicator for this watchlist</indicator:Description>
            <indicator:Observable id="example:Observable-87c9a5bb-d005-4b3e-8081-99f720fad62b">
                <cybox:Object id="example:Object-12c760ba-cd2c-4f5d-a37d-18212eac7928">
                    <cybox:Properties xsi:type="DomainNameObj:DomainNameObjectType" type="FQDN">
                        <DomainNameObj:Value condition="Equals" apply_condition="ANY"
                        >malicious1.example.com##comma##malicious2.example.com##comma##malicious3.example.com</DomainNameObj:Value>
                    </cybox:Properties>
                </cybox:Object>
            </indicator:Observable>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>'''

    def get_arg_parser(self, *args, **kwargs):
        parser = super(InboxClient11Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--content-binding",
                            dest="content_binding",
                            default=CB_STIX_XML_111,
                            help="Content binding of the Content Block to send. Defaults to %s" % CB_STIX_XML_111)
        parser.add_argument("--subtype",
                            dest="subtype",
                            default=None,
                            help="The subtype of the Content Binding. Defaults to None")
        parser.add_argument("--content-file",
                            dest="content_file",
                            default=self.stix_watchlist,
                            help="Content of the Content Block to send. Defaults to a STIX watchlist.")
        parser.add_argument("--dcn",
                            dest="dcn",
                            default=None,
                            help="The Destination Collection Name for this Inbox Message. Defaults to None. "
                                 "This script only supports one Destination Collection Name")
        return parser

    def create_request_message(self, args):
        if args.content_file is self.stix_watchlist:
            data = self.stix_watchlist
        else:
            with open(args.content_file, 'r') as f:
                data = f.read()

        cb = tm11.ContentBlock(tm11.ContentBinding(args.content_binding), data)
        if args.subtype is not None:
            cb.content_binding.subtype_ids.append(args.subtype)

        inbox_message = tm11.InboxMessage(message_id=tm11.generate_message_id(), content_blocks=[cb])
        if args.dcn:
            inbox_message.destination_collection_names.append(args.dcn)

        return inbox_message


def main():
    script = InboxClient11Script()
    script()

if __name__ == "__main__":
    main()
