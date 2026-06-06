from typing import Dict, List, Optional

import browser_cookie3
import requests
from bilibili_api import login_v2
from database import AuthProfile, Session, engine
from sqlmodel import select

# Global instance for QR code login
qr_login_instance: Optional[login_v2.QrCodeLogin] = None

def get_bilibili_cookies_from_browser() -> List[Dict]:
    """Scans browsers for Bilibili cookies and returns a list of active sessions."""
    profiles = []
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
                # We found a valid login. Fetch user info to show profile card
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
    try:
        r = requests.get(
            "https://api.bilibili.com/x/space/myinfo", cookies=cookies, timeout=5
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
