#!/usr/bin/env python
# coding: utf-8
"""
地理情報関連ユーティリティ
"""
import os
import math
import json
import urllib
import urllib2

# 東西南北端の(緯度: latitude，経度: longitude)
# 世界測地系で算出
EAST  = ( 24.28305556, 153.98638889)
WEST  = ( 24.44944444, 122.93361111)
SOUTH = ( 20.42527778, 136.06972222)
NORTH = ( 45.55777778, 148.75388889)
LAT   = ( 24.28305556,  45.55777778)
LON   = (122.93361111, 153.98638889)

# findsの設定
url = 'http://www.finds.jp/ws/rgeocode.php?'

def rgeocode(lat, lon, lr=500, lx=1, ar=0, ax=0):
    """
    逆ジオコーディング
    via
    簡易逆ジオコーディングサービス
    http://www.finds.jp/wsdocs/rgeocode/
    by 独立行政法人農業・食品産業技術研究機構
    """
    vals = {
            'json': 1,
            'lat':  lat,
            'lon':  lon,
            'lr':   lr,
            'lx':   lx,
            'ar':   ar,
            'ax':   ax,
            }
    data = urllib.urlencode(vals)
    res  = urllib2.urlopen(url + data)
    js   = json.load(res)
    return js

def detect_jp_light(lat, lon, lr=500, lx=1, ar=0, ax=0):
    """
    緯度経度からの日本判定
    """
    flat, flon = float(lat), float(lon)
    # 緯度範囲チェック
    if flat < LAT[0] or flat > LAT[1]:
        return False
    # 経度範囲チェック
    if flon < LON[0] or flon > LON[1]:
        return False
    return True

def detect_jp(lat, lon, lr=500, lx=1, ar=0, ax=0):
    """
    緯度経度からの日本判定
    """
    if not detect_jp_light(lat, lon, lr, lx, ar, ax):
        return False
    # 日本範囲チェック
    js = rgeocode(lat, lon, lr, lx, ar, ax)
    status = js['status']
    if status == 400 or status == 500:
        return False
    return True

def deg2dms(lat, lon):
    """
    10進数表記(degree)から60進数表記(dms)へ変換
    """
    latd = int(lat)
    latm = int((lat - latd) * 60)
    lats = int(round((((lat - latd) * 60) - latm) * 60))
    lond = int(lon)
    lonm = int((lon - lond) * 60)
    lons = int(round((((lon - lond) * 60) - lonm) * 60))
    return (latd, latm, lats), (lond, lonm, lons)

def dms2deg(lat, lon):
    """
    60進数表記(dms)から10進数表記(deg)へ変換
    """
    latd, latm, lats = lat
    lond, lonm, lons = lon
    lat10 = round(latd + latm / 60.0 + lats / 3600.0, 8)
    lon10 = round(lond + lonm / 60.0 + lons / 3600.0, 8)
    return lat10, lon10

def TKY2WGS(lat, lon):
    """
    日本測地系から世界測地系へ変換
    東西南北端だと結構誤差がある簡易版
    """
    wlat = lat - lat * 0.00010695  + lon * 0.000017464 + 0.0046017;
    wlon = lon - lat * 0.000046038 - lon * 0.000083043 + 0.010040;
    return round(wlat, 8), round(wlon, 8)

def WGS2TKY(lat, lon):
    """
    世界測地系から日本測地系へ変換
    東西南北端だと結構誤差がある簡易版
    """
    jlat = lat + lat * 0.00010696  - lon * 0.000017467 - 0.0046020;
    jlon = lon + lat * 0.000046047 + lon * 0.000083049 - 0.010041;
    return round(jlat, 8), round(jlon, 8)

