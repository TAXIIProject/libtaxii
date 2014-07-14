# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# Contributors:
# * Mark Davidson - mdavidson@mitre.org

"""
Creating, handling, and parsing TAXII Default Queries.
"""

import libtaxii.messages_11 as tm11
import libtaxii as t


from .common import TAXIIBase
from .validation import (do_check, uri_regex)

from operator import attrgetter
from lxml import etree
import datetime
import os

#: Format ID for this version of TAXII Default Query
FID_TAXII_DEFAULT_QUERY_10 = 'urn:taxii.mitre.org:query:default:1.0'

# Capability Module IDs
#: Capability Module ID for Core
CM_CORE = 'urn:taxii.mitre.org:query:capability:core-1'
#: Capability Module ID for Regex
CM_REGEX = 'urn:taxii.mitre.org:query:capability:regex-1'
#: Capability Module ID for Timestamp
CM_TIMESTAMP = 'urn:taxii.mitre.org:query:capability:timestamp-1'

# Tuple of all capability modules defined in TAXII Default Query 1.0
CM_IDS = (CM_CORE, CM_REGEX, CM_TIMESTAMP)

# Operators
#:Operator OR
OP_OR = 'OR'
#:Operator AND
OP_AND = 'AND'

# Tuple of all operators
OP_TYPES = (OP_OR, OP_AND)


#: Status Type indicating an unsupported capability module
ST_UNSUPPORTED_CAPABILITY_MODULE = 'UNSUPPORTED_CAPABILITY_MODULE'
#: Status Type indicating an unsupported targeting expression
ST_UNSUPPORTED_TARGETING_EXPRESSION = 'UNSUPPORTED_TARGETING_EXPRESSION'
#: Status Type indicating an unsupported targeting expression id
ST_UNSUPPORTED_TARGETING_EXPRESSION_ID = 'UNSUPPORTED_TARGETING_EXPRESSION_ID'

#: TAXII namespace map for default queries
ns_map = {'tdq': 'http://taxii.mitre.org/query/taxii_default_query-1'}

# A Capability Module has valid relationships
# Each relationship has 0-n valid parameters

class CapabilityModule(object):
    def __init__(self, capability_module_id, relationships):
        self.capability_module_id = capability_module_id
        self.relationships = relationships

    @property
    def capability_module_id(self):
        return self._capability_module_id

    @capability_module_id.setter
    def capability_module_id(self, value):
        do_check(value, 'capability_module_id', type=basestring)
        self._capability_module_id = value

    @property
    def relationships(self):
        return self._relationships

    @relationships.setter
    def relationships(self, value):
        do_check(value, 'relationships', type=Relationship)
        self._relationships = {}
        for item in value:
            self._relationships[item.name] = item

    # def __hash__(self):
    #    return hash(self.capability_module_id)

class Relationship(object):
    def __init__(self, name, parameters=None):
        self.name = name
        self.parameters = parameters or []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        do_check(value, 'name', type=basestring)
        self._name = value

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        do_check(value, 'parameters', type=Parameter)
        self._parameters = {}
        for item in value:
            self._parameters[item.name] = item

    # def __hash__(self):
    #    return hash(self.name)


class Parameter(object):
    def __init__(self, name, type, value_tuple=None):
        self.name = name
        self.type = type
        self.value_tuple = value_tuple

    def verify(self, value):
        if not isinstance(value, self.type):
            return False, 'value not of correct type!'

        if self.value_tuple is not None:
            if value not in self.value_tuple:
                return False, 'value not in value tuple'

        return True, 'OK'

    # def deserialize(self, value):#Deserializes a value
        # if self.type

# params - Define parameters for the Core/Regex/Timestamp capability modules
param_str_value = Parameter('value', basestring)
param_float_value = Parameter('value', float)
param_ts_value = Parameter('value', datetime.datetime)
param_match_type = Parameter('match_type', basestring, ('case_sensitive_string', 'case_insensitive_string', 'number'))
param_case_sensitive = Parameter('case_sensitive', bool, (True, False))

# CORE Relationships - Define relationships for the core capability module
rel_equals = Relationship('equals', [param_str_value, param_match_type])
rel_not_equals = Relationship('not_requals', [param_str_value, param_match_type])
rel_greater_than = Relationship('greater_than', [param_float_value])
rel_greater_than_or_equal = Relationship('greater_than', [param_float_value])
rel_less_than = Relationship('greater_than', [param_float_value])
rel_less_than_or_equal = Relationship('greater_than', [param_float_value])
rel_dne = Relationship('does_not_exist')
rel_ex = Relationship('exists')
rel_begins_with = Relationship('begins_with', [param_case_sensitive, param_str_value])
rel_ends_with = Relationship('ends_with', [param_case_sensitive, param_str_value])
rel_contains = Relationship('contains', [param_case_sensitive, param_str_value])

# REGEX relationships
rel_matches = Relationship('matches', [param_case_sensitive, param_str_value])

# TIMESTAMP relationships
rel_ts_eq = Relationship('equals', [param_ts_value])
rel_ts_gt = Relationship('greater_than', [param_ts_value])
rel_ts_gte = Relationship('greater_than_or_equals', [param_ts_value])
rel_ts_lt = Relationship('less_than', [param_ts_value])
rel_ts_lte = Relationship('less_than_or_equals', [param_ts_value])

# CORE - Define the Core Capability Module
cm_core = CapabilityModule(CM_CORE, 
                           [rel_equals, rel_not_equals, rel_greater_than, 
                            rel_greater_than_or_equal, rel_less_than, 
                            rel_less_than_or_equal, rel_dne, rel_ex, 
                            rel_begins_with, rel_contains, rel_ends_with]
                           )

# REGEX - Define the RegEx Capability Module
cm_regex = CapabilityModule(CM_REGEX, [rel_matches])

# TIMESTAMP - Define the timestamp Capability Module
cm_timestamp = CapabilityModule(CM_TIMESTAMP, [rel_ts_eq, rel_ts_gt, rel_ts_gte, rel_ts_lt, rel_ts_lte])

capability_modules = {CM_CORE: cm_core, CM_REGEX: cm_regex, CM_TIMESTAMP: cm_timestamp}

class DefaultQueryInfo(tm11.SupportedQuery):
    """ Used to describe the TAXII Default Queries that are supported. 

    	:param targeting_expression_infos: Describe the supported targeting expressions
    	:type targeting_expression_infos: :class:`list` of :class:`TargetingExpressionInfo` objects
    	:param capability_modules: Indicate the supported capability modules
    	:type capability_modules: :class:`list` of :class:`str`
    """

    def __init__(self, targeting_expression_infos, capability_modules):
        super(DefaultQueryInfo, self).__init__(FID_TAXII_DEFAULT_QUERY_10)
        self.targeting_expression_infos = targeting_expression_infos
        self.capability_modules = capability_modules

    @property
    def targeting_expression_infos(self):
        return self._targeting_expression_infos

    @targeting_expression_infos.setter
    def targeting_expression_infos(self, value):
        do_check(value, 'targeting_expression_infos', type=DefaultQueryInfo.TargetingExpressionInfo)
        self._targeting_expression_infos = value

    @property
    def capability_modules(self):
        return self._capability_modules

    @capability_modules.setter
    def capability_modules(self, value):
        do_check(value, 'capability_modules', regex_tuple=uri_regex)
        self._capability_modules = value

    def to_etree(self):
        q = super(DefaultQueryInfo, self).to_etree()
        dqi = etree.SubElement(q, '{%s}Default_Query_Info' % ns_map['tdq'])
        for expression_info in self.targeting_expression_infos:
            dqi.append(expression_info.to_etree())

        for cmod in self.capability_modules:
            cm = etree.SubElement(dqi, '{%s}Capability_Module' % ns_map['tdq'], nsmap=ns_map)
            cm.text = cmod
        return q

    def to_dict(self):
        d = super(DefaultQueryInfo, self).to_dict()
        d['targeting_expression_infos'] = []
        for expression_info in self.targeting_expression_infos:
            d['targeting_expression_infos'].append(expression_info.to_dict())
        d['capability_modules'] = self.capability_modules
        return d

    def __hash__(self):
        return hash(str(self.to_dict()))

    @staticmethod
    def from_etree(etree_xml):
        texpr_infos = etree_xml.xpath('./tdq:Default_Query_Info/tdq:Targeting_Expression_Info', namespaces=ns_map)
        texpr_info_list = []
        for texpr_info in texpr_infos:
            texpr_info_list.append(DefaultQueryInfo.TargetingExpressionInfo.from_etree(texpr_info))

        cms = etree_xml.xpath('./tdq:Default_Query_Info/tdq:Capability_Module', namespaces=ns_map)
        cms_list = []
        for cm in cms:
            cms_list.append(cm.text)
        return DefaultQueryInfo(texpr_info_list, cms_list)

    @staticmethod
    def from_dict(d):
        kwargs = {}

        kwargs['targeting_expression_infos'] = []
        for expression_info in d['targeting_expression_infos']:
            kwargs['targeting_expression_infos'].append(DefaultQueryInfo.TargetingExpressionInfo.from_dict(expression_info))

        kwargs['capability_modules'] = d['capability_modules']

        return DefaultQueryInfo(**kwargs)

    class TargetingExpressionInfo(TAXIIBase):
        """This class describes supported Targeting Expressions

        	:param string targeting_expression_id: The supported targeting expression ID
        	:param preferred_scope: Indicates the preferred scope of queries
        	:type preferred_scope: :class:`list` of :class:`string`
        	:param allowed_scope: Indicates the allowed scope of queries
        	:type allowed_scope: :class:`list` of :class:`string`
        """

        def __init__(self, targeting_expression_id, preferred_scope=None, allowed_scope=None):
            self.targeting_expression_id = targeting_expression_id
            self.preferred_scope = preferred_scope or []
            self.allowed_scope = allowed_scope or []

        @property
        def sort_key(self):
            return self.targeting_expression_id

        @property
        def targeting_expression_id(self):
            return self._targeting_expression_id

        @targeting_expression_id.setter
        def targeting_expression_id(self, value):
            do_check(value, 'targeting_expression_id', regex_tuple=uri_regex)
            self._targeting_expression_id = value

        @property
        def preferred_scope(self):
            return self._preferred_scope

        @preferred_scope.setter
        def preferred_scope(self, value):
            do_check(value, 'preferred_scope', type=basestring)
            self._preferred_scope = value

        @property
        def allowed_scope(self):
            return self._allowed_scope

        @allowed_scope.setter
        def allowed_scope(self, value):
            do_check(value, 'allowed_scope', type=basestring)
            self._allowed_scope = value

        def to_etree(self):
            tei = etree.Element('{%s}Targeting_Expression_Info' % ns_map['tdq'])
            tei.attrib['targeting_expression_id'] = self.targeting_expression_id
            for scope in self.preferred_scope:
                preferred = etree.SubElement(tei, '{%s}Preferred_Scope' % ns_map['tdq'])
                preferred.text = scope
            for scope in self.allowed_scope:
                allowed = etree.SubElement(tei, '{%s}Allowed_Scope' % ns_map['tdq'])
                allowed.text = scope
            return tei

        def to_dict(self):
            d = {}
            d['targeting_expression_id'] = self.targeting_expression_id
            d['preferred_scope'] = self.preferred_scope
            d['allowed_scope'] = self.allowed_scope
            return d

        def __hash__(self):
            return hash(str(self.to_dict()))

        @staticmethod
        def from_etree(etree_xml):
            kwargs = {}
            kwargs['targeting_expression_id'] = etree_xml.xpath('./@targeting_expression_id', namespaces=ns_map)[0]
            kwargs['preferred_scope'] = []

            preferred_scope_set = etree_xml.xpath('./tdq:Preferred_Scope', namespaces=ns_map)
            for preferred in preferred_scope_set:
                kwargs['preferred_scope'].append(preferred.text)

            kwargs['allowed_scope'] = []
            allowed_scope_set = etree_xml.xpath('./tdq:Allowed_Scope', namespaces=ns_map)
            for allowed in allowed_scope_set:
                kwargs['allowed_scope'].append(allowed.text)

            return DefaultQueryInfo.TargetingExpressionInfo(**kwargs)

        @staticmethod
        def from_dict(d):
            return DefaultQueryInfo.TargetingExpressionInfo(**d)



class DefaultQuery(tm11.Query):
    """ 
        Conveys a TAXII Default Query. 

    	:param string targeting_expression_id: The targeting_expression used in the query
    	:param criteria: The criteria of the query
    	:type criteria: :class:`DefaultQuery.Criteria`
    """

    def __init__(self, targeting_expression_id, criteria):
        super(DefaultQuery, self).__init__(FID_TAXII_DEFAULT_QUERY_10)
        self.targeting_expression_id = targeting_expression_id
        self.criteria = criteria

    @property
    def targeting_expression_id(self):
        return self._targeting_expression_id

    @targeting_expression_id.setter
    def targeting_expression_id(self, value):
        do_check(value, 'targeting_expression_id', regex_tuple=uri_regex)
        self._targeting_expression_id = value

    @property
    def criteria(self):
        return self._criteria

    @criteria.setter
    def criteria(self, value):
        do_check(value, 'criteria', type=DefaultQuery.Criteria)
        self._criteria = value

    def to_etree(self):
        q = super(DefaultQuery, self).to_etree()
        dq = etree.SubElement(q, '{%s}Default_Query' % ns_map['tdq'], nsmap=ns_map)
        dq.attrib['targeting_expression_id'] = self.targeting_expression_id
        dq.append(self.criteria.to_etree())
        return q

    def to_dict(self):
        d = super(DefaultQuery, self).to_dict()
        d['targeting_expression_id'] = self.targeting_expression_id
        d['criteria'] = self.criteria.to_dict()
        return d

    @staticmethod
    def from_etree(etree_xml):
        tei = etree_xml.xpath('./tdq:Default_Query/@targeting_expression_id', namespaces=ns_map)[0]  # attrib['targeting_expression_id']
        criteria = DefaultQuery.Criteria.from_etree(etree_xml.xpath('./tdq:Default_Query/tdq:Criteria', namespaces=ns_map)[0])
        return DefaultQuery(tei, criteria)

    @staticmethod
    def from_dict(d):
        tei = d['targeting_expression_id']
        criteria = DefaultQuery.Criteria.from_dict(d['criteria'])
        return DefaultQuery(tei, criteria)

    class Criteria(TAXIIBase):
        """Represents criteria for a :class:`DefaultQuery`. **Note**: At least one criterion OR criteria MUST be present

        :param str operator: The logical operator (should be one of `OP_AND` or `OP_OR`)
        :param criteria: The criteria for the query
        :type criteria: :class:`DefaultQuery.Criteria`
        :param criterion: The criterion for the query
        :type criterion: :class:`DefaultQuery.Criterion`
        """

        def __init__(self, operator, criteria=None, criterion=None):
            self.operator = operator
            self.criteria = criteria or []
            self.criterion = criterion or []

        @property
        def sort_key(self):
            key_list = []
            ia = sorted(self.criteria, key=attrgetter('sort_key'))
            ion = sorted(self.criterion, key=attrgetter('sort_key'))
            for i in ia:
                key_list.append(i.sort_key)
            for i in ion:
                key_list.append(i.sort_key)
            return ''.join(key_list)

        @property
        def operator(self):
            return self._operator

        @operator.setter
        def operator(self, value):
            do_check(value, 'operator', value_tuple=OP_TYPES)
            self._operator = value

        @property
        def criteria(self):
            return self._criteria

        @criteria.setter
        def criteria(self, value):
            do_check(value, 'critiera', type=DefaultQuery.Criteria)
            self._criteria = value

        @property
        def criterion(self):
            return self._criterion

        @criterion.setter
        def criterion(self, value):
            do_check(value, 'criterion', type=DefaultQuery.Criterion)
            self._criterion = value

        def to_etree(self):
            cr = etree.Element('{%s}Criteria' % ns_map['tdq'], nsmap=ns_map)
            cr.attrib['operator'] = self.operator
            for criteria in self.criteria:
                cr.append(criteria.to_etree())

            for criterion in self.criterion:
                cr.append(criterion.to_etree())

            return cr

        def to_dict(self):
            d = {}
            d['operator'] = self.operator

            d['criteria'] = []
            for criteria in self.criteria:
                d['criteria'].append(criteria.to_dict())

            d['criterion'] = []
            for criterion in self.criterion:
                d['criterion'].append(criterion.to_dict())

            return d

        @staticmethod
        def from_etree(etree_xml):
            kwargs = {}
            kwargs['operator'] = etree_xml.attrib['operator']

            kwargs['criteria'] = []
            criteria_set = etree_xml.xpath('./tdq:Criteria', namespaces=ns_map)
            for criteria in criteria_set:
                kwargs['criteria'].append(DefaultQuery.Criteria.from_etree(criteria))

            kwargs['criterion'] = []
            criterion_set = etree_xml.xpath('./tdq:Criterion', namespaces=ns_map)
            for criterion in criterion_set:
                kwargs['criterion'].append(DefaultQuery.Criterion.from_etree(criterion))

            return DefaultQuery.Criteria(**kwargs)

        @staticmethod
        def from_dict(d):
            kwargs = {}
            kwargs['operator'] = d['operator']

            kwargs['criteria'] = []
            criteria_set = d.get('criteria', [])
            for criteria in criteria_set:
                kwargs['criteria'].append(DefaultQuery.Criteria.from_dict(criteria))

            kwargs['criterion'] = []
            criterion_set = d.get('criterion', [])
            for criterion in criterion_set:
                kwargs['criterion'].append(DefaultQuery.Criterion.from_dict(criterion))

            return DefaultQuery.Criteria(**kwargs)

    class Criterion(TAXIIBase):
        """Represents criterion for a :class:`DefaultQuery.Criteria`

        	:param string target: A targeting expression identifying the target
        	:param test: The test to be applied to the target
        	:type test: :class:`DefaultQuery.Criterion.Test`
        	:param bool negate: Whether the result of applying the test to the target should be negated
        """

        def __init__(self, target, test, negate=False):
            self.negate = negate
            self.target = target
            self.test = test

        @property
        def sort_key(self):
            return self.target

        @property
        def negate(self):
            return self._negate

        @negate.setter
        def negate(self, value):
            do_check(value, 'negate', value_tuple=(True, False), can_be_none=True)
            self._negate = value

        @property
        def target(self):
            return self._target

        @target.setter
        def target(self, value):
            do_check(value, 'target', type=basestring)
            self._target = value

        @property
        def test(self):
            return self._test

        @test.setter
        def test(self, value):
            do_check(value, value, type=DefaultQuery.Criterion.Test)
            self._test = value

        def to_etree(self):
            cr = etree.Element('{%s}Criterion' % ns_map['tdq'], nsmap=ns_map)
            if self.negate is not None:
                cr.attrib['negate'] = str(self.negate).lower()

            target = etree.SubElement(cr, '{%s}Target' % ns_map['tdq'], nsmap=ns_map)
            target.text = self.target

            cr.append(self.test.to_etree())

            return cr

        def to_dict(self):
            d = {}
            d['negate'] = None
            if self.negate is not None:
                d['negate'] = self.negate
            d['target'] = self.target
            d['test'] = self.test.to_dict()

            return d

        @staticmethod
        def from_etree(etree_xml):
            negate_set = etree_xml.xpath('./@negate')
            negate = None
            if len(negate_set) > 0:
                negate = negate_set[0] == 'true'

            target = etree_xml.xpath('./tdq:Target', namespaces=ns_map)[0].text
            test = DefaultQuery.Criterion.Test.from_etree(etree_xml.xpath('./tdq:Test', namespaces=ns_map)[0])

            return DefaultQuery.Criterion(target, test, negate)

        @staticmethod
        def from_dict(d):
            negate = d.get('negate', None)
            target = d['target']
            test = DefaultQuery.Criterion.Test.from_dict(d['test'])

            return DefaultQuery.Criterion(target, test, negate)

        class Test(TAXIIBase):
            """
            	:param string capability_id: The ID of the capability module that defines the relationship & parameters
            	:param string relationship: The relationship (e.g., equals)
            	:param parameters: The parameters for the relationship.
            	:type parameters: :class:`dict` of key/value pairs
            """

            def __init__(self, capability_id, relationship, parameters=None):
                self.capability_id = capability_id
                self.relationship = relationship
                self.parameters = parameters or {}

                self.validate()

            @property
            def capability_id(self):
                return self._capability_id

            @capability_id.setter
            def capability_id(self, value):
                do_check(value, 'capability_id', regex_tuple=uri_regex)
                self._capability_id = value

            @property
            def relationship(self):
                return self._relationship

            @relationship.setter
            def relationship(self, value):
                # TODO: For known capability IDs, check that the relationship is valid
                # TODO: provide a way to register other capability IDs
                do_check(value, 'relationship', type=basestring)
                self._relationship = value

            @property
            def parameters(self):
                return self._parameters

            @parameters.setter
            def parameters(self, value):
                do_check(value.keys(), 'parameters.keys()', regex_tuple=uri_regex)
                self._parameters = value

            # TODO: Can this be done better?
            def validate(self):
                capability_module = capability_modules.get(self.capability_id)
                if capability_module is None:  # Nothing is defined for this, validation not possible
                    print 'Cannot validate'
                    return True

                relationship = capability_module.relationships.get(self.relationship)
                if relationship is None:
                    raise Exception('relationship not in defined relationships. %s not in %s' % (self.relationship, capability_module.relationships.keys()))


                for name, value in self.parameters.items():
                    param = relationship.parameters.get(name)
                    if param is None:
                        raise Exception('name not valid. %s not in %s' % (name, relationship.parameters.keys()))
                    param.verify(value)

            def to_etree(self):
                t = etree.Element('{%s}Test' % ns_map['tdq'], nsmap=ns_map)
                t.attrib['capability_id'] = self.capability_id
                t.attrib['relationship'] = self.relationship

                for k, v in self.parameters.items():
                    p = etree.SubElement(t, '{%s}Parameter' % ns_map['tdq'])
                    p.attrib['name'] = k
                    if isinstance(v, bool):
                        p.text = str(v).lower()
                    elif isinstance(v, datetime.datetime):
                        p.text = v.isoformat()
                    else:
                        p.text = v

                return t

            def to_dict(self):
                d = {}
                d['capability_id'] = self.capability_id
                d['relationship'] = self.relationship
                d['parameters'] = self.parameters
                return d

            @staticmethod
            def from_etree(etree_xml):
                capability_id = etree_xml.attrib['capability_id']
                relationship = etree_xml.attrib['relationship']
                parameters = {}
                for parameter in etree_xml.xpath('./tdq:Parameter', namespaces=ns_map):
                    k = parameter.attrib['name']
                    v = parameter.text
                    if v in ('true', 'false'):  # Assume bool
                        parameters[k] = v == 'true'
                    else:
                        try:  # attempt to deserialize as a datetime
                            parameters[k] = dateutil.parser.parse(v)
                        except:  # Just use it as a string
                            parameters[k] = v

                return DefaultQuery.Criterion.Test(capability_id, relationship, parameters)

            @staticmethod
            def from_dict(d):
                return DefaultQuery.Criterion.Test(**d)

package_dir, package_filename = os.path.split(__file__)
schema_file = os.path.join(package_dir, "xsd", "TAXII_DefaultQuery_Schema.xsd")

tm11.register_query_format(
    format_id=FID_TAXII_DEFAULT_QUERY_10, 
    query=DefaultQuery,
    query_info=DefaultQueryInfo,
    schema=schema_file)
