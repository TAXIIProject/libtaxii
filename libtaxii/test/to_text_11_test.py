
#!/usr/bin/env python
# Copyright (c) 2015, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import glob
import os
import libtaxii.messages_11 as tm11


input_path = os.path.join('input', '1.1')
output_path = os.path.join('output', '1.1')

def main():
    input_fns = glob.glob(os.path.join(input_path, '*.xml'))

    for input_fn in input_fns:
        with open(input_fn, 'r') as f:
            text = f.read()

        # parse the file to a TAXII message/object
        msg = tm11.get_message_from_xml(text)

        # create the output files
        basename = os.path.splitext(os.path.basename(input_fn))[0]

        # write XML and text to files.
        xml_out = os.path.join(output_path, basename + ".xml")
        with open(xml_out, 'w') as f:
            f.write(msg.to_xml(pretty_print=True))

        txt_out = os.path.join(output_path, basename + ".txt")
        with open(txt_out, 'w') as f:
            f.write(msg.to_text())
        raise


if __name__ == '__main__':
    main()
