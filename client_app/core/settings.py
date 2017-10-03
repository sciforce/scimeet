import json
from datetime import time

AVAILABLE_TIME_MINIMUM_DURATION = 900
EVENT_MINIMUM_DURATION = 900
WORKDAY_START = time(9, 0, 0)
WORKDAY_END = time(20, 0, 0)


GC_CONFIG = {"SCOPES": "https://www.googleapis.com/auth/calendar",
             "CLIENT_SECRET_FILE": "./google_secret.json",
             "APPLICATION_NAME": "SciMeet",
             "CREDENTIAL_PATH": "./google_credentials.json"}


def get_settings_temlate():
    """
    return json.dumps([{'type': 'title',
                        'title': 'example title'},
                       {'type': 'bool',
                        'title': 'A boolean setting',
                        'desc': 'Boolean description text',
                        'section': 'example',
                        'key': 'boolexample'},
                       {'type': 'numeric',
                        'title': 'A numeric setting',
                        'desc': 'Numeric description text',
                        'section': 'example',
                        'key': 'numericexample'},
                       {'type': 'options',
                        'title': 'An options setting',
                        'desc': 'Options description text',
                        'section': 'example',
                        'key': 'optionsexample',
                        'options': ['option1', 'option2', 'option3']},
                       {'type': 'string',
                        'title': 'A string setting',
                        'desc': 'String description text',
                        'section': 'example',
                        'key': 'stringexample'},
                       {'type': 'path',
                        'title': 'A path setting',
                        'desc': 'Path description text',
                        'section': 'example',
                        'key': 'pathexample'}])
    """
    return json.dumps([{'type': 'bool',
                        'title': 'Debug mode',
                        'desc': 'Mute network errors if disabled',
                        'section': 'main',
                        'key': 'debugmode'}])


def get_default_settings():
    """
      {'debugmode': True,
       'numericexample': 10,
       'optionsexample': 'option2',
       'stringexample': 'some_string',
       'pathexample': '/some/path'}
    """
    return 'main', {'debugmode': True}
