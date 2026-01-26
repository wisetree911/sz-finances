from app.api.routers.adm import routers as admin_routers
from app.api.routers.public import routers as public_routers
from app.core.logging import configure_logging_dev
from app.core.middleware import request_logging_middleware
from app.ws.routes import ws_router
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.redis.client import close_redis, create_redis

configure_logging_dev(log_level='INFO')

app = FastAPI()


@app.on_event('startup')
async def startup():
    app.state.redis = create_redis()
    await app.state.redis.ping()


@app.on_event('shutdown')
async def shutdown():
    await close_redis(app.state.redis)


app.middleware('http')(request_logging_middleware)

api_router = APIRouter(prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api_router.include_router(router=ws_router)

for r in public_routers:
    api_router.include_router(r)


for r in admin_routers:
    api_router.include_router(r, prefix='/admin')

app.include_router(api_router)
