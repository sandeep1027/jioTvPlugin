# -*- coding: utf-8 -*-
import os
from xbmcvfs import translatePath
import xbmcaddon
import urlquick
import json

ADDON = xbmcaddon.Addon()

# Urls
IMG_PUBLIC = "https://jioimages.cdn.jio.com/imagespublic/"
IMG_CATCHUP = "http://jiotv.catchup.cdn.jio.com/dare_images/images/"
IMG_CATCHUP_SHOWS = "http://jiotv.catchup.cdn.jio.com/dare_images/shows/"
PLAY_URL = "plugin://jioTvPlugin/resources/lib/main/play/?"
FEATURED_SRC = "https://tv.media.jio.com/apis/v1.6/getdata/featurednew?start=0&limit=30&langId=6"
CHANNELS_SRC = "https://jiotv.data.cdn.jio.com/apis/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone&usertype=tvYR7NSNn7rymo3F&version=285&langId=6"
GET_CHANNEL_URL = "https://tv.media.jio.com/apis/v2.0/getchannelurl/getchannelurl?langId=6&userLanguages=All"
CATCHUP_SRC = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?offset={0}&channel_id={1}&langId=6"
M3U_SRC = os.path.join(translatePath(
    ADDON.getAddonInfo("profile")), "playlist.m3u")
M3U_CHANNEL = "\n#EXTINF:0 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" group-title=\"{group_title}\" tvg-chno=\"{tvg_chno}\" tvg-logo=\"{tvg_logo}\"{catchup},{channel_name}\n{play_url}"
EPG_SRC = "https://kodi.botallen.com/tv/epg.xml.gz"

DICTIONARY_URL = "https://jiotvapi.cdn.jio.com/apis/v1.3/dictionary/dictionary?langId=6"

# Configs
GENRE_CONFIG = [
    {
        "name": "News",
        "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
    },
    {
        "name": "Music",
        "tvImg":  IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
    },
    {

        "name": "Sports",
        "tvImg":  IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",

    },
    {

        "name": "Entertainment",
        "tvImg":  IMG_PUBLIC + "38/52/Entertainment_1584620980069_tv.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Entertainment_1579245819981.jpg",

    },
    {

        "name": "Devotional",
        "tvImg":  IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",

    },
    {
        "name": "Movies",
        "tvImg":  IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",

    },
    {
        "name": "Infotainment",
        "tvImg":  IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",

    },
    {
        "name": "Business",
        "tvImg":  IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
    },
    {
        "name": "Kids",
        "tvImg":  IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
    },
    {
        "name": "Lifestyle",
        "tvImg":  IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
    },
    {
        "name": "Jio Darshan",
        "tvImg":  IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
    },
    {
        "name": "Shopping",
        "tvImg":  IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
    },
    {
        "name": "Educational",
        "tvImg":  IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
    },
    {
        "name": "Jio Darshan",
        "tvImg":  IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
    }
]
resp = urlquick.get(DICTIONARY_URL).text.encode('utf8')[3:].decode('utf8')
dictionary = json.loads(resp)
GENRE_MAP = dictionary.get("channelCategoryMapping")
LANG_MAP = dictionary.get("languageIdMapping")
tmpArray = []
for dictArray in dictionary.get("languageOnBoarding"):
    tmpArray.append({
        "name": dictArray.get("title"),
        "tvImg": dictArray.get("image"),
        "promoImg": dictArray.get("image"),
    })

LANGUAGE_CONFIG = tmpArray
CONFIG = {"Genres": GENRE_CONFIG, "Languages": LANGUAGE_CONFIG}
