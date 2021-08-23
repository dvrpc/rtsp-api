# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from lib import connections as c
import psycopg2 as psql
from psycopg2 import sql
import json
import re


# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.queryCheck, name='query1')
#     ]

# had been in rtps/urls.py
# url(r'^api/rtps/gap\?*', include('gap.urls')),


def munList():
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
        )
    )
    cur = con.cursor()
    cur.execute(
        "SELECT mun_name, geoid FROM zonemcd_join_region_wpnr_trim GROUP BY mun_name, geoid ORDER BY mun_name;"
    )
    rows = cur.fetchall()
    list = []
    for row in rows:
        list.append([row[0], row[1]])
    return JsonResponse(list, safe=False)


def zoneQuery(query):
    payload = {"status": None}
    parameters = query.split("&")
    for param in parameters:
        if "zones" in param:
            mo = re.findall(r"(\d+)", param)
            eh = ""
            for m in mo:
                eh += "{}, ".format(m)
            zones = "({})".format(eh[:-2])
        elif "direction" in param:
            direction = param.split("=")[1].replace("%20", "")
            if "To" in direction:
                oppo = "FromZone"
            else:
                oppo = "ToZone"
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
        )
    )
    cur = con.cursor()
    query = sql.SQL(c.zq.format(direction, oppo, zones))
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cargo = {}
        for row in rows:
            cargo[row[1]] = row[0]
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


def munQuery(query):
    payload = {"status": None}
    parameters = query.split("&")
    for p in parameters:
        if "muni" in p:
            m = re.match(r"^\w{4}=((\w+%20\w+%20\w+)|(\w+%20\w+)|(\w+))", p)
            if not m.group(4) is None:
                mcd = str(m.group(4))
            elif not m.group(3) is None:
                mcd = m.group(3).replace("%20", " ")
            elif not m.group(2) is None:
                mcd = m.group(2).replace("%20", " ")
        elif "direction" in p:
            direction = p.split("=")[1].replace("%20", "")
            if "To" in direction:
                oppo = "FromZone"
            else:
                oppo = "ToZone"
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
        )
    )
    cur = con.cursor()
    query = sql.SQL(c.mpmqScore.format(direction, oppo, mcd))

    try:
        cur.execute(query)
        rows = cur.fetchall()

        demandScore = rows.pop(0)
        cargo = {}

        for row in rows:
            cargo[str(row[0])] = row[1]

        payload["cargo"] = cargo
        payload["demandScore"] = demandScore

        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
            return JsonResponse(payload, safe=False)
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
            return JsonResponse(payload, safe=False)
    except Exception as e:
        payload["status"] = "failed"
        payload["message"] = "Invalid query parameters: " + e
        return JsonResponse(payload, safe=False)


def regionalSummary():
    payload = {"status": None}
    con = psql.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
        )
    )
    cur = con.cursor()
    try:
        cur.execute(c.rq)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[r[1]] = round(r[0], 2)
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "query returned no results"
    except:
        payload["status"] = "failed"
        payload["message"] = "invalid query parameters"
    return JsonResponse(payload, safe=False)


def queryCheck(request):
    check = request.get_full_path().split("?")[1]
    print(check)
    if check == "list":
        return munList()
    elif check == "summary":
        return regionalSummary()
    else:
        mo = re.match(r"^(\w+)=.*$", check)
        if mo.group(1) == "zones":
            return zoneQuery(check)
        else:
            return munQuery(check)
