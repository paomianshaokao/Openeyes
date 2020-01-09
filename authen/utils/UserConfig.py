from authen.models import UserInfo

class userconfig(object):
    def adduser(self, user,pwd1,email,group_id, project_id):
        UserInfo.objects.create(
            username=user,
            password=pwd1,
            email=email,
            group_id=group_id,
            project_id=project_id,
        )

    def edituser(self, id, user, pwd1, email, group_id, project_id):
        UserInfo.objects.filter(id=id).update(
            username=user,
            password=pwd1,
            email=email,
            group_id=group_id,
            project_id=project_id,
        )

    def duser(self, id):
        UserInfo.objects.filter(id=id).delete()