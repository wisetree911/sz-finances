from fastapi import FastAPI, APIRouter
from app.api.routers import routers as public_routers
from app.api.routers.adm import routers as admin_routers


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in public_routers:
    api_router.include_router(r)

for r in admin_routers:
    api_router.include_router(r)
    
app.include_router(api_router)