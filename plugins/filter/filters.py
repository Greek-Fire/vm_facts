#!/usr/bin/python
  
import ipaddress
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {
            'get_ip_validation': self.get_ip_validation,
            'validate_ip':       self.validate_ip,
            'match_network':     self.match_network
        }
    
    def validate_ip(self, ip_address):
        """
        This filter returns True if the provided IP address is a valid IPv4 address, otherwise False
        """
        try:
            ip = ipaddress.IPv4Address(ip_address)
            assert ip.is_private or ip.is_reserved or ip.is_global
        except ipaddress.AddressValueError:
            raise AnsibleFilterError(
                f"Invalid IP address: {ip}"
                )
        return True

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
            ip = validate_ip(ip_address)
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