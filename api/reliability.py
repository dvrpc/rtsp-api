from enum import Enum

import psycopg2

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


class ReliabilityKind(str, Enum):
    tti = "tti"
    weighted = "weighted"
    score = "score"
    speed = "speed"
    otp = "otp"
    septa = "septa"
    njt = "njt"
    filter = "filter"


@router.get("/api/rtsp/v2/reliability/{type}")
def Reliability(type: ReliabilityKind):
    if type is ReliabilityKind.tti:
        return tti()
    elif type is ReliabilityKind.weighted:
        return weighted()
    elif type == ReliabilityKind.score:
        return score()
    elif type == ReliabilityKind.speed:
        return speed()
    elif type == ReliabilityKind.otp:
        return otp()
    elif type == ReliabilityKind.septa:
        return septa()
    elif type == ReliabilityKind.njt:
        return njt()
    elif type == ReliabilityKind.filter:
        return filter()


score_query = """
    SELECT gid,
        lines,
        reliscore as score
    FROM rel_reliabilityscore_t_ng
    GROUP BY gid, lines, score;
    """

# TODO: this is not used, was it supposed to be?
r_weighted = "SELECT gid, lines, riderrelis as weighted FROM rel_reliabilityscore_t_ng"


def tti():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, tti FROM rel_tti_t_ng")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = round(r[1], 2)
    return payload


def score():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(score_query)
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {
            "lines": r[1],
            "score": round(r[2], 2),
        }
    return payload


def weighted():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(score_query)
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {
            "lines": r[1],
            "weighted": round(r[2], 2),
        }
    return payload


def speed():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, linename, avgspeed FROM rel_avgschedspeed_ng")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "avg_speed": round(r[2])}
    return payload


def otp():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, linename, otp FROM rel_line_ridershipotp_t_ng")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "otp": round(r[2], 2)}
    return payload


def septa():
    """Septa ridership"""
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT gid, route, tot_loads FROM surfacetransitloads_ng")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "total_loads": round(r[2], 2)}
    return payload


def njt():
    """NJT ridership"""
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                SELECT gid,
                    linename,
                    dailyrider
                FROM rel_line_ridershipotp_t_ng
                WHERE 
                    (division = 'WRTC' or division is null) AND 
                    (linename NOT IN ('47M', 'LUCYGO', 'LUCYGR'));
                """
            )
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = {"line": r[1], "ridership": round(r[2], 2)}
    return payload


def filter():
    """Filter routes"""
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename FROM rel_line_ridershipotp_t_ng GROUP BY linename")
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[str(r[0])] = str(r[0])
    return payload
