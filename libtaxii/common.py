"""
Common utility classes and functions used throughout libtaxii.

"""



from operator import attrgetter
from re import sub as resub
import dateutil.parser
import random
from libtaxii.constants import *
from lxml import etree
from uuid import uuid4
import sys
import six

try:
    import simplejson as json
except ImportError:
    import json


_XML_PARSER = None


def parse(s):
    """
    Uses the default parser to parse a string or file-like object

    :param s: The XML String or File-like object to parse
    :return: an etree._Element
    """

    try:
        e = etree.parse(s, get_xml_parser()).getroot()
    except IOError:
        e = etree.XML(s, get_xml_parser())

    return e


def parse_xml_string(xmlstr):
    """Parse an XML string (binary or unicode) with the default parser.

    :param xmlstr: An XML String to parse
    :return: an etree._Element
    """
    if isinstance(xmlstr, six.binary_type):
        xmlstr = six.BytesIO(xmlstr)
    elif isinstance(xmlstr, six.text_type):
        xmlstr = six.StringIO(xmlstr)

    return parse(xmlstr)



def get_xml_parser():
    """Return the XML parser currently in use.

    If one has not already been set (via :py:func:`set_xml_parser()`), a new
    ``etree.XMLParser`` is constructed with ``no_network=True`` and
    ``huge_tree=True``.
    """
    global _XML_PARSER
    if _XML_PARSER is None:
        _XML_PARSER = etree.XMLParser(attribute_defaults=False,
                                      dtd_validation=False,
                                      load_dtd=False,
                                      no_network=True,
                                      ns_clean=True,
                                      recover=False,
                                      remove_blank_text=False,
                                      remove_comments=False,
                                      remove_pis=False,
                                      strip_cdata=True,
                                      compact=True,
                                      # collect_ids=True,
                                      resolve_entities=False,
                                      huge_tree=False)

    return _XML_PARSER


def set_xml_parser(xml_parser=None):
    """Set the libtaxii.messages XML parser.

    Args:
        xml_parser (etree.XMLParser): The parser to use to parse TAXII XML.
    """
    global _XML_PARSER
    _XML_PARSER = xml_parser


def parse_datetime_string(datetime_string):
    """Parse a string into a :py:class:`datetime.datetime`.

    libtaxii users should not need to use this function directly.
    """
    if not datetime_string:
        return None
    return dateutil.parser.parse(datetime_string)


def generate_message_id(maxlen=5, version=VID_TAXII_SERVICES_10):
    """Generate a TAXII Message ID.

    Args:
        maxlen (int): maximum length of the ID, in characters

    Example:
        .. code-block:: python

            msg_id = tm11.generate_message_id()
            message = tm11.DiscoveryRequest(msg_id)
            # Or...
            message = tm11.DiscoveryRequest(tm11.generate_message_id())
    """
    if version == VID_TAXII_SERVICES_10:
        message_id = str(uuid4().int % sys.maxsize)
    elif version == VID_TAXII_SERVICES_11:
        message_id = str(uuid4())
    else:
        raise ValueError('Unknown TAXII Version: %s. Must be a TAXII Services Version ID!' % version)
    return message_id


def append_any_content_etree(etree_elt, content):
    """
    General method for adding content to an etree element. This method can handle:
    * etree._ElementTree
    * etree._Element
    * any python type that can be cast to str
    * str


    :param etree_elt: The etree to append the content to
    :param content: The content to append
    :return: The etree_elt
    """

    if isinstance(content, etree._ElementTree):  # If content is an element tree, append the root element
        etree_elt.append(content.getroot())
        return etree_elt

    if isinstance(content, etree._Element):  # If content is an element, append it
        etree_elt.append(content)
        return etree_elt

    if not isinstance(content, six.string_types):  # If content is a non-string, cast it to string and set etree_elt.text
        etree_elt.text = str(content)
        return etree_elt

    # If content is a string, need to check if it's XML or not
    try:
        etree_elt.append(etree.XML(content, get_xml_parser()))
    except etree.XMLSyntaxError:
        etree_elt.text = content

    return etree_elt


def gen_filename(collection_name, format_part, date_string, extension):
    """
    Creates a filename based on various properties of a Poll Request and Content Block

    :param collection_name: The collection name
    :param format_part: The format part (e.g., '_STIX_10_')
    :param date_string: A datestring
    :param extension: The file extension to use
    :return: A string containing the generated filename
    """

    filename = (collection_name.lstrip(".") +
                format_part +
                resub(r"[^a-zA-Z0-9]", "_", date_string) + extension
                ).translate(None, '/\\:*?"<>|')
    return filename


class TAXIIBase(object):

    """
    Base class for all TAXII Messages and Message component types.

    libtaxii users should not need to use this class directly.
    """

    @property
    def sort_key(self):
        """
        This property allows list of TAXII objects to be compared efficiently.
        The __eq__ method uses this property to sort the lists before
        comparisons are made.

        Subclasses must implement this property.
        """
        raise NotImplementedError()

    def to_etree(self):
        """Create an etree representation of this class.

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    def to_dict(self):
        """Create a dictionary representation of this class.

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    def to_json(self):
        """Create a JSON object of this class.

        Assumes any binary content will be UTF-8 encoded.
        """
        content_dict = self.to_dict()

        _decode_binary_fields(content_dict)

        return json.dumps(content_dict)

    def to_xml(self, pretty_print=False):
        """Create an XML representation of this class.

        Subclasses should not need to implement this method.
        """
        return etree.tostring(self.to_etree(), pretty_print=pretty_print)

    def to_text(self, line_prepend=''):
        """Create a nice looking (this is a subjective term!)
        textual representation of this class. Subclasses should
        implement this method.

        Note that this is just a convenience method for making
        TAXII Messages nice to read for humans and may change
        drastically in future versions of libtaxii.
        """
        raise NotImplementedError()

    @classmethod
    def from_etree(cls, src_etree):
        """Create an instance of this class from an etree.

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, d):
        """Create an instance of this class from a dictionary.

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    @classmethod
    def from_xml(cls, xml):
        """Create an instance of this class from XML.

        Subclasses should not need to implement this method.
        """
        etree_xml = parse_xml_string(xml)
        return cls.from_etree(etree_xml)

    # Just noting that there is not a from_text() method. I also
    # don't think there will ever be one.

    def __str__(self):
        return self.to_xml(pretty_print=True)

    def __eq__(self, other, debug=False):
        """
        Generic method used to check equality of objects of any TAXII type.

        Also allows for ``print``-based debugging output showing differences.

        In order for subclasses to use this function, they must meet the
        following criteria:
        1. All class properties start with one underscore.
        2. The sort_key property is implemented.

        Args:
            self (object): this object
            other (object): the object to compare ``self`` against.
            debug (bool): Whether or not to print debug statements as the
                equality comparison is performed.
        """
        if other is None:
            if debug:
                print('other was None!')
            return False

        if self.__class__.__name__ != other.__class__.__name__:
            if debug:
                print('class names not equal: %s != %s' % (self.__class__.__name__, other.__class__.__name__))
            return False

        # Get all member properties that start with '_'
        members = [attr for attr in vars(self) if attr.startswith('_') and not attr.startswith('__')]
        for member in members:
            if debug:
                print('member name: %s' % member)
            self_value = getattr(self, member)
            other_value = getattr(other, member)

            if isinstance(self_value, TAXIIBase):
                # A debuggable equals comparison can be made
                eq = self_value.__eq__(other_value, debug)
            elif isinstance(self_value, list):
                # We have lists to compare
                if len(self_value) != len(other_value):
                    # Lengths not equal
                    member = member + ' lengths'
                    self_value = len(self_value)
                    other_value = len(other_value)
                    eq = False
                elif len(self_value) == 0:
                    # Both lists are of size 0, and therefore equal
                    eq = True
                else:
                    # Equal sized, non-0 length lists. The list might contain
                    # TAXIIBase objects, or it might not. Peek at the first
                    # item to see whether it is a TAXIIBase object or not.
                    if isinstance(self_value[0], TAXIIBase):
                        # All TAXIIBase objects have the 'sort_key' property implemented
                        self_value = sorted(self_value, key=attrgetter('sort_key'))
                        other_value = sorted(other_value, key=attrgetter('sort_key'))
                        for self_item, other_item in six.moves.zip(self_value, other_value):
                            # Compare the ordered lists element by element
                            eq = self_item.__eq__(other_item, debug)
                    else:
                        # Assume they don't... just do a set comparison
                        eq = set(self_value) == set(other_value)
            elif isinstance(self_value, dict):
                # Dictionary to compare
                if len(set(self_value.keys()) - set(other_value.keys())) != 0:
                    if debug:
                        print('dict keys not equal: %s != %s' % (self_value, other_value))
                    eq = False
                for k, v in six.iteritems(self_value):
                    if other_value[k] != v:
                        if debug:
                            print('dict values not equal: %s != %s' % (v, other_value[k]))
                        eq = False
                eq = True
            elif isinstance(self_value, etree._Element):
                # Non-TAXII etree element (i.e. STIX)
                eq = (etree.tostring(self_value) == etree.tostring(other_value))
            else:
                # Do a direct comparison
                eq = (self_value == other_value)

            # TODO: is this duplicate?
            if not eq:
                if debug:
                    print('%s was not equal: %s != %s' % (member, self_value, other_value))
                return False

        return True

    def __ne__(self, other, debug=False):
        return not self.__eq__(other, debug)


def get_required(etree_xml, xpath, ns_map):
    elements = etree_xml.xpath(xpath, namespaces=ns_map)
    if len(elements) == 0:
        raise ValueError('Element "%s" is required' % xpath)
    return elements[0]


def get_optional(etree_xml, xpath, ns_map):
    try:
        return get_required(etree_xml, xpath, ns_map)
    except ValueError:
        pass


def get_optional_text(etree_xml, xpath, ns_map):
    try:
        return get_required(etree_xml, xpath, ns_map).text
    except ValueError:
        pass


def _decode_binary_fields(dict_obj):
    """Given a dict, decode any binary values, assuming UTF-8 encoding.
    Will recurse into nested dicts.
    Modifies the values in-place.
    """
    for key, value in dict_obj.items():

        if isinstance(value, six.binary_type):
            dict_obj[key] = value.decode('utf-8')

        elif isinstance(value, dict):
            _decode_binary_fields(value)
