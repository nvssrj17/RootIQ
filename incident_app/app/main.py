import logging
from fastapi import FastAPI 

from .database import Base, engine
from .orders import router as orders_router

logging.basicConfig(
    filename="logs/application.log",
    level = logging.INFO,
    format= "%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title = "RootIQ Incident Demo"
)

Base.metadata.create_all(bind=engine)
app.include_router(orders_router)

@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return{
        "status": "healthy"
    }