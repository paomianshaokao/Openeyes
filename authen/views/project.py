from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo

from audits.utils import yualert
from system.utils import yuoem
from authen.utils import FormAuthen, ProjectConfig

import json

class project(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                system = System.objects.filter(system='openeyes').first()
                oem = yuoem.yuoem()
                yuopera = yualert.yuoperalog(loginuser.id)
                alert = yuopera.alertGet()
                project = Project.objects.all()
                return render(request, 'project.html', {
                    'loginuser': loginuser, 'project': project,
                    'oem': oem, 'system': system, 'alert': alert,
                })
            else:
                return redirect('/authen/login/')
        else:
            return redirect('/authen/login/')

class projectadd(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                project = request.POST.get('project')
                p = Project.objects.filter(project=project).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checkminlen(project, 2, '项目名至少2个字符')
                ret = formau.checkmaxlen(project, 32, '项目名最多32个字符')
                ret = formau.checkinput(project, '项目名只能为汉字、数字、字母或下划线')
                ret = formau.checksame(project, 'admin', '项目名禁止使用')
                ret = formau.checkalive(p, '项目名已存在')
                if ret['status']:
                    projectconfig = ProjectConfig.project_config()
                    projectconfig.addproject(project)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '项目{0}创建成功'.format(project))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class projectedit(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                id = request.POST.get('id')
                project = request.POST.get('project')
                pj = Project.objects.filter(id=id).first()
                p = Project.objects.filter(project=project).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checksame(pj.project, 'admin', '禁止修改admin项目')
                ret = formau.checkminlen(project, 2, '项目名至少2个字符')
                ret = formau.checkmaxlen(project, 32, '项目名最多32个字符')
                ret = formau.checkinput(project, '项目名只能为汉字、数字、字母或下划线')
                ret = formau.checksame(project, 'admin', '项目名禁止使用')
                ret = formau.checkalive(p, '项目名已存在')
                if ret['status']:
                    projectconfig = ProjectConfig.project_config()
                    projectconfig.editproject(id, project)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '项目{0}修改成功'.format(project))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class projectdel(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                idlist = request.POST.getlist('idlist[]')
                formau = FormAuthen.formauthen(ret)
                ret = formau.checksame(idlist, [], '请选择需要删除的项目')
                if ret['status']:
                    projectlist = []
                    projectconfig = ProjectConfig.project_config()
                    yuopera = yualert.yuoperalog(loginuser.id)
                    for id in idlist:
                        project = Project.objects.filter(id=id).first()
                        ret = formau.checknoalive(project, '项目不存在')
                        if ret['status']:
                            if project.project != 'admin':
                                projectconfig.dproject(id)
                                projectlist.append(project.project)
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '项目{0}删除成功'.format('、'.join(projectlist)))
                            else:
                                yuopera.alertSet('error', '您好 {0}'.format(loginuser.username), '禁止删除admin项目')
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))