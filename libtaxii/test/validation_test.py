
# Copyright (C) 2105 - The MITRE Corporation
# For license information, see the LICENSE.txt file

import unittest

from libtaxii.validation import do_check, message_id_regex_10


class ValidationTests(unittest.TestCase):

    def test_numeric_regex_valid(self):
        # This message ID is valid. It should not raise an exception
        do_check("12345", "Test Value", regex_tuple=message_id_regex_10)

    # See: https://github.com/TAXIIProject/libtaxii/issues/166
    def test_numeric_regex_invalid_end(self):
        # This message ID is not valid.
        args = ("12345abcd", "Message ID")
        kwargs = {'regex_tuple': message_id_regex_10}
        self.assertRaises(ValueError, do_check, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
