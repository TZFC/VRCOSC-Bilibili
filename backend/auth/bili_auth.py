import base64
import glob
import logging
import os
import shutil
import sqlite3
import tempfile
from typing import Dict, List, Optional

import requests
from bilibili_api import login_v2
from database import AuthProfile, Session
from sqlmodel import select

qr_login_instance: Optional[login_v2.QrCodeLogin] = None
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

async def get_bilibili_cookies_from_browser() -> List[Dict]:
    """Scans Firefox for active Bilibili login sessions."""
    profiles = []
    
    try:
        logger.info("Scanning Firefox profiles for active Bilibili login cookies...")
        firefox_cookies = get_firefox_cookies()
        if firefox_cookies:
            logger.info(f"[Firefox] Found {len(firefox_cookies)} potential Bilibili cookie session(s).")
            for item in firefox_cookies:
                try:
                    profile = await verify_and_fetch_profile(
                        item["bili_jct"], item["dedeuserid"], item["sessdata"], item["buvid3"]
                    )
                    if profile and profile not in profiles:
                        logger.info(f"[API] Verified active Firefox Bilibili login for user: {profile['name']} (UID: {profile['uid']})")
                        profiles.append(profile)
                except Exception as ex:
                    logger.debug(f"Failed to verify profile for extracted Firefox cookie: {ex}")
        else:
            logger.info("[Firefox] No Bilibili cookies found.")
    except Exception as e:
        logger.error(f"Error in Firefox cookie extraction: {e}")
            
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
    if qr_login_instance.has_done():
        cred = qr_login_instance.get_credential()
        if cred:
            profile = await verify_and_fetch_profile(
                cred.bili_jct, cred.dedeuserid, cred.sessdata, cred.buvid3
            )
            if profile:
                saved = save_auth_profile(session, profile, set_active=True)
                return {"status": "done", "profile": saved.model_dump()}
        return {"status": "error"}
    return {"status": info.name}
