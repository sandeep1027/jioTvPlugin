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


from xbmcaddon import Addon
import xbmc
import xbmcvfs
import os
from contextlib import contextmanager
from collections import defaultdict
from resources.lib.constants import HOST,REFRESH_TOKEN_URL,REFRESH_LOGIN_OTP,UPDATE_REFRESH_TOKEN_URL

import json

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
            headers = db.get("headers")
            exp = db.get("exp", 0)
        if headers and exp > time.time():
            refreshAuth(headers["refreshToken"], headers["accesstoken"], headers["appName"], headers["deviceId"])
            refreshSsoTokenAuth(headers["ssotoken"], headers["deviceid"], headers["uniqueid"])
            updateRefreshToken(headers["refreshToken"], headers["accesstoken"], headers["uniqueid"],headers["appName"], headers["deviceId"])
            return func(*args, **kwargs)
        elif headers and exp < time.time():
            Script.notify(
                "Login Error", "Session expired. Please login again")
            executebuiltin(
                "RunPlugin(plugin://jioTvPlugin/resources/lib/main/login/)")
            return False
        else:
            Script.notify(
                "Login Error", "You need to login with OTP to use this add-on")
            executebuiltin(
                "RunPlugin(plugin://jioTvPlugin/resources/lib/main/login/)")
            return False
    return login_wrapper


def refreshAuth(refreshToken, authToken, appName, deviceId):
    body = {
        "appName": appName,
        "deviceId": deviceId,
        "refreshToken": refreshToken
    }
    headers = {
        'accesstoken': authToken,
        'devicetype': 'phone ',
        'os': 'android',
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'Content-Type': 'application/json'
    }
    resp = urlquick.post(REFRESH_TOKEN_URL, json=body, headers=headers, max_age=-1, verify=False, raise_for_status=False).json()
    if resp.get("authToken", "") != "":
        with PersistentDict("headers") as db:
            db["accesstoken"] = resp.get("authToken")
            db["exp"] = time.time() + 432000
    else:
        Script.log(resp, lvl=Script.INFO)
        msg = resp.get("message", "Unknow Error")
        Script.notify("Login Failed", msg)
        return msg

def refreshSsoTokenAuth(ssotoken, deviceid, uniqueid):
    headers = {
        'ssotoken': ssotoken,
        'devicetype': 'phone',
        'deviceid': deviceid,
        'uniqueid':uniqueid,
        'os': 'android',
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'Content-Type': 'application/json',
        'versioncode':330
    }
    resp = urlquick.get(REFRESH_LOGIN_OTP, headers=headers, max_age=-1, verify=False, raise_for_status=False).json()
    if resp.get("ssoToken", "") != "":
        with PersistentDict("headers") as db:
            db["ssotoken"] = resp.get("ssoToken")
    else:
        Script.log(resp, lvl=Script.INFO)
        msg = resp.get("message", "Unknow Error")
        Script.notify("Login Failed", msg)
        return msg

def updateRefreshToken(refreshToken, authToken, uniqueid, appName, deviceid):
    body = {
        "appName": appName,
        "deviceId": deviceid,
        "refreshToken": refreshToken,
        "thirdPartyApp": "RJIL_JioEngage"
    }
    headers = {
        'accesstoken': authToken,
        'devicetype': 'phone ',
        'os': 'android',
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'Content-Type': 'application/json',
        uniqueid:uniqueid
    }
    resp = urlquick.post(UPDATE_REFRESH_TOKEN_URL, json=body, headers=headers, max_age=-1, verify=False, raise_for_status=False).json()
    if resp.get("shortToken", "") != "":
        with PersistentDict("headers") as db:
            db["refreshToken"] = resp.get("shortToken")
    else:
        Script.log(resp, lvl=Script.INFO)
        msg = resp.get("message", "Unknow Error")
        Script.notify("Login Failed", msg)
        return msg

def login(mobile, otp):
    body = {
        "number": base64.b64encode(mobile),
        "otp": otp,
        "deviceInfo": {
            "consumptionDeviceName": "ZUK Z1",
            "info": {
            "type": "android",
            "platform": {
                "name": "ham"
            },
            "androidId": "3259d8734a88b7f1"
            }
        }
    }
    headers = {
        'appname': 'RJIL_JioTV',
        'devicetype': 'phone ',
        'os': 'android',
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'Content-Type': 'application/json'
    }
    resp = urlquick.post(HOST+"/userservice/apis/v1/loginotp/verify", json=body, headers=headers, max_age=-1, verify=False, raise_for_status=False).json()
    if resp.get("ssoToken", "") != "":
        _CREDS = {
            "accesstoken":resp.get("authToken"),
            "refreshToken": resp.get("refreshToken"),
            "ssotoken": resp.get("ssoToken"),
            "userid": resp.get("sessionAttributes", {}).get("user", {}).get("uid"),
            "uniqueid": resp.get("sessionAttributes", {}).get("user", {}).get("unique"),
            "crmid": resp.get("sessionAttributes", {}).get("user", {}).get("subscriberId"),
            "subscriberid": resp.get("sessionAttributes", {}).get("user", {}).get("subscriberId"),
        }
        headers = {
            "appName": "RJIL_JioTV",
            "deviceId": resp.get("deviceId"),
            "devicetype": "phone",
            "os": "android",
            "osversion": "12",
            "user-agent": "plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7",
            "usergroup": "tvYR7NSNn7rymo3F",
            "versioncode": "289",
            "dm" : "ONEPLUS 11",
            "appkey": "NzNiMDhlYzQyNjJm"
        }
        headers.update(_CREDS)
        with PersistentDict("headers") as db:
            db["headers"] = headers
            db["exp"] = time.time() + 432000
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
    body = {"number" : base64.b64encode(mobile)}
    headers = {
        'appname': 'RJIL_JioTV',
        'devicetype': 'phone ',
        'os': 'android',
        'user-agent': 'plaYtv/7.0.8 (Linux;Android 9) ExoPlayerLib/2.11.7',
        'Content-Type': 'application/json'
    }
    Script.log(body, lvl=Script.ERROR)
    resp = urlquick.post(HOST+"/userservice/apis/v1/loginotp/send", json=body, headers=headers, max_age=-1, verify=False, raise_for_status=False)
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
        'accesstoken' : headers['accesstoken'],
        'ssotoken': headers['ssotoken'],
        'userId': headers['userid'],
        'uniqueId': headers['uniqueid'],
        'crmid': headers['crmid'],
        'user-agent':  headers['user-agent'],
        'deviceid': headers['deviceId'],
        'devicetype': 'phone',
        'os':  headers['os'],
        'osversion':  headers['osversion'],
        'appkey': headers['appkey'],
        'subscriberid': headers['subscriberid'],
        'uniqueid': headers['uniqueid'],
        'userid': headers['userid'],
        'versioncode': 330
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


def getQualityIndex(qualityStr, len):
    """Converts quality into a numeric value. Max clips to fall within valid bounds."""
    mapping = {
        'Best': len-1,
        'High': 4,
        'Medium+': 3,
        'Medium': 2,
        'Low': 1,
        'Lowest': 0,
    }
    if qualityStr in mapping:
        return min(mapping[qualityStr], len-1)
    return 0

_signals = defaultdict(list)
_skip = defaultdict(int)


def emit(signal, *args, **kwargs):
    if _skip[signal] > 0:
        _skip[signal] -= 1
        return

    for f in _signals.get(signal, []):
        f(*args, **kwargs)


class Monitor(xbmc.Monitor):
    def onSettingsChanged(self):
        emit('on_settings_changed')


monitor = Monitor()


def kodi_rpc(method, params=None, raise_on_error=False):
    try:
        payload = {'jsonrpc': '2.0', 'id': 1}
        payload.update({'method': method})
        if params:
            payload['params'] = params

        data = json.loads(xbmc.executeJSONRPC(json.dumps(payload)))
        if 'error' in data:
            raise Exception('Kodi RPC "{} {}" returned Error: "{}"'.format(
                method, params or '', data['error'].get('message')))

        return data['result']
    except Exception as e:
        if raise_on_error:
            raise
        else:
            return {}


def set_kodi_setting(key, value):
    return kodi_rpc('Settings.SetSettingValue', {'setting': key, 'value': value})


def same_file(path_a, path_b):
    if path_a.lower().strip() == path_b.lower().strip():
        return True
    stat_a = os.stat(path_a) if os.path.isfile(path_a) else None
    if not stat_a:
        return False
    stat_b = os.stat(path_b) if os.path.isfile(path_b) else None
    if not stat_b:
        return False
    return (stat_a.st_dev == stat_b.st_dev) and (stat_a.st_ino == stat_b.st_ino) and (stat_a.st_mtime == stat_b.st_mtime)


def safe_copy(src, dst, del_src=False):
    src = xbmcvfs.translatePath(src)
    dst = xbmcvfs.translatePath(dst)

    if not xbmcvfs.exists(src) or same_file(src, dst):
        return

    if xbmcvfs.exists(dst):
        if xbmcvfs.delete(dst):
            Script.log('Deleted: {}'.format(dst))
        else:
            Script.log('Failed to delete: {}'.format(dst))

    if xbmcvfs.copy(src, dst):
        Script.log('Copied: {} > {}'.format(src, dst))
    else:
        Script.log('Failed to copy: {} > {}'.format(src, dst))

    if del_src:
        xbmcvfs.delete(src)


@contextmanager
def busy():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def _setup(m3uPath, epgUrl):
    ADDON_ID = 'pvr.iptvsimple'
    addon = Addon(ADDON_ID)
    ADDON_NAME = addon.getAddonInfo('name')
    addon_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    instance_filepath = os.path.join(addon_path, 'instance-settings-91.xml')

    with busy():
        kodi_rpc('Addons.SetAddonEnabled', {
                 'addonid': ADDON_ID, 'enabled': False})

        # newer PVR Simple uses instance settings that can't yet be set via python api
        # so do a workaround where we leverage the migration when no instance settings found
        if LooseVersion(addon.getAddonInfo('version')) >= LooseVersion('20.8.0'):
            xbmcvfs.delete(instance_filepath)

            for file in os.listdir(addon_path):
                if file.startswith('instance-settings-') and file.endswith('.xml'):
                    file_path = os.path.join(addon_path, file)
                    with open(file_path) as f:
                        data = f.read()
                    # ensure no duplication in other instances
                    if 'id="m3uPath">{}</setting>'.format(m3uPath) in data or 'id="epgUrl">{}</setting>'.format(epgUrl) in data:
                        xbmcvfs.delete(os.path.join(addon_path, file_path))
                    else:
                        safe_copy(file_path, file_path+'.bu', del_src=True)

            kodi_rpc('Addons.SetAddonEnabled', {
                     'addonid': ADDON_ID, 'enabled': True})
            # wait for migration to occur
            while not os.path.exists(os.path.join(addon_path, 'instance-settings-1.xml')):
                monitor.waitForAbort(1)
            kodi_rpc('Addons.SetAddonEnabled', {
                     'addonid': ADDON_ID, 'enabled': False})
            monitor.waitForAbort(1)

            safe_copy(os.path.join(addon_path, 'instance-settings-1.xml'),
                      instance_filepath, del_src=True)
            with open(instance_filepath, 'r') as f:
                data = f.read()
            with open(instance_filepath, 'w') as f:
                f.write(data.replace('Migrated Add-on Config', ADDON_NAME))

            for file in os.listdir(addon_path):
                if file.endswith('.bu'):
                    safe_copy(os.path.join(addon_path, file), os.path.join(
                        addon_path, file[:-3]), del_src=True)
            kodi_rpc('Addons.SetAddonEnabled', {
                     'addonid': ADDON_ID, 'enabled': True})
        else:
            kodi_rpc('Addons.SetAddonEnabled', {
                     'addonid': ADDON_ID, 'enabled': True})

        set_kodi_setting('epg.futuredaystodisplay', 7)
        #  set_kodi_setting('epg.ignoredbforclient', True)
        set_kodi_setting('pvrmanager.syncchannelgroups', True)
        set_kodi_setting('pvrmanager.preselectplayingchannel', True)
        set_kodi_setting('pvrmanager.backendchannelorder', True)
        set_kodi_setting('pvrmanager.usebackendchannelnumbers', True)

    return True