import unittest

from queue_worker import process_shipment


class QueueWorkerTest(unittest.TestCase):
    def test_successful_lookup_returns_backend_value(self):
        value = process_shipment("order-1", lambda order_id: {"order_id": order_id})
        self.assertEqual(value, {"order_id": "order-1"})


if __name__ == "__main__":
    unittest.main()
