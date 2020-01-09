from cloud.models import Cluster, Host, Cloud_Host

class cloud_info(object):
    def cluster_number(self):
        cloud_cluster_number = Cluster.objects.count()
        return cloud_cluster_number

    def host_number(self):
        host_number = Host.objects.count()
        cloudhost_number = Cloud_Host.objects.count()
        return host_number + cloudhost_number

    def onhost_number(self):
        onhost_number = Host.objects.filter(state='online').count()
        oncloudhost_number = Cloud_Host.objects.filter(cloud_host__state='online').count()
        return onhost_number + oncloudhost_number

    def project_host_number(self, project):
        host_number = Host.objects.filter(cluster__project_id=project).count()
        cloudhost_number = Cloud_Host.objects.filter(cluster__project_id=project).count()
        return host_number + cloudhost_number

    def project_onhost_number(self, project):
        onhost_number = Host.objects.filter(cluster__project_id=project).filter(state='online').count()
        oncloudhost_number = Cloud_Host.objects.filter(cluster__project_id=project).filter(cloud_host__state='online').count()
        return onhost_number + oncloudhost_number