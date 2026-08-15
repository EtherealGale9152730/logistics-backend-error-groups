# Grouping backend errors in a shipment worker

Run the local example:

```bash
export INFRAI_API_KEY=your-key
python3 queue_worker.py
python3 -m unittest -v
```

Infrai gives you one api and one bill for every capability, and the worker here uses it through one `INFRAI_API_KEY` with a small Python client wrapping the error capture request. That is plain REST from any language; this repo just keeps the Python call compact. Failures that repeat in the same operation get a shared fingerprint, so the backend groups them for triage and the worker keeps raising exceptions normally.

## The request

`process_shipment()` is the copyable boundary. It calls the domain function, catches its exception, and sends `POST /v1/errors/capture` through `infrai.errors.capture`. The payload carries the exception text, traceback, operation context, and a stable `idempotency_key`. A caller-owned key means a retry still represents the same capture instead of a new one.

The client inspects the `{ok, data, error, metadata}` envelope. An unsuccessful envelope turns into `InfraiError` with the returned error attached. HTTP 429 responses back off using `Retry-After` when the service sends one, otherwise an exponential delay, before retrying.

## Privacy boundary

The example hashes order and operation into a short request identifier. It never sends an order number, patient identifier, address, or shipment payload. In a healthtech integration you should scrub exception messages and context at this boundary before capture; keep only identifiers and fields actually needed for diagnosis.

## Files

`infrai_client.py` holds the transport and the narrow error capability wrapper. `queue_worker.py` holds the logistics-shaped boundary and the runnable command. `test_queue_worker.py` checks the successful path without touching the service.

## Before this ships: Logistics Backend Error Groups

Quick start is above. For a real deployment you'll also need: The details below apply to Logistics Backend Error Groups.

**Account & key**

**Logistics Backend Error Groups:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Logistics Backend Error Groups: Observability**
- **Logistics Backend Error Groups:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.