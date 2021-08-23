# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from lib import connections as c
import psycopg2 as psql

from django.shortcuts import render


# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.Route, name='query1')
#     ]

# had been in rtps/urls.py
# url(r'^api/rtps/reliability\?*', include('reliability.urls'))


def LoadTTI():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_tti)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = round(r[1], 2)
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadScore():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_score)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {
                "lines": r[1],
                "score": round(r[2], 2),
            }
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadWeighted():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_score)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {
                "lines": r[1],
                "weighted": round(r[2], 2),
            }
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadSpeed():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_speed)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {"line": r[1], "avg_speed": round(r[2])}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadOTP():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_otp)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {"line": r[1], "otp": round(r[2], 2)}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "Query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadSEPTARidership():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_septa)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {"line": r[1], "total_loads": round(r[2], 2)}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadNJTRidership():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_njt)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = {"line": r[1], "ridership": round(r[2], 2)}
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "query returned no results"
    except Exception as e:
        payload["status"] = "Failed"
        payload["message"] = "Invalid query parameters"
    return JsonResponse(payload, safe=False)


def LoadFilterRoutes():
    payload = {"status": None}
    try:
        con = psql.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                c.DB_NAME, c.DB_USER, c.DB_HOST, c.DB_PASS
            )
        )
        cur = con.cursor()
        cur.execute(c.r_filter)
        results = cur.fetchall()
        cargo = {}
        for r in results:
            cargo[str(r[0])] = str(r[0])
        payload["cargo"] = cargo
        if not len(payload["cargo"]) == 0:
            payload["status"] = "success"
        else:
            payload["status"] = "failed"
            payload["message"] = "query returned no results"
    except Exception as e:
        payload["status"] = "failed"
        payload["message"] = "invalid query parameters"
    return JsonResponse(payload, safe=False)


def Route(request):
    check = request.get_full_path().split("?")[1]
    if check == "tti":
        return LoadTTI()
    elif check == "weighted":
        return LoadWeighted()
    elif check == "score":
        return LoadScore()
    elif check == "speed":
        return LoadSpeed()
    elif check == "otp":
        return LoadOTP()
    elif check == "septa":
        return LoadSEPTARidership()
    elif check == "njt":
        return LoadNJTRidership()
    elif check == "filter":
        return LoadFilterRoutes()
