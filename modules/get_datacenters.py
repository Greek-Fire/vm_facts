#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_datacenters
version_added: 1.0.0
short_description: Retrieve a list of datacenters in a vCenter.
description:
  - This module uses the vCenter API to retrieve a list of datacenters.
  - Returns a list of datacenter names.
author:
  - "Louis Tiches"
options:
  vcenter:
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
'''

EXAMPLES = '''
- name: Get vCenter datacenters
  get_datacenters:
    vcenter: vcenter.example.com
    username: admin
    password: password
  register: vcenter_datacenters

- name: Debug vCenter datacenters
  debug:
    var: vcenter_datacenters.ansible_facts.vcenter_datacenters
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts

def main():
    module_args = dict(
        vcenter=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Retrieve vCenter facts and get datacenters
    vcenter_facts = VcenterFacts(
        module.params['vcenter'],
        module.params['username'],
        module.params['password'],
        module.params['disable_ssl_verification'],
    )
    try:
        vcenter_facts = VcenterFacts(vcenter, username, password, disable_ssl_verification)
        datacenter = vcenter_facts.get_datacenters()
        result['datacenter'] = [dc.name for dc in datacenter]
    except Exception as e:
        result['error'] = f"Failed to retrieve datcenter {datacenter}: {str(e)}"
        module.fail_json(msg=result['error'])

    module.exit_json(**result)

if __name__ == '__main__':
    main()