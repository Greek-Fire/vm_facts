#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_clusters
version_added: 1.0.0
short_description: Retrieve a list of clusters in a vCenter.
description:
  - This module uses the vCenter API to retrieve a list of clusters.
  - You can filter the clusters by datacenter name.
  - Returns a list of cluster names.
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
  datacenter:
    description: The name of the datacenter to filter by. If not specified, retrieves all clusters.
    required: false
    type: list
'''

EXAMPLES = '''
- name: Get vCenter clusters
  get_clusters:
    host: vcenter.example.com
    username: admin
    password: password
    datacenter: 
    - Datacenter1
  register: vcenter_clusters

- name: Debug vCenter clusters
  debug:
    var: vcenter_clusters.ansible_facts.vcenter_clusters
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts


def main():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(type='bool', default=False),
        datacenter=dict(type='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Retrieve vCenter facts and get clusters
    vcenter_facts = VcenterFacts(
        module.params['host'],
        module.params['username'],
        module.params['password'],
        module.params['disable_ssl_verification'],
    )
    clusters = vcenter_facts.get_clusters(module.params['datacenter'])

    module.exit_json(changed=False, ansible_facts=dict(vcenter_clusters=clusters))


if __name__ == '__main__':
    main()