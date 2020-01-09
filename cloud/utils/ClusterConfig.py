from cloud.models import Cluster

class cluster_config(object):
    def addcluster(self, cluster,hostnum,project_id):
        Cluster.objects.create(
            cluster=cluster,
            host_number=hostnum,
            project_id=project_id,
        )

    def editcluster(self, id,cluster,project_id,hostnum):
        Cluster.objects.filter(id=id).update(
            cluster=cluster,
            project_id=project_id,
            host_number=hostnum,
        )

    def dcluster(self, id):
        Cluster.objects.filter(id=id).delete()
        
class cluster_onhost(object):
    def onhost(self, cluster_list, host_list, cloudhost_list):
        for cluster in cluster_list:
            c_host = 0
            on_host = 0
            if cluster.project.project == 'admin':  # 如果是主设备
                for host in host_list:
                    if cluster.id == host.cluster_id:  # 设备属于这个集群
                        c_host = c_host + 1
                        if host.state == 'online':  # 再查看设备是否在线
                            on_host = on_host + 1
            else:  # 如果是虚拟云主机，即不是admin项目的Cloud集群
                for cloudhost in cloudhost_list:
                    if cluster.id == cloudhost.cluster_id:  # 云设备属于这个集群
                        c_host = c_host + 1
                        if cloudhost.cloud_host.state == 'online':  # 再查看云设备的主机是否在线
                            on_host = on_host + 1
            if c_host == 0:
                onhost = '0%'
            else:
                onhost = '{:.0%}'.format(on_host / c_host)
            cluster.onhost = onhost
        return  cluster_list