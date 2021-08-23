# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse, HttpResponse
from lib import connections as c
import psycopg2, re

# had been in this module's urls.py:
# urlpatterns = [
#     url(r'^$', views.pageLoad, name='pageLoad')
# ]

# had been in rtps/urls.py
# url(r'^api/rtps/access\?*', include('access.urls')),

# Create your views here.
def stations():
    try:
        con = psycopg2.connect(
            "dbname='{}' host='{}' password='{}' user='{}'".format(
                c.DB_NAME, c.DB_HOST, c.DB_PW, c.DB_USER
            )
        )
        cursor = con.cursor()
        cursor.execute(c.stations_all)
        stations = cursor.fetchall()
        payload = {}
        columns = [desc[0] for desc in cursor.description]
        for station in stations:
            cargo = {}
            cnt = 0
            for col in columns:
                if not col == "dvrpc_id":
                    cargo["{}".format(col)] = station[cnt]
                else:
                    cargo["{}".format(col)] = int(station[cnt])
                cnt += 1
            payload["{}".format(cargo["dvrpc_id"])] = cargo
        if not len(payload) == 0:
            return JsonResponse(payload, safe=False)
        else:
            return HttpResponse("yo")
    except Exception as e:
        print(e)


def zones():
    try:
        con = psycopg2.connect(
            "dbname='{}' host='{}' password='{}' user='{}'".format(
                c.DB_NAME, c.DB_HOST, c.DB_PW, c.DB_USER
            )
        )
        cursor = con.cursor()
        cursor.execute(c.zones_all)
        zones = cursor.fetchall()
        payload = {}
        columns = [desc[0] for desc in cursor.description]
        for zone in zones:
            cargo = {}
            cnt = 0
            for col in columns:
                cargo["{}".format(col)] = int(zone[cnt])
                cnt += 1
            payload["{}".format(cargo["no"])] = cargo
        if not len(payload) == 0:
            return JsonResponse(payload, safe=False)
        else:
            return HttpResponse("yo")
    except Exception as e:
        print(e)


def pageLoad(request):
    path = request.get_full_path()
    exp = re.compile(r"^/\w{3}/\w{4}/\w{6}\?(?=(stations|zones))")
    mo = re.search(exp, path)
    if "stations" in mo.group(1):
        payload = stations()
    elif "zones" in mo.group(1):
        payload = zones()
    return payload
