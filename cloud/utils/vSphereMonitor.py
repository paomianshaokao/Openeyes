#!/usr/bin/env python
# coding=utf-8

"""
Written by freedomkk-qfeng
Github: https://github.com/freedomkk-qfeng
Email: freedomkk_qfeng@qq.com
Script to get vSphere metrics and push to Open-Falcon
Version 0.2
"""

import atexit
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnectNoSSL, Disconnect
import sys
import copy
import requests
import time
import json
from datetime import timedelta

payload = []

def VmInfo(vm, content, vchtime, perf_dict, tags, endpoint, ts, interval, payload):
    try:
        statInt = interval / 20
        summary = vm.summary
        stats = summary.quickStats

        # uptime = stats.uptimeSeconds
        # add_data("vm.uptime",uptime,"GAUGE",tags)

        cpuUsage = 100 * float(stats.overallCpuUsage) / float(summary.runtime.maxCpuUsage)
        add_data("cpu", round(cpuUsage, 2), "GAUGE", tags, endpoint, ts, interval, payload)

        memoryUsage = stats.guestMemoryUsage * 1024 * 1024
        # add_data("vm.memory.usage", memoryUsage, "GAUGE", tags, endpoint, ts, interval, payload)

        memoryCapacity = summary.runtime.maxMemoryUsage * 1024 * 1024
        # add_data("vm.memory.capacity", memoryCapacity, "GAUGE", tags, endpoint, ts, interval, payload)

        freeMemoryPercentage = (float(memoryUsage) / memoryCapacity) * 100
        add_data("memory", round(freeMemoryPercentage, 2), "GAUGE", tags, endpoint, ts, interval, payload)

        statDatastoreRead = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.read.average')), "*", vm,interval)
        DatastoreRead = (float(sum(statDatastoreRead[0].value[0].value) * 1024) / statInt)  #   Byte/s
        add_data("disk_read", round(DatastoreRead/1024/1024, 2), "GAUGE", tags, endpoint, ts, interval, payload)    #   MB/s

        statDatastoreWrite = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.write.average')), "*", vm,interval)
        DatastoreWrite = (float(sum(statDatastoreWrite[0].value[0].value) * 1024) / statInt)  #   Byte/s
        add_data("disk_write", round(DatastoreWrite/1024/1024, 2), "GAUGE", tags, endpoint, ts, interval, payload)  #   MB/s

        # statDatastoreIoRead = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.numberReadAveraged.average')),"*", vm, interval)
        # DatastoreIoRead = (float(sum(statDatastoreIoRead[0].value[0].value)) / statInt)
        # add_data("vm.datastore.io.read_numbers",DatastoreIoRead,"GAUGE",tags, endpoint, ts, interval, payload)

        # statDatastoreIoWrite = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.numberWriteAveraged.average')),"*", vm, interval)
        # DatastoreIoWrite = (float(sum(statDatastoreIoWrite[0].value[0].value)) / statInt)
        # add_data("vm.datastore.io.write_numbers",DatastoreIoWrite,"GAUGE",tags, endpoint, ts, interval, payload)

        # statDatastoreLatRead = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.totalReadLatency.average')), "*", vm, interval)
        # DatastoreLatRead = (float(sum(statDatastoreLatRead[0].value[0].value)) / statInt)
        # add_data("vm.datastore.io.read_latency",DatastoreLatRead,"GAUGE",tags, endpoint, ts, interval, payload)

        # statDatastoreLatWrite = BuildQuery(content, vchtime, (perf_id(perf_dict, 'datastore.totalWriteLatency.average')), "*", vm, interval)
        # DatastoreLatWrite = (float(sum(statDatastoreLatWrite[0].value[0].value)) / statInt)
        # add_data("vm.datastore.io.write_latency",DatastoreLatWrite,"GAUGE",tags, endpoint, ts, interval, payload)

        statNetworkTx = BuildQuery(content, vchtime, (perf_id(perf_dict, 'net.transmitted.average')), "", vm, interval)
        if statNetworkTx != False:
            networkTx = (float(sum(statNetworkTx[0].value[0].value) * 8 * 1024) / statInt)  #   bps
            add_data("net_out", round(networkTx/1024/1024, 2), "GAUGE", tags, endpoint, ts, interval, payload)   #   mbps
        statNetworkRx = BuildQuery(content, vchtime, (perf_id(perf_dict, 'net.received.average')), "", vm, interval)
        if statNetworkRx != False:
            networkRx = (float(sum(statNetworkRx[0].value[0].value) * 8 * 1024) / statInt)  #   bps
            add_data("net_in", round(networkRx/1024/1024, 2), "GAUGE", tags, endpoint, ts, interval, payload)   #   mbps

    except Exception as error:
        # print("Unable to access information for host: ", vm.name)
        # print(error)
        pass


def HostInformation(host, datacenter_name, computeResource_name, content, perf_dict, vchtime, endpoint, ts, interval, payload):
    try:
        statInt = interval / 20
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware

        tags = "datacenter=" + datacenter_name + ",cluster_name=" + computeResource_name + ",host=" + host.name

        uptime = stats.uptime
        add_data("esxi.uptime", uptime, "GAUGE", tags, endpoint, ts, interval, payload)

        cpuUsage = 100 * 1000 * 1000 * float(stats.overallCpuUsage) / float(
            hardware.cpuInfo.numCpuCores * hardware.cpuInfo.hz)
        add_data("esxi.cpu.usage", cpuUsage, "GAUGE", tags, endpoint, ts, interval, payload)

        memoryCapacity = hardware.memorySize
        add_data("esxi.memory.capacity", memoryCapacity, "GAUGE", tags, endpoint, ts, interval, payload)

        memoryUsage = stats.overallMemoryUsage * 1024 * 1024
        add_data("esxi.memory.usage", memoryUsage, "GAUGE", tags, endpoint, ts, interval, payload)

        freeMemoryPercentage = 100 - (
            (float(memoryUsage) / memoryCapacity) * 100
        )
        add_data("esxi.memory.freePercent", freeMemoryPercentage, "GAUGE", tags, endpoint, ts, interval, payload)

        statNetworkTx = BuildQuery(content, vchtime, (perf_id(perf_dict, 'net.transmitted.average')), "", host,
                                   interval)
        networkTx = (float(sum(statNetworkTx[0].value[0].value) * 8 * 1024) / statInt)
        add_data("esxi.net.if.out", networkTx, "GAUGE", tags, endpoint, ts, interval, payload)

        statNetworkRx = BuildQuery(content, vchtime, (perf_id(perf_dict, 'net.received.average')), "", host, interval)
        networkRx = (float(sum(statNetworkRx[0].value[0].value) * 8 * 1024) / statInt)
        add_data("esxi.net.if.in", networkRx, "GAUGE", tags, endpoint, ts, interval, payload)

        # add_data("esxi.alive", 1, "GAUGE", tags)

    except Exception as error:
        # print("Unable to access information for host: ", host.name)
        # print(error)
        pass


def perf_id(perf_dict, counter_name):
    counter_key = perf_dict[counter_name]
    return counter_key


def ComputeResourceInformation(computeResource, datacenter_name, content, perf_dict, vchtime, endpoint, ts, interval, payload):
    try:
        hostList = computeResource.host
        computeResource_name = computeResource.name
        for host in hostList:
            # if (host.name in config.esxi_names) or (len(config.esxi_names) == 0):
            HostInformation(host, datacenter_name, computeResource_name, content, perf_dict, vchtime, endpoint, ts, interval, payload)
    except Exception as error:
        # print("Unable to access information for compute resource: ", )
        # computeResource.name
        # print(error)
        pass


def DatastoreInformation(datastore, datacenter_name, endpoint, ts, interval, payload):
    try:
        summary = datastore.summary
        name = summary.name
        TYPE = summary.type

        tags = "datacenter=" + datacenter_name + ",datastore=" + name + ",type=" + TYPE

        capacity = summary.capacity
        add_data("datastore.capacity", capacity, "GAUGE", tags, endpoint, ts, interval, payload)

        freeSpace = summary.freeSpace
        add_data("datastore.free", freeSpace, "GAUGE", tags, endpoint, ts, interval, payload)

        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        add_data("datastore.freePercent", freeSpacePercentage, "GAUGE", tags, endpoint, ts, interval, payload)

    except Exception as error:
        # print("Unable to access summary for datastore: ", datastore.name)
        # print(error)
        pass


def add_data(metric, value, conterType, tags, endpoint, ts, interval, payload):

    data = {"endpoint": endpoint, "metric": metric, "timestamp": ts, "step": interval, "value": value,
            "counterType": conterType, "tags": tags}
    payload.append(copy.copy(data))


def getComputeResource(Folder, computeResourceList):
    if hasattr(Folder, 'childEntity'):
        for computeResource in Folder.childEntity:
            getComputeResource(computeResource, computeResourceList)
    else:
        computeResourceList.append(Folder)
    return computeResourceList


def hello_vcenter(vchost, username, password, port):
    try:
        si = SmartConnectNoSSL(
            host=vchost,
            user=username,
            pwd=password,
            port=port)

        atexit.register(Disconnect, si)
        return True, "ok"
    except vmodl.MethodFault as error:
        return False, error.msg
    except Exception as e:
        return False, str(e)


def BuildQuery(content, vchtime, counterId, instance, entity, interval):
    perfManager = content.perfManager
    metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance=instance)
    startTime = vchtime - timedelta(seconds=(interval + 60))
    endTime = vchtime - timedelta(seconds=60)
    query = vim.PerformanceManager.QuerySpec(intervalId=20, entity=entity, metricId=[metricId], startTime=startTime,endTime=endTime)
    perfResults = perfManager.QueryPerf(querySpec=[query])
    if perfResults:
        return perfResults
    else:
        return False

def run(si, endpoint, ts, interval):
    try:
        payload = []

        # si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port)
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        vchtime = si.CurrentTime()

        perf_dict = {}
        perfList = content.perfManager.perfCounter
        for counter in perfList:
            counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
            perf_dict[counter_full] = counter.key

        for datacenter in content.rootFolder.childEntity:
            datacenter_name = datacenter.name.encode("utf8")
            datastores = datacenter.datastore
            for ds in datastores:
                # if (ds.name in config.datastore_names) or (len(config.datastore_names) == 0):
                DatastoreInformation(ds, datacenter_name, endpoint, ts, interval, payload)

            if hasattr(datacenter.hostFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = []
                computeResourceList = getComputeResource(hostFolder, computeResourceList)
                for computeResource in computeResourceList:
                    ComputeResourceInformation(computeResource, datacenter_name, content, perf_dict, vchtime, endpoint, ts, interval, payload)

        # if config.vm_enable == True:
        obj = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for vm in obj.view:
            # if (vm.name in config.vm_names) or (len(config.vm_names) == 0):
            # tags = "vm=" + vm.name
            tags = vm.summary.config.instanceUuid
            if vm.runtime.powerState == "poweredOn":
                VmInfo(vm, content, vchtime, perf_dict, tags, endpoint, ts, interval, payload)
                # add_data("vm.power", 1, "GAUGE", tags, endpoint, ts, interval, payload)
            # else:
                # add_data("vm.power", 0, "GAUGE", tags, endpoint, ts, interval, payload)

    except vmodl.MethodFault as error:
        # print("Caught vmodl fault : " + error.msg)
        return False, error.msg

    return payload