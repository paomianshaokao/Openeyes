from system.models import System
from audits.models import Alert
from authen.models import Project, UserGroup, UserInfo

from audits.utils import Mongodb
from audits.utils import SystemAudits, SystemLog, OperaLog
from cloud.utils import CloudORM

import os

class ormconfig(object):
    def initorm(self):
        System.objects.create(
            system='openeyes',
            hostname='OpenEyes',
        )
        Project.objects.create(
            project='admin'
        )
        project = Project.objects.filter(project='admin').first()
        UserGroup.objects.create(
            caption='admin',
        )
        # UserGroup.objects.create(
        #     caption='user',
        # )
        admin = UserGroup.objects.filter(caption='admin').first()
        UserInfo.objects.create(
            username='admin',
            password='admin',
            group_id=admin.id,
            project_id=project.id,
            state='Active'
        )
        # models.HostParm.objects.create(
        #     system='yuos',
        #     username='aidayu',
        #     password='yuadn@2018',
        #     port='19941',
        # )
        user_admin = UserInfo.objects.filter(username='admin').first()
        Alert.objects.create(
            alert = '',
            user_id = user_admin.id
        )
        return 'ORM初始化成功'

    def deletorm(self):
        System.objects.all().delete()
        Project.objects.all().delete()
        UserGroup.objects.all().delete()
        UserInfo.objects.all().delete()
        Alert.objects.all().delete()

        cloudorm = CloudORM.ormconfig()
        cloudorm.deletorm()
        systeminfo = SystemAudits.systemInfoConfig()
        systeminfo.canvas_remove()
        systemlog = SystemLog.systemLogConfig()
        systemlog.log_remove()
        operalog = OperaLog.operaLogConfig()
        operalog.opera_remove()

        Mongodb.del_openeyes()
        return 'ORM删除成功'