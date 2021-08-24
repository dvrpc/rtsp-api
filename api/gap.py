import re

import fastapi
from fastapi import JSONResponse

from config import PG_CREDS
from main import db

# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.queryCheck, name='query1')
#     ]

# had been in rtps/urls.py
# url(r'^api/rtps/gap\?*', include('gap.urls')),

router = fastapi.APIRouter()


def munList():
    with db(PG_CREDS) as cursor:
        cursor.execute(
            """
            SELECT mun_name, geoid
            FROM zonemcd_join_region_wpnr_trim
            GROUP BY mun_name, geoid
            ORDER BY mun_name
            """
        )
        results = cursor.fetchall()
    list = []
    for row in results:
        list.append([row[0], row[1]])
    return list


def zoneQuery(query):
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

    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                WITH a as(
                    SELECT
                        "%s" as zone,
                        case when SUM("ConnectionScore"*demandscore)/SUM(demandscore) >= 5.5 then 'not served'
                            else 'served'
                        end status,
                        SUM("gapscore"*demandscore)/SUM(demandscore) AS w_avg_gap
                    FROM odgaps_ts_s_trim
                    WHERE "%s" IN %s
                    AND demandscore <> 0
                    GROUP BY "%s", gapscore, demandscore
                )

                SELECT
                    case when w_avg_gap < 7.5 AND status = 'served' then 1
                        when (w_avg_gap BETWEEN 7.5 AND 15) AND status = 'served' then 2
                        when (w_avg_gap BETWEEN 15 AND 22.5) AND status = 'served' then 3
                        when (w_avg_gap BETWEEN 22.5 AND 30) AND status = 'served' then 4
                        when (w_avg_gap BETWEEN 30 AND 37.5) AND status = 'served' then 5
                        when (w_avg_gap BETWEEN 37.5 AND 45) AND status = 'served' then 6
                        when w_avg_gap < 10 AND status = 'not served' then 7
                        when (w_avg_gap BETWEEN 10 AND 20) AND status = 'not served' then 8
                        when (w_avg_gap BETWEEN 20 AND 30) AND status = 'not served' then 9
                        when (w_avg_gap BETWEEN 30 AND 40) AND status = 'not served' then 10
                        when (w_avg_gap BETWEEN 40 AND 50) AND status = 'not served' then 11
                        when (w_avg_gap BETWEEN 50 AND 60) AND status = 'not served' then 12
                        else 13
                    end rank,
                    zone as no
                FROM a
                """,
                (direction, oppo, zones, direction),
            )
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for row in results:
        payload[row[1]] = row[0]
    return payload


def munQuery(query):
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

    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                WITH a AS(
                    SELECT
                        "%s" as zone,
                            case when SUM("ConnectionScore"*demandscore)/SUM(demandscore) >= 5.5 then 'not served'
                                else 'served'
                            end status,
                        SUM("gapscore"*demandscore)/SUM(demandscore) AS w_avg_gap,
                        SUM("DailyVols") AS sumvol
                    FROM odgaps_ts_s_trim
                    WHERE "%s" IN(
                        SELECT
                            no
                        FROM zonemcd_join_region_wpnr_trim
                        WHERE geoid = '%s' )
                    AND demandscore <> 0
                    GROUP BY "%s"
                )

                SELECT
                    ROUND(SUM(sumvol)) rank,
                    NULL AS no
                FROM a

                UNION ALL

                SELECT
                    zone as no,
                    case when w_avg_gap < 7.5 AND status = 'served' then 1
                        when (w_avg_gap BETWEEN 7.5 AND 15) AND status = 'served' then 2
                        when (w_avg_gap BETWEEN 15 AND 22.5) AND status = 'served' then 3
                        when (w_avg_gap BETWEEN 22.5 AND 30) AND status = 'served' then 4
                        when (w_avg_gap BETWEEN 30 AND 37.5) AND status = 'served' then 5
                        when (w_avg_gap BETWEEN 37.5 AND 45) AND status = 'served' then 6
                        when w_avg_gap < 10 AND status = 'not served' then 7
                        when (w_avg_gap BETWEEN 10 AND 20) AND status = 'not served' then 8
                        when (w_avg_gap BETWEEN 20 AND 30) AND status = 'not served' then 9
                        when (w_avg_gap BETWEEN 30 AND 40) AND status = 'not served' then 10
                        when (w_avg_gap BETWEEN 40 AND 50) AND status = 'not served' then 11
                        when (w_avg_gap BETWEEN 50 AND 60) AND status = 'not served' then 12
                        else 13
                    end rank
                FROM a;
            """,
                (direction, oppo, mcd, direction),
            )
        except Exception as e:
            return JSONResponse({"message": "Invalid query parameters " + str(e)})
        results = cursor.fetchall()

    if not results:
        return JSONResponse({"message": "No results"})
    demandScore = results.pop(0)
    cargo = {}
    for row in results:
        cargo[str(row[0])] = row[1]
    return {"cargo": cargo, "demandScore": demandScore}


def regionalSummary():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                SELECT
                    case when w_avgscore < 7.5 AND w_avgcon < 5.5 then 1
                        when (w_avgscore BETWEEN 7.5 AND 15) AND w_avgcon < 5.5 then 2
                        when (w_avgscore BETWEEN 15 AND 22.5) AND w_avgcon < 5.5 then 3
                        when (w_avgscore BETWEEN 22.5 AND 30) AND w_avgcon < 5.5 then 4
                        when (w_avgscore BETWEEN 30 AND 37.5) AND w_avgcon < 5.5 then 5
                        when (w_avgscore BETWEEN 37.5 AND 45) AND w_avgcon < 5.5 then 6
                        when w_avgscore < 10 AND w_avgcon >= 5.5 then 7
                        when (w_avgscore BETWEEN 10 AND 20) AND w_avgcon >= 5.5 then 8
                        when (w_avgscore BETWEEN 20 AND 30) AND w_avgcon >= 5.5 then 9
                        when (w_avgscore BETWEEN 30 AND 40) AND w_avgcon >= 5.5 then 10
                        when (w_avgscore BETWEEN 40 AND 50) AND w_avgcon >= 5.5 then 11
                        when (w_avgscore BETWEEN 50 AND 60) AND w_avgcon >= 5.5 then 12
                        else 13
                    end rank,
                    zone as no
                FROM g_summary ORDER BY zone
                """
            )
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[r[1]] = round(r[0], 2)
    return payload


@router.get("/api/rtps/v1/gap")
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
