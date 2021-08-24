import fastapi
from fastapi import JSONResponse

from config import PG_CREDS
from main import db

# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.Route, name='query1')
#     ]

# had been in rtps/urls.py
# url(r'^api/rtps/reliability\?*', include('reliability.urls'))

router = fastapi.APIRouter()

score_query = """
    SELECT gid,
        lines,
        reliscore as score
    FROM rel_reliabilityscore_t_ng
    GROUP BY gid, lines, score;
    """

# TODO: this is not used, was it supposed to be?
r_weighted = "SELECT gid, lines, riderrelis as weighted FROM rel_reliabilityscore_t_ng"


def LoadTTI():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, tti FROM rel_tti_t_ng")
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = round(r[1], 2)
    return payload


def LoadScore():
    payload = {"status": None}
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(score_query)
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {
            "lines": r[1],
            "score": round(r[2], 2),
        }
    return payload


def LoadWeighted():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(score_query)
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {
            "lines": r[1],
            "weighted": round(r[2], 2),
        }
    return payload


def LoadSpeed():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, linename, avgspeed FROM rel_avgschedspeed_ng")
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "avg_speed": round(r[2])}
    return payload


def LoadOTP():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, linename, otp FROM rel_line_ridershipotp_t_ng")
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "otp": round(r[2], 2)}
    return payload


def LoadSEPTARidership():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(" SELECT gid, route, tot_loads FROM surfacetransitloads_ng")
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "total_loads": round(r[2], 2)}
    return payload


def LoadNJTRidership():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                SELECT gid,
                    linename,
                    dailyrider
                FROM rel_line_ridershipotp_t_ng
                WHERE (division = 'WRTC' or division is null) AND (linename NOT IN ('47M', 'LUCYGO', 'LUCYGR'));
                """
            )
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "ridership": round(r[2], 2)}
    return payload


def LoadFilterRoutes():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename FROM rel_line_ridershipotp_t_ng GROUP BY linename")
        except:
            return JSONResponse({"message": "Invalid query parmaters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for r in results:
        payload[str(r[0])] = str(r[0])
    return payload


@router.get("/api/rtps/v1/reliability")
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
