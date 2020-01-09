from django.shortcuts import render, redirect
from django.views import View

from system.models import System
from authen.models import UserInfo

from audits.utils import yualert, SystemAudits, SystemLog, OperaLog
from system.utils import yuoem
from cloud.utils import CloudInfo

class home(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            system = System.objects.filter(system='openeyes').first()
            oem = yuoem.yuoem()
            yuopera = yualert.yuoperalog(loginuser.id)
            alert = yuopera.alertGet()

            cloudinfo = CloudInfo.cloud_info()
            systemlog = SystemLog.systemLogConfig()
            operalog = OperaLog.operaLogConfig()
            if loginuser.project.project == 'admin':
                log = systemlog.log_home_all()
                system.normal = log['normal_number']
                system.warning = log['warning_number']
                system.danger = log['danger_number']
                system.login = operalog.opera_home_all()

                system.hostnumber = cloudinfo.host_number()
                system.onhostnumber = cloudinfo.onhost_number()

                system.loginusername = operalog.opera_home_login_all()
            else:
                log = systemlog.log_home_project(loginuser.project_id)
                system.normal = log['normal_number']
                system.warning = log['warning_number']
                system.danger = log['danger_number']
                system.login = operalog.opera_home_project(loginuser.project_id)

                system.hostnumber = cloudinfo.project_host_number(loginuser.project_id)
                system.onhostnumber = cloudinfo.project_onhost_number(loginuser.project_id)

                system.loginusername = operalog.opera_home_login_project(loginuser.project_id)
            # cluster_number = len(cluster_list)
            # host_list = models.Host.objects.all()
            # host_number = len(host_list)

            # canvas = yucanvas()
            systeminfoconfig = SystemAudits.systemInfoConfig()
            systemcanvas = systeminfoconfig.canvas_home()
            # if host_number <= 5:
            #     top5hostcpu = host_list
            #     top5hostmem = host_list
            # else:
            #     top5hostcpu = canvas.gettop5host(host_list, 'cpu')
            #     top5hostmem = canvas.gettop5host(host_list, 'mem')
            # top5hostcpu = canvas.top5host_canvas(top5hostcpu)
            # top5hostmem = canvas.top5host_canvas(top5hostmem)

            # f = yufile(r'/home/www/yuweb/top/{0}-top.yu'.format(loginuser.user_project_id))
            # string = f.openfile()
            # top = {'network': [], 'server': [], 'pc': [], 'edges': []}
            # if string != '':
            #     top = eval(string)
            # return render(request, 'admin-home.html',
            #               {'loginuser': loginuser, 'cluster_list': cluster_list, 'cluster_number': cluster_number,
            #                'systemcanvas': systemcanvas, 'top5hostcpu': top5hostcpu, 'top5hostmem': top5hostmem,
            #                'top': json.dumps(top),
            #                'oem':oem, 'system': system, 'alert':alert })
            return render(request, 'home.html',
                          {'loginuser': loginuser,'system': system,
                           'systemcanvas': systemcanvas,
                           'oem': oem, 'alert': alert})
        else:
            return redirect('/authen/login/')