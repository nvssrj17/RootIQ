import logging
from fastapi import FastAPI 

from .database import Base, engine, SessionLocal
from .orders import router as orders_router
from .models import Order

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

db = SessionLocal()

if db.query(Order).count() == 0:
    db.add_all([
        Order(
            customer_name = "Alice",
            product = "Laptop",
            status = "confirmed"
        ),
        Order(
            customer_name = "Bob",
            product = "keyboard",
            status = "pending"
        ),
        Order(
            customer_name = "Charlie",
            product = "Monitor",
            status = "shipped"
        )
    ])
    db.commit()
db.close()
app.include_router(orders_router)

@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return{
        "status": "healthy"
    }