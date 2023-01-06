from enum import Enum

import psycopg2

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


class DirectionKind(str, Enum):
    tozone = "ToZone"
    fromzone = "FromZone"


@router.get("/api/rtsp/v2/gap/zones/{zones}/{direction}")
def gaps_by_zones(zones: str, direction: DirectionKind):
    if direction is DirectionKind.tozone:
        chosen_direction = "ToZone"
        opposite_direction = "FromZone"
    elif direction is DirectionKind.fromzone:
        chosen_direction = "FromZone"
        opposite_direction = "ToZone"

    zones = tuple([zone for zone in zones.split(",")])

    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                f"""WITH a as (
                    SELECT "{chosen_direction}" as zone,
                        case 
                            when SUM("ConnectionScore"*demandscore)/SUM(demandscore) >= 5.5 
                            then 'not served'
                            else 'served'
                        end status,
                        SUM(gapscore*demandscore)/SUM(demandscore) AS w_avg_gap
                    FROM odgaps_ts_s_trim
                    WHERE "{opposite_direction}" IN %s
                    AND demandscore <> 0
                    GROUP BY "{chosen_direction}", gapscore, demandscore
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
                FROM a;
                """,
                (zones,),
            )
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()

    payload = {}
    for row in results:
        payload[row[1]] = row[0]
    return payload


@router.get("/api/rtsp/v2/gap/muni/{mcd}/{direction}")
def gaps_by_municipality(mcd: str, direction: DirectionKind):
    if direction is DirectionKind.tozone:
        chosen_direction = "ToZone"
        opposite_direction = "FromZone"
    elif direction is DirectionKind.fromzone:
        chosen_direction = "FromZone"
        opposite_direction = "ToZone"

    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                f"""WITH a AS(
                    SELECT 
                        "{chosen_direction}" as zone,
                        case 
                            when SUM("ConnectionScore"*demandscore)/SUM(demandscore) >= 5.5 
                            then 'not served'
                            else 'served'
                        end status,
                        SUM(gapscore*demandscore)/SUM(demandscore) AS w_avg_gap,
                        SUM("DailyVols") AS sumvol
                    FROM odgaps_ts_s_trim
                    WHERE "{opposite_direction}" IN (
                        SELECT
                            no
                        FROM zonemcd_join_region_wpnr_trim
                        WHERE geoid = %s )
                    AND demandscore <> 0
                    GROUP BY "{chosen_direction}"
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
                (mcd,),
            )
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()

    if not results:
        return []

    demand_score = results.pop(0)
    gaps = {}
    for row in results:
        gaps[str(row[0])] = row[1]
    return {"gaps": gaps, "demand_score": demand_score}


@router.get("/api/rtsp/v2/gap/summary")
def gaps_summary():
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
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    payload = {}
    for r in results:
        payload[r[1]] = round(r[0], 2)
    return payload
