import os
import logging

import requests

logger = logging.getLogger(__name__)


def send_order_notification(order_id: int) -> bool:
    """Send an order notification to the external notification service."""

    notification_url = os.getenv("NOTIFICATION_URL")

    if not notification_url:
        logger.error(
            "NOTIFICATION_URL is not configured"
        )
        return False

    try:
        response = requests.post(
            notification_url,
            json={"order_id": order_id},
            timeout=5
        )

        response.raise_for_status()

        logger.info(
            "Order notification sent successfully for order %s",
            order_id
        )

        return True

    except requests.RequestException:
        logger.exception(
            "Notification service request failed for order %s",
            order_id
        )

        return False