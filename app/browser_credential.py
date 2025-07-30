from bilibili_api import Credential
from browser_cookie3 import firefox
import logging
logger = logging.getLogger(__name__)


def get_credentials() -> Credential | None:
    credential = {}
    cj = None
    logger.info("尝试获取火狐浏览器bilbili登录信息")
    try:
        cj = firefox(domain_name="bilibili.com")
    except Exception as e:
        logger.warning("未找到火狐浏览器,将以游客身份链接")
        return None
    if not cj:
        logger.warning("火狐浏览器缺少biibili登录信息,将以游客身份链接")
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
            logger.warning("火狐浏览器缺少biibili登录信息,将以游客身份链接")
            return None
    my_credential = Credential(**credential)
    logger.info(f"获取到登录信息, uid={my_credential.dedeuserid}")
    return my_credential