import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Order

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    logger.info("Fetching order %s", order_id)

    try:
        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:
            logger.warning("Order %s not found", order_id)

            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        logger.info(
            "Successfully retrieved order %s",
            order_id
        )

        return {
            "id": order.id,
            "customer_name": order.customer_name,
            "product": order.product,
            "status": order.status
        }

    except SQLAlchemyError:
        logger.exception(
            "Database error while fetching order %s",
            order_id
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
