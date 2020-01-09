import re, os
# from utils.WMI_Client import WMIClient
# from utils.OSGet import linuxget, windowsget
# from utils.License import Crypto,licenseconfig
# from utils.Home_Tools import hosts_number, cluster_number

class formauthen(object):
    def __init__(self, ret):
        self.rets = ret

    def checkinput(self, string, error):
        ret = self.rets
        if ret['status']:
            sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a_])", "", string)
            if string != sub_str:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkip(self, ip, error, blank=None):
        ret = self.rets
        if ret['status']:
            ipadd = re.findall("(\d+)\.(\d+)\.(\d+)\.(\d+)", ip)
            if ipadd:
                for add in ipadd[0]:
                    if int(add) > 255 or int(add) < 0:
                        ret['status'] = False
                        ret['error'] = error
            elif blank:
                pass
            else:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkmask(self, mask, error):
        ret = self.rets
        if ret['status']:
            if int(mask) > 32 or int(mask) < 0:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果值1大于值2则报错
    def checkmaxint(self, num, max, error):
        ret = self.rets
        if ret['status']:
            if int(num) > int(max):
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkint(self, num, min, max, error):
        ret = self.rets
        if ret['status']:
            if int(num) < min or int(num) > max:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checklen(self, s, min, max, error):
        ret = self.rets
        if ret['status']:
            if len(s) < min or len(s) > max:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkmaxlen(self, s, max, error):
        ret = self.rets
        if ret['status']:
            if len(s) > max:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkminlen(self, s, min, error):
        ret = self.rets
        if ret['status']:
            if len(s) < min:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果值为空就报错
    def checkempty(self, s, error):
        ret = self.rets
        if ret['status']:
            if s == '':
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果值不存在就报错
    def checknoalive(self, c, error):
        ret = self.rets
        if ret['status']:
            if not c:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果值存在就报错
    def checkalive(self, c ,error):
        ret = self.rets
        if ret['status']:
            if c:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果值不是邮件格式
    def checkemail(self, email, error):
        ret = self.rets
        if ret['status']:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果两个值不相同就报错
    def checknosame(self, s1, s2, error):
        ret = self.rets
        if ret['status']:
            if s1 != s2:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   如果两个值相同就报错
    def checksame(self, s1, s2, error):
        ret = self.rets
        if ret['status']:
            if s1 == s2:
                ret['status'] = False
                ret['error'] = error
        return ret

    def checkvm(self, vm, vmname, error):
        ret = self.rets
        if ret['status']:
            if not vm or not vm.name == vmname:
                ret['status'] = False
                ret['error'] = error
        return ret

    #   添加集群授权认证
    # def checkClusterLicense(self, type):
    #     ret = self.rets
    #     if ret['status']:
    #         clusternumber = cluster_number()
    #         system = models.System.objects.filter(system='yuadn').first()
    #         formau = formauthen(ret)
    #         if type == 'Network':
    #             ret = formau.checknosame('已授权', system.networkstate, '网络授权未开启，请在授权页面添加授权')
    #             ret = formau.checkmaxint(clusternumber.network_number() + 1, system.networknumber, '集群数量不能超过当前类型已授权的设备数，请增加授权数量')
    #         elif type == 'Server':
    #             ret = formau.checknosame('已授权', system.serverstate, '服务器授权未开启，请在授权页面添加授权')
    #             ret = formau.checkmaxint(clusternumber.server_number() + 1, system.servernumber, '集群数量不能超过当前类型已授权的设备数，请增加授权数量')
    #         elif type == 'PC':
    #             ret = formau.checknosame('已授权', system.pcstate, 'PC授权未开启，请在授权页面添加授权')
    #             ret = formau.checkmaxint(clusternumber.pc_number() + 1, system.pcnumber, '集群数量不能超过当前类型已授权的设备数，请增加授权数量')
    #         elif type == 'Cloud':
    #             ret = formau.checknosame('已授权', system.cloudstate, '云计算授权未开启，请在授权页面添加授权')
    #             ret = formau.checkmaxint(clusternumber.cloud_number() + 1, system.cloudnumber, '集群数量不能超过当前类型已授权的设备数，请增加授权数量')
    #         elif type == 'Dumb':
    #             ret = formau.checknosame('已授权', system.dumbstate, '哑终端授权未开启，请在授权页面添加授权')
    #             ret = formau.checkmaxint(clusternumber.dumb_number() + 1, system.dumbnumber, '集群数量不能超过当前类型已授权的设备数，请增加授权数量')
    #         else:
    #             ret['status'] = False
    #             ret['error'] = '请求错误'
    #     return ret

    #   添加主机授权认证
    # def checkHostLicense(self, cluster, hostnum):
    #     ret = self.rets
    #     if ret['status']:
    #         hostsnumber = hosts_number()
    #         system = models.System.objects.filter(system='yuadn').first()
    #         formau = formauthen(ret)
    #         if cluster.type == 'Network':
    #             ret = formau.checkmaxint(hostsnumber.network_number() + hostnum, system.networknumber, '需要添加网络设备数量超过了授权的最大值，请增加授权数量')
    #         elif cluster.type == 'Server':
    #             ret = formau.checkmaxint(hostsnumber.server_number() + hostnum, system.servernumber, '需要添加服务器设备数量超过了授权的最大值，请增加授权数量')
    #         elif cluster.type == 'PC':
    #             ret = formau.checkmaxint(hostsnumber.pc_number() + hostnum, system.pcnumber, '需要添加PC设备数量超过了授权的最大值，请增加授权数量')
    #         elif cluster.type == 'Cloud':
    #             ret = formau.checkmaxint(hostsnumber.cloud_number() + hostnum, system.cloudnumber, '需要添加云计算设备数量超过了授权的最大值，请增加授权数量')
    #         elif cluster.type == 'Dumb':
    #             ret = formau.checkmaxint(hostsnumber.dumb_number() + hostnum, system.dumbnumber, '需要添加哑终端设备数量超过了授权的最大值，请增加授权数量')
    #         else:
    #             ret['status'] = False
    #             ret['error'] = '请求错误'
    #     return ret


    # def checksystemsn(self, system_sn, error):
    #     ret = self.rets
    #     if ret['status']:
    #         linux_uuid = os.popen('blkid').read()
    #         linux_get = linuxget('localhost')
    #         rootuuid, swapuuid = linux_get.linux_get_uuid(linux_uuid)
    #         yucrypto = Crypto()
    #         uuid = yucrypto.MD5_Encrypt(rootuuid)[:8] + yucrypto.MD5_Encrypt(swapuuid)[:8]
    #         licenconfig = licenseconfig()
    #         systemsn = licenconfig.getsystemsn(uuid)
    #         if system_sn != systemsn:
    #             ret['status'] = False
    #             ret['error'] = error
    #     return ret