#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_template
version_added: 1.0.0
short_description: Get a template in vCenter by name.
description:
  - This module uses the vCenter API to retrieve a template by name.
  - Returns the full path of the template.
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
  template_name:
    description: The name of the template to retrieve.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Get vCenter template path
  get_template:
    vcenter: vcenter.example.com
    username: admin
    password: password
    template_name: my_template
  register: vcenter_template

- name: Debug vCenter template path
  debug:
    var: vcenter_template.ansible_facts.vcenter_template
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts


def main():
    module_args = dict(
        vcenter=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(type='bool', default=False),
        template_name=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        vcenter_template={},
        error="",
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    # Retrieve vCenter template path
    vcenter_facts = VcenterFacts(
        module.params['vcenter'],
        module.params['username'],
        module.params['password'],
        module.params['disable_ssl_verification'],
    )
    template_path = vcenter_facts.get_template_path(
        module.params['template_name']
    )
    result['vcenter_template'] = template_path
    module.exit_json(**result)


if __name__ == '__main__':
    main()
