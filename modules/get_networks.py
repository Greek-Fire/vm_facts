#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_networks
version_added: 1.0.0
short_description: Retrieve a list of networks connected to more than one datacenter and more than one cluster in a vCenter.
description:
  - This module uses the vCenter API to retrieve a list of networks connected to more than one datacenter and more than one cluster.
  - You can filter the networks by datacenters and/or clusters.
  - Returns a list of dictionaries containing the network name, datacenter name, and cluster name for each network.
author:
  - "Louis Tiches"
options:
  host:
    description: The hostname or IP address of the vCenter server.
    required: true
    type: str
  username:
    description: The username to use for authentication with the vCenter server.
    required: true
    type: str
  password:
    description: The password to use for authentication with the vCenter server.
    required: true
    type: str
  disable_ssl_verification:
    description: Whether to disable SSL certificate verification for the vCenter server.
    required: false
    default: false
    type: bool
  datacenters:
    description: A list of datacenter names to filter by. If not specified, retrieves all datacenters.
    required: false
    default: []
    type: list
  clusters:
    description: A list of cluster names to filter by. If not specified, retrieves all clusters.
    required: false
    default: []
    type: list
'''

EXAMPLES = '''
- name: Get vCenter networks
  get_networks:
    host: vcenter.example.com
    username: admin
    password: password
    datacenters:
      - Datacenter1
    clusters:
      - Cluster1
  register: vcenter_networks

- name: Debug vCenter networks
  debug:
    var: get_networks.ansible_facts.vcenter_networks
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts


def main():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(type='bool', default=False),
        datacenters=dict(type='list', default=[]),
        clusters=dict(type='list', default=[]),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Retrieve vCenter facts and filter networks by datacenters and clusters
    vcenter_facts = VcenterFacts(
        module.params['host'],
        module.params['username'],
        module.params['password'],
        module.params['disable_ssl_verification'],
    )
    networks = vcenter_facts.get_networks(
        datacenters=module.params['datacenters'],
        clusters=module.params['clusters'],
    )

    module.exit_json(changed=False, ansible_facts=dict(vcenter_networks=networks))


if __name__ == '__main__':
    main()