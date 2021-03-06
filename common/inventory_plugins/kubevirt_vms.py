#!/usr/bin/env python
# vim: sw=4 sts=4 et ft=python
"""Ansible inventory plugin for kubevirt VMs
"""
from __future__ import absolute_import

import json
from six import iteritems

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# HACK import the inventory plugin openshift_nodes while running in Ansible
import imp
import os.path
openshift_nodes = imp.load_source('openshift_nodes',
    os.path.join(os.path.dirname(__file__), 'openshift_nodes.py'))
ansible_annotation_vars = openshift_nodes.ansible_annotation_vars
dict_merge = openshift_nodes.dict_merge


def get_vms():
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)

    v1_vmis = dyn_client.resources.get(api_version='kubevirt.io/v1alpha3', kind='VirtualMachineInstance')

    v1_vmi_list = v1_vmis.get()
    vmi_details = [vmi for vmi in v1_vmi_list.items]

    # Find a master node and get SSH proxy options
    # from it. This is needed to connect to minishift VMs
    # as they are hidden withing the minishift host virtual machine
    cluster_inventory = [node for node in openshift_nodes.get_nodes()
                              if "master" in node["groups"]]
    master_node = cluster_inventory[0]
    extra_ssh_args = cluster_inventory[0]["vars"].get("ssh_via_arguments", "")

    first_ip = lambda vmi: next(intf.ipAddress
                for intf in vmi.status.interfaces
                if intf.ipAddress != "127.0.0.1" and \
                   any(s.status == "True" and s.type == "Ready" for s in vmi.status.conditions))

    nodes = [{
        "name": vmi.metadata.name if vmi.metadata.name != "localhost" else "vm",
        "groups": ["vms"],
        "vars": dict_merge({
            "ansible_ssh_host": first_ip(vmi),
            "ansible_ssh_extra_args": extra_ssh_args,
            "ansible_become": False,
            "ansible_user": "root",
            "ansible_become_method": "sudo",
            "ansible_ssh_pass": "password"
        }, ansible_annotation_vars(vmi.metadata.annotations))
    } for vmi in vmi_details if vmi.status.interfaces]

    return nodes

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = 'kubevirt_vms'
    
    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        # base class verifies that file exists and is readable by current user
        return super(InventoryModule, self).verify_file(path) and \
            path.endswith(('kubevirt.yaml',
                           'kubevirt.yml'))

    def parse(self, inventory, loader, path, cache=True):
        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        config = self._read_config_data(path)

        for node in get_vms():
            self.inventory.add_host(node["name"])
            for k, v in iteritems(node["vars"]):
                self.inventory.set_variable(node["name"], k, v)
            for group in node["groups"]:
                self.inventory.add_group(group)
                self.inventory.add_child(group, node["name"])


