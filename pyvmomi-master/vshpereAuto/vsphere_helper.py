from optparse import OptionParser, make_option
from pyVim.connect import SmartConnect, Disconnect

import pyVmomi
import textwrap
import argparse
import atexit

import yaml

import os

import vsphere


def get_child_vm_names(vappname, count):
    vmnames = []
    for i in range(1, count+1):
        if i < 10:
            temp = '{v}_00'.format(v=vappname.lstrip('vApp_')) + str(i)
        else:
            temp = '{v}_0'.format(v=vappname.lstrip('vApp_')) + str(i)
        vmnames.append(temp)
    return vmnames


def get_child_vm_ips(vmFolderList, vappname, child_count=17):
    child_vm_names = get_child_vm_names(vappname, count=child_count)
    ips = []
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for vmname in child_vm_names:
                for cvm in citem.vm:
                    if cvm.name == vmname:
                        ips.append(cvm.summary.guest.ipAddress)
                        break
            break
    dict_yaml = {}
    dict_yaml['hosts'] = ips
    print yaml.dump(dict_yaml, default_flow_style=False)


def power_on(vmFolderList, vappname):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for cvm in citem.vm:
                print 'Power on vm {v}'.format(v=cvm.name)
                cvm.PowerOn()
            break


def power_off(vmFolderList, vappname):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for cvm in citem.vm:
                print 'Power off vm {v}'.format(v=cvm.name)
                cvm.PowerOff()
            break


def start_operation(operation, vappname, snapname, arguments_confirmed=False):
    if not arguments_confirmed:
        raw_input('Press ENTER to confirm vappname: {v}'.format(v=vappname))
        if bool(snapname):
            raw_input('Press ENTER to confirm operation: {o} {s}'.format(o=operation, s=snapname))
            
        else:
            raw_input('Press ENTER to confirm operation: {o}'.format(o=operation))
        raw_input('Press ENTER to start ...')

    with open("params.yml", 'r') as stream:
        params = yaml.load(stream)

    si = SmartConnect(
            host  = params['host'],
            user  = os.getenv('VSPHERE_USER'),
            pwd   = os.getenv('VSPHERE_PASSWORD'),
            port  = int(params['port']))

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    vmFolderList = []
    for datacenter in content.rootFolder.childEntity:
        for citem in datacenter.vmFolder.childEntity:
            if type(citem) == pyVmomi.types.vim.Folder:
                vmFolderList = vmFolderList + citem.childEntity
            else:
                vmFolderList.append(citem)

    vs = vsphere.vsphere()

    if operation == 'list':
        vs.getmyList(vmFolderList)
    elif operation == 'ip':
        get_child_vm_ips(vmFolderList, vappname)
    elif operation == 'poweron':
        power_on(vmFolderList, vappname)
    elif operation == 'poweroff':
        power_off(vmFolderList, vappname)
    elif operation == 'revertsnapshot':
        vs.revertSnap_vapp(vmFolderList, vappname, snapname)
    elif operation == 'createsnapshot':
        vs.createSnap_vapp(vmFolderList, vappname, snapname)
    elif operation == 'deletesnapshot':
        vs.removeSnap_vapp(vmFolderList, vappname, snapname)
    else:
        print "operation {o} is not supported".format(o=operation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'operation', nargs='?', default='list', 
        choices=['list', 'createsnapshot', 'revertsnapshot', 'deletesnapshot', 'ip', 'poweron', 'poweroff'],
        help='operation to take, default is list')
    parser.add_argument(
        '-a', '--vappname', default=None, help='vpp name')
    parser.add_argument(
        '-s', '--snapname', default=None, help='snapshot name')
    parser.add_argument(
        '--confirmed',
        help='confirm the arguments without interaction',
        action='store_true')

    args = parser.parse_args()
    start_operation(
        operation=args.operation, vappname=args.vappname, snapname=args.snapname, 
        arguments_confirmed=args.confirmed)
