# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urlquick
from uuid import uuid4
import base64
import hashlib
import time
from functools import wraps
from distutils.version import LooseVersion
from codequick import Script
from codequick.storage import PersistentDict
from xbmc import executebuiltin
from xbmcgui import Dialog
import socket


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def isLoggedIn(func):
    """
    Decorator to ensure that a valid login is present when calling a method
    """
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        with PersistentDict("headers") as db:
            username = db.get("username")
            password = db.get("password")
            headers = db.get("headers")
            exp = db.get("exp", 0)
        if headers and exp > time.time():
            return func(*args, **kwargs)
        elif username and password:
            login(username, password)
            return func(*args, **kwargs)
        elif headers and exp < time.time():
            Script.notify(
                "Login Error", "Session expired. Please login again")
            executebuiltin(
                "RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/login/)")
            return False
        else:
            Script.notify(
                "Login Error", "You need to login with Jio Username and password to use this add-on")
            executebuiltin(
                "RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/login/)")
            return False
    return login_wrapper


def login(username, password, mode="unpw"):
    body = {
        "identifier": username if '@' in username else "+91" + username,
        "password" if mode == "unpw" else "otp": password,
        "rememberUser": "T",
        "upgradeAuth": "Y",
        "returnSessionDetails": "T",
        "deviceInfo": {
            "consumptionDeviceName": "ZUK Z1",
            "info": {
                "type": "android",
                "platform": {
                    "name": "ham",
                    "version": "9"
                },
                "androidId": ""
            }
        }
    }
    resp = urlquick.post("https://api.jio.com/v3/dip/user/{0}/verify".format(mode), json=body, headers={
                         "User-Agent": "JioTV", "x-api-key": "l7xx75e822925f184370b2e25170c5d5820a"}, max_age=-1, verify=False, raise_for_status=False).json()
    if resp.get("ssoToken", "") != "":
        _CREDS = {
            "ssotoken": resp.get("ssoToken"),
            "userid": resp.get("sessionAttributes", {}).get("user", {}).get("uid"),
            "uniqueid": resp.get("sessionAttributes", {}).get("user", {}).get("unique"),
            "crmid": resp.get("sessionAttributes", {}).get("user", {}).get("subscriberId"),
            "subscriberid": resp.get("sessionAttributes", {}).get("user", {}).get("subscriberId"),
        }
        headers = {
            "deviceId": str(uuid4()),
            "devicetype": "phone",
            "os": "android",
            "osversion": "9",
            "user-agent": "plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7",
            "usergroup": "tvYR7NSNn7rymo3F",
            "versioncode": "289",
            "dm" : "ZUK ZUK Z1"
        }
        headers.update(_CREDS)
        with PersistentDict("headers") as db:
            db["headers"] = headers
            db["exp"] = time.time() + 432000
            if mode == "unpw":
                db["username"] = username
                db["password"] = password
        Script.notify("Login Success", "")
        return None
    else:
        Script.log(resp, lvl=Script.INFO)
        msg = resp.get("message", "Unknow Error")
        Script.notify("Login Failed", msg)
        return msg


def sendOTP(mobile):
    if "+91" not in mobile:
        mobile = "+91" + mobile
    body = {"identifier": mobile, "otpIdentifier": mobile,
            "action": "otpbasedauthn"}
    Script.log(body, lvl=Script.ERROR)
    resp = urlquick.post("https://api.jio.com/v3/dip/user/otp/send", json=body, headers={
        "x-api-key": "l7xx75e822925f184370b2e25170c5d5820a"}, max_age=-1, verify=False, raise_for_status=False)
    if resp.status_code != 204:
        return resp.json().get("errors", [{}])[-1].get("message")
    return None


def logout():
    with PersistentDict("headers") as db:
        del db["headers"]
    Script.notify("You\'ve been logged out", "")


def getHeaders():
    with PersistentDict("headers") as db:
        return db.get("headers", False)

def getChannelHeaders():
    headers = getHeaders()
    return {
        'ssotoken': headers['ssotoken'],
        'userId': headers['userid'],
        'uniqueId': headers['uniqueid'],
        'crmid': headers['crmid'],
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'deviceid': headers['deviceId'],
        'devicetype': 'phone',
        'os': 'android',
        'osversion': '9',
    }

def check_addon(addonid, minVersion=False):
    """Checks if selected add-on is installed."""
    try:
        curVersion = Script.get_info("version", addonid)
        if minVersion and LooseVersion(curVersion) < LooseVersion(minVersion):
            Script.log('{addon} {curVersion} doesn\'t setisfy required version {minVersion}.'.format(
                addon=addonid, curVersion=curVersion, minVersion=minVersion))
            Dialog().ok("Error", "{minVersion} version of {addon} is required to play this content.".format(
                addon=addonid, minVersion=minVersion))
            return False
        return True
    except RuntimeError:
        Script.log('{addon} is not installed.'.format(addon=addonid))
        if not _install_addon(addonid):
            # inputstream is missing on system
            Dialog().ok("Error",
                        "[B]{addon}[/B] is missing on your Kodi install. This add-on is required to play this content.".format(addon=addonid))
            return False
        return True


def _install_addon(addonid):
    """Install addon."""
    try:
        # See if there's an installed repo that has it
        executebuiltin('InstallAddon({})'.format(addonid), wait=True)

        # Check if add-on exists!
        version = Script.get_info("version", addonid)

        Script.log(
            '{addon} {version} add-on installed from repo.'.format(addon=addonid, version=version))
        return True
    except RuntimeError:
        Script.log('{addon} add-on not installed.'.format(addon=addonid))
        return False
