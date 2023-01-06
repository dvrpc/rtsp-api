from enum import Enum

import psycopg2

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


class AccessKind(str, Enum):
    stations = "stations"
    zones = "zones"


@router.get("/api/rtps/v1/access/{type}")
def access(type: AccessKind):
    if type is AccessKind.stations:
        return stations()
    elif type is AccessKind.zones:
        return zones()


def stations():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT dvrpc_id, accessible FROM a_stations")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        stations = cursor.fetchall()

    if not stations:
        return {}

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
    with db(PG_CREDS) as cursor:
        try:
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
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        zones = cursor.fetchall()

    if not zones:
        return {}

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
