from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo
from cloud.models import Cluster, Host, Cloud_Host

from audits.utils import yualert
from authen.utils import FormAuthen
from cloud.utils import CloudHostConfig

import json

class cloudhostadd(View):
    def post(self, request, id):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                host = request.POST.get('host')
                adminhost = request.POST.get('adminhost')
                user = request.POST.get('user')
                pwd = request.POST.get('pwd')
                cloudh = Cloud_Host.objects.filter(host=host).first()
                h = Host.objects.filter(host=adminhost).first()
                c = Cluster.objects.filter(id=id).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checkminlen(host, 2, '设备名至少2个字符')
                ret = formau.checkmaxlen(host, 32, '设备名最多32个字符')
                ret = formau.checkinput(host, '设备名只能为汉字、数字、字母或下划线')
                ret = formau.checkalive(cloudh, '设备名已存在')
                ret = formau.checkempty(user, '账号不能为空')
                ret = formau.checkmaxlen(user, 32, '账号最多32个字符')
                ret = formau.checkempty(pwd, '密码不能为空')
                ret = formau.checkmaxlen(pwd, 32, '密码最多32个字符')
                ret = formau.checknoalive(h, '主设备不存在')
                ret = formau.checknoalive(c, '集群不存在')
                hostnum = 1
                # 设备最大数量认证
                ret = formau.checkmaxint(Host.objects.filter(cluster_id=c.id).count() + hostnum, c.host_number, '已达到最大设备数量')
                #   license数量认证
                # ret = formau.checkHostLicense(c, hostnum)
                if ret['status']:
                    cloudhostconfig = CloudHostConfig.cloudhost_config()
                    cloudhostconfig.addcloudhost(host, h.id, user, pwd, c.id)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '云设备{0}创建成功'.format(host))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class cloudhostedit(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                id = request.POST.get('id')
                host = request.POST.get('host')
                adminhost = request.POST.get('adminhost')
                user = request.POST.get('user')
                pwd = request.POST.get('pwd')
                oh = Cloud_Host.objects.filter(id=id).first()
                cloudh = Cloud_Host.objects.filter(host=host).first()
                h = Host.objects.filter(host=adminhost).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checknoalive(oh, '原设备不存在')
                ret = formau.checkminlen(host, 2, '设备名至少2个字符')
                ret = formau.checkmaxlen(host, 32, '设备名最多32个字符')
                ret = formau.checkinput(host, '设备名只能为汉字、数字、字母或下划线')
                ret = formau.checknoalive(h, '主设备不存在')
                if oh.host != host:  # 如果需要改设备名，验证新设备名是否已存在
                    ret = formau.checkalive(cloudh, '设备名已存在,不区分大小写')
                if user and pwd:     #   如果需要改账号密码，验证下
                    ret = formau.checkempty(user, '账号不能为空')
                    ret = formau.checkmaxlen(user, 32, '账号最多32个字符')
                    ret = formau.checkempty(pwd, '密码不能为空')
                    ret = formau.checkmaxlen(pwd, 32, '密码最多32个字符')
                if loginuser.project.project != 'admin':   #   防止不是admin的租户使用id修改别人租户的设备
                    ret = formau.checknosame(oh.cluster.project_id, loginuser.project_id, '设备不属于此账号')
                if ret['status']:
                    cloudhostconfig = CloudHostConfig.cloudhost_config()
                    if user and pwd:  # 如果需要改账号密码
                        cloudhostconfig.editcloudhost(oh.id , host, h.id, user, pwd)
                    else:
                        cloudhostconfig.editcloudhost(oh.id, host, h.id, oh.username, oh.password)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '云设备{0}编辑成功'.format(host))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class cloudhostdel(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':  # 只有admin项目账号的admin权限可以编辑删除主设备、云设备
                idlist = request.POST.getlist('idlist[]')
                formau = FormAuthen.formauthen(ret)
                ret = formau.checksame(idlist, [], '请选择需要删除的主机')
                if ret['status']:
                    cloudhostlist = []
                    cloudhostconfig = CloudHostConfig.cloudhost_config()
                    for id in idlist:
                        host = Cloud_Host.objects.filter(id=id).first()
                        ret = formau.checknoalive(host, '设备不存在')
                        if ret['status']:
                            cloudhostconfig.dcloudhost(host)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '设备{0}删除成功'.format('、'.join(cloudhostlist)))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))