from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserGroup, UserInfo

from audits.utils import yualert
from system.utils import yuoem
from authen.utils import FormAuthen, UserConfig

import json

class user(View):
    def get(self, request):
        if request.session.get('is_login', None):
            try:    #如果用户删掉了正在使用的账号，cookies没清空，下面查账号会报错
                loginuser = UserInfo.objects.filter(username=request.session['username']).first()
                loginip = request.META['REMOTE_ADDR']
                system = System.objects.filter(system='openeyes').first()
                oem = yuoem.yuoem()
                yuopera = yualert.yuoperalog(loginuser.id)
                alert = yuopera.alertGet()

                if loginuser.project.project == 'admin':
                    user_list = UserInfo.objects.all()
                    project = Project.objects.all()
                else:
                    user_list = UserInfo.objects.filter(project_id=loginuser.project_id).all()
                    project = Project.objects.filter(id=loginuser.project_id).all()

                return render(request, 'user.html', {
                    'loginuser': loginuser, 'user_list': user_list, 'project': project,
                    'oem': oem, 'system': system, 'alert': alert,
                })
            except Exception as e:
                return redirect('/authen/login/')
        else:
            return redirect('/authen/login/')

class useradd(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']

            user = request.POST.get('user')
            email = request.POST.get('email')
            pwd1 = request.POST.get('pwd1')
            pwd2 = request.POST.get('pwd2')
            group = request.POST.get('group')
            project = request.POST.get('project')
            if loginuser.project.project != 'admin':  # 如果是用户
                project = loginuser.project.project  # 由于用户没能选择项目，补上用户的项目参数
            u = UserInfo.objects.filter(username=user).first()
            g = UserGroup.objects.filter(caption=group).first()
            p = Project.objects.filter(project=project).first()
            if loginuser.project.project == 'admin'or p.id == loginuser.project_id:  # 身份判断
                formau = FormAuthen.formauthen(ret)
                ret = formau.checkminlen(user, 2, '用户名至少2个字符')
                ret = formau.checkmaxlen(user, 32, '用户名最多32个字符')
                ret = formau.checkinput(user, '用户名只能为汉字、数字、字母或下划线')
                ret = formau.checksame(user, 'root', '用户名禁止使用')
                ret = formau.checksame(user, 'nginx', '用户名禁止使用')
                ret = formau.checkalive(u, '用户名已存在')
                ret = formau.checkemail(email, '邮箱格式错误')
                ret = formau.checkminlen(pwd1, 3, '密码至少3个字符')
                ret = formau.checkmaxlen(pwd1, 32, '密码最多32个字符')
                ret = formau.checknosame(pwd1, pwd2, '两次密码输入不一致')
                # ret = formau.checkinput(pwd1, '密码只能为汉字、数字、字母或下划线')
                # ret = formau.checkinput(pwd2, '密码只能为汉字、数字、字母或下划线')
                ret = formau.checknoalive(g, '群组不存在')
                ret = formau.checknoalive(p, '项目不存在')
                if ret['status']:
                    userconfig = UserConfig.userconfig()
                    userconfig.adduser(user, pwd1, email, g.id, p.id)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '账号{0}创建成功'.format(user))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class useredit(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']

            id = request.POST.get('id')
            user = request.POST.get('user')
            email = request.POST.get('email')
            # pwd = request.POST.get('pwd') #原密码，无普通用户暂时取消
            pwd1 = request.POST.get('pwd1')
            pwd2 = request.POST.get('pwd2')
            group = request.POST.get('group')
            project = request.POST.get('project')
            u = UserInfo.objects.filter(id=id).first()
            newu = UserInfo.objects.filter(username=user).first()
            g = UserGroup.objects.filter(caption=group).first()
            p = Project.objects.filter(project=project).first()
            if loginuser.project.project == 'admin' or u.id == loginuser.project_id:  # 身份判断
                formau = FormAuthen.formauthen(ret)
                ret = formau.checkemail(email, '邮箱格式错误')
                ret = formau.checknoalive(g, '群组不存在')
                if u.username != user:  #   如果需要修改用户名
                    ret = formau.checkalive(newu, '用户名已存在,不区分大小写')
                    ret = formau.checkminlen(user, 2, '用户名至少2个字符')
                    ret = formau.checkmaxlen(user, 32, '用户名最多32个字符')
                    ret = formau.checkinput(user, '用户名只能为汉字、数字、字母或下划线')
                    ret = formau.checksame(user, 'root', '用户名禁止使用')
                    ret = formau.checksame(user, 'nginx', '用户名禁止使用')
                    if u.username == 'admin':  # 如果修改的是admin用户
                        ret = formau.checknosame(user, 'admin', '禁止修改admin用户名称')
                        ret = formau.checknosame(group, 'admin', 'admin用户只能为admin角色')
                        ret = formau.checknosame(project, 'admin', 'admin用户只能为admin项目')
                if len(pwd1) != 0 or len(pwd2) != 0: #   如果需要修改密码
                    ret = formau.checkminlen(pwd1, 3, '密码至少3个字符')
                    ret = formau.checkmaxlen(pwd1, 32, '密码最多32个字符')
                    ret = formau.checknosame(pwd1, pwd2, '两次密码输入不一致')
                    # ret = formau.checkinput(pwd1, '密码只能为汉字、数字、字母或下划线')
                    # ret = formau.checkinput(pwd2, '密码只能为汉字、数字、字母或下划线')
                    # if loginuser.group.caption == 'user':  #   如果是普通用户修改密码，暂时无普通用户取消原密码
                    #     ret = formau.checkempty(pwd, '原密码不能为空')
                    #     ret = formau.checknosame(pwd, u.password, '原密码错误')
                if ret['status']:
                    userconfig = UserConfig.userconfig()
                    if len(pwd1) == 0 and len(pwd2) == 0:  # 如果不需要修改密码
                        pwd1 = u.password
                    userconfig.edituser(u.id, user, pwd1, email, g.id, p.id)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '账号{0}修改成功'.format(user))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class userdel(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser =UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            idlist = request.POST.getlist('idlist[]')
            # userall = UserInfo.objects.filter(project_id=loginuser.project_id).all()    #获取账号项目的所有账号
            formau = FormAuthen.formauthen(ret)
            ret = formau.checksame(idlist,[],'请选择需要删除的账号')
            # ret = formau.checkmaxint(len(idlist),len(userall)-1,'请至少保留一个可用账号')
            if ret['status']:
                userlist = []
                userconfig = UserConfig.userconfig()
                yuopera = yualert.yuoperalog(loginuser.id)
                for id in idlist:
                    user = UserInfo.objects.filter(id=id).first()
                    ret = formau.checknoalive(user, '用户不存在')
                    ret = formau.checksame(user.id, loginuser.id, '无法删除当前登录的账号')
                    if ret['status']:
                        if loginuser.project.project == 'admin'or user.project_id == loginuser.project_id:  # 身份判断,是admin项目或者是本项目的放行
                            if user.username != 'admin':
                                userconfig.duser(id)
                                userlist.append(user.username)
                                yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '账号{0}删除成功'.format('、'.join(userlist)))
                            else:
                                yuopera.alertSet('error', '您好 {0}'.format(loginuser.username), '禁止删除admin账号')
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))