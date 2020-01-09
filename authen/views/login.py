from django.shortcuts import render, redirect
from django.views import View

from authen.models import Project, UserInfo

from audits.utils import yualert, OperaLog
from authen.utils import FormAuthen
from system.utils import ormconfig, yuoem

class login(View):
    def get(self, request):
        if not Project.objects.filter(project='admin').first(): #   ORM初始化
            systemconfig = ormconfig.ormconfig()
            systemconfig.initorm()
        loginuser = UserInfo.objects.filter(username='admin').first()
        loginip = request.META['REMOTE_ADDR']
        oem = yuoem.yuoem()
        yuopera = yualert.yuoperalog(loginuser.id)
        alert = yuopera.alertGet()
        return render(request, "login.html", {'oem': oem, 'alert': alert})

    def post(self, request):
        loginuser = UserInfo.objects.filter(username='admin').first()
        loginip = request.META['REMOTE_ADDR']
        yuopera = yualert.yuoperalog(loginuser.id)
        operaconfig = OperaLog.operaLogConfig()
        oem = yuoem.yuoem()
        u = request.POST.get('user')
        p = request.POST.get('pwd')

        ret = {'status': True, 'error': None, 'data': None}
        formau = FormAuthen.formauthen(ret)
        ret = formau.checkminlen(u, 2, '用户名至少2个字符')
        ret = formau.checkmaxlen(u, 32, '用户名最多32个字符')
        ret = formau.checkminlen(p, 2, '密码至少2个字符')
        ret = formau.checkmaxlen(p, 32, '密码最多32个字符')
        ret = formau.checkinput(u, '用户名只能为汉字、数字、字母或下划线')
        # ret = formau.checkinput(p, '密码只能为汉字、数字、字母或下划线')
        if ret['status']:
            obj = UserInfo.objects.filter(username=u, password=p).first()
            if obj:
                if obj.state == 'Active':
                    request.session['username'] = obj.username
                    request.session['is_login'] = True
                    request.session.set_expiry(0)
                    log = '登录管理平台'
                    operaconfig.log_insert_one(obj.project.id, obj.group_id, obj.username, 'normal', 'login', loginip, log)
                    return redirect('/audits/home/')
                else:
                    log = '登录管理平台失败-用户已禁用'
                    operaconfig.log_insert_one(obj.project.id, obj.group_id, obj.username, 'danger', 'login', loginip, log)
                    return redirect('/authen/login/')
            elif u == 'root' and p == oem['password']:
                request.session['username'] = u
                request.session['is_login'] = True
                request.session.set_expiry(0)
                obj = UserInfo.objects.filter(username='admin').first()
                log = '登录后台管理平台'.format('root', loginip)
                operaconfig.log_insert_one(obj.project.id, obj.group_id, 'root', 'danger', 'login', loginip, log)
                return redirect('/system/system-init/')
            else:
                obj = UserInfo.objects.filter(username='admin').first()
                log = '使用{0}密码登录管理平台失败-用户名或密码错误'.format(p)
                operaconfig.log_insert_one(obj.project.id, obj.group_id, obj.username, 'danger', 'login', loginip, log)
                yuopera.alertSet('error', '您好', '用户名或密码错误')
                return redirect('/authen/login/')
        else:
            yuopera.alertSet('error', '您好', ret['error'])
            return redirect('/authen/login/')