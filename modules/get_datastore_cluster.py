#!/usr/bin/python

DOCUMENTATION = '''
--- 
module: vcenter_datastore_cluster_facts
short_description: Retrieve information about vSphere datastore clusters
description:
    - Retrieve information about vSphere datastore clusters, including their names, available space,
      and total space.
    - Use the 'datastore_cluster_name' parameter to retrieve information for a specific datastore cluster.
author:
    - Louis Tiches
requirements:
    - python >= 3.6
    - PyVmomi
options:
    vcenter:
        description:
            - The hostname or IP address of the vCenter server.
        required: true
    username:
        description:
            - The username to use to connect to the vCenter server.
        required: true
    password:
        description:
            - The password to use to connect to the vCenter server.
        required: true
    datacenter:
        description:
            - The name of the datacenter to use.
        required: true
     disable_ssl_verification:
        description:
            - Whether to disable SSL verification when connecting to the vCenter server.
        required: false
'''
EXAMPLES = '''
    - name: Retrieve information about all datastore clusters
      vcenter_datastore_facts:
        vcenter: vcenter.example.com
        username: admin
        password: password123
    - name: Retrieve information about a specific datastore cluster
      vcenter_datastore_facts:
        vcenter: vcenter.example.com
        username: admin
        password: password123
        datacenter: Production Datastore 
'''

from ansible.module_utils.basic import AnsibleModule
from vcenter_helper import VcenterFacts

def main():
    module_args = dict(
        vcenter=dict(type='str', required=True),
        username=dict(type='str', required=True, no_log=True),
        password=dict(type='str', required=True, no_log=True),
        disable_ssl_verification=dict(stype=bool, default=False),
        datacenter=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        datastore=None,
        error=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    vcenter = module.params['vcenter']
    username = module.params['username']
    password = module.params['password']
    datacenter = module.params['datacenter']
    disable_ssl_verification = module.params['disable_ssl_verification']

    try:
        vcenter_facts = VcenterFacts(vcenter, username, password, disable_ssl_verification)
        datastore_cluster = vcenter_facts.get_datastore_clusters(datacenter)
        result['datastore_cluster'] = datastore_cluster
    except Exception as e:
        result['error'] = f"Failed to retrieve datastore cluster with most available storage in datastore cluster {datastore_cluster}: {str(e)}"
        module.fail_json(msg=result['error'])

    module.exit_json(**result)

if __name__ == '__main__':
    main()