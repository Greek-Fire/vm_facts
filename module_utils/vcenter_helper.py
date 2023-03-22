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
        Connect to vCenter.
        """
        try:
            if self.disable_ssl_verification:
                service_instance = connect.SmartConnectNoSSL(host=self.host, user=self.user, pwd=self.pwd)
            else:
                service_instance = connect.SmartConnect(host=self.host, user=self.user, pwd=self.pwd)

            atexit.register(connect.Disconnect, service_instance)
            self.si = service_instance
            return service_instance
        except Exception as e:
            raise ConnectionError(f"Unable to connect to vCenter: {e}")

    def disconnect(self):
        """
        Disconnect from vCenter.
        """
        try:
            connect.Disconnect(self.si)
        except Exception as e:
            raise ConnectionError(f"Unable to disconnect from vCenter: {e}")

class VcenterFacts:
    def __init__(self, host, user, pwd, disable_ssl_verification=False):
        self.conn = VcenterConnection(host, user, pwd, disable_ssl_verification)
        self.si = self.conn.connect()

    def get_root(self):
        """
        Retrieve the root folder object.
        """
        content = self.si.content

        return content.rootFolder

    def get_datacenters(self, datacenter_name=None):
        """
        Retrieve a list of datacenter objects in the vCenter.
        If datacenter_name is specified, return a tuple with the matching datacenter and its name.
        """
        content = self.si.content

        if not datacenter_name:
            datacenters = {dc for dc in content.rootFolder.childEntity if isinstance(dc, vim.Datacenter)}
            return datacenters

        datacenters = {dc for dc in content.rootFolder.childEntity if isinstance(dc, vim.Datacenter)}        
        for dc in datacenters:
            if dc.name == datacenter_name:
                return dc

        raise Exception(f"No datacenter found with the name '{datacenter_name}'")
    
    def get_clusters_object(self, datacenter_name, cluster_name):
        """
        Retrieve a list of cluster objects in the vCenter.
        """
        datacenter = self.get_datacenters(datacenter_name)
        for cluster in datacenter.hostFolder.childEntity:
            if isinstance(cluster, vim.ClusterComputeResource) and cluster.name == cluster_name:
                return cluster
        raise Exception(f"No cluster found with the name '{cluster_name}'")


    def get_clusters(self, datacenter_name):
        """
        Retrieve a list of dictionaries, mapping cluster names to datacenter names.
        If datacenters are not specified, retrieves all datacenters.
        """
        clusters = []
        datacenter = self.get_datacenters(datacenter_name)
        for cluster in datacenter.hostFolder.childEntity:
            if isinstance(cluster, vim.ClusterComputeResource):
                total_memory = cluster.summary.totalMemory
                total_cores = cluster.summary.numCpuCores
                clusters.append({
                    'name': cluster.name,
                    'datacenter': datacenter.name,
                    'total_memory': total_memory,
                    'total_cores': total_cores,
                    })

        return clusters

    def get_datastore_clusters(self, datacenter_name):
        """
        Retrieve a list of dictionaries representing all available datastore clusters,
        each with its name, free space, and total space.
        If datacenters are not specified, retrieves all datacenters.
        """
        datacenter = self.get_datacenters(datacenter_name)
        datastore_clusters = []
        for cluster in datacenter.datastoreFolder.childEntity:
            if isinstance(cluster, vim.StoragePod):
                free_space = cluster.summary.freeSpace
                total_space = cluster.summary.capacity
                datastore_clusters.append({
                    'name': cluster.name,
                    'datacenter': datacenter.name,
                    'free_space': free_space,
                    'total_space': total_space,
                })

        return datastore_clusters
    
    def get_datastore_with_most_space_in_cluster(self, datastore_cluster_name):
        """
        Find the datastore with the most available storage in the specified datastore cluster.
        If a datacenter is specified, only consider datastores in that datacenter.
        """
        datacenters = self.get_datacenters()
        datastore_cluster = None

        for datacenter in datacenters:
            for cluster in datacenter.datastoreFolder.childEntity:
                if isinstance(cluster, vim.StoragePod) and cluster.name == datastore_cluster_name:
                    datastore_cluster = cluster
                    break
            if datastore_cluster:
                break

        if not datastore_cluster:
            raise Exception(f"No datastore cluster found with the name '{datastore_cluster_name}'")

        datastores = datastore_cluster.childEntity

        if not datastores:
            raise Exception("No datastores found in the specified datastore cluster")

        # Find the datastore with the most free space
        max_datastore = max(datastores, key=lambda x: x.summary.freeSpace)

        return {
            'name': max_datastore.name,
            'datastore_cluster': datastore_cluster_name,
            'free_space': max_datastore.summary.freeSpace,
            'total_space': max_datastore.summary.capacity
        }


    def get_networks(self, datacenter_name, clusters=None):
        """
        Retrieve a list of dictionaries, mapping network names to datacenter and cluster names.
        If datacenters or clusters are not specified, retrieves all datacenters or clusters.
        """
        datacenter = self.get_datacenters(datacenter_name)

        networks = []
        dc_clusters = [self.get_clusters_object(datacenter_name, clusters)]
        for cluster in dc_clusters:
            if not isinstance(cluster, vim.ClusterComputeResource):
                continue
            if not cluster.network:
                continue
            for network in cluster.network:
                networks.append({
                    'name': network.name,
                    'datacenter': datacenter_name,
                    'cluster': cluster.name,
                })

        return networks
    
    def get_template(self, cluster_name):
        """
        Retrieve all VM templates in the given cluster.
        """
        cluster_obj = self._find_cluster(cluster_name)
        if not cluster_obj:
            raise Exception(f"No cluster found with the name '{cluster_name}'")

        # Loop through VMs in the cluster and add templates to the list
        template_objs = []
        for vm in cluster_obj.vm:
            if isinstance(vm, vim.VirtualMachine) and vm.config.template:
                template_objs.append(vm)

        return template_objs
    
    def get_folders(self):
        """
        Find all folders in the vCenter inventory.
        Return a list of dictionaries containing the folder name and its path.
        """
        root_folder = self.get_root()
        if not isinstance(root_folder, vim.Folder):
            return None

        folder_objs = []
        for dc in root_folder.childEntity:
            if isinstance(dc, vim.Datacenter):
                folder_objs.extend(self._get_dc_folders(dc))

        return [{'name': f['folder'].name, 'path': f['path']} for f in folder_objs]


    def _get_dc_folders(self, datacenter, path=""):
        """
        Helper method to recursively find all folders under a given datacenter object.
        Returns a list of dictionaries containing the folder object and its path.
        """
        folder_objs = []
        folder_objs.append({'folder': datacenter.vmFolder, 'path': f"{datacenter.name}/vm"})
        for item in datacenter.vmFolder.childEntity:
            if isinstance(item, vim.Folder):
                subpath = f"{path}/{item.name}" if path else item.name
                folder_objs.append({'folder': item, 'path': f"{datacenter.name}/{subpath}"})
                folder_objs.extend(self._get_subfolders(item, f"{datacenter.name}/{subpath}"))

        return folder_objs


    def _get_subfolders(self, parent_folder, path=""):
        """
        Helper method to recursively find all subfolders of a given parent folder.
        Returns a list of dictionaries containing the folder object and its path.
        """
        folder_objs = []
        for item in parent_folder.childEntity:
            if isinstance(item, vim.Folder):
                subpath = f"{path}/{item.name}" if path else item.name
                folder_objs.append({'folder': item, 'path': subpath})
                folder_objs.extend(self._get_subfolders(item, subpath))

        return folder_objs


