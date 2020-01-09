from audits.utils import SystemLog

class Alarm(object):
    def cloud_offalarm(self, host):
        if host.state == 'online':
            log =  '{0}集群中设备{1} 已离线，请及时处理'.format(host.cluster.cluster, host.host, host.ip)

            systemlogconfig = SystemLog.systemLogConfig()
            systemlogconfig.log_insert_one(host.cluster.project_id, host.cluster.cluster, host.host, 'danger', host.ip, log)
