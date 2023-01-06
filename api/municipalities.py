import psycopg2

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


@router.get("/api/rtps/v1/municipalities")
def municipality_list():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                SELECT mun_name, geoid
                FROM zonemcd_join_region_wpnr_trim
                GROUP BY mun_name, geoid
                ORDER BY mun_name
                """
            )
        except psycopg2.Error as e:
            return JSONResponse(status_code=500, content={"message": f"Database error: {e}"})
        results = cursor.fetchall()
    munis = []
    for row in results:
        munis.append([row[0], row[1]])
    return munis
