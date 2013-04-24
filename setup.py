from distutils.core import setup
setup (name='libtaxii',
       version='0.1',
       description='TAXII library',
       author='Mark Davidson',
       author_email='mdavidson@mitre.org',
       url='http://taxii.mitre.org/',
       py_modules=['libtaxii.taxii_message_converter', 'libtaxii.taxii_client']
       )