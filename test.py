def get_datastore_with_most_space_in_cluster(self, datastore_cluster_name):
    """
    Find the datastore with the most available storage in the specified datastore cluster.
    If a datacenter is specified, only consider datastores in that datacenter.
    """
    datacenters = self.get_datacenters()
    datastore_cluster = None

    for datacenter in datacenters:
        for cluster in datacenter.hostFolder.childEntity:
            if isinstance(cluster, vim.ClusterComputeResource) and cluster.name == datastore_cluster_name:
                datastore_cluster = cluster
                break
        if datastore_cluster:
            break

    if not datastore_cluster:
        raise Exception(f"No cluster found with the name '{datastore_cluster_name}'")

    datastores = datastore_cluster.datastore

    if not datastores:
        raise Exception("No datastores found in the specified cluster")

    # Find the datastore with the most free space
    max_datastore = max(datastores, key=lambda x: x.summary.freeSpace)

    return {
        'name': max_datastore.name,
        'datastore_cluster': datastore_cluster_name,
        'free_space': max_datastore.summary.freeSpace,
        'total_space': max_datastore.summary.capacity
    }
