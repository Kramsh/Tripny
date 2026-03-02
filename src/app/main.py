from fastapi import FastAPI
from src.app.routers.trips import router


app = FastAPI()
app.include_router(router)
