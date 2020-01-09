from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo
from cloud.models import Cluster, Host, Cloud_Host

from audits.utils import yualert
from system.utils import yuoem
from authen.utils import FormAuthen
from cloud.utils import HostConfig

import json

class host(View):
    def get(self, request, cluster):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            httphostip = request.META['HTTP_HOST'].split(':')[0]
            system = System.objects.filter(system='openeyes').first()
            oem = yuoem.yuoem()
            yuopera = yualert.yuoperalog(loginuser.id)
            alert = yuopera.alertGet()

            clust = Cluster.objects.filter(cluster=cluster).first()
            if loginuser.project.project == 'admin'or clust.project_id == loginuser.project_id:   #   身份判断
                cloudadmin_host = []    #   提前定义防止None
                clouduser_cluster = []   #  提前定义防止None
                if clust.project.project == 'admin': #   进入admin项目的集群，显示本集群所有的主设备
                    host_list = Host.objects.filter(cluster=clust.id).all()
                else:
                    cloudadmin_host = Host.objects.filter(cluster__project__project='admin').all()
                    clouduser_cluster = Cluster.objects.filter(project__project='user').all()
                    host_list = Cloud_Host.objects.filter(cluster_id=clust.id).all()
                return render(request, 'host.html',
                              {'loginuser': loginuser, 'clust': clust, 'host_list': host_list,
                               'cloudadmin_host': cloudadmin_host, 'clouduser_cluster': clouduser_cluster,
                               'httphostip': httphostip, 'oem': oem, 'system': system, 'alert':alert,
                               })
                # return render(request, html,
                #               {'loginuser': loginuser, 'clust': clust, 'host_list': host_list,
                #                'host_number': host_number,
                #                'cloudadmin_host': cloudadmin_host, 'clouduser_cluster': clouduser_cluster,
                #                'httphostip': httphostip,
                #                'oem': oem, 'system': system, 'alert': alert,
                #                })
        else:
            return redirect('/authen/login/')


class hostadd(View):
    def post(self, request, id):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            host = request.POST.get('host')
            ip = request.POST.get('ip')
            # ipstart = request.POST.get('ipstart')
            # ipstop = request.POST.get('ipstop')
            system = request.POST.get('system')
            port = request.POST.get('port')
            user = request.POST.get('user')
            pwd = request.POST.get('pwd')
            c = Cluster.objects.filter(id=id).first()
            if loginuser.project.project == 'admin'or c.project_id == loginuser.project_id:  # 身份判断
                h = Host.objects.filter(host=host).first()
                i = Host.objects.filter(ip=ip).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checknoalive(c, '集群不存在')
                ret = formau.checkint(port, 1, 65535, '端口号必须在1~65535之间')
                ret = formau.checkminlen(host, 2, '设备名至少2个字符')
                ret = formau.checkmaxlen(host, 32, '设备名最多32个字符')
                ret = formau.checkinput(host, '设备名只能为汉字、数字、字母或下划线')
                ret = formau.checkempty(user, '账号不能为空')
                ret = formau.checkmaxlen(user, 32, '账号最多32个字符')
                ret = formau.checkempty(pwd, '密码不能为空')
                ret = formau.checkmaxlen(pwd, 32, '密码最多32个字符')
                if loginuser.project.project != 'admin':   #   防止不是admin的租户使用id给别人租户集群添加的设备
                    ret = formau.checknosame(c.project_id, loginuser.project_id, '集群不属于此账号')
                #   单台添加和批量添加的认证
                # if ipstart and ipstop:
                #     ret = formau.checkip(ipstart, '开始IP格式错误')
                #     ret = formau.checkip(ipstop, '结束IP格式错误')
                #     hostnum = len(findIPs(ipstart, ipstop))    #   为license添加做基础
                # else:
                ret = formau.checkalive(h, '设备名已存在')
                ret = formau.checkip(ip, 'IP格式错误')
                ret = formau.checkalive(i, 'IP地址已存在')
                hostnum = 1     #   为license添加做基础
                #   设备最大数量认证
                ret = formau.checkmaxint(Host.objects.filter(cluster_id=c.id).count()+ hostnum, c.host_number,'已达到最大设备数量')
                #   license数量认证
                # ret = formau.checkHostLicense(c, hostnum)
                if ret['status']:
                    hostconfig = HostConfig.host_config()
                    # if ipstart and ipstop:
                    #     hostconfig.addhostlist(host, ipstart, ipstop, port, user, pwd, en, system, id)
                    # else:
                    hostconfig.addhost(host, ip, port, user, pwd, system, id)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '设备{0}创建成功'.format(host))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class hostedit(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']

            oid = request.POST.get('id')
            host = request.POST.get('host')
            ip = request.POST.get('ip')
            system = request.POST.get('system')
            port = request.POST.get('port')
            user = request.POST.get('user')
            pwd = request.POST.get('pwd')
            if loginuser.project.project == 'admin':  # 只有admin项目账号的admin权限可以编辑删除主设备、云设备
                o = Host.objects.filter(id=oid).first()
                h = Host.objects.filter(host=host).first()
                i = Host.objects.filter(ip=ip).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checknoalive(o, '源设备不存在')
                ret = formau.checkint(port, 1, 65535, '端口号必须在1~65535之间')
                ret = formau.checkminlen(host, 2, '设备名至少2个字符')
                ret = formau.checkmaxlen(host, 32, '设备名最多32个字符')
                ret = formau.checkinput(host, '设备名只能为汉字、数字、字母或下划线')
                ret = formau.checkip(ip, 'IP格式错误')
                if o.host != host:  #   如果需要改设备名，验证新设备名是否已存在
                    ret = formau.checkalive(h, '设备名已存在,不区分大小写')
                if o.ip != ip:  #   如果需要改IP地址，验证新IP地址是否已存在
                    ret = formau.checkalive(i, 'IP地址已存在')
                if user and pwd:     #   如果需要改账号密码，验证下
                    ret = formau.checkempty(user, '账号不能为空')
                    ret = formau.checkmaxlen(user, 32, '账号最多32个字符')
                    ret = formau.checkempty(pwd, '密码不能为空')
                    ret = formau.checkmaxlen(pwd, 32, '密码最多32个字符')
                if loginuser.project.project != 'admin':   #   防止不是admin的租户使用id修改别人租户的设备
                    ret = formau.checknosame(o.cluster.project_id, loginuser.project_id, '设备不属于此账号')
                if ret['status']:
                    hostconfig = HostConfig.host_config()  #   由于只有账号密码，需要获取之前的值，所以判断这两即可
                    if user and pwd:  # 如果需要改账号密码
                        hostconfig.edithost(o.id, host, ip, port, user, pwd)
                    else:   #   如果账号密码都不需要修改
                        hostconfig.edithost(o.id, host, ip, port, o.username, o.password)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '设备{0}编辑成功'.format(host))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class hostdel(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':    #   只有admin项目账号的admin权限可以编辑删除主设备、云设备
                idlist = request.POST.getlist('idlist[]')
                formau = FormAuthen.formauthen(ret)
                ret = formau.checksame(idlist, [], '请选择需要删除的主机')
                if ret['status']:
                    hostlist = []
                    hostconfig = HostConfig.host_config()
                    for id in idlist:
                        host = Host.objects.filter(id=id).first()
                        ret = formau.checknoalive(host, '设备不存在')
                        if ret['status']:   #   下面注释的，因为只有admin项目可以编辑所有觉得不需要这么麻烦
                            hostconfig.dhost(id)
                            hostlist.append(host.host)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '设备{0}删除成功'.format('、'.join(hostlist)))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))