import asyncio

from app.api.routers.public import routers as public_routers
from app.core.logging import configure_logging_dev
from app.core.middleware import request_logging_middleware
from app.core.redis import close_redis, create_redis
from app.ws.redis_listener import redis_prices_listener
from app.ws.routes import ws_router
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

configure_logging_dev(log_level='INFO')

app = FastAPI()

app.middleware('http')(request_logging_middleware)


@app.on_event('startup')
async def on_startup() -> None:
    app.state.redis = create_redis()
    app.state.redis_prices_task = asyncio.create_task(redis_prices_listener(app.state.redis))


@app.on_event('shutdown')
async def on_shutdown() -> None:
    task = getattr(app.state, 'redis_prices_task', None)
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    r = getattr(app.state, 'redis', None)
    if r is not None:
        await close_redis(r)


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


# for r in admin_routers:
#     api_router.include_router(r)

app.include_router(api_router)
