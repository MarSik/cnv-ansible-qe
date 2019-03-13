from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from six import iteritems

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


from ansible.errors import AnsibleFilterError


def countitems(value):
    uniq = {}
    for v in value:
	uniq.setdefault(v, 0)
	uniq[v] += 1
    return uniq

class FilterModule(object):
    ''' CNV QE filters for item counting'''

    def filters(self):
        return {
            'countitems': countitems
        }

