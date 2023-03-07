# vcenter_helper.py

import atexit
from pyVim import connect
from pyVmomi import vim


class VcenterConnection:
    def __init__(self, host, user, pwd, disable_ssl_verification=False):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.disable_ssl_verification = disable_ssl_verification
        self.si = None

    def connect(self):
        """
        connect to vCenter
        """
        try:
            # Connect to vCenter using SSL or not based on the disable_ssl_verification variable
            if self.disable_ssl_verification:
                service_instance = connect.SmartConnectNoSSL(host=self.host, user=self.user, pwd=self.pwd)
            else:
                service_instance = connect.SmartConnect(host=self.host, user=self.user, pwd=self.pwd)

            atexit.register(connect.Disconnect, service_instance)
            self.si = service_instance
            return service_instance
        except Exception as e:
            raise Exception(f"Unable to connect to vCenter: {e}")

    def disconnect(self):
        """
        disconnect from vCenter
        """
        try:
            connect.Disconnect(self.si)
        except Exception as e:
            raise Exception(f"Unable to disconnect from vCenter: {e}")


class VcenterFacts:
    def __init__(self, host, user, pwd, disable_ssl_verification=False):
        self.conn = VcenterConnection(host, user, pwd, disable_ssl_verification)
        self.si = self.conn.connect()

    def get_datacenters(self):
        """
        Retrieve a list of datacenter names in the vCenter.
        """
        content = self.si.content
        datacenters = []
        for dc in content.rootFolder.childEntity[0].childEntity:
            datacenters.append(dc.name)
        return datacenters

    def get_clusters(self, datacenters=None):
        """
        Retrieve a list of dictionaries, mapping cluster names to datacenter names.
        If datacenters are not specified, retrieves all datacenters.
        """
        if not datacenters:
            datacenters = self.get_datacenters()

        content = self.si.content
        clusters = []
        for datacenter in datacenters:
            dc = content.rootFolder.childEntity[0].findChild(datacenter)
            if not dc:
                continue
            for cluster in dc.hostFolder.childEntity[0].childEntity:
                clusters.append({
                    'name': cluster.name,
                    'datacenter': datacenter,
                })
        return clusters

    def get_networks(self, datacenters=None, clusters=None):
        """
        Retrieve a list of dictionaries, mapping network names to datacenter and cluster names.
        If datacenters or clusters are not specified, retrieves all datacenters or clusters.
        """
        if not datacenters:
            datacenters = self.get_datacenters()
        if not clusters:
            clusters = []
            for datacenter in datacenters:
                clusters += [cluster['name'] for cluster in self.get_clusters([datacenter])]

        networks = []
        for datacenter in datacenters:
            dc = self.si.content.rootFolder.childEntity[0].findChild(datacenter)
            if not dc:
                continue
            for cluster in clusters:
                cl = dc.hostFolder.childEntity[0].findChild(cluster)
                if not cl:
                    continue
                for network in cl.network:
                    datacenter_names = [dc.name for dc in network.summary.datacenter]
                    cluster_names = [host.parent.name for host in network.summary.host]
                    if len(datacenter_names) > 1 and len(cluster_names) > 1:
                        networks.append({
                            'name': network.name,
                            'datacenter': datacenter,
                            'cluster': cluster,
                        })
        return
