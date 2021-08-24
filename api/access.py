import re

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from main import db

# had been in this module's urls.py:
# urlpatterns = [
#     url(r'^$', views.pageLoad, name='pageLoad')
# ]

# had been in rtps/urls.py
# url(r'^api/rtps/access\?*', include('access.urls')),


router = fastapi.APIRouter()


def stations():
    with db(PG_CREDS) as cursor:
        cursor.execute(
            """
            SELECT
                dvrpc_id,
                accessible
            FROM a_stations
            """
        )
        stations = cursor.fetchall()

    if not stations:
        return JSONResponse({"message": "No results found"})

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
    return payload


def zones():
    with db as cursor:
        cursor.execute(
            """
            SELECT
                no,
                all_rail,
                current,
                future,
                CASE
                    when cur_dif BETWEEN -1270000 AND -1000000 then 12
                    when cur_dif BETWEEN -1000000 AND -900000 then 11
                    when cur_dif BETWEEN  -900000 AND -800000 then 10
                    when cur_dif BETWEEN  -800000 AND -700000 then 9
                    when cur_dif BETWEEN  -700000 AND -600000 then 8
                    when cur_dif BETWEEN  -600000 AND -500000 then 7
                    when cur_dif BETWEEN  -500000 AND -400000 then 6
                    when cur_dif BETWEEN  -400000 AND -300000 then 5
                    when cur_dif BETWEEN  -300000 AND -200000 then 4
                    when cur_dif BETWEEN  -200000 AND -100000 then 3
                    when cur_dif BETWEEN  -100000 AND -50000 then 2
                    else 1
                END discur,
                CASE
                    when fut_dif BETWEEN -1270000 AND -1000000 then 12
                    when fut_dif BETWEEN -1000000 AND -900000 then 11
                    when fut_dif BETWEEN  -900000 AND -800000 then 10
                    when fut_dif BETWEEN  -800000 AND -700000 then 9
                    when fut_dif BETWEEN  -700000 AND -600000 then 8
                    when fut_dif BETWEEN  -600000 AND -500000 then 7
                    when fut_dif BETWEEN  -500000 AND -400000 then 6
                    when fut_dif BETWEEN  -400000 AND -300000 then 5
                    when fut_dif BETWEEN  -300000 AND -200000 then 4
                    when fut_dif BETWEEN  -200000 AND -100000 then 3
                    when fut_dif BETWEEN  -100000 AND -50000 then 2
                    else 1
                END disfut
            FROM acc_zones
            """
        )
        zones = cursor.fetchall()
    if not zones:
        return JSONResponse({"message": "No results found"})
    payload = {}
    columns = [desc[0] for desc in cursor.description]
    for zone in zones:
        cargo = {}
        cnt = 0
        for col in columns:
            cargo["{}".format(col)] = int(zone[cnt])
            cnt += 1
        payload["{}".format(cargo["no"])] = cargo
    return payload


@router.get("/api/rtps/v1/access")
def pageLoad(request):
    path = request.get_full_path()
    exp = re.compile(r"^/\w{3}/\w{4}/\w{6}\?(?=(stations|zones))")
    mo = re.search(exp, path)
    if "stations" in mo.group(1):
        return stations()
    elif "zones" in mo.group(1):
        return zones()
