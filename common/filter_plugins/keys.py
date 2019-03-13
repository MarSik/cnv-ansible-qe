from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


from ansible.errors import AnsibleFilterError


def keys(value):
    if hasattr(value, "keys"):
        return value.keys()
   
    templates = list(value)

    try:
        return [ v.keys() for v in templates ]
    except TypeError as te:
        raise AnsibleFilterError('Not a dictionary: %s' % value)

class FilterModule(object):
    ''' CNV QE filters '''

    def filters(self):
        return {
            'keys': keys
        }

