#!/usr/bin/env python
# vim: sw=4 sts=4 et ft=python
"""Prepare ansible inventory record for minishift nodes

Usage:
  bootstrap --list
  bootstrap --host <name>
  bootstrap -h | --help
  bootstrap --version

Options:
  -h --help     Show this screen.
  --list        Generate json with ansible inventory.
  --host <name> Generate json vars for specified host.
"""

import json
import os
from docopt import docopt
import sys

from kubernetes import client, config
from openshift.dynamic import DynamicClient

from six import iteritems

def compute_groups(labels):
    groups = []
    for k,v in iteritems(labels):
        if k.startswith("node-role.kubernetes.io/") and v:
            groups.append(k.split("/")[1])

    return groups or ["master", "infra", "worker"]

def get_nodes():
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)

    v1_nodes = dyn_client.resources.get(api_version='v1', kind='Node')

    v1_node_list = v1_nodes.get()
    node_details = [node for node in v1_node_list.items]

    first_ip = lambda node: next(addr.address
                 for addr in node.status.addresses
                 if addr.address != "localhost" and addr.address != "127.0.0.1")

    nodes = [{
        "name": node.metadata.name if node.metadata.name != "localhost" else "node",
        "groups": ["cnv"] + compute_groups(node.metadata.labels),
        "vars": {
            "ansible_ssh_host": first_ip(node),
            "ansible_become": True,
            "ansible_become_method": "sudo",
            "ansible_user": "docker",
            "ansible_ssh_private_key_file": "~/.minishift/machines/minishift/id_rsa",
            "ssh_via_arguments": "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o 'ProxyCommand ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -W %h:%p -i ~/.minishift/machines/minishift/id_rsa docker@" + first_ip(node) + "'"

        }
    } for node in node_details]

    out = {
        "_meta": {
            "hostvars": {
                node["name"]: node["vars"] for node in nodes
            }
        },
    }

    for node in nodes:
        for group in node["groups"]:
            out.setdefault(group, {"hosts": [], "vars": {}})
            out[group]["hosts"].append(node["name"])

    return out

if __name__ == "__main__":
    arguments = docopt(__doc__, version='CNV inventory 1.0')
    if "--list" in arguments:
        print(json.dumps(get_nodes()))
    elif "--host" in arguments:
        print("{}")
    else:
        print(__doc__)
        sys.exit(255)

