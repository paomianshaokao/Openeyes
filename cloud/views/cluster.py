from django.shortcuts import render, redirect, HttpResponse
from django.views import View

from system.models import System
from authen.models import Project, UserInfo
from cloud.models import Cluster, Host, Cloud_Host

from audits.utils import yualert
from system.utils import yuoem
from authen.utils import FormAuthen
from cloud.utils import ClusterConfig

import json

class cluster(View):
    def get(self, request):
        if request.session.get('is_login', None):
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            system = System.objects.filter(system='openeyes').first()
            oem = yuoem.yuoem()
            yuopera = yualert.yuoperalog(loginuser.id)
            alert = yuopera.alertGet()

            project = Project.objects.all()
            if loginuser.project.project == 'admin':
                cluster_list = Cluster.objects.all()
            else:
                cluster_list = Cluster.objects.filter(project_id=loginuser.project.id).all()
            host_list = Host.objects.all()
            cloudhost_list = Cloud_Host.objects.all()
            clusteronhost = ClusterConfig.cluster_onhost()  #   定义计算在线主机对象
            cluster_list = clusteronhost.onhost(cluster_list, host_list, cloudhost_list)   #   计算在线主机
            return render(request, 'cluster.html',
                          {'loginuser': loginuser,
                           'cluster_list': cluster_list, 'project': project,
                           'oem': oem,  'system': system, 'alert':alert,
                           })
        else:
            return redirect('/authen/login/')

class clusteradd(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                system = System.objects.filter(system='openeyes').first()

                cluster = request.POST.get('clu')
                project = request.POST.get('project')
                hostnum = request.POST.get('hostnum')

                c = Cluster.objects.filter(cluster=cluster).first()
                p = Project.objects.filter(project=project).first()
                formau = FormAuthen.formauthen(ret)
                ret = formau.checkminlen(cluster, 2, '集群名至少2个字符')
                ret = formau.checkmaxlen(cluster, 32, '集群名最多32个字符')
                ret = formau.checkinput(cluster, '集群名只能为汉字、数字、字母或下划线')
                ret = formau.checkalive(c, '集群已存在')
                ret = formau.checknoalive(p, '项目不存在')
                ret = formau.checkempty(hostnum, '设备数不能为空')
                ret = formau.checkmaxlen(cluster, 16, '设备数最多16个字符')
                # license授权认证
                # ret = formau.checkClusterLicense(type)
                if ret['status']:
                    clusterconfig = ClusterConfig.cluster_config()
                    clusterconfig.addcluster(cluster, hostnum, p.id)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '集群{0}创建成功'.format(cluster))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Erorr : {0}'.format(e)
        return HttpResponse(json.dumps(ret))

class clusteredit(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                id = request.POST.get('id')
                cluster = request.POST.get('clu')
                project = request.POST.get('project')
                hostnum = request.POST.get('hostnum')
                cid = Cluster.objects.filter(id=id).first()
                c = Cluster.objects.filter(cluster=cluster).first()
                p = Project.objects.filter(project=project).first()
                formau = FormAuthen.formauthen(ret)
                if cid.cluster != cluster:  #   如果修改了集群名
                    ret = formau.checkminlen(cluster, 2, '集群名至少2个字符')
                    ret = formau.checkmaxlen(cluster, 32, '集群名最多32个字符')
                    ret = formau.checkinput(cluster, '集群名只能为汉字、数字、字母或下划线')
                    ret = formau.checkalive(c, '集群已存在,不区分大小写')
                    ret = formau.checknoalive(p, '项目不存在')
                ret = formau.checkempty(hostnum, '设备数不能为空')
                ret = formau.checkmaxlen(cluster, 16, '设备数最多16个字符')
                if ret['status']:
                    clusterconfig = ClusterConfig.cluster_config()
                    clusterconfig.editcluster(cid.id,cluster,p.id,hostnum)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '集群{0}编辑成功'.format(cluster))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))


class clusterdel(View):
    def post(self, request):
        ret = {'status': True, 'error': None, 'data': None}
        try:
            loginuser = UserInfo.objects.filter(username=request.session['username']).first()
            loginip = request.META['REMOTE_ADDR']
            if loginuser.project.project == 'admin':
                idlist = request.POST.getlist('idlist[]')
                formau = FormAuthen.formauthen(ret)
                ret = formau.checksame(idlist, [], '请选择需要删除的集群')
                if ret['status']:
                    cluster = []
                    clusterconfig = ClusterConfig.cluster_config()
                    for id in idlist:
                        c = Cluster.objects.filter(id=id).first()
                        ret = formau.checknoalive(c, '集群不存在')
                        # host = Host.objects.filter(host_cluster_id=id).first()
                        # if host:
                        #     hosts = Host.objects.filter(host_cluster_id=id).all()
                        #     hostconfig = host_config()
                        #     hostconfig.dhosts(hosts)
                        #     hosts.delete()
                        if ret['status']:
                            clusterconfig.dcluster(id)
                            cluster.append(c.cluster)
                    yuopera = yualert.yuoperalog(loginuser.id)
                    yuopera.alertSet('success', '您好 {0}'.format(loginuser.username), '集群{0}删除成功'.format('、'.join(cluster)))
        except Exception as e:
            ret['status'] = False
            ret['error'] = 'Error : {0}'.format(e)
        return HttpResponse(json.dumps(ret))