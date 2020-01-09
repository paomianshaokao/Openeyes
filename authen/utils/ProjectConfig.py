from authen.models import Project

class project_config(object):
    def addproject(self, project):
       Project.objects.create(
            project=project,
        )

    def editproject(self, id, project):
        Project.objects.filter(id=id).update(
            project=project,
        )

    def dproject(self, id):
        Project.objects.filter(id=id).delete()