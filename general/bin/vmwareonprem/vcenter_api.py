from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
from typing import Iterable
import ssl
import os
import sys
import yaml
import json
import configparser
import warnings


# Console colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Конфигурация экспорта в YAML
class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)
# Конец конфигурации экспорта в YAML

# Reading config file
script_path = os.path.dirname(__file__)
config_file = 'configuration copy.conf'
configpath = script_path + '/' + config_file
config = configparser.ConfigParser()
config.read(configpath)

# Setting Connection properties
host = config['vsphere']['host']
user = config['vsphere']['user']
pwd = config['vsphere']['pwd']

# Setting export path
exportpath = config['params'].get('exportpath', script_path)

# Setting prefix
prefix = ''
if config.has_option('params', 'root'):
    prefix = (config['params']['root'] + '.') if config['params']['root'] not in (None, '') else ''
if config.has_option('params', 'domain'):
    prefix = (prefix + config['params']['domain'] + '.') if config['params']['domain'] not in (None, '') else ''
print(f'\nSetting prefix for architectural objects: {bcolors.BOLD}{prefix}{bcolors.ENDC}\n')

# Setting DC or Office Id
location = ''
if config.has_option('params', 'location'):
    location = (config['params']['location']) if config['params']['location'] not in (None, '') else ''
print(f'\nSetting location for architectural objects: {bcolors.BOLD}{location}{bcolors.ENDC}\n')


# Ignoring warnings
warnings.filterwarnings('ignore')

# Okay here we are connecting to vcenter 
def vsphere_connect(host, user, pwd):
    connection_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    connection_context.verify_mode = ssl.CERT_NONE
    try:
        print(f"Connecting to {bcolors.BOLD}{host}{bcolors.ENDC} as {bcolors.BOLD}{user}{bcolors.ENDC}")
        connection = SmartConnect(
            host=host, user=user, pwd=pwd, sslContext=connection_context)
    except Exception as err:
        print(f'{bcolors.FAIL}Error in vsphere_connect function: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}Congrats we are in...{bcolors.ENDC}')
        content = connection.content
        # print(dir(content))
        return content

# Flat list from list of lists
def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

# Save json object to file
def save(object, path, filename):

    with open(f'{path}/{filename}.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump(object, outfile, allow_unicode=True, encoding='utf-8', indent=4, default_flow_style=False, sort_keys=False, Dumper=IndentDumper, explicit_end=False, explicit_start=False)


# Method that populates objects of type vimtype
def get_all_objs(content, vimtype, folder=None):
    obj = []
    if folder == None:
        folder = content.rootFolder
    container = content.viewManager.CreateContainerView(
        folder, vimtype, True)
    for managed_object_ref in container.view:
        obj.append(managed_object_ref)
    return obj

# Getting objects
# getAllDatastore = get_all_objs(content, [vim.Datastore])

# Iterating each Datacenter object and exporting them all
def get_datacenters(content):
    getAllDCs = get_all_objs(content, [vim.Datacenter])
    print(f"\n\n{bcolors.OKBLUE}Datacenters ##################################### {len(getAllDCs)}{bcolors.ENDC}")
    alldcs_json = {"seaf.ta.reverse.vmwareonprem.vdcs":{}}
    alldcs_list = []
    for dc in getAllDCs:
        try:
            json_dc = json.loads(json.dumps(dc, cls=VmomiSupport.VmomiJSONEncoder))
            alldcs_list.append(json_dc)
        except:
            print(f"{bcolors.WARNING}Error reading props of {dc.get('name')}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_dc.get('name')}{bcolors.ENDC}")

        dc_id = prefix + "vdcs." +json_dc.get("_vimid")
        dc_dict = {
            "id": json_dc.get("_vimid"),
            "original_id": json_dc.get("_vimref"),
            "title": json_dc.get("name"),
            "datastores": json_dc.get("datastore"),
            "networks": [f"{prefix}network.{x.split(':')[-1]}" for x in json_dc.get("network")],
            "dc": location
        }

        alldcs_json["seaf.ta.reverse.vmwareonprem.vdcs"][f"{dc_id}"] = dc_dict

    save(alldcs_json, exportpath, "dcs")
    
    return getAllDCs

# Iterating each vm object and exporting them all
def get_vms(content, dc):
    getAllVms = get_all_objs(content, [vim.VirtualMachine], dc)
    print(f"\n\n{bcolors.OKBLUE}VMs ##################################### {len(getAllVms)}{bcolors.ENDC}")
    allvms_json = {"seaf.ta.components.server":{}}
    allvms_list = []
    for vm in getAllVms:
        try:
            json_vm = json.loads(json.dumps(vm, cls=VmomiSupport.VmomiJSONEncoder))
            allvms_list.append(json_vm)
        except:
            print(f"{bcolors.WARNING}Error reading props of {vm.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_vm.get('name')}{bcolors.ENDC}")
        
        vm_id = prefix + "server." + json_vm.get("_vimid")
        dc_id = prefix + "vdcs." +  dc._moId
        vapp_id = [f"{prefix}vapps.{x.split(':')[-1]}" if not(x in {None, "", "null"}) else '' for x in json_vm.get("parentVApp", "") or []]
        yaml_structure = {
            'id': json_vm.get("_vimid"),
            'type': 'Виртуальный',
            'title': json_vm.get("name"),
            'fqdn': json_vm.get("guest").get("hostName"),
            'description': json_vm.get("config").get("annotation"),
            'os': {
                'type': json_vm.get("config").get("guestFullName", ""),
                'bit': json_vm.get("config").get("guestId", "")
            },
            'cpu': {
                'cores': json_vm["config"]["hardware"].get("numCPU", ""),
                'frequency': "",
            },
            'ram': json_vm.get("config").get("hardware").get("memoryMB"),
            'nic_qty': len(json_vm.get("guest").get("net")),
            'subnets': [f"{prefix}network.{x.split(':')[-1]}" for x in json_vm.get("network") if not(x in {None, ""})],
            'disks': [],
            'reverse':{
                'reverse_type': 'VMwareOnprem',
                'original_id': json_vm.get("_vimref"),
                'addresses': list(flatten([x.get("ipAddress") for x in json_vm.get("guest").get("net") if x.get("connected") == True])),
                'subnet_titles': list(flatten([x.get("network") for x in json_vm.get("guest").get("net")])),
                'tags': [],
                'vapp': vapp_id,
                'vdc': dc_id,
                'vdc_title': dc.name
            }
        }
        
        # Получаем диски
        disks = []
        for disk in [x for x in json_vm.get("config").get("hardware").get("device") if x.get("_vimtype") == "vim.vm.device.VirtualDisk"]:
            disk_id = disk.get("key")
            bus = ""
            for device in json_vm.get("config").get("hardware").get("device"):
                if [str(x) == str(disk_id) for x in device.get("device", "")]:
                    bus = device
            disks.append({disk_id: {
                'device': f"{bus.get('busNumber')}/{disk.get('unitNumber')}",
                'size': int(disk.get("capacityInKB")/1024/1024)
            }})
            
        yaml_structure['disks'] = disks

        allvms_json["seaf.ta.components.server"][f"{vm_id}"] = yaml_structure

    save(allvms_json, exportpath, f"vms_{dc._moId}")

    return allvms_json


# Iterating each vapp object and exporting them all
def get_vapps(content, dc):
    getAllvApps = get_all_objs(content, [vim.VirtualApp], dc)
    print(f"\n\n{bcolors.OKBLUE}vApps ##################################### {len(getAllvApps)}{bcolors.ENDC}")
    allvapps_json = {"seaf.ta.reverse.vmwareonprem.vapps":{}}
    allvapps_list = []
    for vapp in getAllvApps:
        try:
            json_vapp = json.loads(json.dumps(vapp, cls=VmomiSupport.VmomiJSONEncoder))
            allvapps_list.append(json_vapp)
        except:
            print(f"{bcolors.WARNING}Error reading props of {vapp.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_vapp.get('name')}{bcolors.ENDC}")
        
        vapp_id = prefix + "vapps." + json_vapp.get("_vimid")
        dc_id = prefix + "vdcs." + dc._moId
        yaml_structure = {
            'id': json_vapp.get("_vimid"),
            'original_id': json_vapp.get("_vimref"),
            'title': json_vapp.get("name"),
            'description': json_vapp.get("config").get("annotation"),
            'tags': [],
            'vdc': dc_id,
            'vdc_tile': dc.name
        }

        allvapps_json["seaf.ta.reverse.vmwareonprem.vapps"][f"{vapp_id}"] = yaml_structure

    save(allvapps_json, exportpath, f"vapps_{dc._moId}")

    save(allvapps_list, exportpath, "vapps_")

    return allvapps_json

def get_networks(content, dc):
    getAllNetworks = get_all_objs(content, [vim.Network], dc)
    print(f"\n\n{bcolors.OKBLUE}Networks ##################################### {len(getAllNetworks)}{bcolors.ENDC}")
    allnetworks_json = {"seaf.ta.services.network":{}}
    allnetworks_list = []
    for network in getAllNetworks:
        try:
            json_network = json.loads(json.dumps(network, cls=VmomiSupport.VmomiJSONEncoder))
            allnetworks_list.append(json_network)
        except:
            print(f"{bcolors.WARNING}Error reading props of {network.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_network.get('name')}{bcolors.ENDC}")
        
        network_id = prefix + "network." + json_network.get("_vimid")
        dc_id = prefix + "vdcs." + dc._moId
        yaml_structure = {
            'id': json_network.get("_vimid"),
            'original_id': json_network.get("_vimref"),
            'title': json_network.get("name"),
            'description': '',
            'type': 'LAN',
            'lan_type': 'Проводная',
            'ipnetwork': '',
            'reverse':{
                'type': 'vmwarenetwork',
                'reverse_type': 'VMwareOnprem',
                'vdc': dc_id,
                'vdc_title': dc.name
            },
            'dc_id': [location]

        }

        allnetworks_json["seaf.ta.services.network"][f"{network_id}"] = yaml_structure

    save(allnetworks_json, exportpath, f"networks_{dc._moId}")

    save(allnetworks_list, exportpath, "networks")
 
    return allnetworks_json

def get_dvswitch(content, dc):
    getAllDVSwitch = get_all_objs(content, [vim.DistributedVirtualSwitch], dc)
    print(f"\n\n{bcolors.OKBLUE}DVSwitches ##################################### {len(getAllDVSwitch)}{bcolors.ENDC}")
    alldvswitches_json = {"seaf.ta.components.network":{}}
    alldvswitches_list = []
    for switch in getAllDVSwitch:
        try:
            json_switch = json.loads(json.dumps(switch, cls=VmomiSupport.VmomiJSONEncoder))
            alldvswitches_list.append(json_switch)
        except:
            print(f"{bcolors.WARNING}Error reading props of {switch.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_switch.get('name')}{bcolors.ENDC}")
        
        switch_id = prefix + "network." + json_switch.get("_vimid")
        dc_id = prefix + "vdcs." + dc._moId
        yaml_structure = {
            'id': json_switch.get("_vimid"),
            'title': json_switch.get("name"),
            'description': '',
            'realization_type': 'Виртуальный',
            'placement_type': 'Периметр',
            'subnets': '',
            'reverse':{
                'type': 'dvswitch',
                'reverse_type': 'VMwareOnprem',
                'original_id': json_switch.get("_vimref"),
                'vdc': dc_id,
                'vdc_title': dc.name
            },
            'dc': location
        }

        alldvswitches_json["seaf.ta.components.network"][f"{switch_id}"] = yaml_structure

    save(alldvswitches_json, exportpath, f"dvswitches_{dc._moId}")

    save(alldvswitches_list, exportpath, "dvswitches")
  
    return alldvswitches_json

def get_dvportgroup(content, dc):
    getAllDVPortgroup = get_all_objs(content, [vim.dvs.DistributedVirtualPortgroup], dc)
    print(f"\n\n{bcolors.OKBLUE}DVPortgroups ##################################### {len(getAllDVPortgroup)}{bcolors.ENDC}")
    alldvportgroups_json = {"seaf.ta.reverse.vmwareonprem.dvportgroups":{}}
    alldvportgroups_list = []
    for pg in getAllDVPortgroup:
        try:
            json_pg = json.loads(json.dumps(pg, cls=VmomiSupport.VmomiJSONEncoder))
            alldvportgroups_list.append(json_pg)
        except:
            print(f"{bcolors.WARNING}Error reading props of {pg.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{json_pg.get('name')}{bcolors.ENDC}")
        # Getting VLAN
        vlan_info = pg.config.defaultPortConfig.vlan
        vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec
        if isinstance(vlan_info, vlan_spec):
            vlanlist = []
            for item in vlan_info.vlanId:
                if item.start == item.end:
                    vlanlist.append(str(item.start))
                else:
                    vlanlist.append(str(item.start)+' - '+str(item.end))
            vlan_id = vlanlist
        else:
            vlan_id = [str(vlan_info.vlanId)]

        id = prefix + "dvportgroups." + json_pg.get("_vimid")
        dc_id = prefix + "vdc." + dc._moId
        yaml_structure = {
            'id': json_pg.get("_vimid"),
            'original_id': json_pg.get("_vimref"),
            'title': json_pg.get("name"),
            'description': '',
            'subnets': '',
            'dvswitch': prefix + "dvswitch." + json_pg.get("config").get("distributedVirtualSwitch").split(":")[-1],
            'vlan': vlan_id,
            'vdc': dc_id,
            'vdc_title': dc.name
        }

        alldvportgroups_json["seaf.ta.reverse.vmwareonprem.dvportgroups"][f"{id}"] = yaml_structure

    save(alldvportgroups_json, exportpath, f"dvportgroups_{dc._moId}")

    save(alldvportgroups_list, exportpath, "dvportgroups")
  
    return alldvportgroups_json

def get_hosts(content, dc):
    getAllHosts = get_all_objs(content, [vim.HostSystem], dc)
    print(f"\n\n{bcolors.OKBLUE}Hosts ##################################### {len(getAllHosts)}{bcolors.ENDC}")
    allhosts_json = {"seaf.ta.reverse.vmwareonprem.hosts":{}}
    allhosts_list = []
    for vchost in getAllHosts:
        try:
            json_config = json.loads(json.dumps(vchost.config, cls=VmomiSupport.VmomiJSONEncoder))
            allhosts_list.append(json_config)
        except:
            print(f"{bcolors.WARNING}Error reading props of {vchost.name}{bcolors.ENDC}")
            print(Exception)
        else:
            print(f"Successfully got {bcolors.OKGREEN}{vchost.name}{bcolors.ENDC}")
        
        id = prefix + 'hosts.' + vchost._moId
        original_id = vchost.__class__.__name__ + vchost._moId
        dc_id = prefix + 'vdcs.' + dc._moId
        yaml_structure = {
            'id': vchost._moId,
            'original_id': original_id,
            'title': vchost.name,
            'description': '',
            'product': {
                "name": json_config.get("product", "").get("name", ""),
                "version": json_config.get("product", "").get("version", ""),
                "build": json_config.get("product", "").get("build", ""),
                "fullname": json_config.get("product", "").get("fullname", "")
            },
            'network': {},
            'vdc': dc_id,
            'vdc_title': dc.name,
            'dc': location
        }


        def get_hostnetwork(host_config):
            # Physical Nics
            host_pnics = []
            for pnic in host_config.get("network","").get("pnic",""):
                pnic_info = dict()
                pnic_info.update(
                    {
                        pnic.get("key"): {
                            'device': pnic.get("device", ""), 
                            'driver': pnic.get("driver",""), 
                            'mac': pnic.get("mac","")
                        }
                    }
                )
                host_pnics.append(pnic_info)
            # Virtual Nics
            host_vnics = []
            for vnic in host_config.get("network","").get("vnic",""):
                vnic_info = dict()
                vnic_info.update(
                    {
                        vnic.get("key"): {
                            'device': vnic.get("device",""), 
                            'portgroup': vnic.get("portgroup",""),
                            'port': vnic.get("port",""),
                            'dhcp': vnic.get("spec", "").get("ip","").get("dhcp",""), 
                            'ipAddress': vnic.get("spec", "").get("ip","").get("ipAddress",""),
                            'subnetMask': vnic.get("spec", "").get("ip","").get("subnetMask",""),
                            'mac': vnic.get("spec","").get("mac",""), 
                            'mtu': vnic.get("spec","").get("mtu","")
                        }
                    }
                )
                host_vnics.append(vnic_info)
            # Virtual Switches
            host_vswitches = []
            for vswitch in host_config.get("network","").get("vswitch",""):
                vswitch_info = dict()
                vswitch_pnics = []
                vswitch_portgroups = []
                for pnic in vswitch.get("pnic"):
                    vswitch_pnics.append(pnic)
                for pg in vswitch.get("portgroup"):
                    vswitch_portgroups.append(pg)
                vswitch_info.update(
                    {
                        vswitch.get("key", ""): {
                            'name': vswitch.get("name"), 
                            'pnics': vswitch_pnics,
                            'portgroups': vswitch_portgroups, 
                            'mtu': vswitch.get("mtu","")
                        }
                    }
                )
                host_vswitches.append(vswitch_info)
            # Port Groups
            host_portgroups = []
            for portgroup in host_config.get("network","").get("portgroup",""):
                portgroup_info = dict()
                nicteamingplc = ""
                if 'nicTeaming' in portgroup.get("spec","").get("policy",""):
                    # print(portgroup.get("spec","").get("policy",""))
                    if portgroup.get("spec","").get("policy","").get("nicTeaming","") != None:
                        nicteamingplc = portgroup.get("spec","").get("policy","").get("nicTeaming","").get("policy","")
                else:
                    nicteamingplc = None

                if portgroup.get("spec","").get("policy","").get("security","") != None:
                    securitypolicy = portgroup.get("spec","").get("policy","").get("security","")
                else:
                    securitypolicy = dict()
                portgroup_info.update(
                    {
                        portgroup.get("key", ""): {
                            'name': portgroup.get("spec","").get("name",""), 
                            'vlanId': portgroup.get("spec","").get("vlanId",""),
                            'vswitchName': portgroup.get("spec","").get("vswitchName",""),
                            'vswitch_id': portgroup.get("vswitch",""),
                            'nicTeamingPolicy': nicteamingplc,
                            'allowPromiscuous': securitypolicy.get("allowPromiscuous",""),
                            'macChanges': securitypolicy.get("macChanges",""),
                            'forgedTransmits': securitypolicy.get("forgedTransmits","")
                        }
                    }
                )
                host_portgroups.append(portgroup_info)
            result = {"pnics": host_pnics, "vnics": host_vnics, "vswitches": host_vswitches, "pgs": host_portgroups}
            return result
        network = get_hostnetwork(json_config)
        yaml_structure["network"] = network
        allhosts_json["seaf.ta.reverse.vmwareonprem.hosts"][f"{id}"] = yaml_structure

    save(allhosts_json, exportpath, f"hosts_{dc._moId}")

    save(allhosts_list, exportpath, "hosts")
  
    return allhosts_json

content = vsphere_connect(host, user, pwd)
datacenters = get_datacenters(content=content)

for dc in datacenters:
    print(f"\n\n{bcolors.HEADER} Receiving data for datacenter: {dc.name}{bcolors.ENDC}")
    get_vms(content, dc)
    get_vapps(content, dc)
    get_networks(content, dc)
    get_dvswitch(content, dc)
    get_dvportgroup(content, dc)
    get_hosts(content, dc)
