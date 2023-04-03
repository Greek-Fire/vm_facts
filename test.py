def get_datastore_with_most_space_in_cluster(self, datastore_cluster_name, compute_cluster_name):
    """
    Find the datastore with the most available storage in the specified datastore cluster and compute cluster.
    """
    datacenters = self.get_datacenters()
    datastore_cluster = None
    compute_cluster = None

    for datacenter in datacenters:
        for cluster in datacenter.datastoreFolder.childEntity:
            if isinstance(cluster, vim.StoragePod) and cluster.name == datastore_cluster_name:
                datastore_cluster = cluster
                break
        for cluster in datacenter.hostFolder.childEntity:
            if isinstance(cluster, vim.ComputeResource) and cluster.name == compute_cluster_name:
                compute_cluster = cluster
                break
        if datastore_cluster and compute_cluster:
            break

    if not datastore_cluster:
        raise Exception(f"No datastore cluster found with the name '{datastore_cluster_name}'")
    if not compute_cluster:
        raise Exception(f"No compute cluster found with the name '{compute_cluster_name}'")

    datastores = []
    for host in compute_cluster.host:
        for datastore in host.datastore:
            if datastore in datastore_cluster.childEntity:
                datastores.append(datastore)

    if not datastores:
        raise Exception("No datastores found in the specified datastore cluster and compute cluster")

    # Find the datastore with the most free space
    max_datastore = max(datastores, key=lambda x: x.summary.freeSpace)

    return {
        'name': max_datastore.name,
        'datastore_cluster': datastore_cluster_name,
        'compute_cluster': compute_cluster_name,
        'free_space': max_datastore.summary.freeSpace,
        'total_space': max_datastore.summary.capacity
    }

def get_datastore_clusters_for_compute_cluster(self, compute_cluster_name):
    """
    Find all the datastore clusters that can be accessed by a VM in a certain compute cluster.
    """
    datacenters = self.get_datacenters()
    datastore_clusters = []

    for datacenter in datacenters:
        for cluster in datacenter.hostFolder.childEntity:
            if isinstance(cluster, vim.ClusterComputeResource) and cluster.name == compute_cluster_name:
                for datastore_cluster in cluster.datastoreCluster:
                    datastore_clusters.append({
                        'name': datastore_cluster.name,
                        'datacenter': datacenter.name,
                        'compute_cluster': compute_cluster_name,
                        'datastores': [ds.name for ds in datastore_cluster.childEntity]
                    })

    if not datastore_clusters:
        raise Exception(f"No datastore clusters found for the compute cluster '{compute_cluster_name}'")

    return datastore_clusters

def get_datastores_in_compute_cluster(self, compute_cluster_name, datacenter_name=None):
    """
    Find all datastores mapped to a compute cluster in the specified datacenter.
    If no datacenter is specified, search across all datacenters.
    """
    datacenters = self.get_datacenters()
    datastores = []

    for datacenter in datacenters:
        if datacenter_name and datacenter.name != datacenter_name:
            continue

        compute_cluster = self.get_compute_cluster(datacenter.name, compute_cluster_name)
        if not compute_cluster:
            continue

        for datastore in compute_cluster.datastore:
            datastores.append({
                'name': datastore.name,
                'free_space': datastore.summary.freeSpace,
                'total_space': datastore.summary.capacity,
                'compute_cluster': compute_cluster_name,
                'datacenter': datacenter.name
            })

    return datastores
