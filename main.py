import fastapi

from api import access, frequency, gap, municipalities, reliability

app = fastapi.FastAPI()

app.include_router(access.router)
app.include_router(frequency.router)
app.include_router(gap.router)
app.include_router(municipalities.router)
app.include_router(reliability.router)
