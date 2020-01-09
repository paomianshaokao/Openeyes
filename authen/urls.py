"""openeyes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from .views import login, logout, project, user

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', login.login.as_view()),
    path('logout/', logout.logout.as_view()),
    path('project/', project.project.as_view()),
    path('projectadd/', project.projectadd.as_view()),
    path('projectedit/', project.projectedit.as_view()),
    path('projectdel/', project.projectdel.as_view()),
    path('user/', user.user.as_view()),
    path('useradd/', user.useradd.as_view()),
    path('useredit/', user.useredit.as_view()),
    path('userdel/', user.userdel.as_view()),
]
