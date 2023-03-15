#!/usr/bin/python
  
import ipaddress
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {
            'get_ip_validation': self.get_ip_validation
        }

    def get_ip_validation(self, ip_address, network_address, gateway_address):
        """
        This filter returns True if the provided IP address is valid for the provided network,
        is not a broadcast address, and is not the same as the gateway address, otherwise False
        """
        ip = ipaddress.IPv4Address(ip_address)
        try:
            if '/' in network_address:
                network = ipaddress.IPv4Network(network_address)
            else:
                raise AnsibleFilterError(
                    "Network address '{}' is missing the netmask".format(network_address)
                )
        except ValueError:
            raise AnsibleFilterError(
                "Network address '{}' is not a valid IP network address".format(network_address)
            )
        gateway = ipaddress.IPv4Address(gateway_address)

        is_valid = True
        if ip == network.network_address:
            is_valid = False
        elif ip == network.broadcast_address:
            is_valid = False
        elif ip == gateway:
            is_valid = False
        elif not network.overlaps(ipaddress.IPv4Network(ip_address + '/32')):
            is_valid = False

        return is_valid