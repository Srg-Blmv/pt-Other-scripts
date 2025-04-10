import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


global_gr_id = ""
cookies = ""
headers = {"Content-Type": "application/json"}

def auth():
    global global_gr_id, cookies
    
    url = f"https://{mgmt_ip}/api/v2/Login"
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



def get_ip(obj_name):
    # ---------------------  GET IP ----------------------
    url = f"https://{mgmt_ip}:443/api/v2/ListNetworkObjects"

    payload = {
        "deviceGroupId": global_gr_id,
        "objectKinds": ["OBJECT_NETWORK_KIND_IPV4_ADDRESS","OBJECT_NETWORK_KIND_IPV4_RANGE","OBJECT_NETWORK_KIND_FQDN"],
        "offset": 0,
        "limit": 10000
    }

    response = requests.request("POST", url, json=payload, headers=headers, cookies=cookies, verify=False)

    if response.status_code == 200:
        data = response.json()
        #print(data)
        # Проверка по адресу
        for obj in data.get("addresses", []):
            if obj.get("name") == obj_name:
                return obj["id"]
        
        # Проверка по диапазону
        for obj in data.get("ranges", []):
            if obj.get("name") == obj_name:
                return obj["id"]
        
        # Проверка по доменным именам
        for obj in data.get("fqdnAddresses", []):
            if obj.get("name") == obj_name:
                return obj["id"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()


# ---------------  DEL IP  ----------------
def remove_ip(name):
    auth()
    id_obj = get_ip(name)
    url = f"https://{mgmt_ip}:443/api/v2/DeleteNetworkObject"
    payload = {
        "id": id_obj
    }
    response = requests.request("POST", url, json=payload,  headers=headers, cookies=cookies, verify=False)
    if response.status_code == 200:
        print(f"del: {id_obj}")
    else:
        print(f"Error: {response.status_code} - {response.text} - ID RULE: {id_obj}")


mgmt_ip = "192.168.212.10"
mgmt_login =  "admin"
mgmt_pass = "xxXX1234$"
groupe_name = "Global"
name = "fqdn_fl6btig1h2.net"


remove_ip(name)