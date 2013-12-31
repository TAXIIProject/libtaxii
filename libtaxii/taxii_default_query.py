""" 
| Copyright (C) 2013 - The MITRE Corporation
| For license information, see the LICENSE.txt file

| Contributors:
  
* Mark Davidson - mdavidson@mitre.org

"""

import libtaxii.messages_11 as tm11
import libtaxii as t

from lxml import etree

#: Format ID for this version of TAXII Default Query
FID_TAXII_DEFAULT_QUERY_10 = 'urn:taxii.mitre.org:query:default:1.0'

#Targeting Expression Vocabulary IDs
#: Targeting Expression Vocabulary ID for STIX XML 1.0
TEV_STIX_10 = t.CB_STIX_XML_10
#: Targeting Expression Vocabulary ID for STIX XML 1.0.1
TEV_STIX_101 = t.CB_STIX_XML_101
#: Targeting Expression Vocabulary ID for STIX XML 1.1
TEV_STIX_11 = t.CB_STIX_XML_11

#Capability Module IDs
#: Capability Module ID for Core
CM_CORE = 'urn:taxii.mitre.org:query:capability:core-1'
#: Capability Module ID for Regex
CM_REGEX = 'urn:taxii.mitre.org:query:capability:regex-1'
#: Capability Module ID for Timestamp
CM_TIMESTAMP = 'urn:taxii.mitre.org:query:capability:timestamp-1'

#Tuple of all capability modules defined in TAXII Default Query 1.0
CM_IDS = (CM_CORE, CM_REGEX, CM_TIMESTAMP)


ns_map = {'tdq': 'http://taxii.mitre.org/query/taxii_default_query-1'}

class DefaultQueryInformation(tm11.SupportedQuery):
    def __init__(self, format_id, targeting_expression_ids, capability_modules):
        super(DefaultQueryInformation, self).__init__(format_id)
        self.targeting_expression_ids = targeting_expression_ids
        self.capability_modules = capability_modules
    
    @property
    def targeting_expression_ids(self):
        return self._targeting_expression_ids
    
    @targeting_expression_ids.setter
    def targeting_expression_ids(self, value):
        #TODO: Check that the valud is URI formatted
        self._targeting_expression_ids = value
    
    @property
    def capability_modules(self):
        return self._capability_modules
    
    @capability_modules.setter
    def capability_modules(self, value):
        #TODO: Check that the value is URI formatted (and a defined CM id?)
        self._capability_modules = value
    
    def to_etree(self):
        q = super(DefaultQueryInformation, self).to_etree()
        dqi = etree.SubElement(q, '{%s}DefaultQueryInformation' % ns_map['tdq'], nsmap = ns_map)
        for expr_id in self.targeting_expression_ids:
            te = etree.SubElement(dqi, '{%s}TargetingExpressionId' % ns_map['tdq'], nsmap = ns_map)
            te.text = expr_id
        
        for cmod in self.capability_modules:
            cm = etree.SubElement(dqi, '{%s}CapabilityModule' % ns_map['tdq'], nsmap = ns_map)
            cm.text = cmod
        return q
    
    def to_dict(self):
        d = super(DefaultQueryInformation, self).to_dict()
        d['targeting_expression_ids'] = self.targeting_expression_ids
        d['capability_modules'] = self.capability_modules
        return d
    
    def __eq__(self, other, debug=False):
        if not super(DefaultQueryInformation, self).__eq__(other, debug):
            return False
        
        if set(self.capability_modules) != set(other.capability_modules):
            if debug:
                print 'capability modules not equal: %s != %s' % (self.capability_modules, other.capability_modules)
            return False
        
        if set(self.targeting_expression_ids) != set(other.targeting_expression_ids):
            if debug:
                print 'targeting expression ids not equal: (%s) != (%s)' % (self.targeting_expression_ids, other.targeting_expression_ids)
            return False
        
        return True
    
    @staticmethod
    def from_etree(etree_xml):
        format_id = etree_xml.xpath('./@format_id', namespaces = ns_map)[0]
        texpr_ids = etree_xml.xpath('./tdq:DefaultQueryInformation/tdq:TargetingExpressionId', namespaces = ns_map)
        texpr_id_list = []
        for texpr_id in texpr_ids:
            texpr_id_list.append(texpr_id.text)
        
        cms = etree_xml.xpath('./tdq:DefaultQueryInformation/tdq:CapabilityModule', namespaces = ns_map)
        cms_list = []
        for cm in cms:
            cms_list.append(cm.text)
        return DefaultQueryInformation(format_id, texpr_id_list, cms_list)
    
    @staticmethod
    def from_dict(d):
        return DefaultQueryInformation(**d)

class DefaultQuery(tm11.Query):
    pass

tm11.register_deserializers(FID_TAXII_DEFAULT_QUERY_10, DefaultQuery, DefaultQueryInformation)