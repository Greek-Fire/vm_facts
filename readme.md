# VM Builder

This script is a command-line tool to help launch a VM build playbook. The tool accepts various arguments, such as IP address, hostname, VM name, memory size, CPU cores, storage size, and log file, among others. It also supports two authentication methods: Active Directory (AD) and Identity Management (IDM).

# Functionality
The tool checks for the following conditions:

Validates the IP address provided.
Validates the hostname prefix. It checks the first four characters of the hostname string. The fourth character should be 's', 'w', or 'a', otherwise it is considered invalid.
Validates the memory size. It should not be greater than 64GB.
Validates the number of CPU cores. It should not be greater than 12.
Validates the storage size. It should not be greater than 10000 GB.

If all the conditions are met, the tool creates a playbook, creates an inventory ini file, and runs the playbook using Ansible Runner.
The tool also prompts the user for the password for each environment variable that is not set.
The output of the playbook run is saved in a JSON file. The default location for the file is /tmp/builder-logs.json.

## Prerequisites

- Ansible
- ansible-runner

## Installation

1. Install the required ansible-runner library
- yum update
- yum install ansible-runner

2. Clone this repository and navigate to the directory containing the script.

git clone <repo>

Set the following environment variables (optional) to avoid being prompted for passwords:

- `VCENTER_PASSWORD`
- `SATELLITE_PASSWORD`
- `AD_PASSWORD`
- `IDM_PASSWORD`

# Usage
Run the script with the desired options. For example:

cd automated_builder/scripts

bash wrapper.bash
--ip 192.168.1.2 \
--hostname tempw01.example.com \
  --vmname myvm \
  --memory 64 \
  --cores 10 \
  --storage 10000 \
  --log-file /tmp/builder-logs.json \
  --verbosity 1 \
  --satellite-username admin \
  --vcenter-username admin \
  --ad-principal admin