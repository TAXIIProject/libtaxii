# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# Contributors:
# * Mark Davidson - mdavidson@mitre.org

"""
Common data validation functions used across libtaxii
"""


import collections
import re
import datetime
from lxml import etree
import os

from .common import (parse, parse_datetime_string)
import six

# General purpose helper methods #

RegexTuple = collections.namedtuple('_RegexTuple', ['regex', 'title'])
# URI regex per http://tools.ietf.org/html/rfc3986
uri_regex = RegexTuple("(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", "URI Format")
message_id_regex_10 = RegexTuple("^[0-9]+$", "Numbers only")
targeting_expression_regex = RegexTuple("^(@?\w+|\*{1,2})(/(@?\w+|\*{1,2}))*$", "Targeting Expression Syntax")

_none_error = "%s is not allowed to be None and the provided value was None"
_type_error = "%s must be of type %s. The incorrect value was of type %s"
_regex_error = "%s must be a string conforming to %s. The incorrect value was: %s"
_tuple_error = "%s must be one of %s. The incorrect value was %s"


def do_check(var, varname, type=None, regex_tuple=None, value_tuple=None, can_be_none=False):
    """
    Checks supplied var against all of the supplied checks using the following
    process:

    1. If var is iterable, call this function for every item in the iterable object
    2. If the var is none and can be none, return
    3. If the var is none and cannot be none, raise ValueError
    4. If a type is specified, and the var is not of the specified type, raise ValueError
    5. If a regex is specified, and the var doesn't match the regex, raise ValueError
    6. If a value_tuple is specified, and the var is not in the value_tuple, raise ValueError

    varname is used in the error messages

    """

    if isinstance(var, list) or isinstance(var, set) or isinstance(var, tuple):

        x = 0
        for item in var:
            do_check(item, "%s[%s]" % (varname, x), type, regex_tuple, value_tuple, can_be_none)
            x = x + 1

        return

    if var is None and can_be_none:
        return

    if var is None and not can_be_none:
        raise ValueError(_none_error % varname)

    if type is not None:
        if not isinstance(var, type):
            bad_type = var.__class__.__name__
            raise ValueError(_type_error % (varname, type, bad_type))

    if regex_tuple is not None:
        if not isinstance(var, six.string_types):
            raise ValueError('%s was about to undergo a regex check, but is not of type basestring! Regex check was not performed' % (varname))
        if re.match(regex_tuple.regex, var) is None:
            raise ValueError(_regex_error % (varname, regex_tuple.title, var))

    if value_tuple is not None:
        if var not in value_tuple:
            raise ValueError(_tuple_error % (varname, value_tuple, var))
    return


def check_timestamp_label(timestamp_label, varname, can_be_none=False):
    """
    Checks the timestamp_label to see if it is a valid timestamp label
    using the following process:

    1. If the timestamp_label is None and is allowed to be None, Pass
    2. If the timestamp_label is None and is not allowed to be None, Fail
    3. If the timestamp_label arg is a string, convert to datetime
    4. If the timestamp_label does not have a tzinfo attribute, Fail
    5. Pass
    """

    if timestamp_label is None and can_be_none:
        return

    if timestamp_label is None and not can_be_none:
        raise ValueError(_none_error % varname)

    if isinstance(timestamp_label, six.string_types):
        timestamp_label = parse_datetime_string(timestamp_label)

    do_check(timestamp_label, varname, type=datetime.datetime, can_be_none=can_be_none)

    if timestamp_label.tzinfo is None:
        raise ValueError('%s.tzinfo must not be None!' % varname)

    return timestamp_label


class SchemaValidationResult(object):
    """A wrapper for the results of schema validation."""

    def __init__(self, valid, error_log):
        self.valid = valid
        self.error_log = error_log

_pkg_dir = os.path.dirname(__file__)

#: Automatically-calculated path to the bundled TAXII 1.0 schema.
TAXII_10_SCHEMA = os.path.join(_pkg_dir, "xsd", "TAXII_XMLMessageBinding_Schema.xsd")

#: Automatically-calculated path to the bundled TAXII 1.1 schema.
TAXII_11_SCHEMA = os.path.join(_pkg_dir, "xsd", "TAXII_XMLMessageBinding_Schema_11.xsd")


class SchemaValidator(object):
    """
    A helper class for TAXII Schema Validation.

    Example:
        See validate_etree(...) for an example how to use this class
    """

    # Create class-level variables equal to module-level variables for
    # backwards-compatibility
    TAXII_10_SCHEMA = TAXII_10_SCHEMA
    TAXII_11_SCHEMA = TAXII_11_SCHEMA

    def __init__(self, schema_file):
        """
        Args:
            schema_file (str) - The file location of the schema to
                                validate against. Use the TAXII_11_SCHEMA
                                and TAXII_10_SCHEMA constants to validate
                                against TAXII 1.1 / 1.0. This schema file
                                will be used when validate_file/string/etree
                                is used.
        """
        schema_doc = parse(schema_file)
        self.xml_schema = etree.XMLSchema(schema_doc)

    def validate_file(self, file_location):
        """
        A wrapper for validate_etree. Parses file_location,
        turns it into an etree, then calls validate_etree( ... )
        """

        with open(file_location, 'r') as f:
            etree_xml = parse(f)

        return self.validate_etree(etree_xml)

    def validate_string(self, xml_string):
        """
        A wrapper for validate_etree. Parses xml_string,
        turns it into an etree, then calls validate_etree( ... )
        """
        etree_xml = parse(xml_string)
        return self.validate_etree(etree_xml)

    def validate_etree(self, etree_xml):
        """Validate an LXML etree with the specified schema_file.

        Args:
            etree_xml (etree): The XML to validate.
            schema_file (str): The schema file to validate against

        Returns:
            A SchemaValidationResult object

        Raises:
            lxml.etree.XMLSyntaxError: When the XML to be validated is not well formed

        Example:
            .. code-block:: python

                from libtaxii import messages_11
                from libtaxii.validation import SchemaValidator, TAXII_11_SCHEMA
                from lxml.etree import XMLSyntaxError

                sv = SchemaValidator(TAXII_11_SCHEMA)

                try:
                   result = sv.validate_etree(some_etree)
                   # Note that validate_string() and validate_file() can also be used
                except XMLSyntaxError:
                    # Handle this exception, which occurs when
                    # some_xml_string is not valid XML (e.g., 'foo')

                if not result.valid:
                    for error in result.error_log:
                        print error
                    sys.exit(1)

                # At this point, the XML is schema valid
                do_something(some_xml_string)
        """
        valid = self.xml_schema.validate(etree_xml)
        return SchemaValidationResult(valid, self.xml_schema.error_log)


class TAXII10Validator(SchemaValidator):
    """A :py:class:`SchemaValidator` that uses the TAXII 1.0 Schemas"""

    def __init__(self):
        super(TAXII10Validator, self).__init__(TAXII_10_SCHEMA)


class TAXII11Validator(SchemaValidator):
    """A :py:class:`SchemaValidator` that uses the TAXII 1.1 Schemas"""

    def __init__(self):
        super(TAXII11Validator, self).__init__(TAXII_11_SCHEMA)
