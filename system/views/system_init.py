from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from authen.models import UserInfo

from ..utils import ormconfig
import json

class system_init(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            return render(request, "system-init.html")
        else:
            return redirect('/')
    def post(self, request):
        mode = request.POST.get('mode')
        orm = ormconfig.ormconfig()
        log = '操作失败'
        if mode == '初始化ORM':
            log = orm.initorm()
        elif mode == '清除所有ORM':
            log = orm.deletorm()
        elif mode == '重置admin密码':
            UserInfo.objects.filter(username='admin').update(password='admin')
            log = 'admin密码重置成功'
        #     log = 'admin密码重置成功'
        # if (mode == '清除主机日志'):
        #     models.HostCanvas.objects.all().delete()
        #     log = '主机日志清除成功'
        # if (mode == '清除系统日志'):
        #     models.SystemLog.objects.all().delete()
        #     log = '系统日志清除成功'
        # if (mode == '清除操作日志'):
        #     models.OperaLog.objects.all().delete()
        #     log = '操作日志清除成功'
        return HttpResponse(json.dumps(log))