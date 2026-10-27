#!/usr/bin/env python3
"""
Senior Singular S2S Session & Custom Event Attribution Client
Reads SINGULAR_API_KEY & SINGULAR_BUNDLE_ID automatically from project environment (.env).
"""
import os
import json
import urllib.parse
import urllib.request
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SingularS2S")


class SingularS2SClient:
    LAUNCH_URL = "https://sdk-api-v1.singular.net/api/v1/launch"
    EVENT_URL = "https://sdk-api-v1.singular.net/api/v1/evt"

    def __init__(self, api_key: Optional[str] = None, bundle_id: Optional[str] = None, platform: str = "Android"):
        self.api_key = api_key or os.environ.get("SINGULAR_API_KEY", "YOUR_SINGULAR_KEY")
        self.bundle_id = bundle_id or os.environ.get("SINGULAR_BUNDLE_ID", "com.shoxx.app")
        self.platform = platform

    def track_event(
        self,
        event_name: str,
        device_ids: Dict[str, str],
        ip: str,
        revenue: Optional[float] = None,
        currency: str = "EUR",
        extra_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, str] = {
            "a": self.api_key,
            "i": self.bundle_id,
            "p": self.platform,
            "n": event_name,
            "ip": ip,
            **device_ids,
        }
        if revenue is not None:
            params["is_revenue_event"] = "true"
            params["amt"] = f"{revenue:.2f}"
            params["cur"] = currency
        if extra_attributes:
            params["e"] = json.dumps(extra_attributes, separators=(",", ":"))

        query = urllib.parse.urlencode(params)
        url = f"{self.EVENT_URL}?{query}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logger.info("Singular S2S response: %s", data)
            return data


if __name__ == "__main__":
    client = SingularS2SClient()
    logger.info("Singular S2S Senior Client ready (Bundle-ID: %s)", client.bundle_id)
