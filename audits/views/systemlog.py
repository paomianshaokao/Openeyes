from django.shortcuts import render, redirect
from django.views import View

from system.models import System
from authen.models import UserInfo

from audits.utils import yualert, SystemLog
from system.utils import yuoem

class systemlog(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            system = System.objects.filter(system='openeyes').first()
            oem = yuoem.yuoem()
            yuopera = yualert.yuoperalog(loginuser.id)
            alert = yuopera.alertGet()

            systemlog = SystemLog.systemLogConfig()
            if loginuser.project.project == 'admin':
                log = systemlog.log_all()
            else:
                log = systemlog.log_project(loginuser.project_id)
            return render(request, 'systemlog.html',
                          {'loginuser': loginuser, 'log': log,
                           'oem': oem, 'system':system, 'alert':alert,})
        else:
            return redirect('/authen/login/')