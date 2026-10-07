from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import jobs, certificates

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0"
)
app.include_router(jobs.router)
app.include_router(certificates.router)

@app.get("/")
def home():
    return {
        "message": "Bulk Certificate Generator is running!"
    }