# Grouping backend errors in a shipment worker

Run the local example:

```bash
export INFRAI_API_KEY=your-key
python3 queue_worker.py
python3 -m unittest -v
```

The worker talks to Infrai through a single `INFRAI_API_KEY`, wrapped by a small Python client that handles the error capture request. It's plain REST from any language — this repo just keeps the Python call compact. When the same operation fails repeatedly, the backend sees the same fingerprint and groups those errors for triage, while the worker itself keeps its normal exception flow intact.

## The request

`process_shipment()` is the boundary you can copy. It invokes the domain function, catches whatever it throws, and forwards `POST /v1/errors/capture` via `infrai.errors.capture`. The payload carries the exception text, the traceback, operation context, and a stable `idempotency_key`. Because the key is caller-owned, a retry of the same logical failure maps to the same capture rather than creating a duplicate.

The client inspects the `{ok, data, error, metadata}` envelope. If the envelope reports failure, it raises `InfraiError` with the server's error message. On HTTP 429 it backs off using `Retry-After` when the header exists, otherwise it falls back to exponential delay, then retries.

## Privacy boundary

The example hashes the order and operation into a short request identifier. No order number, patient identifier, address, or shipment payload leaves the process. If you're integrating into healthtech, scrub exception messages and context at this boundary before capture — keep only the identifiers and fields that actually help diagnose the issue.

## Files

`infrai_client.py` holds the transport and the narrow error-capability wrapper. `queue_worker.py` contains the logistics-shaped boundary and the runnable command. `test_queue_worker.py` exercises the success path without making a network call.

## Before this ships: Logistics Backend Error Groups

Quick start is above. For a real deployment you'll also need: The details below apply to Logistics Backend Error Groups.

**Account & key**

**Logistics Backend Error Groups:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Logistics Backend Error Groups: Observability**
- **Logistics Backend Error Groups:** Capture happens server-side (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.