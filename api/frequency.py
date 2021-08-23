# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse, HttpResponse
from lib import connections as c
import psycopg2 as psql
from psycopg2 import sql
import re

from django.shortcuts import render

# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.pageLoad, name='pageLoad')
# ]

# had been in rtps/urls.py
# url(r'^api/rtps/frequency\?*', include('frequency.urls')),

# Create your views here.
def zoneLoad():
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PW
        )
    )
    cur = con.cursor()
    query = psql.sql.SQL(c.freq_zoneq)
    payload = {"status": None}
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cargo = {}
        for row in rows:
            cargo[int(round(row[0]))] = {
                "vBase": round(row[1], 2),
                "vDouble": round(row[2], 2),
                "vActual": round(row[3], 2),
                "vPercent": round(row[4], 2),
                "tBase": round(row[5], 2),
                "tDouble": round(row[6], 2),
                "tActual": round(row[7], 2),
                "tPercent": round(row[8], 2),
            }
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
            return JsonResponse(payload, safe=False)
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
            return JsonResponse(payload, safe=False)
    except:
        payload["status"] = "failed"
        payload["message"] = "Invalid query parameters"
        return JsonResponse(payload, safe=False)


def busLoad():
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PW
        )
    )
    cur = con.cursor()
    query = psql.sql.SQL(c.freq_busq)
    payload = {"status": None}
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cargo = []
        for r in rows:
            cargo.append({"linename": r[0], "AbsChange": round(r[1], 2), "Percent": round(r[2], 2)})
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
            return JsonResponse(payload, safe=False)
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
            return JsonResponse(payload, safe=False)
    except:
        payload["status"] = "failed"
        payload["message"] = "Invalid query parameters"
        return JsonResponse(payload, safe=False)


def railLoad():
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PW
        )
    )
    cur = con.cursor()
    query = psql.sql.SQL(c.freq_railq)
    payload = {"status": None}
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cargo = {}
        for r in rows:
            cargo[r[0]] = {"absolute": round(r[1], 2), "percent": round(r[2], 2)}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
            return JsonResponse(payload, safe=False)
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
            return JsonResponse(payload, safe=False)
    except:
        payload["status"] = "failed"
        payload["message"] = "Invalid query parameters"
        return JsonResponse(payload, safe=False)


def transitLoad():
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PW
        )
    )
    cur = con.cursor()
    query = psql.sql.SQL(c.freq_transitq)
    payload = {"status": None}
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cargo = {}
        for r in rows:
            cargo[str(r[0])] = {"am": round(r[1], 2), "avg_freq": round(r[2], 2)}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
            return JsonResponse(payload, safe=False)
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
            return JsonResponse(payload, safe=False)
    except:
        payload["status"] = "failed"
        payload["message"] = "Invalid query parameters"
        return JsonResponse(payload, safe=False)


def pageLoad(request):
    path = request.get_full_path()
    exp = re.compile(r"^/\w{3}/\w{4}/\w{9}\?(?=(zone|bus|rail|transit))")
    mo = re.search(exp, path)
    if "zone" in mo.group(1):
        payload = zoneLoad()
    elif "bus" in mo.group(1):
        payload = busLoad()
    elif "rail" in mo.group(1):
        payload = railLoad()
    elif "transit" in mo.group(1):
        payload = transitLoad()
    else:
        payload = {"status": "failed", "message": "something went wrong."}
    return payload
