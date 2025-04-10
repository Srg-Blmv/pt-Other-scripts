import requests
import random
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

global_gr_id = ""
cookies = ""


def auth():
    global global_gr_id, cookies

    url = f"https://{mgmt_ip}/api/v2/Login"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "login": mgmt_login,
        "password": mgmt_pass
    }
    
    response_auth = requests.post(url, json=payload, headers=headers, verify=False)
    if response_auth.status_code == 200:
        print("auth ok")
        url =  f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
        r = requests.post(url, headers=headers, verify=False, cookies=response_auth.cookies)
        cookies = response_auth.cookies
        # ПОЛУЧАЕМ ID глобальной группы
        global_gr_id = get_id_groupe(r.json()['groups'][0])
        # Или заберите нужное ID через web api интерфейс: https://IP_MGMT/apidoc/v2/ui/#tag/device-groups/POST/api/v2/GetDeviceGroupsTree

    else:
        print("auth fail")
        exit()


def get_id_groupe(groups):
    # Проверка текущей группы
    if groups.get("name") == groupe_name:
        return groups.get("id")
    # Проверка вложенных групп, если они существуют
    if "subgroups" in groups:
        for subgroup in groups["subgroups"]:  # Проходим по списку подгрупп
            result = get_id_groupe(subgroup)
            if result:  # Если id найдено, возвращаем его
                return result
    return None  # Возвращаем None, если ничего не найдено



def load_data_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()



def parse_data(data):

    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    cidr_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}'
    fqdn_pattern = r'[a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
    lines = data.split('\n')

    # Создаем списки для хранения результатов
    ipv4_addresses = []
    networks = []
    domains = []
    
    for line in lines:

        if not line.strip():  # Пропускаем пустые строки
            continue
        # Поиск IP-адресов
        matches = re.findall(ip_pattern, line)
        if matches:
            # print(matches)
            ipv4_addresses.extend(matches)
            
        # Поиск сетей
        matches = re.findall(cidr_pattern, line)
        if matches:
            networks.extend(matches)
        
        # Поиск доменов
        matches = re.findall(fqdn_pattern, line)
        if matches:
            domains.extend(matches)
    
    return ipv4_addresses, networks, domains


# ----------------------------------  IP ------------------------------
def ipv4(ip_list):
    url_serv  = f"https://{mgmt_ip}/api/v2/CreateNetworkObject"
    id_ip = []
    for ip in ip_list:
        payload_serv = {
            "deviceGroupId": global_gr_id,
            "name": f"{ip.replace('.', '_')}",
            "description": "",
            "value": {
            "inet": {
                "inet": f"{ip}/32"
            }
        }
       }
        headers = {"Content-Type": "application/json"}
        response_ser = requests.post(url_serv, json=payload_serv, headers=headers, verify=False, cookies=cookies)
        if response_ser.status_code == 200:
            id_ip.append(response_ser.json()['id'])
            print(response_ser.json())
        else:
            print(response_ser.json())

    return id_ip


# ---------------------------------- CIDR -----------------------------
def cidr(cidr_list):
    id_cidr = []
    url_serv  = f"https://{mgmt_ip}/api/v2/CreateNetworkObject"

    for cidr in cidr_list:
        payload_serv = {
            "name": f"{cidr.replace('.', '_')}",
            "deviceGroupId": global_gr_id,
            "description": "",
            "value": {
            "inet": {
                "inet": f"{cidr}"
            }
            }
        }
        headers = {"Content-Type": "application/json"}
        response_ser = requests.post(url_serv, json=payload_serv, headers=headers, verify=False, cookies=cookies)
        if response_ser.status_code == 200:
            id_cidr.append(response_ser.json()['id'])
            print(response_ser.json())
        else:
            print(response_ser.json())

    return id_cidr



# --------------------------------- FQDN -------------------------------


def fqdn(fqdn_list):
    id_fqdn = []
    url_serv  = f"https://{mgmt_ip}/api/v2/CreateNetworkObject"
    for fqdn in fqdn_list:
        payload_serv = {
            "name": f"{fqdn}",
            "deviceGroupId": global_gr_id,
            "description": "",
            "value": {
            "fqdn": {
                "fqdn": f"{fqdn}"
            }
        }
        }
        headers = {"Content-Type": "application/json"}
        response_ser = requests.post(url_serv, json=payload_serv, headers=headers, verify=False, cookies=cookies)
        if response_ser.status_code == 200:
            id_fqdn.append(response_ser.json()['id'])
            print(response_ser.json())
        else:
            print(response_ser.json())
    return id_fqdn

# ---------------------------------------------------

def add_in_groupe(name_group, list_obj):
    url_groupe  = f"https://{mgmt_ip}/api/v2/CreateNetworkObjectGroup"
    payload = {
            "name": f"{name_group}",
            "deviceGroupId": global_gr_id,
            "description": "",
            "items": list_obj
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url_groupe, json=payload, headers=headers, verify=False, cookies=cookies)
    print("groupe_add: ", response.json())


def main(path_txt_file, name_groupe):
   auth()
   data_from_txt = load_data_from_file(path_txt_file)
   ipv4_addresses, networks, domains = parse_data(data_from_txt)
   ip_id = ipv4(ipv4_addresses)
   net_id = cidr(networks)
   fqdn_id = fqdn(domains)
   all_id = ip_id + net_id +  fqdn_id

   # Создаем группу и добавялем объекты
   add_in_groupe(name_groupe, all_id)


mgmt_ip = "192.168.212.10"
mgmt_login =  "admin"
mgmt_pass = "xxXX1234$"
groupe_name= "Global"

filename = 'H:/scripts/pt-Other-scripts/block.txt'
name_object_groupe = "black_list_ip"

main(filename, name_object_groupe)


