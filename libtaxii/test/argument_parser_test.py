import os
import unittest

import libtaxii.scripts.poll_client as pc11


class ArgumentParserTests(unittest.TestCase):

    def setUp(self):
        self.module_path = os.path.dirname(__file__)

    def test_valid_argument_passing_poll_client11(self):
        script = pc11.PollClient11Script()
        arg_parse = script.get_arg_parser(script.parser_description, path=script.path)
        namespace = arg_parse.parse_args(
            [
                "--from-file", os.path.join(self.module_path, "data", "configuration.ini")
            ]
        )
        self.assertEqual(namespace.url, "http://hailataxii2.com:80")
        self.assertEqual(namespace.path, "/taxii-data")
        self.assertEqual(namespace.port, 80)
        self.assertEqual(namespace.password, "myS3crEtp@asswOrd!")

    def test_argument_override_poll_client11(self):
        script = pc11.PollClient11Script()
        arg_parse = script.get_arg_parser(script.parser_description, path=script.path)
        namespace = arg_parse.parse_args(
            [
                "-u", "http://hailataxii.com:80",
                "--from-file", os.path.join(self.module_path, "data", "configuration.ini")
            ]
        )
        self.assertEqual(namespace.url, "http://hailataxii2.com:80")  # note the argument was overwritten
        self.assertEqual(namespace.path, "/taxii-data")
        self.assertEqual(namespace.port, 80)
        self.assertEqual(namespace.password, "myS3crEtp@asswOrd!")
