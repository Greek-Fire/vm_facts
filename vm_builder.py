#!/usr/bin/env python3

import argparse
import ipaddress
import sys
import getpass
import os
from ansible_runner import run
import yaml
import json

def run_playbook(playbook_path, inventory_path, **kwargs):
    # Set the runner parameters
    runner_params = {
                        'quiet': False,
                        'verbosity': args.verbosity,
                        'envvars':
                        {
                            'IDM_PASSWORD': os.getenv('IDM_PASSWORD'),
                            'AD_PASSWORD': os.getenv('AD_PASSWORD'), 
                            'VCENTER_PASSWORD': os.getenv('VCENTER_PASSWORD'),
                            'SATELLITE_PASSWORD': os.getenv('SATELLITE_PASSWORD')
                        }, 
                    }

    playbook_path = os.path.abspath(playbook_path)

    # Run the playbook
    status = run(playbook=playbook_path, inventory=inventory_path, **runner_params)

    # Print the status of the playbook run
    print(status)
    
    with open(args.log_file, 'w') as file:
        for x in status.events:
            file.write(json.dumps(x, indent=4))
def create_playbook(args, capsule):
    """
    This function creates a dictionary of data to be used by the Jinja2 template
    """
    data = {}
    data['vmname'] = args.hostname or args.vmname
    data['hostname'] = args.hostname
    data['ip'] = args.ip
    data['memory'] = args.memory
    data['cores'] = args.cores
    data['ad_principal'] = args.ad_principal
    data['idm_principal'] = args.idm_principal
    data['capsule'] = capsule

    playbook = [
    {
        "hosts": capsule,
        "gather_facts": False,
        "tasks": [
            {
                "name": "Print environment variables",
                "debug": {
                    "var": "lookup('env', item)"
                },
                "loop": [
                    "VCENTER_PASSWORD",
                    "SATELLITE_PASSWORD",
                    "AD_PASSWORD",
                    "IDM_PASSWORD"
                ]
                }
            ]
        }
    ]

    with open('runtime/playbooks/main.yaml', 'w') as f:
        yaml.dump(playbook, f, sort_keys=False)

    # Create inventory JSON file
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "children": [capsule],
        },
        capsule: {
            "hosts": [args.hostname],
            "vars": {
                "ansible_connection": "ssh",
                "ansible_user": "root",
                "ansible_become_method": "sudo"
            }
        }
    }
    with open('inv.json', 'w') as file:
        json.dump(inventory, file)

    run_playbook('runtime/playbooks/main.yaml', 'runtime/inventory/inv.json')


def get_password(password_env_var):
    """
    Returns a password either from an environment variable or prompts the user for it
    """
    password = os.getenv(password_env_var)
    if not password:
        password = getpass.getpass(prompt=f"{password_env_var} password: ")
        os.environ[password_env_var] = password
    return password

def validate_ip(ip_address):
    """
    This function returns True if the provided IP address is a valid IPv4 address and not a multicast address, otherwise False
    """
    try:
        ip = ipaddress.IPv4Address(ip_address)
        if ip.is_multicast:
            return False
    except ipaddress.AddressValueError:
        return False
    return True

def check_hostname_prefix(hostname):
    """
    This function checks the first four characters of a hostname string.
    and the fourth character is 's', 'w', or 'a', otherwise False.
    """
    if len(hostname) < 4:
        return False
        
    if not hostname[3] in ['s', 'w', 'a']:
        return False
    
    if hostname[3] == 's':
        result = 'temp'
    elif hostname[3] == 'w':
        result = ' tempw'
    elif hostname[3] == 'a':
        result = ' tempa'
    return result

def main(args):
    # Your command line tool logic here
    try:
        vmname = args.hostname or args.vmname
        hostname = args.hostname
        ip_valid = validate_ip(args.ip)
        if args.storage and args.storage > 10000:
            print("Storage size can't be greater than 10TB.")
            sys.exit(1)
        if args.memory > 64:
            print("Memory size can't be greater than 64GB.")
            sys.exit(1)
        if args.cores > 12:
            print("Number of CPU cores can't be greater than 12.")
            sys.exit(1)
        if not ip_valid:
            print(f"Invalid IP address: {args.ip}")
            sys.exit(1)
        if not check_hostname_prefix(args.hostname):
            print(f"Invalid hostname: {args.hostname}")
            sys.exit(1)

        if args.ad_principal:
            if hostname[3] == 'a':
                ad_password = get_password('AD_PASSWORD')
            else:
                print(f"Invalid hostname: {args.hostname}. Make sure to use the correct principal.")
                sys.exit(1)

        if args.idm_principal:
            if hostname[3] in ['s', 'w']:
                idm_password = get_password('IDM_PASSWORD')
            else:
                print(f"Invalid hostname: {args.hostname}. Make sure to use the correct principal.")
                sys.exit(1)
        vcenter_password = get_password('VCENTER_PASSWORD')
        satellite_password = get_password('SATELLITE_PASSWORD')
        
        print(f"Hostname: {args.hostname}")
        print(f"VM name: {vmname}")
        print(f"IP address: {args.ip}")
        create_playbook(args, 'localhost')
    except KeyboardInterrupt:
        print("\nUser interrupted the program.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Command line tool to help launch the VM build playbook. Also, you can chose to set the following environment variables: VCENTER_PASSWORD, SATELLITE_PASSWORD, AD_PASSWORD, IDM_PASSWORD. If you do, you won't be prompted for the password.")
    parser.add_argument('--ip', required=True, help="IP address for the VM: --ip 192.168.1.2")
    parser.add_argument('--hostname', required=True, help="Name of the hostname: --hostname tempw01.example.com")
    parser.add_argument('--vmname', help="Name of the VM (defaults to hostname): --vmname myvm")
    parser.add_argument('--memory', required=True, type=int, help="Memory size in GB (max 64GB): --memory 64")
    parser.add_argument('--cores', required=True, type=int, help="Number of CPU cores (max 12 cores): --cores 10")
    parser.add_argument('--storage',type=int, help="This will be used to create a vm with the datastore with the most available space (max 10000 GB): --storage 10000")
    parser.add_argument('--log-file', default='/tmp/builder-logs.json',help="Output file for the playbook run: --output-file /tmp/output.txt")
    parser.add_argument('--verbosity', type=int, default=0, help="Verbosity level of the playbook run: --verbosity 0 (default) is normal, --verbosity 1 is verbose, --verbosity 2 is more verbose, --verbosity 3 is debug, --verbosity 4 is connection debug, --verbosity 5 is winrm debug.")
    parser.add_argument('--satellite-username',required=True,help="Username for Satellite: --satellite-username admin")
    parser.add_argument('--vcenter-username',required=True,help="Username for Vcenter: --vcenter-username admin")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ad-principal', help="Use AD for authentication: --ad-principal admin")
    group.add_argument('--idm-principal',help="Use IDM for authentication: --idm-principal admin")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)