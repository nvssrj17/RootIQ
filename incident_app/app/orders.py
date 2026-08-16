from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 

from .database import get_db
from .models import Order

router = APIRouter()

@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return {
            "error" : "Order not found"
        }

    return{
        "id" : order.id,
        "customer_name": order.customer_name,
        "product": order.product,
        "status": order.status
    }
