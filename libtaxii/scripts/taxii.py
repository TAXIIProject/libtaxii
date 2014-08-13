#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii.scripts as scripts
import sys

def main():
    #TODO: THIS IS A WORK IN PROGRESS!
    script_name = sys.argv[1]
    script_map = {
    'discovery': scripts.DiscoveryClient11Script,
    'inbox': scripts.InboxClient11Script,
    'poll': scripts.PollClient11Script,
    'fulfillment': scripts.FulfillmentClient11Script,
    'collection_information': scripts.CollectionInformationClient11Script,
    'subscription': scripts.SubscriptionClient11Script,
    
    'discovery_10': scripts.DiscoveryClient10Script,
    'inbox_10': scripts.InboxClient10Script,
    'poll_10': scripts.PollClient10Script,
    'collection_information_10': scripts.FeedInformationClient10Script,
    'subscription_10': scripts.SubscriptionClient10Script,
    }
    
    script_class = script_map[script_name]
    script_instance = script_class()
    script_instance()

if __name__ == "__main__":
    main()