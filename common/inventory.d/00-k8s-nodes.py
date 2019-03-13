#!/usr/bin/env python
# vim: sw=4 sts=4 et ft=python
"""Prepare ansible inventory record for API endpoint

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

def get_nodes():
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)

    v1_nodes = dyn_client.resources.get(api_version='v1', kind='Node')

    v1_node_list = v1_nodes.get()
    node_details = [node for node in v1_node_list.items]

    nodes = [{
        "name": node.metadata.name if node.metadata.name != "localhost" else "node",
        "groups": ["cnv", "masters", "etcd", "nodes"],
        "vars": {
            "ansible_ssh_host": next(addr.address
                for addr in node.status.addresses
                if addr.address != "localhost" and addr.address != "127.0.0.1"),
            "ansible_become": True,
            "ansible_become_method": "sudo",
            "ansible_user": "docker",
            "ansible_ssh_private_key_file": "~/.minishift/machines/minishift/id_rsa"
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

