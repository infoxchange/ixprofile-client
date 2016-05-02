# IXProfileClient

[![Build Status](https://travis-ci.org/infoxchange/ixprofile-client.svg?branch=master)](https://travis-ci.org/infoxchange/ixprofile-client)
[![Coverage Status](https://coveralls.io/repos/github/infoxchange/ixprofile-client/badge.svg)](https://coveralls.io/github/infoxchange/ixprofile-client)
[![PyPI](https://img.shields.io/pypi/v/ixprofile-client.svg?maxAge=2592000)](https://pypi.python.org/pypi/ixprofile-client)

Library package for Django applications using the IX Profiles server for
authentication and user management.


## Functionality

* Logging in is managed by the profile server. Users are redirected to its
  login page for logging in.
* Users are identified by emails, they use their email to log in to the profile
  server.
* User details (e.g. names) are updated from the profile server.
* Creating new users in the admin creates them on the profile server. Setting
  is_active flag subscribes and unsubscribes them from the application.


## Usage

To connect to the profile server, the following settings should be configured:

```
# The URL of the profile server to use.
PROFILE_SERVER = 'https://profiles.somewhere/'

# Key and secret to authenticate on the profile server for user management.
# Must correspond to a registered Website on the profile server specified by
# the above URL.
PROFILE_SERVER_KEY = 'myapp'
PROFILE_SERVER_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

LOGIN_URL = 'ixprofile-start-login'

INSTALLED_APPS = (
    # other applications,
    'social.apps.django_app.default',
    'ixprofile_client',
)

AUTHENTICATION_BACKENDS = (
    'ixprofile_client.backends.IXProfile',
    # any other backends you might want; default ModelBackend is not needed
)
```

If using Django < 1.7, include:

```
from ixprofile_client import SOCIAL_AUTH_PIPELINE

In urls.py, include the following:

url(r'', include('ixprofile_client.urls'))
```
