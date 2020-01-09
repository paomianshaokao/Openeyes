from cloud.models import Host_VM, Cloud_Host, Cloud_VM

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import atexit, ssl, time

from cloud.utils.vSphereMonitor import run
from audits.utils import CloudAudits

class vsphereget(object):
    def __init__(self, ip, username, password, port):
        # context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        # context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = ssl._create_unverified_context
        # self.si = connect.SmartConnect(host=host.ip, user=host.username, pwd=host.password, port=int(host.port), sslContext=context)
        # self.si = connect.SmartConnectNoSSL(host=host.ip, user=host.username, pwd=host.password, port=int(host.port))
        self.si = connect.SmartConnect(host=ip, user=username, pwd=password, port=int(port))
        # self.host = host

    def vsphere_get_vm(self):
        vmlist = []
        atexit.register(connect.Disconnect, self.si)
        content = self.si.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

        children = containerView.view
        for child in children:
            summary = child.summary
            vm = summary.config.name
            ip = summary.guest.ipAddress
            system = summary.config.guestFullName
            cpu = summary.config.numCpu
            mem = summary.config.memorySizeMB / 1024
            disk = round(summary.storage.committed / 1073741824, 1)
            netcard = summary.config.numEthernetCards
            uuid = summary.config.instanceUuid
            power = summary.runtime.powerState
            # hostname = summary.guest.hostName
            vmlist.append({'vm': vm, 'ip': ip, 'system': system, 'cpu': cpu,'mem': mem, 'disk': disk, 'netcard': netcard, 'uuid': uuid,
                           'power': power})
        return vmlist

    def get_vm(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        get_vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)

        summary = get_vm.summary
        vm = summary.config.name
        ip = summary.guest.ipAddress
        system = summary.config.guestFullName
        cpu = summary.config.numCpu
        mem = summary.config.memorySizeMB / 1024
        disk = round(summary.storage.committed / 1073741824, 1)
        netcard = summary.config.numEthernetCards
        uuid = summary.config.instanceUuid
        power = summary.runtime.powerState
        # hostname = summary.guest.hostName

        vm_dist = {'vm': vm, 'ip': ip, 'system': system, 'cpu': cpu, 'mem': mem, 'disk': disk, 'netcard': netcard,
                   'uuid': uuid,'power': power}
        return  vm_dist

    def web_token(self, uuid, httphostip, urlport, ip, port):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)

        ticket = vm.AcquireTicket(ticketType='webmks')

        if ticket.host:
            ip = ticket.host

        # return 'wss://{0}:{1}/ticket/{2}'.format(ip, ticket.port, ticket.ticket)
        return 'wss://{0}:{1}/console/?ip={2}&port={3}&ticket={4}'.format(httphostip, urlport, ip, port, ticket.ticket)

    #   给主设备虚拟机添加分派信息
    def vsphere_get_hostvm(self, vmlist, hostvmlist):
        vm_list = []
        if hostvmlist:
            for vm in vmlist:
                for hostvm in hostvmlist:
                    if vm['uuid'] == hostvm.uuid:
                        vm['host'] = hostvm.host.host
                vm_list.append(vm)
        else:
            vm_list = vmlist
        return vm_list

    #   给云设备虚拟机添加分派信息
    def vsphere_get_cloudhostvm(self, vmlist, cloudvmlist):
        vm_list = []
        if cloudvmlist:
            for vm in vmlist:
                for cloudvm in cloudvmlist:
                    if vm['uuid'] == cloudvm.uuid:
                        vm['host'] = cloudvm.cloud_host.host
                vm_list.append(vm)
        else:
            vm_list = vmlist
        return vm_list

    #   过滤出分派给云设备的虚拟机
    def vsphere_get_cloudvm(self, vmlist, cloudvmlist):
        vm_list = []
        if cloudvmlist: #   如果有分配虚拟机
            for cloudvm in cloudvmlist:
                for vm in vmlist:
                    if cloudvm.uuid == vm['uuid']:
                        vm_list.append(vm)
        return vm_list

    #   删除在vcenter中被删除且已被记录分派的主设备虚拟机
    def vsphere_del_hostvm(self, vmlist, hostvmlist):
        if hostvmlist:  # 如果有分配虚拟机
            cloudinfo = CloudAudits.cloudInfoConfig()
            for hostvm in hostvmlist:
                vm_del = True  # 用与判断分派的虚拟机有没有在vcenter中删除，重置状态，Ture表示被删除了
                for vm in vmlist:
                    if hostvm.uuid == vm['uuid']:
                        vm_del = False  # 如果分配的虚拟机还在vcenter中，False表示未被删除
                if vm_del:  # 循环结束，还没有在vcenetor获得虚拟机中找到分配保存在本地的虚拟机，及表示已经在vcenter中被删除
                    Host_VM.objects.filter(id=hostvm.id).delete()  # 删除本地的虚拟机
                    cloudinfo.canvas_del_uuid(hostvm.uuid)  #   同时删除Canvas

    #   删除在vcenter中被删除且已被记录分派的云设备虚拟机
    def vsphere_del_cloudvm(self, vmlist, cloudvmlist):
        if cloudvmlist:  # 如果有分配虚拟机
            cloudinfo = CloudAudits.cloudInfoConfig()
            for cloudvm in cloudvmlist:
                vm_del = True  # 用与判断分派的虚拟机有没有在vcenter中删除，重置状态，Ture表示被删除了
                for vm in vmlist:
                    if cloudvm.uuid == vm['uuid']:
                        vm_del = False  # 如果分配的虚拟机还在vcenter中，False表示未被删除
                if vm_del:  # 循环结束，还没有在vcenetor获得虚拟机中找到分配保存在本地的虚拟机，及表示已经在vcenter中被删除
                    Cloud_VM.objects.filter(id=cloudvm.id).delete()  # 删除本地的虚拟机
                    cloudinfo.canvas_del_uuid(cloudvm.uuid)  # 同时删除Canvas

    #   获取虚拟机实时信息
    def vsphere_get_vm_info(self):
        endpoint = "vcenter"  # 上报给 open-falcon 的 endpoint
        interval = 60  # 上报的 step 间隔

        ts = int(time.time())
        payload = run(self.si, endpoint, ts, interval)

        hostvmlist = Host_VM.objects.all()
        cloudvmlist = Cloud_VM.objects.all()
        cloudinfoconfig = CloudAudits.cloudInfoConfig()

        if hostvmlist:
            for hostvm in hostvmlist:
                vminfo = {'uuid': hostvm.uuid}
                for info in payload:
                    if info['tags'] == hostvm.uuid:
                        vminfo[info['metric']]= info['value']
                if len(vminfo) > 1:
                    cloudinfoconfig.canvas_insert_one(vminfo)
        if cloudvmlist:
            for cloudvm in cloudvmlist:
                vminfo = {'uuid': cloudvm.uuid}
                for info in payload:
                    if info['tags'] == cloudvm.uuid:
                        vminfo[info['metric']] = info['value']
                if len(vminfo) > 1:
                    cloudinfoconfig.canvas_insert_one(vminfo)

#   vSphere配置
class vsphereconf(object):
    def __init__(self, ip, username, password, port):
        # context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        # context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = ssl._create_unverified_context
        # self.si = connect.SmartConnect(host=host.ip, user=host.username, pwd=host.password, port=int(host.port), sslContext=context)
        self.si = connect.SmartConnect(host=ip, user=username, pwd=password, port=int(port))

    def reboot(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)
        task = vm.ResetVM_Task()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        return vm.name, task.info.state

    def soft_reboot(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)
        task = vm.RebootGuest()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        return vm.name, task.info.state

    def suspend(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)
        task = vm.Suspend()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        return vm.name, task.info.state

    def poweron(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)
        task = vm.PowerOn()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        return vm.name, task.info.state


    def poweroff(self, uuid):
        atexit.register(connect.Disconnect, self.si)

        vm = self.si.content.searchIndex.FindByUuid(None, uuid, True, True)
        task = vm.PowerOff()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        return vm.name, task.info.state

    def allocation_host_vm(self, host, uuid):
        hostvm = Host_VM.objects.filter(uuid=uuid).first()
        if hostvm:  #   之前分派给了主设备，就不会在云设备中，直接删除
            Host_VM.objects.filter(uuid=uuid).delete()
        else:   #   主设备没有的话，需要检查下云设备里有没有
            cloudvm = Cloud_VM.objects.filter(uuid=uuid).first()
            if cloudvm: #   如果有,将云设备的分派删掉
                Cloud_VM.objects.filter(uuid=uuid).delete()
            Host_VM.objects.create(uuid=uuid, host_id=host.id)
        cloudinfo = CloudAudits.cloudInfoConfig()
        cloudinfo.canvas_del_uuid(uuid)  # 同时删除Canvas


    def allocation_cloudhost_vm(self, cloudhost, uuid):
        cloudvm = Cloud_VM.objects.filter(uuid=uuid).first()
        if cloudvm: #   之前分派给了云设备，就不会在主设备中，直接删除
            Cloud_VM.objects.filter(uuid=uuid).delete()
        else:   #   云设备没有的话，需要检查下主设备里有没有
            hostvm = Host_VM.objects.filter(uuid=uuid).first()  #   检查下主设备里是否有
            if hostvm:  #   如果有,将主设备的分派删掉
                Host_VM.objects.filter(uuid=uuid).delete()
            Cloud_VM.objects.create(uuid=uuid, cloud_host_id=cloudhost.id)
        cloudinfo = CloudAudits.cloudInfoConfig()
        cloudinfo.canvas_del_uuid(uuid)  # 同时删除Canvas