
import unittest
import os
import glob
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
# from libtaxii.validation import SchemaValidator


class To_text_11_test(unittest.TestCase):
    input_path = os.path.join('input', '1.1')
    output_path = os.path.join('output', '1.1')

    def test_to_text_11_test(self):
        input_filenames = glob.glob(os.path.join(self.input_path, '*.xml'))
        for input_filename in input_filenames:
            input_file = open(input_filename, 'r')
            input_text = input_file.read()

            # parse the file to a TAXII message/object
            msg_from_xml = tm11.get_message_from_xml(input_text)

            # serialize the object to XML and text
            xml_from_msg = msg_from_xml.to_xml(True)
            txt_from_msg = msg_from_xml.to_text()

            # create the output files
            basename = os.path.basename(input_filename)
            name_no_ext = os.path.splitext(basename)[0]

            txt_output_filename = os.path.join(self.output_path, name_no_ext + ".txt")
            xml_output_filename = os.path.join(self.output_path, name_no_ext + ".xml")

            txt_output_file = open(txt_output_filename, 'w')
            xml_output_file = open(xml_output_filename, 'w')

            # write XML and text to files.
            txt_output_file.write(txt_from_msg)
            xml_output_file.write(xml_from_msg)

            txt_output_file.close()
            xml_output_file.close()

if __name__ == '__main__':
    unittest.main()
    