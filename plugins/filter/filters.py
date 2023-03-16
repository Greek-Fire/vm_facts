#!/usr/bin/python
  
import ipaddress
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {
            'network_validation': self.network_validation,
            'validate_ip':       self.validate_ip,
            'get_subnet_info':   self.get_subnet_info,
            'match_network':     self.match_network
        }
    
    def get_subnet_info(self, subnet_data):
        """
        This filter returns a list of strings in the format "<subnet_name>/<cidr>" for each subnet in the provided data.
        """
        subnet_info = []
        for subnet in subnet_data:
            subnet_name = subnet['name']
            cidr = str(subnet['cidr'])
            subnet_str = subnet_name + '/' + cidr
            subnet_info.append(subnet_str)
        return subnet_info
    
    def validate_ip(self, ip_address):
        """
        This filter returns True if the provided IP address is a valid IPv4 address and not a broadcast address, otherwise False
        """
        try:
            ip = ipaddress.IPv4Address(ip_address)
            if (ip.is_private or
                ip.is_reserved or
                ip.is_global
                ):
                if ip.is_multicast:
                    return False
                return ip
            else:
                return False
        except ipaddress.AddressValueError:
            return False

    def network_validation(self, ip_address, network_address, gateway_address):
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
            gw = self.validate_ip(gateway_address)
            ip = self.validate_ip(ip_address)
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
        """
        This filter returns the network address if the provided IP address is in the given network list,
        otherwise False
        """
        try:
            ip = ipaddress.IPv4Address(ip_address)
        except ipaddress.AddressValueError:
            raise AnsibleFilterError(f"Invalid IP address: {ip_address}")

        for network_address in network_list:
            network_parts = network_address.split('/')
            if len(network_parts) != 2:
                raise AnsibleFilterError(f"Network address {network_address} is missing the netmask")

            network_ip = network_parts[0]
            try:
                network = ipaddress.IPv4Network(network_address)
            except ipaddress.AddressValueError:
                print(f"Invalid network address: {network_address}")
                continue

            if ip in network:
                return str(network)

        return False