from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from six import iteritems

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


from ansible.errors import AnsibleFilterError


def k8s_condition(status, name):
    return any(cond.get("status", False) == "True" and cond["type"] == name for cond in status.get("conditions", []))

def k8s_condition_message(status, name):
    for cond in status.get("conditions", []):
      if cond["type"] == name:
        return cond.get("message", "")

class FilterModule(object):
    ''' CNV QE filters for checking the presence of status conditions'''

    def filters(self):
        return {
            'k8s_condition': k8s_condition,
            'k8s_condition_message': k8s_condition_message
        }

