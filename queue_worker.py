"""Run one shipment lookup and group backend failures by operation."""
import hashlib
import traceback

import infrai_client


def capture_backend_error(order_id, operation, exc):
    """Send useful diagnostics without sending patient or customer details."""
    request_id = hashlib.sha256(f"{order_id}:{operation}".encode()).hexdigest()[:16]
    return infrai_client.infrai.errors.capture(
        title=f"logistics/{operation} failed",
        message=f"{type(exc).__name__}: {exc}",
        exception=traceback.format_exc(),
        level="error",
        fingerprint=["logistics", operation],
        context={"operation": operation, "request_id": request_id},
        idempotency_key=f"shipment-error:{request_id}",
    )


def process_shipment(order_id, lookup):
    """Execute a shipment lookup; capture and re-raise its backend exception."""
    try:
        return lookup(order_id)
    except Exception as exc:
        capture_backend_error(order_id, "shipment_lookup", exc)
        raise


if __name__ == "__main__":
    def demo_lookup(_order_id):
        return {"status": "in_transit", "carrier": "local"}

    print(process_shipment("order-demo-17", demo_lookup))
