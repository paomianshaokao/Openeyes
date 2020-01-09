from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo

from audits.utils import yualert, SystemAudits
from authen.utils import FormAuthen
from system.utils import yuoem, yuversion, yusystemconfig

import json

class system(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                system = System.objects.filter(system='openeyes').first()
                oem = yuoem.yuoem()
                version = yuversion.yuversion()
                yuopera = yualert.yuoperalog(loginuser.id)
                alert = yuopera.alertGet()
                # interfaces = getcentos7ip()
                # interfaces_nunber = len(interfaces)
                systeminfoconfig = SystemAudits.systemInfoConfig()
                systemcanvas = systeminfoconfig.canvas_home()

                return render(request, 'system.html',
                              {'loginuser': loginuser, 'systemcanvas': systemcanvas,
                                'oem': oem, 'version': version,
                                'system':system, 'alert': alert,
                                })
            else:
                return redirect('/authen/login/')
        else:
            return redirect('/authen/login/')

class systemconfig(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                action = request.POST.get('action')
                yuopera = yualert.yuoperalog(loginuser.id)
                formau = FormAuthen.formauthen(ret)
                sysconfig = yusystemconfig.yusystemconfig()
                if action == 'systemname':
                    host = request.POST.get('host')
                    ret = formau.checkminlen(host, 2, '主机名至少2个字符')
                    ret = formau.checkmaxlen(host, 32, '主机名最多32个字符')
                    ret = formau.checkinput(host, '主机名只能为汉字、数字、字母或下划线')
                    if ret['status']:
                        sysconfig.editsystem(host)
                        yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '主机名修改成功')
                elif action == 'theme':
                    theme = request.POST.get('theme')
                    sysconfig.systemtheme(theme)
                elif action == 'reload':
                    sysconfig.systemreload()
                elif action == 'shutdown':
                    sysconfig.systemshutdown()
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))