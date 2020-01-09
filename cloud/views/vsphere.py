from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo
from cloud.models import Cluster, Host, Host_VM, Cloud_Host, Cloud_VM

from audits.utils import yualert, OperaLog, CloudAudits
from system.utils import yuoem
from authen.utils import FormAuthen
from cloud.utils import HostConfig, vSphereConfig

import json

class cloud(View):
    def get(self, request, hostname):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            httphostip = request.META['HTTP_HOST'].split(':')[0]
            system = System.objects.filter(system='openeyes').first()
            oem = yuoem.yuoem()
            yuopera = yualert.yuoperalog(loginuser.id)
            alert = yuopera.alertGet()

            clu = request.GET.get('cluster')
            tab = request.GET.get('tab')
            cluster = Cluster.objects.filter(cluster=clu).first()
            if loginuser.project.project == 'admin' or cluster.project_id == loginuser.project_id:  # 身份判断
                if tab == 'vm':
                    try:
                        if cluster.project.project == 'admin':  #   如果是主设备
                            host = Host.objects.filter(host=hostname).first()
                            hostvmlist = Host_VM.objects.filter(host_id=host.id).all()
                            cloudhost = Cloud_Host.objects.filter(cloud_host_id=host.id).first()
                            cloudvmlist = ''
                            if cloudhost:   #如果cloudhost还没有则为None，下面就不能这么查找
                                cloudvmlist = Cloud_VM.objects.filter(cloud_host_id=cloudhost.id).all()

                            vsphere = vSphereConfig.vsphereget(host.ip, host.username, host.password, host.port)  # 访问不了会报错
                            vmlist = vsphere.vsphere_get_vm()  #   获取主设备账号可用的虚拟机

                            vmlist = vsphere.vsphere_get_hostvm(vmlist, hostvmlist)  # 添加主设备分派信息
                            vmlist = vsphere.vsphere_get_cloudhostvm(vmlist, cloudvmlist)  # 添加云设备分派信息

                            vsphere.vsphere_del_hostvm(vmlist, hostvmlist)  # 删除在vcenter中被删除且已被记录分派的主设备虚拟机
                            vsphere.vsphere_del_cloudvm(vmlist, cloudvmlist)  # 删除已经在vcenter删除但是已经分派的云设备虚拟机
                        elif loginuser.project.project == 'admin':  #   如果是云设备，且登录账号是admin项目管理员
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            cloudvmlist = Cloud_VM.objects.filter(cloud_host_id=cloudhost.id).all()
                            host = cloudhost.cloud_host
                            hostvmlist = Host_VM.objects.filter(host_id=host.id).all()

                            vsphere = vSphereConfig.vsphereget(host.ip, cloudhost.username, cloudhost.password, host.port)  # 访问不了会报错
                            vmlist = vsphere.vsphere_get_vm()  # 获取云设备账号可用的虚拟机

                            vmlist = vsphere.vsphere_get_hostvm(vmlist, hostvmlist)  # 添加主设备分派信息
                            vmlist = vsphere.vsphere_get_cloudhostvm(vmlist, cloudvmlist)  #   添加云设备分派信息
                        else:   # 如果是云设备。且登录是user项目的云租户的话
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            cloudvmlist = Cloud_VM.objects.filter(cloud_host_id=cloudhost.id).all()
                            host = cloudhost.cloud_host
                            hostvmlist = Host_VM.objects.filter(host_id=host.id).all()

                            vsphere = vSphereConfig.vsphereget(host.ip, cloudhost.username, cloudhost.password, host.port)  # 访问不了会报错
                            vmlist = vsphere.vsphere_get_vm()  # 获取云设备账号可用的虚拟机

                            vmlist = vsphere.vsphere_get_cloudvm(vmlist, cloudvmlist)   #   过滤出分派的虚拟机
                        return render(request, 'vsphere.html',
                                      {'loginuser': loginuser, 'host': host, 'cloudhost': cloudhost, 'cluster': cluster,
                                       'vmlist': vmlist, 'system': system, 'oem': oem, 'alert': alert})
                    except Exception as e:
                        vmlist = []
                        cloudhost = []
                        if cluster.project.project == 'admin':
                            host = Host.objects.filter(host=hostname).first()
                            yuopera.alertSet('error', '您好 {0}'.format(loginuser.username),'无法访问{0}设备'.format(host.host))
                        else:
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            host = cloudhost.cloud_host
                            yuopera.alertSet('error', '您好 {0}'.format(loginuser.username),'无法访问{0}设备'.format(cloudhost.host))
                        alert = yuopera.alertGet()
                        return render(request, 'vsphere.html',
                                      {'loginuser': loginuser, 'host': host, 'cloudhost': cloudhost, 'cluster': cluster,
                                       'vmlist': vmlist,
                                       'system': system, 'oem': oem, 'alert': alert})
                elif tab == 'manager':
                    try:
                        uuid = request.GET.get('uuid')
                        cloudinfoconfig = CloudAudits.cloudInfoConfig()
                        if cluster.project.project == 'admin':  #   如果是主设备
                            host = Host.objects.filter(host=hostname).first()
                            cloudhost = Cloud_Host.objects.filter(cloud_host_id=host.id).first()
                            vsphere = vSphereConfig.vsphereget(host.ip, host.username, host.password,host.port)  # 访问不了会报错
                            vm = vsphere.get_vm(uuid)
                        else:  # 如果不是admin项目的云计算，需要查找云计算的用户主机
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            host = cloudhost.cloud_host
                            vsphere = vSphereConfig.vsphereget(host.ip, cloudhost.username, cloudhost.password,host.port)  # 访问不了会报错
                            vm = vsphere.get_vm(uuid)
                        cloudcanvas = cloudinfoconfig.canvas_vm(uuid, '10min')
                        cloudbar = {'cpu': '0', 'memory': '0'}
                        if len(cloudcanvas['cpucanvas']) > 0:
                            cloudbar = {'cpu' : cloudcanvas['cpucanvas'][-1]['y'], 'memory' : cloudcanvas['memorycanvas'][-1]['y']}
                        return render(request, 'vm.html',
                                      {'loginuser': loginuser, 'host': host, 'cloudhost': cloudhost, 'cluster': cluster,
                                       'vm': vm, 'cloudcanvas': json.dumps(cloudcanvas), 'cloudbar': cloudbar,
                                       'system': system, 'oem': oem, 'alert': alert})
                    except Exception as e:
                        uuid = request.GET.get('uuid')
                        vm = request.GET.get('vm')
                        vm = { 'uuid': uuid, 'vm': vm }   # 防止前端报错
                        cloudinfoconfig = CloudAudits.cloudInfoConfig()
                        if cluster.project.project == 'admin':  # 如果是主设备
                            host = Host.objects.filter(host=hostname).first()
                            cloudhost = Cloud_Host.objects.filter(cloud_host_id=host.id).first()
                        else:  # 如果不是admin项目的云计算，需要查找云计算的用户主机
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            host = cloudhost.cloud_host
                        cloudcanvas = cloudinfoconfig.canvas_vm(uuid, 'day')
                        cloudbar = {'cpu': '0', 'memory': '0'}
                        yuopera.alertSet('error', '您好 {0}'.format(loginuser.username), '无法访问{0}虚拟机'.format(vm['vm']))
                        return render(request, 'vm.html',
                                      {'loginuser': loginuser, 'host': host, 'cloudhost': cloudhost, 'cluster': cluster,
                                       'vm': vm, 'cloudcanvas': json.dumps(cloudcanvas), 'cloudbar': cloudbar,
                                       'system': system, 'oem': oem, 'alert': alert})
                elif tab == 'console':
                    try:
                        uuid = request.GET.get('uuid')
                        vm = request.GET.get('vm')
                        urlport = request.GET.get('urlport', '443')
                        if cluster.project.project == 'admin':
                            host = Host.objects.filter(host=hostname).first()
                            vsphere = vSphereConfig.vsphereget(host.ip, host.username, host.password, host.port)  # 访问不了会报错
                            token_result = vsphere.web_token(uuid, httphostip, urlport, host.ip, host.port)
                        else:   # 如果不是admin项目的云计算，需要查找云计算的用户主机
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            # adminhost = Host.objects.filter(id=host.cloudhost_host_id).first()
                            host = cloudhost.cloud_host
                            vsphere = vSphereConfig.vsphereget(host.ip, cloudhost.username, cloudhost.password,host.port) # 访问不了会报错
                            token_result = vsphere.web_token(uuid, httphostip, urlport, host.ip, host.port)
                        operaconfig = OperaLog.operaLogConfig()
                        log = '打开了虚拟机{2}控制台'.format(loginuser.username, loginip, vm)
                        operaconfig.log_insert_one(loginuser.project.id, loginuser.group_id, loginuser.username,
                                                   'normal', 'config', loginip, log)
                        return render(request, 'vsphereconsole.html',
                                      {'loginuser': loginuser, 'token_result': token_result, 'host': host, 'uuid': uuid, 'vm': vm,'cluster': cluster,
                                       'system': system, 'oem': oem, 'alert':alert})
                    except Exception as e:
                        uuid = request.GET.get('uuid')
                        vm = request.GET.get('vm')
                        if cluster.project.project == 'admin':
                            host = Host.objects.filter(host=hostname).first()
                        else:
                            cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                            host = cloudhost.cloud_host
                        yuopera.alertSet('error', '您好 {0}'.format(loginuser.username), '{0}未开机或无法访问vSphereWeb服务'.format(vm))
                        alert = yuopera.alertGet()
                        return render(request, 'vsphereconsole.html',
                                      {'loginuser': loginuser, 'token_result': '', 'host': host, 'uuid': uuid, 'vm': vm,'cluster': cluster,
                                       'system': system, 'oem': oem, 'alert':alert})
                else:
                    return redirect('/authen/login/')
            else:
                return redirect('/authen/login/')
        else:
            return redirect('/authen/login/')

#   vSphereConfig配置
class vsphereconfig(View):
    def post(self, request, clu, hostname):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            cluster = Cluster.objects.filter(cluster=clu).first()
            if loginuser.project.project == 'admin' or cluster.project_id == loginuser.project_id:  # 身份判断
                if cluster.project.project == 'admin':  # 如果是主设备
                    host = Host.objects.filter(host=hostname).first()
                    vsphere = vSphereConfig.vsphereconf(host.ip, host.username, host.password, host.port)
                else:  #   如果是云设备
                    cloudhost = Cloud_Host.objects.filter(host=hostname).first()
                    host = cloudhost.cloud_host
                    vsphere = vSphereConfig.vsphereconf(host.ip, cloudhost.username, cloudhost.password, host.port)
                action = request.POST.get('action')
                uuidlist = request.POST.getlist('uuidlist[]')
                operaconfig = OperaLog.operaLogConfig()
                yuopera = yualert.yuoperalog(loginuser.id)
                if ret['status']:
                    for uuid in uuidlist:
                        if action == 'poweron':
                            vm, state = vsphere.poweron(uuid)
                            if state == 'success':
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username),'虚拟机{0}电源开启成功'.format(vm))
                                log = '开启虚拟机{0}的电源成功'.format(vm)
                            else:
                                yuopera.alertSet('danger', '您好 {0}'.format(loginuser.username), '虚拟机{0}无法在当前状况下执行此操作'.format(vm))
                                log = '开启虚拟机{0}的电源失败'.format(vm)
                        elif action == 'poweroff':
                            vm, state = vsphere.poweroff(uuid)
                            if state == 'success':
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username),'虚拟机{0}电源关闭成功'.format(vm))
                                log = '关闭虚拟机{0}的电源成功'.format(vm)
                            else:
                                yuopera.alertSet('danger', '您好 {0}'.format(loginuser.username), '虚拟机{0}无法在当前状况下执行此操作'.format(vm))
                                log = '关闭虚拟机{0}的电源失败'.format(vm)
                        elif action == 'suspend':
                            vm, state = vsphere.suspend(uuid)
                            if state == 'success':
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username),'虚拟机{0}挂起成功'.format(vm))
                                log = '挂起虚拟机{0}的电源成功'
                            else:
                                yuopera.alertSet('danger', '您好 {0}'.format(loginuser.username), '虚拟机{0}无法在当前状况下执行此操作'.format(vm))
                                log = '挂起虚拟机{0}的电源失败'.format(vm)
                        elif action == 'softreboot':
                            vm, state = vsphere.soft_reboot(uuid)
                            if state == 'success':
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username),'虚拟机{0}重置成功'.format(vm))
                                log = '重置虚拟机{0}的电源成功'.format(vm)
                            else:
                                yuopera.alertSet('danger', '您好 {0}'.format(loginuser.username), '虚拟机{0}无法在当前状况下执行此操作'.format(vm))
                                log = '重置虚拟机{0}的电源失败'.format(vm)
                        elif action == 'reboot':
                            vm, state = vsphere.reboot(uuid)
                            if state == 'success':
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username),'虚拟机{0重新启动成功'.format(vm))
                                log = '重新启动虚拟机{0}的电源成功'.format(vm)
                            else:
                                yuopera.alertSet('danger', '您好 {0}'.format(loginuser.username), '虚拟机{0}无法在当前状况下执行此操作'.format(vm))
                                log = '重新启动虚拟机{0}的电源失败'.format(vm)
                        elif action == 'allocation':
                            if cluster.project.project == 'admin':  # 如果是主设备
                                vsphereget = vSphereConfig.vsphereget(host.ip, host.username, host.password, host.port)
                                vm = vsphereget.get_vm(uuid)
                                vsphere.allocation_host_vm(host, uuid)
                            else:   #   如果是云设备
                                vsphereget = vSphereConfig.vsphereget(host.ip, cloudhost.username, cloudhost.password, host.port)
                                vm = vsphereget.get_vm(uuid)
                                vsphere.allocation_cloudhost_vm(cloudhost, uuid)
                            yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '虚拟机{0}分派成功'.format(vm['vm']))
                            log = '分派了虚拟机{0}成功'.format(vm['vm'])
                        else:
                            ret['status'] = False
                            ret['error'] = 'Error : 无法在当前状况下执行此操作'
                            log = '错误的操作了虚拟机'
                        operaconfig.log_insert_one(loginuser.project.id, loginuser.group_id, loginuser.username,
                                                   'danger', 'config', loginip, log)
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : 无法在当前状况下执行此操作'
            # ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

#   CanvasConfig配置
class canvasconfig(View):
    def post(self, request, clu):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            cluster = Cluster.objects.filter(cluster=clu).first()
            if loginuser.project.project == 'admin' or cluster.project_id == loginuser.project_id:  # 身份判断
                time = request.POST.get('time')
                uuid = request.POST.get('uuid')
                if ret['status']:
                    cloudinfoconfig = CloudAudits.cloudInfoConfig()
                    ret['data'] = cloudinfoconfig.canvas_vm(uuid, time)
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : 无法在当前状况下执行此操作'
        return HttpResponse(json.dumps(ret))
