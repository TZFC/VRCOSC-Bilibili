import asyncio
import base64
import glob
import json
import logging
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional

import browser_cookie3
import requests
import websockets
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

def find_browser_executable(browser_name: str) -> Optional[str]:
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    
    paths = []
    if browser_name == "Chrome":
        paths = [
            os.path.join(program_files, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(program_files_x86, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(local_appdata, r"Google\Chrome\Application\chrome.exe")
        ]
    elif browser_name == "Edge":
        paths = [
            os.path.join(program_files_x86, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(program_files, r"Microsoft\Edge\Application\msedge.exe")
        ]
    elif browser_name == "Brave":
        paths = [
            os.path.join(program_files, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.join(program_files_x86, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.join(local_appdata, r"BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
    elif browser_name == "Opera":
        paths = [
            os.path.join(local_appdata, r"Programs\Opera\launcher.exe"),
            os.path.join(program_files, r"Opera\launcher.exe"),
            os.path.join(program_files_x86, r"Opera\launcher.exe")
        ]
        
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def copy_file_vss(source_path: str, dest_path: str) -> bool:
    """Attempts to copy a locked file using Windows Volume Shadow Copy (VSS) via PowerShell."""
    if sys.platform != "win32":
        return False
        
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return False
    except Exception:
        return False
        
    abs_source = os.path.abspath(source_path)
    drive = abs_source[:2] + "\\"
    relative_path = abs_source[3:]
    
    # PowerShell script to create shadow copy, copy file, and clean up
    ps_script = f"""
    $ErrorActionPreference = 'Stop'
    try {{
        $wmi = [wmiclass]"root\\cimv2:Win32_ShadowCopy"
        $shadow = $wmi.Create("{drive}", "ClientAccessible")
        if ($shadow.ReturnValue -ne 0) {{
            exit 1
        }}
        $shadowCopy = Get-WmiObject Win32_ShadowCopy | Where-Object {{ $_.ID -eq $shadow.ShadowID }}
        $devicePath = $shadowCopy.DeviceObject + "\\"
        $sourcePath = Join-Path $devicePath "{relative_path}"
        
        $destDir = Split-Path -Parent "{os.path.abspath(dest_path)}"
        if (!(Test-Path $destDir)) {{
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }}
        
        Copy-Item -Path $sourcePath -Destination "{os.path.abspath(dest_path)}" -Force
        $shadowCopy.Delete()
        exit 0
    }} catch {{
        exit 1
    }}
    """
    
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            check=True
        )
        return proc.returncode == 0
    except Exception as e:
        logger.debug(f"VSS copy failed for {source_path}: {e}")
        return False

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

async def retrieve_cookies_via_ws(port: int) -> List[Dict]:
    import urllib.request
    ws_url = None
    # Poll up to 5 seconds for the browser to launch and become ready
    for _ in range(25):
        await asyncio.sleep(0.2)
        try:
            url = f"http://127.0.0.1:{port}/json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=1.0) as response:
                targets = json.loads(response.read().decode())
                for target in targets:
                    if target.get("type") == "page":
                        ws_url = target.get("webSocketDebuggerUrl")
                        break
                if ws_url:
                    break
        except Exception:
            continue
            
    if not ws_url:
        logger.debug(f"Failed to obtain WebSocket debugger URL on port {port}")
        return []
        
    try:
        async with websockets.connect(ws_url) as ws:
            # Navigate to Bilibili first to load cookie database context
            navigate_payload = {
                "id": 1,
                "method": "Page.navigate",
                "params": {"url": "https://www.bilibili.com"}
            }
            await ws.send(json.dumps(navigate_payload))
            await ws.recv()
            await asyncio.sleep(2) # wait for Bilibili page load and cookie decryption
            
            # Fetch the decrypted cookies
            cmd_payload = {
                "id": 2,
                "method": "Network.getCookies",
                "params": {
                    "urls": ["https://bilibili.com", "https://www.bilibili.com", "https://api.bilibili.com"]
                }
            }
            await ws.send(json.dumps(cmd_payload))
            resp = await ws.recv()
            result = json.loads(resp)
            cookies_list = result.get("result", {}).get("cookies", [])
            
            cookies_dict = {}
            for c in cookies_list:
                cookies_dict[c["name"]] = c["value"]
                
            bili_jct = cookies_dict.get("bili_jct", "")
            dedeuserid = cookies_dict.get("DedeUserID", "")
            sessdata = cookies_dict.get("SESSDATA", "")
            buvid3 = cookies_dict.get("buvid3", "")
            
            if bili_jct and dedeuserid and sessdata:
                return [{
                    "bili_jct": bili_jct,
                    "dedeuserid": dedeuserid,
                    "sessdata": sessdata,
                    "buvid3": buvid3
                }]
    except Exception as e:
        logger.debug(f"Error during WS CDP communication: {e}")
        
    return []

def get_browser_cookies_cdp(browser_name: str, local_state_path: str, cookies_dir: str) -> List[Dict]:
    executable_path = find_browser_executable(browser_name)
    if not executable_path:
        logger.debug(f"Executable for {browser_name} not found.")
        return []
        
    cookies_found = []
    profile_dirs = glob.glob(os.path.join(cookies_dir, "Default")) + \
                   glob.glob(os.path.join(cookies_dir, "Profile *"))
                   
    for prof in profile_dirs:
        cookies_db_candidates = [
            os.path.join(prof, "Network", "Cookies"),
            os.path.join(prof, "Cookies")
        ]
        cookies_db = None
        for cand in cookies_db_candidates:
            if os.path.exists(cand):
                cookies_db = cand
                break
        if not cookies_db:
            continue
            
        temp_dir = os.path.join(tempfile.gettempdir(), f"vrcosc_cdp_{browser_name}_{os.path.basename(prof)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Copy Local State
        copied = False
        try:
            shutil.copy2(local_state_path, os.path.join(temp_dir, "Local State"))
            copied = True
        except Exception:
            if copy_file_vss(local_state_path, os.path.join(temp_dir, "Local State")):
                copied = True
                
        if not copied:
            shutil.rmtree(temp_dir, ignore_errors=True)
            continue
            
        # Copy Cookies
        copied_cookies = False
        dest_cookies_dir = os.path.join(temp_dir, "Default", "Network")
        os.makedirs(dest_cookies_dir, exist_ok=True)
        dest_cookies_path = os.path.join(dest_cookies_dir, "Cookies")
        
        try:
            shutil.copy2(cookies_db, dest_cookies_path)
            copied_cookies = True
        except Exception:
            if copy_file_vss(cookies_db, dest_cookies_path):
                copied_cookies = True
                
        if not copied_cookies:
            shutil.rmtree(temp_dir, ignore_errors=True)
            continue
            
        # Spawn headless browser
        port = find_free_port()
        cmd = [
            executable_path,
            "--headless=old",
            f"--user-data-dir={temp_dir}",
            f"--remote-debugging-port={port}",
            "--disable-gpu",
            "--remote-allow-origins=*"
        ]
        
        proc = None
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            proc = subprocess.Popen(cmd, startupinfo=startupinfo)
            
            # Execute async WebSocket client synchronously
            found = asyncio.run(retrieve_cookies_via_ws(port))
            if found:
                cookies_found.extend(found)
        except Exception as e:
            logger.debug(f"Failed running headless {browser_name}: {e}")
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=2.0)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    return cookies_found

def get_chromium_cookies(browser_name: str, local_state_path: str, cookies_dir: str) -> List[Dict]:
    cookies_found = []
    if not os.path.exists(local_state_path) or win32crypt is None or AES is None:
        return cookies_found

    has_v20 = False
    locked = False

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
            conn.text_factory = bytes
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%bilibili.com%'"
            )
            cookies = {}
            for name, encrypted_value in cursor.fetchall():
                decrypted = ""
                try:
                    name_str = name.decode('utf-8', errors='ignore')
                    if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                        iv = encrypted_value[3:15]
                        payload = encrypted_value[15:]
                        cipher = AES.new(key, AES.MODE_GCM, iv)
                        decrypted = cipher.decrypt(payload)[:-16].decode('utf-8', errors='ignore')
                    elif encrypted_value.startswith(b'v20'):
                        has_v20 = True
                        break
                    else:
                        decrypted = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                except Exception as ex:
                    logger.debug(f"Failed to decrypt cookie {name} in {browser_name}: {ex}")
                    continue
                if decrypted:
                    cookies[name_str] = decrypted
            conn.close()

            if has_v20:
                break

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
        except PermissionError:
            logger.info(f"[{browser_name}] Cookie database is locked by the running browser.")
            locked = True
            break
        except Exception as e:
            logger.debug(f"Failed to read cookies from {db_path} for {browser_name}: {e}")
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass

    # 3. Fall back to headless browser CDP scan if v20 cookies exist or database is locked
    if has_v20 or locked:
        logger.info(f"[{browser_name}] Initiating headless browser CDP cookie scan (to decrypt v20 App-Bound cookies)...")
        cdp_cookies = get_browser_cookies_cdp(browser_name, local_state_path, cookies_dir)
        if cdp_cookies:
            for item in cdp_cookies:
                if item not in cookies_found:
                    cookies_found.append(item)
        else:
            if locked:
                logger.warning(f"[{browser_name}] Failed to scan locked browser. If standard scan fails, please run this launcher as Administrator or close your browser.")
            else:
                logger.warning(f"[{browser_name}] Headless scan returned no cookies. Make sure you are logged into Bilibili in your browser.")

    return cookies_found

async def get_bilibili_cookies_from_browser() -> List[Dict]:
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
                    profile = await verify_and_fetch_profile(
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
                    profile = await verify_and_fetch_profile(
                        bili_jct, dedeuserid, sessdata, buvid3
                    )
                    if profile and profile not in profiles:
                        profiles.append(profile)
            except Exception:
                continue
                
    return profiles


def download_face_as_base64(url: str) -> str:
    if not url:
        return ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }
    try:
        import base64
        import requests
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "image/jpeg")
            encoded = base64.b64encode(r.content).decode("utf-8")
            return f"data:{content_type};base64,{encoded}"
    except Exception as e:
        logger.debug(f"Failed to download profile picture from {url}: {e}")
    return url # Return original url as fallback


async def verify_and_fetch_profile(
    bili_jct: str, dedeuserid: str, sessdata: str, buvid3: str
) -> Optional[Dict]:
    from bilibili_api import user, Credential
    try:
        credential = Credential(
            sessdata=sessdata,
            bili_jct=bili_jct,
            dedeuserid=dedeuserid,
            buvid3=buvid3
        )
        u = user.User(uid=int(dedeuserid), credential=credential)
        info = await u.get_user_info()
        if info and "name" in info:
            face = info.get("face", "")
            if face and face.startswith("//"):
                face = "https:" + face
            face_base64 = download_face_as_base64(face)
            return {
                "uid": int(dedeuserid),
                "name": info.get("name", ""),
                "face_url": face_base64,
                "bili_jct": bili_jct,
                "dedeuserid": dedeuserid,
                "sessdata": sessdata,
                "buvid3": buvid3,
            }
    except Exception as e:
        logger.debug(f"Failed to fetch profile via bilibili-api: {e}")

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
                face = data["data"]["face"]
                if face and face.startswith("//"):
                    face = "https:" + face
                face_base64 = download_face_as_base64(face)
                return {
                    "uid": int(dedeuserid),
                    "name": data["data"]["name"],
                    "face_url": face_base64,
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
