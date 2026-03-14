from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import links, users
from app.core.database import engine, Base, get_db
import threading
from sqlalchemy.orm import Session 
from app.services.cleanup_service import start_cleanup_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(links.router, prefix=settings.API_V1_STR + "/links", tags=["links"])
app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "URL Shortener"}

@app.get("/{short_code}")
def root_redirect(
    short_code: str, 
    db: Session = Depends(get_db)
):
    """Redirect from root path (e.g., /google-test)"""
    from app.api.endpoints.links import redirect_to_original
    return redirect_to_original(short_code, db)

@app.get("/")
def root():
    return {
        "message": "Welcome to URL Shortener Service",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_cleanup_scheduler, daemon=True)
    thread.start()
    print("Service started successfully")