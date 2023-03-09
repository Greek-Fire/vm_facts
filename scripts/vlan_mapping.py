from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import requests
import yaml

def get_hosts_by_domain(domain):
    """
    Retrieves a list of hosts in Foreman that match a specified domain name.

    Parameters:
    - domain (str): The domain name to search for.

    Returns:
    - A list of host dictionaries, or an empty list if no hosts are found.
    """

    lis = []
    params = {
        "search": f"name~{domain}",
        "thin": 1,
    }
    response = requests.get(
        f"{foreman_url}/api/hosts",
        params=params,
        auth=(username, password),
        verify=False  # Disable SSL certificate verification
    )
    response.raise_for_status()
    data = response.json()["results"]
    for x in data:
        lis.append(x['name'])
    return lis

def host_facts(host_id,host,params=None):
    """
    Retrieves the Ansible network facts for a specified host in Foreman.

    Parameters:
    - host_id (int): The ID of the host to retrieve facts for.
    - host (str): The hostname or FQDN of the host.
    - params (dict): Optional query parameters to pass to the API.

    Returns:
    - A list of network fact dictionaries.
    """

    if params is None:
        params = default_params

    response = requests.get(
        f"{foreman_url}/api/hosts/{host_id}/facts",
        params=params,
        auth=(username, password),
        verify=False  # Disable SSL certificate verification
    )
    response.raise_for_status()
    data = response.json()['results']
        
    return data 

def grab_facts(endpoint,params=None):
    """
    Retrieves a list of facts from Foreman.

    Parameters:
    - endpoint (str): The API endpoint to retrieve facts from.
    - params (dict): Optional query parameters to pass to the API.

    Returns:
    - A list of fact dictionaries.
    """

    if params is None:
        params = default_params
    response = requests.get(
        f"{foreman_url}{endpoint}",
        params=params,
        auth=(username, password),
        verify=False  # Disable SSL certificate verification
    )
    response.raise_for_status()
    data = response.json()['results']
    if len(data) == 0:
        return None
    else:
        return data[0]

def create_subnet(name, network, description, mask, gw, dns1, dns2):
    """
    Creates a new subnet in Foreman.

    Returns:
    - The subnet dictionary for the newly created subnet.
    """

    desc = ",".join(description)
    data = {
        "subnet": {
            "description": desc,
            "name":    name,
            "network": network,
            "mask":    mask,
            "gateway": gw,
            "dns_primary":   dns1,
            "dns_secondary": dns2,
            "dhcp":      None,
            "boot_mode": None,
            "vlanid":    None,
        }
    }

    response = requests.post(
        f"{foreman_url}{subnets_endpoint}",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'},
        auth=(username, password),
        verify=False  # Disable SSL certificate verification
    )
    response.raise_for_status()

    return response.json()['subnet']

def update_subnet(name, network, desc, mask, gw, dns1, dns2):
    """
    Updates an existing subnet in Foreman.

    Returns:
    - The subnet dictionary for the updated subnet.
    """

    data = {
        "subnet": {
            "description": desc,
            "name":    name,
            "network": network,
            "mask":    mask,
            "gateway": gw,   
            "dns_primary":   dns1, 
            "dns_secondary": dns2,
            "dhcp":      None,  
            "boot_mode": None, 
            "vlanid":    None,
        }
    }

    response = requests.put(
        f"{foreman_url}{subnets_endpoint}/{subnet_id}",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'},
        auth=(username, password),
        verify=False  # Disable SSL certificate verification
    )
    response.raise_for_status()

    return response.json()['subnet']

def connect_vcenter(vcenter, vc_username, vc_password, verify=True):
    """
    Connects to a vCenter server using the specified credentials.

    Parameters:
    - verify (bool): Whether to verify the server's SSL/TLS certificate (default True).

    Returns:
    - A ServiceInstance object representing the connection to the vCenter server, or None if the connection failed.
    """

    if verify:
        context = ssl.create_default_context()
    else:
        context = ssl._create_unverified_context()

    try:
        si = SmartConnect(
            host=vcenter,
            user=vc_username,
            pwd=vc_password,
            sslContext=context
        )
    except Exception as e:
        print(f"Could not connect to vCenter server: {e}")
        si = None

    return si

def get_vm_details(si, vm_name):
    """
    Searches for virtual machine facts

    Parameters:
    - si: A ServiceInstance object representing the connection to the vCenter server.
    - vm_name: The name of the virtual machine to retrieve details for.

    Returns:
    - Returns a dictionary containing the name, cluster, and network of the virtual machine.
    """

    vm = None
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            vm_folder = child.vmFolder
            vm = vm_folder.find(vm_name)
            if vm is not None:
                break

    if vm is None:
        return None

    host_system = vm.summary.runtime.host
    cluster_compute_resource = host_system.parent
    cluster_name = cluster_compute_resource.name
    network_name = None
    for device in vm.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            network_name = device.deviceInfo.summary
            break

    if network_name is not None:
        datacenter = vm.parent.parent.name
        return {"datacenter": datacenter, "cluster": cluster_name, "network": network_name}
    else:
        return None


def sort_dicts(dicts):
    """
    Sort the list of dictionaries by the number of key-value pair matches.

    Returns:
    - A list of sorted dictionaries.
    """
    count_dict = {}
    # Count occurrences of each dictionary
    for d1 in dicts:
        d1_tuple = tuple(sorted(d1.items()))
        for d2 in dicts:
            if d1 != d2:
                count = sum(1 for k, v in d1.items() if k in d2 and d2[k] == v)
                if d1_tuple not in count_dict:
                    count_dict[d1_tuple] = count
                else:
                    count_dict[d1_tuple] += count

    # Sort the dictionaries by count
    sorted_dicts = sorted(dicts, key=lambda d: count_dict[tuple(sorted(d.items()))], reverse=False)
    return sorted_dicts



with open("/root/.hammer/cli.modules.d/foreman.yml", "r") as s:
    config = yaml.safe_load(s)

username = config[':foreman'][':username']
password = config[':foreman'][':password']
foreman_url = 'https://sat.example.net'

with open("/home/$USER/.vcenter", "r") as v:
    config = yaml.safe_load(v)
vc_username = config['vcenter']['username']
vc_password = config['vcenter']['password']

s.close()
v.close()

# Set the API endpoints and query parameters
net_params = {
    "search": "ansible_default_ipv4",  # Set the search filter to retrieve only the ansible_default_ipv4 fact
    "per_page": 9000,  # Set the number of facts to retrieve per page
}
dns_params = {
    "search": "ansible_dns",  # Set the search filter to retrieve only the ansible_dns facts
    "per_page": 9000,  # Set the number of facts to retrieve per page
}

default_params = {
    "per_page": 9000,
}

# Create a list to store the network facts for each host
network_facts = []
temp_list = []
no_facts =  []
no_dns =  []
no_net =  []
subnets = []

# Retrieve the host ID for each host using the Satellite API
hosts = get_hosts_by_domain('example.net')

# Connect to the vCenter server
si = connect_vcenter(vcenter, vc_username, vc_password)

for host in hosts:
    # grab host_id
    host_id = grab_facts(f"/api/hosts?search=name={host}")
    if host_id is None:
        no_facts.append(host)
        continue
    host_id = host_id['id']

    # Retrieve the Ansible network facts for the host using the Satellite API
    r = host_facts(host_id,host,net_params)
    try:
        net = r[host]
    except KeyError:
        continue

    if (
        "ansible_default_ipv4::address" not in net or
        "ansible_default_ipv4::netmask" not in net or
        "ansible_default_ipv4::gateway" not in net
    ):
        print(f"Skipping host {host}: missing network facts")
        no_net.append(host)
        continue

    # Retrieve the Ansible dns facts for the host using the Satellite API
    r = host_facts(host_id,host,dns_params)
    try:
        dns = r[host]
    except KeyError:
        continue

    if "ansible_dns::nameservers" in dns:
        value = dns["ansible_dns::nameservers"]
        if isinstance(value, str):
            dns["ansible_dns::nameservers"] = eval(value)

    if (
        "ansible_dns::nameservers"      not in dns or
        len(dns["ansible_dns::nameservers"]) <= 1
    ):
        print(f"Skipping host {host}: missing dns facts")
        no_dns.append(host)
        continue
    dns.update(net)

    vm_details = get_vm_details(si, host)
    if vm_details is not None:
        
        # Add the network facts to the network_facts list
        network_facts.append({
            "network":   dns["ansible_default_ipv4::network"],
            "subnet": dns["ansible_default_ipv4::netmask"],
            "gw":     dns["ansible_default_ipv4::gateway"],
            "dns1":   dns["ansible_dns::nameservers"][0],
            "dns2":   dns["ansible_dns::nameservers"][1],
            "vlan":       vm_details['network'],
            "cluster":    vm_details['cluster'],
            "datacenter": vm_details['datacenter'],
            "vcenter": vcenter
            })

Disconnect(si)
res = sort_dicts(subnets)
for subnet in res:
    name = subnet['network']
    network = subnet['network']
    mask = subnet['subnet']
    gw =   subnet['gw']
    dns1 = subnet['dns1']
    dns2 = subnet['dns2']
    vlan = subnet['vlan']
    dc = subnet['datacenter']
    vc = vcenter
    cluster = subnet['cluster']
    description = f"{vc},{dc},{cluster},{vlan}"
    subnet_check = grab_facts(f"/api/subnets?search=network={subnet['name']}")
    if subnet_checks is not None:
        subnet_id = subnet_check['id']
        update_subnet(name,network,description,mask,gw,dns1,dns2)
    else:
        create_subnet(name,network,description,mask,gw,dns1,dns2)
