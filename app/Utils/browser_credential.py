"""
Retreive Bilibili login credential from Firefox browser
!!HIGH SECURITY RISK!! USE WITH CAUTION

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - browser_cookie3 (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import logging
from bilibili_api import Credential
from browser_cookie3 import firefox, BrowserCookieError
logger = logging.getLogger(__name__)


def get_credentials() -> Credential | None:
    """
    Get Bilibili Login credentials from Firefox browser cookie
    WARNING: HIGH SECURITY RISK
    """
    credential: dict = {}
    cj = None
    logger.info("尝试获取火狐浏览器bilbili登录信息")
    try:
        cj = firefox(domain_name="bilibili.com")
    except BrowserCookieError:
        logger.warning("未找到火狐浏览器,将以游客身份链接")
        return None
    if not cj:
        logger.warning("火狐浏览器缺少biibili登录信息,将以游客身份链接")
        return None
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
    logger.info("获取到登录信息, uid = %d", int(my_credential.dedeuserid))
    return my_credential
