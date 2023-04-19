import requests
import vcenter_helper

class VcenterFacts:
    def __init__(self, host, user, pwd, disable_ssl_verification=False):
        self.conn = VcenterConnection(host, user, pwd, disable_ssl_verification)
        self.session_id = self.conn.connect()
        self.host = host
        self.verify = not disable_ssl_verification

    def get_datacenters(self, datacenter_name=None):
        """
        Retrieve a list of datacenter objects in the vCenter.
        If datacenter_name is specified, return a tuple with the matching datacenter and its name.
        """
        url = f"https://{self.host}/rest/vcenter/datacenter"
        headers = {"vmware-api-session-id": self.session_id}
        response = requests.get(url, headers=headers, verify=self.verify)
        response.raise_for_status()

        datacenters = response.json()["value"]

        if not datacenter_name:
            return datacenters

        for dc in datacenters:
            if dc['name'] == datacenter_name:
                return dc

        raise Exception(f"No datacenter found with the name '{datacenter_name}'")
