#!/usr/bin/env python3
"""
Senior Adjust S2S Event & Session Pipeline
Reads ADJUST_APP_TOKEN, ADJUST_BEARER_TOKEN & ADJUST_ENVIRONMENT from project environment (.env).
"""
import os
import json
import time
import logging
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AdjustS2S")


class AdjustS2SClient:
    EVENT_ENDPOINT = "https://s2s.adjust.com/event"
    SESSION_ENDPOINT = "https://s2s.adjust.com/session"

    def __init__(
        self,
        app_token: Optional[str] = None,
        bearer_token: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        self.app_token = app_token or os.environ.get("ADJUST_APP_TOKEN", "YOUR_APP_TOKEN")
        self.bearer_token = bearer_token or os.environ.get("ADJUST_BEARER_TOKEN", "")
        self.environment = environment or os.environ.get("ADJUST_ENVIRONMENT", "production")

    def send_event(
        self,
        event_token: str,
        device_identifiers: Dict[str, str],
        callback_params: Optional[Dict[str, str]] = None,
        partner_params: Optional[Dict[str, str]] = None,
        revenue: Optional[float] = None,
        currency: str = "EUR",
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "s2s": "1",
            "app_token": self.app_token,
            "event_token": event_token,
            "environment": self.environment,
            "created_at_unix": str(int(time.time())),
            **device_identifiers,
        }
        if revenue is not None:
            payload["revenue"] = f"{revenue:.2f}"
            payload["currency"] = currency
        if callback_params:
            payload["callback_params"] = json.dumps(callback_params, separators=(",", ":"))
        if partner_params:
            payload["partner_params"] = json.dumps(partner_params, separators=(",", ":"))

        encoded_body = urllib.parse.urlencode(payload).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        req = urllib.request.Request(self.EVENT_ENDPOINT, data=encoded_body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            logger.info("Adjust S2S HTTP %d: %s", resp.status, body)
            return {"status": resp.status, "body": body}


if __name__ == "__main__":
    client = AdjustS2SClient()
    logger.info("Adjust S2S Senior Client ready (App-Token: %s | Env: %s)", client.app_token, client.environment)
