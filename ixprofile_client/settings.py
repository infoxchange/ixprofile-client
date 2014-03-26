"""
Standard config for defining required Django settings for connecting with
Profile Server
"""

import os
import sys

# Copy BASE_DIR from the main configuration
BASE_DIR = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']].BASE_DIR

# Environment
ENVIRONMENT = os.environ.get('ENVIRONMENT', None)

if ENVIRONMENT in (None, 'dev', 'dev_local'):
    PROFILE_SERVER = os.environ.get('PROFILE_SERVER_URL',
                                    'https://profiles.docker.dev/')
    PROFILE_SERVER_KEY = os.environ.get('PROFILE_SERVER_KEY', 'iss3-dev')
    PROFILE_SERVER_SECRET = os.environ.get('PROFILE_SERVER_SECRET',
                                           '1Bn7W3V9Xb3HLrwZ1zXE6EGacbQxlGch')
    SSL_CA_FILE = os.path.join(BASE_DIR, 'conf', 'ixacustomca.crt')

elif ENVIRONMENT in ('test',):
    PROFILE_SERVER = 'https://profiles-test.docker.dev/'
    PROFILE_SERVER_KEY = 'iss3-test'
    PROFILE_SERVER_SECRET = 'HqEPT7NX6jXDAmwlgsNvgR9OW955C601'
