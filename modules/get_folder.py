#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_folder
version_added: 1.0.0
short_description: Get a folder in vCenter by name and return its path.
description:
  - This module uses the vCenter API to retrieve a folder by name and return its full path.
  - You can optionally provide the name of the folder's parent folder to help narrow the search.
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
  folder_name:
    description: The name of the folder to retrieve.
    required: true
    type: str
  parent_folder_name:
    description: The name of the parent folder to search under. If not provided, search from the root folder.
    required: false
    type: str
'''

EXAMPLES = '''
- name: Get vCenter folder path
  get_folder:
    host: vcenter.example.com
    username: admin
    password: password
    folder_name: my_folder
    parent_folder_name: my_parent_folder
  register: vcenter_folder

- name: Debug vCenter folder path
  debug:
    var: vcenter_folder.ansible_facts.vcenter_folder
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts


def main():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(type='bool', default=False),
        folder_name=dict(type='str', required=True),
        parent_folder_name=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        vcenter_folder={},
        error="",
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    # Retrieve vCenter folder path
    vcenter_facts = VcenterFacts(
        module.params['host'],
        module.params['username'],
        module.params['password'],
        module.params['disable_ssl_verification'],
    )
    folder_path = vcenter_facts.get_folder_path(
        module.params['folder_name']
    )
    result['vcenter_folder'] = folder_path
    module.exit_json(**result)


if __name__ == '__main__':
    main()
