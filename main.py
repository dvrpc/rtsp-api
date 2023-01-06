import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api import access, frequency, gap, municipalities, reliability


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DVRPC RTPS API",
        version="1.0",
        description=(
            "API for the Delaware Valley Regional Planning Commission's Regional Transit "
            "Screening Platform."
        ),
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = fastapi.FastAPI(openapi_url="/api/rtps/v1/openapi.json", docs_url="/api/rtps/v1/docs")
app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(access.router)
app.include_router(frequency.router)
app.include_router(gap.router)
app.include_router(municipalities.router)
app.include_router(reliability.router)
