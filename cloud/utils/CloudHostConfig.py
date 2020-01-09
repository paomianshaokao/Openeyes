from cloud.models import Cloud_Host

class cloudhost_config(object):
    def addcloudhost(self, cloudhost, hostid, username, password, clusterid):
        Cloud_Host.objects.create(
            host=cloudhost,
            cloud_host_id=hostid,
            username=username,
            password=password,
            cluster_id=clusterid,
        )


    def editcloudhost(self, oid, cloudhost, hostid, username, password):
        Cloud_Host.objects.filter(id=oid).update(
            host=cloudhost,
            cloud_host_id=hostid,
            username=username,
            password=password,
        )

    def dcloudhost(self, host):
        Cloud_Host.objects.filter(id=host.id).delete()