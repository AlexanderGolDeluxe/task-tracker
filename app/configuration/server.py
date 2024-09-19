from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.configuration.db_helper import db_helper
from app.configuration.initial_db_data import insert_all_initial_db_data
from app.configuration.routes import __routes__
from app.core.models import Base


class Server:

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routes(app)

    def get_app(self):
        return self.__app

    @staticmethod
    def __register_routes(app: FastAPI):
        __routes__.register_routers(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await insert_all_initial_db_data()
    yield
    await db_helper.engine.dispose()
