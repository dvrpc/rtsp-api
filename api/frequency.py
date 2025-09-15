from enum import Enum

import psycopg

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


class FrequencyKind(str, Enum):
    zone = "zone"
    bus = "bus"
    rail = "rail"
    transit = "transit"


@router.get("/api/rtsp/v2/frequency/{type}")
def frequency(type: FrequencyKind):
    if type is FrequencyKind.zone:
        return zone()
    elif type is FrequencyKind.bus:
        return bus()
    elif type is FrequencyKind.rail:
        return rail()
    elif type is FrequencyKind.transit:
        return transit()


def zone():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                WITH a as (
                    SELECT zonenum,
                        basescen as tBase,
                        x2tfreqsc as tDouble,
                        changetact as tActual,
                        percchange as tPercent
                    FROM public."f_zonet"
                )
                SELECT public."f_zonev".zonenum,
                    public."f_zonev".basescen as vBase,
                    public."f_zonev".x2tfreqsc as vDouble,
                    public."f_zonev".changevact as vActual,
                    public."f_zonev".percchange as vPercent,
                    a.tBase as tBase,
                    a.tDouble as tDouble,
                    a.tActual as tActual,
                    a.tPercent as tPercent
                FROM public."f_zonev"
                JOIN a ON public."f_zonev".zonenum = a.zonenum;
                """
            )
        except psycopg.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for row in results:
        payload[int(round(row[0]))] = {
            "vBase": round(row[1], 2),
            "vDouble": round(row[2], 2),
            "vActual": round(row[3], 2),
            "vPercent": round(row[4], 2),
            "tBase": round(row[5], 2),
            "tDouble": round(row[6], 2),
            "tActual": round(row[7], 2),
            "tPercent": round(row[8], 2),
        }
    return payload


def bus():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename, changeride, percchange FROM f_bus")
        except psycopg.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = []
    for row in results:
        payload.append(
            {"linename": row[0], "AbsChange": round(row[1], 2), "Percent": round(row[2], 2)}
        )
    return payload


def rail():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename, changeride, percchange FROM f_rail")
        except psycopg.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for row in results:
        payload[row[0]] = {"absolute": round(row[1], 2), "percent": round(row[2], 2)}
    return payload


def transit():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename, ampeakfreq, avg_freq FROM f_existing")
        except psycopg.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for row in results:
        payload[str(row[0])] = {"am": round(row[1], 2), "avg_freq": round(row[2], 2)}
    return payload
