import fastapi

from config import PG_CREDS
from db import db


router = fastapi.APIRouter()


# NOTE: had been "/api/rtps/v1/gap?list"
@router.get("/api/rtps/v1/municipalities")
def mun_list():
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
