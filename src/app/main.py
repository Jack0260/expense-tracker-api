from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine
from .errors import install_error_handlers
from .routers import auth, expenses

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Expense Tracker API", version="0.1.0", lifespan=lifespan)
install_error_handlers(app)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
