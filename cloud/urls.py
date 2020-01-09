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
from .views import cluster, host, cloudhost, vsphere

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('cluster/', cluster.cluster.as_view()),
    path('clusteradd/', cluster.clusteradd.as_view()),
    path('clusteredit/', cluster.clusteredit.as_view()),
    path('clusterdel/', cluster.clusterdel.as_view()),
    path('host-<str:cluster>/', host.host.as_view()),
    path('hostadd-<int:id>/', host.hostadd.as_view()),
    path('hostedit/', host.hostedit.as_view()),
    path('hostdel/', host.hostdel.as_view()),
    path('cloudhostadd-<int:id>/', cloudhost.cloudhostadd.as_view()),
    path('cloudhostedit/', cloudhost.cloudhostedit.as_view()),
    path('cloudhostdel/', cloudhost.cloudhostdel.as_view()),
    path('vsphere-<str:hostname>/', vsphere.cloud.as_view()),
    path('vsphereconfig-<str:clu>-<str:hostname>/', vsphere.vsphereconfig.as_view()),
    path('canvasconfig-<str:clu>/', vsphere.canvasconfig.as_view()),
]
