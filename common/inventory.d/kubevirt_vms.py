#!/usr/bin/env python
# vim: sw=4 sts=4 et ft=python
"""Prepare ansible inventory record for kubevirt VMs

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

import minishift

def get_nodes():
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)

    v1_vmis = dyn_client.resources.get(api_version='kubevirt.io/v1alpha3', kind='VirtualMachineInstance')

    v1_vmi_list = v1_vmis.get()
    vmi_details = [vmi for vmi in v1_vmi_list.items]

    # Find a master node and get SSH proxy options
    # from it. This is needed to connect to minishift VMs
    # as they are hidden withing the minishift host virtual machine
    cluster_inventory = minishift.get_nodes()
    master_node = cluster_inventory["masters"]["hosts"][0]
    extra_ssh_args = cluster_inventory["_meta"]["hostvars"][master_node].get("ssh_via_arguments", "")

    first_ip = lambda vmi: next(intf.ipAddress
                for intf in vmi.status.interfaces
                if intf.ipAddress != "127.0.0.1" and \
                   any(s.status == "True" and s.type == "Ready" for s in vmi.status.conditions))

    nodes = [{
        "name": vmi.metadata.name if vmi.metadata.name != "localhost" else "vm",
        "groups": ["vms"],
        "vars": {
            "ansible_ssh_host": first_ip(vmi),
            "ansible_ssh_extra_args": extra_ssh_args,
            "ansible_become": False,
            "ansible_user": "root",
            "ansible_become_method": "sudo",
            "ansible_ssh_pass": "password"
        }
    } for vmi in vmi_details if vmi.status.interfaces]

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
    arguments = docopt(__doc__, version='CNV VM inventory 1.0')
    if "--list" in arguments:
        print(json.dumps(get_nodes()))
    elif "--host" in arguments:
        print("{}")
    else:
        print(__doc__)
        sys.exit(255)

