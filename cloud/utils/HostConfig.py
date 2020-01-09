from cloud.models import Host

class host_config(object):
    def addhost(self, host,ip,port,user,pwd,system,cluster_id):
        Host.objects.create(
            host=host,
            ip=ip,
            port=port,
            username=user,
            password=pwd,
            system=system,
            cluster_id=cluster_id,
        )
        # classhost = Host.objects.filter(ip=ip).first()
        # models.Alarm.objects.create(
        #     alarm_host_id=classhost.id,
        # )

    # def addhostlist(self, host,ipstart,ipstop,port,user,pwd,enable,system,cluster_id):
    #     iplist = findIPs(ipstart, ipstop)
    #     for ip in iplist:
    #         i = models.Host.objects.filter(ip=ip).first()
    #         if not i:
    #             host_ip = host + '-'+ ip
    #             h = models.Host.objects.filter(host=host_ip).first()
    #             if not h:
    #                 hostconfig = host_config()
    #                 hostconfig.addhost(host_ip,ip,port,user,pwd,enable,system,cluster_id)

    def edithost(self, oldid, host, ip, port, user, pwd):
        Host.objects.filter(id=oldid).update(
            host = host,
            ip = ip,
            port = port,
            username = user,
            password = pwd,
        )

    def dhost(self, id):
        Host.objects.filter(id=id).delete()

    def dhosts(self, hosts):
        for host in hosts:
            # if 'YuOS' in host.system :
            #     delconfigfile(host.host)
            #     os.system('ssh-keygen -R [{0}]:{1}'.format(host.ip, host.port))
            Host.objects.filter(id=host.id).delete()

    # def edithost_ip(self, oldid, ip):
    #     models.Host.objects.filter(id=oldid).update(
    #         ip=ip,
    #     )
    #

