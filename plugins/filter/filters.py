#!/usr/bin/python
  
import ipaddress
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {
            'get_ip_validation': self.get_ip_validation,
            'match_network': self.match_network
        }

    def get_ip_validation(self, ip_address, network_address, gateway_address):
        """
        This filter returns True if the provided IP address is valid for the provided network,
        is not a broadcast address, and is not the same as the gateway address, otherwise False
        """
        try:
            if '/' in network_address:
                network = ipaddress.IPv4Network(network_address)
            else:
                raise AnsibleFilterError(
                    f"Network address {network_address} is missing the netmask"
                )
            gw = ipaddress.IPv4Address(gateway_address)
            ip = ipaddress.IPv4Address(ip_address)
        except ipaddress.AddressValueError:
            raise AnsibleFilterError(
                f"Invalid IP address: {ip_address} or {gw}"
            )

        is_valid = True
        if ip == network.network_address:
            is_valid = False
        elif ip == network.broadcast_address:
            is_valid = False
        elif ip == gw:
            is_valid = False
        elif not network.overlaps(ipaddress.IPv4Network(ip_address + '/32')):
            is_valid = False

        return is_valid
    
    def match_network(self, ip_address, network_list):
        '''
        # Convert the input IP address to an IPv4Address object
        '''
        try:
            ip = ipaddress.IPv4Address(ip_address)

        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IP address: {ip}")
        
        for network_address in network_list:
            if '/' in network_address:
                network = ipaddress.IPv4Network(network_address)
            else:
                raise AnsibleFilterError(
                    f"Network address {network_address} is missing the netmask"
                )
            network = ipaddress.IPv4Network(network_address)
            if ip in network:
                return str(network)
        return False