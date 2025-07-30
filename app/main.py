#! F:\VRCOSC-Bilibili\OSC\Scripts\python.exe

from time import sleep
from bilibili_api import Credential
from browser_cookie3 import firefox

def get_credentials() -> Credential | None:
    credential = {}
    cj = None
    try:
        cj = firefox(domain_name="bilibili.com")
    except Exception as e:
        print(e)
        pass
    if not cj:
        print("请先在浏览器登录b站")
        sleep(3)
        return None
    else:
        for cookie in cj:
            name = cookie.name
            if name == 'DedeUserID':
                credential["dedeuserid"] = cookie.value
            elif name == 'bili_jct':
                credential["bili_jct"] = cookie.value
            elif name == 'buvid3':
                credential["buvid3"] = cookie.value
            elif name == 'SESSDATA':
                credential["sessdata"] = cookie.value
        if not credential:
            print("请在火狐浏览器登录b站")
            sleep(3)
            return None
    my_credential = Credential(**credential)
    return my_credential