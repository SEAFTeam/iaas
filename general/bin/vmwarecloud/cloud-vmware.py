import requests
import os
import json
import yaml
import lxml.etree as ET
import re
import math
import configparser
import sys

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

# Reading config file
script_path = os.path.dirname(__file__)
config_file = 'configuration copy.conf'
configpath = script_path + '/' + config_file
config = configparser.ConfigParser()
config.read(configpath)

# Setting Connection properties
site = config['connection']['host']
tenant = config['connection']['tenant']
dc = config['params']['DC']

# Setting Access or Refresh Token
if config.has_option('connection', 'access_token'):
    access_token = {'access_token': config['connection']['access_token']} if config['connection']['access_token'] not in [None, ''] else None
if config.has_option('connection', 'refresh_token'):
    refresh_token = config['connection']['refresh_token']

# Setting prefix
prefix = ''
if config.has_option('params', 'root'):
    prefix = (config['params']['root'] + '.') if config['params']['root'] not in (None, '') else ''
if config.has_option('params', 'domain'):
    prefix = (prefix + config['params']['domain'] + '.') if config['params']['domain'] not in (None, '') else ''
print(f'\n{bcolors.HEADER}Setting prefix for architectural objects:{bcolors.ENDC} {bcolors.BOLD}{prefix}{bcolors.ENDC}')

# Setting export path
exportpath = config['params'].get('exportpath', script_path)

# Что выгружаем
orgs_export = True
export_vdc = True
vm = True
vapp = True
export_vappnet = True
export_egw = True
export_nat = True
export_fw = True
export_orgnetwork = True
export_vdcgroups = True

# Конец блока с выбором объектов для выгрузки

# Конфигурация экспорта в YAML
class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

# Save json object to file
def save(object, path, filename):
    with open(f'{path}/{filename}.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump(object, outfile, allow_unicode=True, encoding='utf-8', indent=4, default_flow_style=False, sort_keys=False, Dumper=IndentDumper, explicit_end=False, explicit_start=False)

# Вычисляем адрес сети
def get_cidr(*args):
    addr = args[0] if args[0] != '' else "0.0.0.0"
    mask = args[1] if args[1] != '' else "0.0.0.0"

    addr = [int(x) for x in addr.split(".")]
    mask = [int(x) for x in mask.split(".")]
    cidr = sum((bin(x).count('1') for x in mask))

    netw = [addr[i] & mask[i] for i in range(4)]

    result = "{0}/{1}".format(('.'.join(map(str, netw))), cidr)
    return result


# Получаем версию API
def get_api_versions(**kwarg):
    # Определение URL аутентификации
    site = kwarg['site']
    url_ver = f'https://{site}/api/versions'
    res = requests.get(url_ver)
    res_xml = res.text
    parser = ET.XMLParser(ns_clean=True)
    root = ET.fromstring(bytes(res_xml, encoding='utf-8'), parser)

    # Creating namespace for find() and findall()
    ns = '{' + root.nsmap.pop(None) + '}'

    # Choosing latest version
    current_ver = float(0)
    login_url = ''
    for item in root.findall(f'{ns}VersionInfo'):
        if item.get('deprecated') == 'false':
            item_ver = item.findall(f'{ns}Version')[0].text
            if current_ver < float(item_ver):
                current_ver = float(item_ver)
                login_url = item.findall(f'{ns}LoginUrl')[0].text

    result = {'version': current_ver, 'url': login_url}
    return result

def get_cloud_enterprise_auth(**kwarg):
    site = kwarg['site']
    tenant = kwarg['tenant']
    token = kwarg['token']
    url = f'https://{site}/oauth/tenant/{tenant}/token'
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '71'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token
    }

    result = requests.post(url, headers=header, data=data)
    return result

def get_cloud_enterprise_org_objects(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    header = {
        'Accept': f'application/*;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }

    result = requests.get(url, headers=header)
    return result

def get_cloud_enterprise_vdcs(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    if 'partial' in kwarg:
        vdcs = kwarg['vdcs']
    else:
        vdcs = {'vdcs': []}
    header = {
        'Accept': f'application/*+json;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }
    req = requests.get(url, headers=header)
    return req

def get_cloud_enterprise_req(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    header = {
        'Accept': f'application/*+json;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }
    req = requests.get(url, headers=header)
    return req

def convert_cidr_to_netmask(cidr):
  cidr = int(cidr)
  mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
  return (str( (0xff000000 & mask) >> 24)   + '.' +
          str( (0x00ff0000 & mask) >> 16)   + '.' +
          str( (0x0000ff00 & mask) >> 8)    + '.' +
          str( (0x000000ff & mask)))

def get_cloudapi(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    header = {
        'Accept': f'application/json;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }
    req = requests.get(url, headers=header)
    return req

def get_pages(pagecount, query, api_init):
    result = []
    for page in range(2, pagecount + 1):
        query = query + f'&page={page}'
        try:
            r = get_cloudapi(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(f'\n{bcolors.FAIL}Could not receive page{bcolors.ENDC} {bcolors.BOLD}{page}{bcolors.ENDC}{bcolors.FAIL} at {bcolors.ENDC}{bcolors.BOLD}{query}{bcolors.ENDC}: {err.strerror}')
        else:
            print(f'{bcolors.OKGREEN}Successfully received page{bcolors.ENDC} {bcolors.BOLD}{page}{bcolors.ENDC} {bcolors.OKGREEN}at{bcolors.ENDC} {bcolors.BOLD}{query}{bcolors.ENDC}')
            for item in r_json.get('values',''):
                result.append(item)
    return result

def get_pages_oldapi(pagecount, query, api_init):
    result = []
    for page in range(2, pagecount + 1):
        query = query + f'&page={page}'
        try:
            r = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(f'\n{bcolors.FAIL}Could not receive page{bcolors.ENDC} {bcolors.BOLD}{page}{bcolors.ENDC}{bcolors.FAIL} at {bcolors.ENDC}{bcolors.BOLD}{query}{bcolors.ENDC}: {err.strerror}')
        else:
            print(f'{bcolors.OKGREEN}Successfully received page{bcolors.ENDC} {bcolors.BOLD}{page}{bcolors.ENDC} {bcolors.OKGREEN}at{bcolors.ENDC} {bcolors.BOLD}{query}{bcolors.ENDC}')
            for item in r_json.get('record',''):
                result.append(item)
    return result

def get_orgs(site, access_token, api_init, prefix, dc):
    # Receiving Organizations
    print(f'{bcolors.HEADER}Organizations *************************************** {bcolors.ENDC}')
    orgs = []
    orgs_list = {'seaf.ta.reverse.vmwarecloud.orgs': {}}

    query = f'https://{site}/cloudapi/1.0.0/orgs?pageSize=100'
    try:
        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get Orgs: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.strerror)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')

    # Putting first batch to the list
    for item in r_json.get('values',''):
        orgs.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount','') > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
        items = get_pages(r_json.get('pageCount',''), query, api_init)
        for item in items:
            orgs.append(item)
    
    for org in orgs:
        org_urn_id = org.get('id','')
        org_id = org_urn_id.split(":")[-1]
        org_seaf_id = prefix + 'orgs.' + org_id

        print(f'{org.get("name")}\t\t{org_id}\t\t{org_urn_id}')

        yaml_structure = {
            'id': org_id,
            'original_id': org_urn_id,
            'title': org.get('name',''),
            'description': org.get('description', ''),
            'dc': dc
        }

        orgs_list['seaf.ta.reverse.vmwarecloud.orgs'][f'{org_seaf_id}'] = yaml_structure

    save(orgs_list, exportpath, "enterprise_orgs")

def get_vdcgroups(site, access_token, api_init, prefix, dc):
    # Receiving VDC Groups
    print(f'{bcolors.HEADER}VDC Groups *************************************** {bcolors.ENDC}')

    vdcgroups = []
    vdcgroups_list = {'seaf.ta.reverse.vmwarecloud.vdcgroups': {}}
    
    query = f'https://{site}/cloudapi/1.0.0/vdcGroups?pageSize=100'
    try:
        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get VDCGroups: {err.strerror}{bcolors.ENDC}\n')
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')

    # Putting first batch to the list
    for item in r_json.get('values',''):
        vdcgroups.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount','') > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
        items = get_pages(r_json.get('pageCount',''), query, api_init)
        for item in items:
            vdcgroups.append(item)

    for vdcgroup in vdcgroups:
        vdcgroup_urn_id = vdcgroup.get('id','')
        vdcgroup_id = vdcgroup_urn_id.split(':')[-1]
        vdcgroup_seaf_id = prefix + 'vdcgroups.' + vdcgroup_id

        print(f'{vdcgroup.get("name")}\t\t{vdcgroup_id}\t\t{vdcgroup_urn_id}')

        # Getting all corresponding networks
        networks = []
        net_query = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks?filter=ownerRef.id=={vdcgroup_urn_id}&pageSize=100'
        try:
            net_request = get_cloudapi(url=net_query, bearer=access_token, version=api_init)
            net_json = json.loads(net_request.text)
        except Exception as err:
            print(f'{bcolors.FAIL}Could not get VDCGroups Networks: {err.strerror}{bcolors.ENDC}\n')

        for network in net_json.get('values',''):
            network_urn_id = network.get('id','')
            network_id = prefix + 'orgnets.' + network_urn_id.split(':')[-1]
            networks.append(
                {
                    'id': network_id, 
                    'title': network.get('name', '')
                }
            )

        # Getting all corresponding vdcs
        vdcs = []
        for orgvdc in vdcgroup.get('participatingOrgVdcs',''):
            orgvdc_seaf_id = prefix + 'vdcs.' + orgvdc.get('vdcRef','').get('id','').split(':')[-1]
            org_seaf_id = prefix + 'orgs.' + orgvdc.get('orgRef','').get('id','').split(':')[-1]
            vdcs.append(
                {
                    'id': orgvdc_seaf_id,
                    'title': orgvdc.get('vdcRef','').get('name'),
                    'org': org_seaf_id,
                    'org_title': orgvdc.get('orgRef','').get('name')
                }
            )
        
        org_id = prefix + 'orgs.' + vdcgroup.get('orgId','').split(":")[-1]
        netpool_id = prefix + 'netpools.' + vdcgroup.get('networkPoolId','').split(":")[-1]

        yaml_structure = {
            'id': vdcgroup_id,
            'original_id': vdcgroup_urn_id,
            'title': vdcgroup.get('name',''),
            'networkprovidertype': vdcgroup.get('networkProviderType',''),
            'type': vdcgroup.get('type',''),
            'networkpool': netpool_id,
            'localegress': vdcgroup.get('localEgress',''),
            'dfwenabled': vdcgroup.get('dfwEnabled',''),
            'org': org_id,
            'networks': [],
            'vdcs': [],
            'dc': dc
        }
        yaml_structure['networks'] = networks
        yaml_structure['vdcs'] = vdcs

        vdcgroups_list['seaf.ta.reverse.vmwarecloud.vdcgroups'][f'{vdcgroup_seaf_id}'] = yaml_structure

    save(vdcgroups_list, exportpath, "enterprise_vdcgroups")

def get_vdcs(site, access_token, api_init, prefix, dc):
    # Receiving VDCs
    print(f'{bcolors.HEADER}VDCs *************************************** {bcolors.ENDC}')
    vdcs = []
    vdcs_list = {'seaf.ta.reverse.vmwarecloud.vdcs': {}}

    query = f'https://{site}/cloudapi/1.0.0/vdcs?pageSize=100'
    try:
        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get VDCs: {err.strerror}{bcolors.ENDC}\n')
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')

    # Putting first batch to the list
    for item in r_json.get('values',''):
        vdcs.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount','') > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
        items = get_pages(r_json.get('pageCount',''), query, api_init)
        for item in items:
            vdcs.append(item)

    for vdc in vdcs:
        vdc_urn_id = vdc.get('id','')
        vdc_id = vdc_urn_id.split(':')[-1]
        vdc_seaf_id = prefix + 'vdcs.' + vdc_id

        print(f'{vdc.get("name")}\t\t{vdc_id}\t\t{vdc_urn_id}')

        networks = []
        net_query = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks?filter=orgVdc.id=={vdc_urn_id}&pageSize=100'
        try:
            net_request = get_cloudapi(url=net_query, bearer=access_token, version=api_init)
            net_json = json.loads(net_request.text)
        except Exception as err:
            print(f'{bcolors.FAIL}Could not get VDC Networks: {err.strerror}{bcolors.ENDC}\n')


        for network in net_json.get('values',''):
            network_urn_id = network.get('id','')
            network_id = prefix + 'orgnets.' + network_urn_id.split(':')[-1]
            networks.append(
                {
                    'id': network_id, 
                    'title': network.get('name', '')
                }
            )

        org_id = prefix + 'orgs.' + vdc.get('org','').get('id','')

        yaml_structure = {
            'id': vdc_id,
            'original_id': vdc_urn_id,
            'title': vdc.get('name',''),
            'allocationtype': vdc.get('allocationType',''),
            'org_title': vdc.get('org','').get('name',''),
            'org': org_id,
            'availablenetworks': [],
            'dc': dc
        }
        yaml_structure['availablenetworks'] = networks

        vdcs_list['seaf.ta.reverse.vmwarecloud.vdcs'][f'{vdc_seaf_id}'] = yaml_structure

    save(vdcs_list, exportpath, "enterprise_vdcs")

def get_orgnetworks(site, access_token, api_init, prefix, dc):
    # Receiving OrgNetworks 
    print(f'{bcolors.HEADER}Org Networks *************************************** {bcolors.ENDC}')
    orgnetworks = []
    orgnetworks_list = {'seaf.ta.services.network': {}}

    query = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks?pageSize=100'
    try:
        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get OrgNetworks: {err.strerror}{bcolors.ENDC}\n')
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')
        r_json = json.loads(r.text)

    # Putting first batch to the list
    for item in r_json.get('values',''):
        orgnetworks.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount','') > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
        items = get_pages(r_json.get('pageCount',''), query, api_init)
        for item in items:
            orgnetworks.append(item)

    for orgnet in orgnetworks:
        orgnet_urn_id = orgnet.get('id','')
        orgnet_id = orgnet_urn_id.split(':')[-1]
        orgnet_seaf_id = prefix + 'orgnets.' + orgnet_id
        
        print(f'{orgnet.get("name")}\t\t{orgnet_id}\t\t{orgnet_urn_id}')

        # Getting all DNS server address in subnets
        dns = []
        for item in orgnet.get('subnets','').get('values',''):
            dns1 = item.get('dnsServer1','') 
            dns2 = item.get('dnsServer2','') 
            if dns1 not in [None, '', dns]:
                dns.append(dns1)
            if dns2 not in [None, '', dns]:
                dns.append(dns2)
    
        if orgnet.get('orgVdc','') not in [None, '']:
            vdc_name = orgnet.get('orgVdc','').get('name','')
            vdc_id = prefix + 'vdcs.' + orgnet.get('orgVdc','').get('id','').split(':')[-1]
        else:
            vdc_name = None
            vdc_id = None
        
        if orgnet.get('ownerRef','') not in [None, '']:
            if re.match(r'.*:vdcGroup:.*', orgnet.get('ownerRef').get('id')):
                vdcgroup_id = prefix + 'vdcgroups.' + orgnet.get('ownerRef','').get('id','').split(':')[-1]
                vdcgroup_name = orgnet.get('ownerRef','').get('name','')
            else:
                vdcgroup_name = None
                vdcgroup_id = None
        else:
            vdcgroup_name = None
            vdcgroup_id = None

        org_id = prefix + 'orgs.' + orgnet.get('orgRef','').get('id','').split(":")[-1]
        parentnetwork_id = prefix + 'orgnets.' + orgnet.get('parentNetworkId','') if orgnet.get('parentNetworkId','') not in [None, ''] else None

        if orgnet.get('connection','') not in ['', None]:
            if orgnet.get('connection').get('connected') not in ['', None]:
                connected = orgnet.get('connection').get('connected')
            else:
                connected = False
        else: connected = False

        yaml_structure = {
            'id': orgnet_id,
            'title': orgnet.get('name',''),
            'description': orgnet.get('description',''),
            'type': 'Проводная',
            'lan_type': 'LAN',
            'az':'',
            'segment':'',
            'vlan':'',
            'ipnetwork':'',
            'purpose': '',
            'network_appliance_id': '',
            'reverse': {
                'reverse_type': 'VMwareCloud',
                'original_id': orgnet_urn_id,
                'type': 'orgNetwork',
                'netmask': '',
                'gateway': '',
                'parentnetwork': parentnetwork_id,
                'backingnetworktype': orgnet.get('backingNetworkType',''),
                'networkpool': '',
                'networkpool_title': '',
                'isdefaultnetwork': orgnet.get('isDefaultNetwork',''),
                'shared': orgnet.get('shared',''),
                'status': orgnet.get('status',''),
                'org': org_id,
                'vdc': vdc_id,
                'vdc_title':  vdc_name,
                'vdcgroup': vdcgroup_id,
                'vdcgroup_title': vdcgroup_name,
                'connected': connected,
                'dns': dns,
                'fencemode': orgnet.get('networkType',''),
                'ipscopes': []
            },
            'dc': dc
        }

        # Getting All Networks
        ipscope = []
        for scope in orgnet.get('subnets','').get('values',''):
            if scope.get('ipRanges','').get('values','') != None:
                for item in scope.get('ipRanges','').get('values',''):
                    ipranges = map(lambda w: {'startaddress': w['startAddress'],
                                            'endaddress': w['endAddress']}, scope['ipRanges']['values'])
                netmask = convert_cidr_to_netmask(scope.get('prefixLength',''))
                yaml_scope = {
                    'gateway': scope.get('gateway',''),
                    'netmask': netmask,
                    'subnetprefixlength': scope.get('prefixLength',''),
                    'ipranges': [x for x in ipranges]
                }
                ipscope.append(yaml_scope)
        yaml_structure['reverse']['ipscopes'] = ipscope
        netmask = [x.get('netmask','') for x in ipscope if x.get('netmask') not in [None,'']]
        gateway = [x.get('gateway','') for x in ipscope if x.get('gateway') not in [None,'']]
        yaml_structure['reverse']['netmask'] = netmask[0] if netmask not in [None, '', []] else ''
        yaml_structure['reverse']['gateway'] = gateway[0] if gateway not in [None, '', []] else ''
        ipnetwork = get_cidr(yaml_structure['reverse']['gateway'], yaml_structure['reverse']['netmask'])
        yaml_structure['ipnetwork'] = ipnetwork

        orgnetworks_list['seaf.ta.services.network'][orgnet_seaf_id] = yaml_structure

    save(orgnetworks_list, exportpath, "enterprise_orgnets")

def get_edgegw(site, access_token, api_init, prefix, dc):
    # Receiving Edge Gateways 
    print(f'{bcolors.HEADER}Edge Gateways ***************************************{bcolors.ENDC}')
    egws = []
    egw_list = {'seaf.ta.components.network': {}}

    query = f'https://{site}/cloudapi/1.0.0/edgeGateways?pageSize=100'
    try:
        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get Edge Gateways: {err.strerror}{bcolors.ENDC}\n')
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')
        r_json = json.loads(r.text)

    # Putting first batch to the list
    for item in r_json.get('values',''):
        egws.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount','') > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
        items = get_pages(r_json.get('pageCount',''), query, api_init)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_urn_id = gw.get('id','')
        gw_id = gw_urn_id.split(':')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id

        print(f'{gw.get("name")}\t\t{gw_id}\t\t{gw_urn_id}')

        # Getting networks
        print(f'\t{bcolors.HEADER}Edge Gateway Networks *************************************** {bcolors.ENDC}')
        networks = []
        nquery = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks?filter=connection.routerRef.id=={gw_urn_id}&pageSize=100'
        try:
            r = get_cloudapi(url=nquery, bearer=access_token, version=api_init)
        except Exception as err: 
            print(f'\t{bcolors.FAIL}Could not get Edge Gateway Networks: {err.strerror}{bcolors.ENDC}\n')
        else:
            r_network = json.loads(r.text)

            # Putting first batch to the list
            for item in r_network.get('values',''):
                networks.append(item)

            # Working with pages if there are more than one
            if r_network.get('pageCount','') > 1:
                print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
                items = get_pages(r_network.get('pageCount',''), nquery, api_init)
                for item in items:
                    networks.append(item)
            
            # Appending networks and uplinks to interfaces
            interfaces = []
            #uplinks
            for item in gw.get('edgeGatewayUplinks',''):
                uplink_ref_id = item.get('uplinkId','')
                uplink_id = uplink_ref_id.split(':')[-1]
                uplink_seaf_id = prefix + 'orgnets.' + uplink_id

                yaml_if = {
                    'title': item.get('uplinkName',''),
                    'network': uplink_seaf_id,
                    'iftype': 'uplink',
                    'usefordefaultroute': 'No idea where to get from new API',
                    'connected': item.get('connected',''),
                    'subnetparticipation': []
                }

                subnets = []
                for subnet in [x for x in item.get('subnets','').get('values','') if x.get('primaryIp','') not in [None, '']]:
                    netmask = convert_cidr_to_netmask(subnet.get('prefixLength',''))
                    yaml_subn = {
                        'gateway': subnet.get('gateway',''),
                        'netmask': netmask,
                        'ipaddress': subnet.get('primaryIp'),
                        'ipranges': []
                    }

                    ipranges = []
                    if subnet.get('ipRanges').get('values','') == None: 
                        continue
                    for range in subnet.get('ipRanges').get('values',''):
                        yaml_ranges = {
                            'startaddress': range.get('startAddress',''),
                            'endaddress': range.get('endAddress','')
                        }
                        ipranges.append(yaml_ranges)
                    yaml_subn['ipranges'] = ipranges
                    subnets.append(yaml_subn)

                yaml_if['subnetparticipation'] = subnets
                interfaces.append(yaml_if)

        # Internal networks
        for item in networks:
            network_ref_id = item.get('id','')
            network_id = network_ref_id.split(':')[-1]
            network_seaf_id = prefix + 'orgnets.' + network_id

            print(f'\t\t\t{item.get("name")}\t\t{network_id}\t\t{network_ref_id}')

            if item.get('connection','') not in ['', None]:
                if item.get('connection').get('connected') not in ['', None]:
                    connected = item.get('connection').get('connected')
                else:
                    connected = False
            else: connected = False

            if item.get('isDefaultNetwork', '') not in [None,'']:
                usefordefaultroute = item.get('isDefaultNetwork')
            else: usefordefaultroute = False

            yaml_if = {
                'title': item.get('name',''),
                'network': network_seaf_id,
                'iftype': item.get('connection','').get('connectionType',''),
                'usefordefaultroute': usefordefaultroute,
                'connected': connected,
                'subnetparticipation': []
            }

            subnets = []
            for subnet in item.get('subnets','').get('values',''):
                netmask = convert_cidr_to_netmask(subnet.get('prefixLength',''))

                ipaddresses = []
                ipquery = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks/{network_ref_id}/allocatedIpAddresses'
                try:
                    r = get_cloudapi(url=ipquery, bearer=access_token, version=api_init)
                except Exception as err: 
                    print(f'{bcolors.FAIL}Could not get Network allocated IPs: {err.strerror}{bcolors.ENDC}\n')
                    ipaddress = "Not found (error)"
                else:
                    r_ip = json.loads(r.text)
                
                    # Putting first batch to the list
                    for item in r_ip.get('values',''):
                        ipaddresses.append(item)

                    # Working with pages if there are more than one
                    if r_ip.get('pageCount','') > 1:
                        print(f'Working with pages. Pages qty: {bcolors.BOLD}{r_json.get("pageCount")}{bcolors.ENDC}')
                        items = get_pages(r_ip.get('pageCount',''), ipquery, api_init)
                        for item in items:
                            ipaddresses.append(item)

                    ipaddress = next(iter([x.get('ipAddress') for x in ipaddresses if x.get('allocationType') == 'VSM_ALLOCATED']), None)

                yaml_subn = {
                    'gateway': subnet.get('gateway',''),
                    'netmask': netmask,
                    'ipaddress': ipaddress,
                    'ipranges': []
                }

                ipranges = []
                if subnet.get('ipRanges','').get('values','') not in [None, '']:
                    for range in subnet.get('ipRanges').get('values',''):
                        yaml_ranges = {
                            'startaddress': range.get('startAddress',''),
                            'endaddress': range.get('endAddress','')
                        }
                        ipranges.append(yaml_ranges)
                    yaml_subn['ipranges'] = ipranges
                    subnets.append(yaml_subn)

            yaml_if['subnetparticipation'] = subnets
            interfaces.append(yaml_if)

        if gw.get('orgVdc','') not in [None, '']:
            vdc_name = gw.get('orgVdc','').get('name','')
            vdc_id = prefix + 'vdcs.' + gw.get('orgVdc','').get('id','').split(':')[-1]
        else:
            vdc_name = None
            vdc_id = None
        
        if gw.get('ownerRef','') not in [None, '']:
            if re.match(r'.*:vdcGroup:.*', gw.get('ownerRef').get('id')):
                vdcgroup_id = prefix + 'vdcgroups.' + gw.get('ownerRef','').get('id','').split(':')[-1]
                vdcgroup_name = gw.get('ownerRef','').get('name','')
            else:
                vdcgroup_name = None
                vdcgroup_id = None
        else:
            vdcgroup_name = None
            vdcgroup_id = None

        # vdc_id = prefix + 'vdcs.' + gw.get('orgVdc').get('id', None).split(':')[-1]  if gw.get('orgVdc') not in [None, ''] else None
        # vdc_name = gw.get('orgVdc').get('name', None) if gw.get('orgVdc') not in [None, ''] else None
        # vdcgroup_id = prefix + 'vdcgroups.' + gw.get('ownerRef').get('id', None).split(':')[-1] if gw.get('ownerRef','') not in [None, ''] else None
        # vdcgroup_name = gw.get('ownerRef','').get('name', None)
        org_id = prefix + 'orgs.' + gw.get('orgRef','').get('id', None).split(':')[-1]
        yaml_structure = {
            'id': gw_id,
            'original_id': gw_urn_id,
            'title': gw.get('name'),
            'description': gw.get('description',''),
            'type': gw.get('gatewayBacking','').get('gatewayType'),
            'vdc': vdc_id,
            'vdc_title': vdc_name,
            'vdcgroup': vdcgroup_id,
            'vdcgroup_title': vdcgroup_name,
            'org': org_id,
            # 'advancedNetworkingEnabled': r_details['configuration']['advancedNetworkingEnabled'],
            # 'distributedRoutingEnabled': r_details['configuration']['distributedRoutingEnabled'],
            'gatewayinterfaces': [],
            'dc': dc
        }
        yaml_structure['gatewayinterfaces'] = interfaces

        egw_list['seaf.ta.components.network'][gw_seaf_id] = yaml_structure

    save(egw_list, exportpath, "enterprise_egws")

def get_vms(site, access_token, api_init, prefix, dc):
    # Получаем список VM
    vms = []
    vms_list = {'seaf.ta.components.server': {}}

    print(f'{bcolors.HEADER}VMs ***************************************{bcolors.ENDC}')

    # Initial request
    query = f'https://{site}/api/query?type=vm&pageSize=100'
    try:
        vms_request = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
        vms_json = json.loads(vms_request.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get vms list: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {vms_request.status_code}')


    # Putting first batch to the list
    for item in vms_json.get('record',''):
        vms.append(item)

    # Working with pages if there are more than one
    pagecount = math.ceil(vms_json.get('total') / vms_json.get('pageSize'))
    if pagecount > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{pagecount}{bcolors.ENDC}')
        items = get_pages(pagecount, query, api_init)
        for item in items:
            vms.append(item)

    # Getting vm details
    for vm in vms:

        # Не выгружаем Template
        if vm.get('isVAppTemplate') == True:
            continue

        query = vm.get('href','')
        try:
            vm_request = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
            if not vm_request.ok:
                print(f'{bcolors.FAIL}Could not get vm details: {vm_request.text}{bcolors.ENDC}\n')
                continue
            vm_json = json.loads(vm_request.text)
        except Exception as err:
            print(f'{bcolors.FAIL}Could not get vm details: {err.strerror}{bcolors.ENDC}\n')
            continue

        vm_urn_id = vm_json.get('id','')
        vm_id = vm_urn_id.split(':')[-1]
        vm_seaf_id = prefix + 'vms.' + vm_id

        print(f'{vm.get("name")}\t\t{vm_id}\t\t{vm_urn_id}')

        disks = []
        vmspec = [x for x in vm_json.get('section') if x.get('_type','') == 'VmSpecSectionType']
        disksettings = [x.get('diskSection').get('diskSettings') for x in vmspec if x.get('diskSection','') not in [None, '']]
        for disk in [x[0] for x in disksettings]:
            disk_id = disk.get('diskId','0')
            disks.append({disk_id: {
                'device': f'{disk.get("busNumber")}/{disk.get("unitNumber")}',
                'size': int(disk.get('sizeMb',1024)/1024),
                'az': '',
                'type': disk.get('storageProfile','').get('name','')
            }})

        addresses = []
        subnets = []
        subnetids = []
        computername = [x for x in vm_json['section'] if x['_type'] == 'GuestCustomizationSectionType'][0]['computerName']

        for adapter in [x for x in vm_json['section'] if x['_type'] == 'NetworkConnectionSectionType'][0]['networkConnection']:
            addresses.append(adapter['ipAddress'])

            query = f'https://{site}/api/query?type=vAppNetwork&filter=name=={adapter.get("network")};vAppName=={vm.get("containerName")}'
            try: 
                subnet_request = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
                s = json.loads(subnet_request.text)
            except Exception as err:
                print(f'{bcolors.FAIL}Could not get vm subnets: {err.strerror}{bcolors.ENDC}\n')
                continue
            else:
                if adapter['network'] not in subnets:
                    subnets.append(adapter['network'])
                if len(s['record']) > 0:
                    networkid = prefix + 'vappnets.' + s['record'][0]['href'].split('/')[-1]
                else:
                    networkid = None
                if networkid not in subnetids:
                    subnetids.append(networkid)

        vdc_id = prefix + 'vdcs.' + vm['vdc'].split('/')[-1]
        vapp_id = prefix + 'vapps.' + vm['container'].split('/')[-1].split('-', 1)[-1]

        yaml_structure = {
            'id': vm_id,
            'type': 'Виртуальный'
            'title': computername,
            'fqdn': computername,
            'description': vm_json['description'],
            'os': {
                'type': [x for x in vm_json['section'] if x['_type'] == 'OperatingSystemSectionType'][0]['description']['value'],
                'bit': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['virtualCpuType'].split('_')[-1]
            },
            'cpu': {
                'cores': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['numCpus'],
                'frequency': '',
                # 'arch': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['virtualCpuType']
            },
            'ram': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['memoryResourceMb']['configured'],
            'nic_qty': len([x for x in vm_json['section'] if x['_type'] == 'NetworkConnectionSectionType'][0]['networkConnection']),
            'subnets': [],
            'disks': [],
            'reverse': {
                'reverse_type': 'VMwareCloud'
                'original_id': vm_urn_id,
                'addresses': [],
                'subnet_titles': [],
                'tags': [],
                'vdc': vdc_id,
                'vdc_title': vm['vdcName'],
                'vapp': vapp_id,
                'tenant': ''
            }
        }

        yaml_structure['disks'] = disks
        yaml_structure['reverse']['addresses'] = addresses
        yaml_structure['subnets'] = subnetids
        yaml_structure['reverse']['subnet_titles'] = subnets

        vms_list['seaf.ta.components.server'][vm_seaf_id] = yaml_structure

    save(vms_list, exportpath, 'enterprise_vms')

def get_vapps(site, access_token, api_init, prefix, dc):
    # Получаем vApps
    vapps = []
    vapps_list = {'seaf.ta.reverse.vmwarecloud.vapps': {}}
        
    print(f'{bcolors.HEADER}VApps ***************************************{bcolors.ENDC}')

    # Initial request
    query = f'https://{site}/api/query?type=vApp&pageSize=100'
    try:
        vapps_request = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
        vapps_json = json.loads(vapps_request.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get vApps list: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {vapps_request.status_code}')
    
    # Putting first batch to the list
    for vapp in vapps_json.get('record',''):
        vapps.append(vapp)


    # Working with pages if there are more than one
    pagecount = math.ceil(vapps_json.get('total') / vapps_json.get('pageSize'))
    if pagecount > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{pagecount}{bcolors.ENDC}')
        items = get_pages(pagecount, query, api_init)
        for item in items:
            vapps.append(item)

    # Getting vapp details
    for vapp in vapps:
        query = vapp['href']
        try:
            vapp_details_req = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
            vapp_details_json = json.loads(vapp_details_req.text)
        except ExceptionGroup as err:
            print(f'{bcolors.FAIL}Could not get vapps details: {err.strerror}{bcolors.ENDC}\n')
            continue


        vapp_urn_id = vapp_details_json.get('id','')
        vapp_id = vapp_urn_id.split(':')[-1]
        vapp_seaf_id = prefix + 'vapps.' + vapp_id

        print(f'{vapp.get("name")}\t\t{vapp_id}\t\t{vapp_urn_id}')
    
        vdc_id = prefix + 'vdcs.' + vapp.get('vdc','').split('/')[-1]

        yaml_structure = {
            'id': vapp_id,
            'original_id': vapp_urn_id,
            'title': vapp.get('name',''),
            'description': vapp.get('description',''),
            'vdc': vdc_id,
            'vdc_title': vapp.get('vdcName',''),
            'dc': dc
        }
        vapps_list['seaf.ta.reverse.vmwarecloud.vapps'][vapp_seaf_id] = yaml_structure

    save(vapps_list, exportpath, 'enterprise_vapps')

def get_vappnets(site, access_token, api_init, prefix, dc):
    # Получаем vAppNets
    vappnets = []
    vappnet_list = {'seaf.ta.services.network': {}}

    print(f'{bcolors.HEADER}VApp Networks ***************************************{bcolors.ENDC}')

    # Initial request
    query = f'https://{site}/api/query?type=vAppNetwork&format=records&pageSize=100'
    try:
        vappnets_request = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
        vappnets_json = json.loads(vappnets_request.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get vAppNets list: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {vappnets_request.status_code}')

    # Putting first batch to the list
    for vappnet in vappnets_json.get('record',''):
        vappnets.append(vappnet)

    # Working with pages if there are more than one
    pagecount = math.ceil(vappnets_json.get('total') / vappnets_json.get('pageSize'))
    if pagecount > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{pagecount}{bcolors.ENDC}')
        items = get_pages(pagecount, query, api_init)
        for item in items:
            vappnets.append(item)

    # Getting vappnet details
    for vappnet in vappnets:
        query = vappnet['href']
        try:
            vappnet_details_req = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
            vappnet_details = json.loads(vappnet_details_req.text)
        except Exception as err:
            print(f'{bcolors.FAIL}Could not get vappnet details: {err.strerror}{bcolors.ENDC}\n')
            continue

        dns = []
        iter = []
        if vappnet['dns1'] is not None and vappnet['dns1'] is not None:
            iter = [vappnet['dns1'], vappnet['dns2']]
        elif vappnet['dns1'] is not None:
            iter = [vappnet['dns1']]
        elif vappnet['dns2'] is not None:
            iter = [ vappnet['dns2']]
        for item in iter:
            if re.match(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', item):
                dns.append(item)
        if 'parentNetwork' in vappnet_details['configuration']:
            if vappnet_details['configuration']['parentNetwork'] != None:
                parentnetwork_id = prefix + 'orgnets.' + vappnet_details['configuration']['parentNetwork']['id'].split(':')[-1]
            else:
                parentnetwork_id = None
        else:
            parentnetwork_id = None

        vappnet_urn_id = vappnet_details.get('id')
        vappnet_id = vappnet_urn_id.split(':')[-1]
        vappnet_seaf_id = prefix + 'vappnets.' + vappnet_id

        print(f'{vappnet.get("name")}\t\t{vappnet_id}\t\t{vappnet_urn_id}')

        vapp_id = prefix + "vapps." + vappnet['vApp'].split('/')[-1].split('-', 1)[-1]
        
        if vappnet['otherAttributes']['isLinked'] == 'true':
            islinked = True
        else: islinked = False

        yaml_structure = {
            'id': vappnet_id,
            'title': vappnet['name'],
            'type': 'Проводная',
            'lan_type': 'LAN',
            'az':'',
            'segment':'',
            'vlan':'',
            'ipnetwork':'',
            'purpose': '',
            'network_appliance_id': '',
            'reverse':{
                'reverse_type': 'VMwareCloud',
                'type': 'vAppNetwork',
                'original_id': vappnet_urn_id,
                'vapp': vapp_id,
                'gateway': vappnet['gateway'],
                'netmask': vappnet['netmask'],
                'dns': dns,
                'fencemode': vappnet_details['configuration']['fenceMode'],
                'connected': islinked,
                'parentnetwork': parentnetwork_id,
                'ipscopes': []
            },
            'dc': dc
        }

        ipscope = []
        if 'ipScopes' in vappnet_details['configuration']:
            for scope in vappnet_details['configuration']['ipScopes']['ipScope']:
                if scope['ipRanges'] != None:
                    ipranges = map(lambda w: {'startaddress': w['startAddress'],
                                            'endaddress': w['endAddress']}, scope['ipRanges']['ipRange'])
                    yaml_scope = {
                        'gateway': scope.get('gateway',''),
                        'netmask': scope.get('netmask',''),
                        'subnetprefixlength': scope.get('subnetPrefixLength',''),
                        'ipranges': [x for x in ipranges]
                    }
                    ipscope.append(yaml_scope)
        yaml_structure['reverse']['ipscopes'] = ipscope

        vappnet_list['seaf.ta.services.network'][vappnet_seaf_id] = yaml_structure

    save(vappnet_list, exportpath, 'enterprise_vappnets')

def get_edgenat(site, access_token, api_init, prefix, dc):
    # Получаем edgeGWNat
    egws = []
    nat_list = {'seaf.ta.reverse.vmwarecloud.egws_nat': {}}

    print(f'{bcolors.HEADER}Edge Gateway NAT Rules ***************************************{bcolors.ENDC}')

    # Initial request
    query = f'https://{site}/api/query?type=edgeGateway&format=records&pageSize=100'
    try:
        r = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get Edge Gateways list: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')

    # Putting first batch to the list
    for item in r_json.get('record',''):
        egws.append(item)
    
    # Working with pages if there are more than one
    pagecount = math.ceil(r_json.get('total') / r_json.get('pageSize'))
    if pagecount > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{pagecount}{bcolors.ENDC}')
        items = get_pages(pagecount, query, api_init)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_id = gw['href'].split('/')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id
        gw_urn_id = 'urn:vcloud:gateway:' + gw_id

        print(f'{bcolors.BOLD}{gw.get("name")}{bcolors.ENDC}')

        # Получаем данные о NAT правилах
        query = f'https://{site}/cloudapi/1.0.0/edgeGateways/{gw_urn_id}/nat/rules'
        try:
            r = get_cloudapi(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(f'\t{bcolors.FAIL}Could not get Edge Gateway {gw.get("name")} NAT Rules: {err.strerror}{bcolors.ENDC}\n')
            continue

        for value in r_json['values']:
            id = value['id']
            seaf_id = prefix + 'egws_nat.' + id
            name = value.get('name','')

            print(f'\t{name}\t\t{id}')

            yaml_structure = {
                'id': id,
                'gw': gw_seaf_id,
                'title': name,
                'description': value.get('description',''),
                'enabled': value.get('enabled',''),
                'type': value.get('type',''),
                'rule_type': value.get('ruleType',''),
                'external_address': value.get('externalAddresses',''),
                'internal_address': value.get('internalAddresses',''),
                'system_rule': value.get('systemRule',''),
                'snat_dst_address': value.get('snatDestinationAddresses',''),
                'dnat_ext_port': value.get('dnatExternalPort',''),
                'fw_match': value.get('firewallMatch',''),
                'dc': dc
            }
            nat_list['seaf.ta.reverse.vmwarecloud.egws_nat'][seaf_id] = yaml_structure

    save(nat_list, exportpath, 'enterprise_egws_nat')

def get_edgefw(site, access_token, api_init, prefix, dc):
    egws = []
    fw_list = {'seaf.ta.reverse.vmwarecloud.egws_fw': {}}

    print(f'{bcolors.HEADER}Edge Gateway FW Rules ***************************************{bcolors.ENDC}')

    query = f'https://{site}/api/query?type=edgeGateway&format=records&pageSize=100'
    try:
        r = get_cloud_enterprise_req(url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get Edge Gateways list: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}First request status:{bcolors.ENDC} {r.status_code}')

    # Putting first batch to the list
    for item in r_json.get('record',''):
        egws.append(item)
    
    # Working with pages if there are more than one
    pagecount = math.ceil(r_json.get('total') / r_json.get('pageSize'))
    if pagecount > 1:
        print(f'Working with pages. Pages qty: {bcolors.BOLD}{pagecount}{bcolors.ENDC}')
        items = get_pages(pagecount, query, api_init)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_id = gw['href'].split('/')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id
        gw_urn_id = 'urn:vcloud:gateway:' + gw_id

        print(f'{bcolors.BOLD}{gw.get("name")}{bcolors.ENDC}')

        # Получаем данные о FW правилах
        query = f'https://{site}/cloudapi/1.0.0/edgeGateways/{gw_urn_id}/firewall/rules'
        try:
            r = get_cloudapi(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(f'\t{bcolors.FAIL}Could not get Edge Gateway {gw.get("name")} FW Rules: {err.strerror}{bcolors.ENDC}\n')
            continue
        
        if 'userDefinedRules' not in r_json or r_json['userDefinedRules'] is None:
            continue
        for rule in r_json.get('userDefinedRules'):
            id = rule['id']
            seaf_id = prefix + 'egws_fw.' + id
            name = rule.get('name','')

            print(f'\t{name}\t\t{id}')

            yaml_structure = {
                'id': id,
                'gw': gw_seaf_id,
                'title': name,
                'description': rule.get('description',''),
                'enabled': rule.get('enabled'),
                'sourceFirewallGroups': rule.get('sourceFirewallGroups',''),
                'destinationFirewallGroups': rule.get('destinationFirewallGroups',''),
                'ip_protocol': rule.get('ipProtocol',''),
                'action': rule.get('action',''),
                'action_value': rule.get('actionValue',''),
                'direction': rule.get('direction',''),
                'port_profiles': [],
                'dc': dc
            }

            src_fw_groups = {}
            if rule['sourceFirewallGroups'] != None:
                for group in rule['sourceFirewallGroups']:
                    fw_group_id = group['id']
                    query = f'https://{site}/cloudapi/1.0.0/firewallGroups/{fw_group_id}'
                    try:
                        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(f'\t{bcolors.FAIL}Could not get Edge Gateway {gw.get("name")} SRC FW Groups: {err.strerror}{bcolors.ENDC}\n')
                        continue
                    
                    srcmembers = []
                    if r_json['members'] != None:
                        src_mem_list = [x['id'] for x in r_json['members']]
                        for item in src_mem_list:
                            if re.match(r'.*:network:.*', item):
                                item_id = prefix + 'orgnets.' + item.split(':')[-1]
                                srcmembers.append(item_id)
                            elif re.match(r'.*:vm:.*', item):
                                item_id = prefix + 'vms.' + item.split(':')[-1]
                                srcmembers.append(item_id)
                            else:
                                srcmembers.append(item)
                        
                    else:
                        srcmembers = None

                    yaml_src_fw = {
                        'type': r_json['type'],
                        'ip_addresses': r_json['ipAddresses'],
                        'members': srcmembers
                    }

                    src_fw_groups[fw_group_id] = yaml_src_fw

            yaml_structure['sourceFirewallGroups'] = src_fw_groups

            dst_fw_groups = {}
            if rule['destinationFirewallGroups'] != None:
                for group in rule['destinationFirewallGroups']:
                    fw_group_id = group['id']
                    query = f'https://{site}/cloudapi/1.0.0/firewallGroups/{fw_group_id}'
                    try:
                        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(f'\t{bcolors.FAIL}Could not get Edge Gateway {gw.get("name")} DST FW Groups: {err.strerror}{bcolors.ENDC}\n')
                        continue

                    dstmembers = []
                    if r_json['members'] != None:
                        dst_mem_list = [x['id'] for x in r_json['members']]
                        for item in dst_mem_list:
                            if re.match(r'.*:network:.*', item):
                                item_id = prefix + 'networks.' + item.split(':')[-1]
                                dstmembers.append(item_id)
                            elif re.match(r'.*:vm:.*', item):
                                item_id = prefix + 'vms.' + item.split(':')[-1]
                                dstmembers.append(item_id)
                            else:
                                dstmembers.append(item)
                        
                    else:
                        dstmembers = None
                    print(dstmembers)
                    yaml_dst_fw = {
                        'type': r_json['type'],
                        'ip_addresses': r_json['ipAddresses'],
                        'members': dstmembers
                    }

                    dst_fw_groups[fw_group_id] = yaml_dst_fw

            yaml_structure['destinationFirewallGroups'] = dst_fw_groups

            port_profiles = {}
            if 'applicationPortProfiles' in rule and rule['applicationPortProfiles'] != None:
                for profile in rule['applicationPortProfiles']:
                    profile_id = profile['id']
                    query = f'https://{site}/cloudapi/1.0.0/applicationPortProfiles/{profile_id}'
                    try:
                        r = get_cloudapi(url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(f'\t{bcolors.FAIL}Could not get Edge Gateway {gw.get("name")} Port Profiles: {err.strerror}{bcolors.ENDC}\n')
                        continue  

                    name = profile['name']
                    ports = []
                    for port in r_json['applicationPorts']:
                        yaml_port = {
                            'protocol': port['protocol'],
                            'dst_ports': port['destinationPorts']
                        }
                        ports.append(yaml_port)
                    port_profiles[name] = ports

                yaml_structure['port_profiles'] = port_profiles
            fw_list['seaf.ta.reverse.vmwarecloud.egws_fw'][seaf_id] = yaml_structure

    save(fw_list, exportpath, 'enterprise_egws_fw')


# Получаем токен
if access_token == None:
    try:
        token_request = get_cloud_enterprise_auth(site=site, tenant=tenant, token=refresh_token)
        access_token = json.loads(token_request.text)
    except Exception as err:
        print(f'{bcolors.FAIL}Could not get auth token: {err.strerror}{bcolors.ENDC}\n')
        sys.exit(err.errno)
    else:
        print(f'{bcolors.OKGREEN}Successfully authenticated. Your new refresh_token:{bcolors.ENDC} {access_token["refresh_token"]}')
        # Закомментировать если не требуется сохранять ключ
        try:
           with open(f'{exportpath}/key.txt', 'w', encoding='utf-8') as outfile:
               outfile.write(token_request.text)
        except Exception as err:
           print(f'{bcolors.FAIL}Could not write key to{bcolors.ENDC} {bcolors.UNDERLINE}{exportpath}/key.txt{bcolors.ENDC}{bcolors.FAIL} auth token: {err.strerror}{bcolors.ENDC}\n')
else:
    print(f'{bcolors.OKGREEN}Working with predefined access token from config:{bcolors.ENDC} {bcolors.BOLD}{access_token["access_token"][0:15]}...{bcolors.ENDC}')

# Получаем последнюю версию API и url для создания сессии
try:
    api_init = get_api_versions(site=site)
except Exception as err:
    print(f'{bcolors.FAIL}Failed to get API Versions {err.strerror}{bcolors.ENDC}\n')
    sys.exit(err.errno)
else:
    print(f'{bcolors.OKGREEN}API Version:{bcolors.ENDC} {bcolors.UNDERLINE}{api_init["version"]}{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}Session URL:{bcolors.ENDC} {bcolors.UNDERLINE}{api_init["url"]}{bcolors.ENDC}\n')


############################ Main Program ############################
    
# Orgs
if orgs_export == True:
    get_orgs(site, access_token, api_init, prefix, dc)

# VDCs
if export_vdc == True:
    get_vdcs(site, access_token, api_init, prefix, dc)

# vdcGroups
if export_vdcgroups == True:
    get_vdcgroups(site, access_token, api_init, prefix, dc)

# orgNetwork
if export_orgnetwork == True:
    get_orgnetworks(site, access_token, api_init, prefix, dc)

# edgeGateways
if export_egw == True:
    get_edgegw(site, access_token, api_init, prefix, dc)

# vms
if vm == True:
    get_vms(site, access_token, api_init, prefix, dc)

# vApps
if vapp == True:
    get_vapps(site, access_token, api_init, prefix, dc)

# vApp Networks
if export_vappnet == True:
    get_vappnets(site, access_token, api_init, prefix, dc)

# edgeGateway Nat Rules
if export_nat == True:
    get_edgenat(site, access_token, api_init, prefix, dc)

# edgeGateway FW Rules
if export_fw == True:
    get_edgefw(site, access_token, api_init, prefix, dc)
