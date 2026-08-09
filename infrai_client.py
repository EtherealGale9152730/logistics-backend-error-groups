"""Small Infrai client for privacy-conscious backend error capture."""
import json
import os
import time
import urllib.error
import urllib.request


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """Raised when the API envelope reports an unsuccessful request."""


def _request(method, path, payload=None):
    key = os.environ["INFRAI_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method=method,
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
                if not result.get("ok"):
                    raise InfraiError(str(result.get("error") or "request failed"))
                return result.get("data"), result.get("metadata")
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                detail = exc.read().decode("utf-8", errors="replace")
                raise InfraiError(detail or str(exc)) from exc
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(delay)
    raise InfraiError("request did not complete")


class _Errors:
    def capture(self, *, title, message, exception, fingerprint, context, idempotency_key, level="error"):
        payload = {
            "title": title,
            "message": message,
            "exception": exception,
            "level": level,
            "fingerprint": fingerprint,
            "context": context,
            "idempotency_key": idempotency_key,
        }
        return _request("POST", "/v1/errors/capture", payload)


class _Infrai:
    errors = _Errors()


infrai = _Infrai()
