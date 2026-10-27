#!/usr/bin/env python3
"""
Senior AppsFlyer S2S Events API v3 & OneLink Attribution Handler
Reads APPSFLYER_APP_ID & APPSFLYER_DEV_KEY automatically from project environment (.env).
"""
import os
import json
import time
import uuid
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AppsFlyerS2S")


class AppsFlyerS2SClient:
    BASE_URL = "https://api2.appsflyer.com/inappevent"

    def __init__(self, app_id: Optional[str] = None, dev_key: Optional[str] = None, timeout: int = 10):
        self.app_id = app_id or os.environ.get("APPSFLYER_APP_ID", "id123456789")
        self.dev_key = dev_key or os.environ.get("APPSFLYER_DEV_KEY", "YOUR_AF_DEV_KEY")
        self.timeout = timeout

    def send_inapp_event(
        self,
        appsflyer_id: str,
        event_name: str,
        event_value: Dict[str, Any],
        customer_user_id: Optional[str] = None,
        advertising_id: Optional[str] = None,
        ip: Optional[str] = None,
        event_currency: str = "EUR",
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self.app_id}"
        payload: Dict[str, Any] = {
            "appsflyer_id": appsflyer_id,
            "eventName": event_name,
            "eventValue": json.dumps(event_value, separators=(",", ":")),
            "eventCurrency": event_currency,
            "eventTime": time.strftime("%Y-%m-%d %H:%M:%S.000", time.gmtime()),
        }
        if customer_user_id:
            payload["customer_user_id"] = customer_user_id
        if advertising_id:
            payload["advertising_id"] = advertising_id
        if ip:
            payload["ip"] = ip

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "authentication": self.dev_key,
            "Accept": "application/json",
        }

        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                    logger.info("AppsFlyer S2S Event '%s' delivered (HTTP %s): %s", event_name, resp.status, body)
                    return {"status": resp.status, "response": body}
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                logger.warning("Attempt %d HTTP %d: %s", attempt, e.code, err_body)
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                return {"status": e.code, "error": err_body}
            except Exception as ex:
                logger.error("Attempt %d network error: %s", attempt, ex)
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    raise
        return {"status": 500, "error": "Max retries exceeded"}


if __name__ == "__main__":
    client = AppsFlyerS2SClient()
    sample_id = f"{int(time.time() * 1000)}-{uuid.uuid4().int % (10**19)}"
    logger.info("AppsFlyer Client ready (App-ID: %s | Sample AF-ID: %s)", client.app_id, sample_id)
