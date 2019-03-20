from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from six import iteritems

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


from ansible.errors import AnsibleFilterError

def keys(value):
    '''Get list of keys in dictionary'''
    if hasattr(value, "keys"):
        return value.keys()
   
    templates = list(value)

    try:
        return [ v.keys() for v in templates ]
    except TypeError as te:
        raise AnsibleFilterError('Not a dictionary: %s' % value)

def countitems(value):
    '''Count occurences of value in list'''
    uniq = {}
    for v in value:
	uniq.setdefault(v, 0)
	uniq[v] += 1
    return uniq

def varname(value):
    '''Ansible variable name sanitization'''
    return value.replace(".", "_").replace("-", "_")

class FilterModule(object):
    ''' CNV QE filters for ansible data manipulation'''

    def filters(self):
        return {
            'countitems': countitems,
            'keys': keys,
            'varname': varname
        }

