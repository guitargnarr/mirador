#!/usr/bin/env python3
"""
Webhook Handler for Mirador AI Framework
Provides webhook management for event notifications.
"""
import json
import logging
import os
import requests
import time
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger("mirador.webhooks")

class WebhookHandler:
    """Handles webhook registration, management, and event dispatch."""

    def __init__(self, config_path: str = "ai_framework/config.json"):
        """Initialize the webhook handler."""
        self.config_path = config_path
        self.webhooks_file = os.path.join(os.path.dirname(config_path), "webhooks.json")
        self.webhooks: Dict[str, Dict] = {}
        self._load_webhooks()

    def _load_webhooks(self):
        """Load webhooks from file."""
        if os.path.exists(self.webhooks_file):
            try:
                with open(self.webhooks_file, 'r') as f:
                    self.webhooks = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load webhooks: {e}")
                self.webhooks = {}
        else:
            self.webhooks = {}

    def _save_webhooks(self):
        """Save webhooks to file."""
        try:
            os.makedirs(os.path.dirname(self.webhooks_file), exist_ok=True)
            with open(self.webhooks_file, 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save webhooks: {e}")

    def add_webhook(self, name: str, url: str, events: List[str],
                    headers: Optional[Dict] = None, max_retries: int = 3,
                    active: bool = True) -> Dict:
        """Register a new webhook."""
        webhook_id = str(uuid.uuid4())[:8]
        webhook = {
            "id": webhook_id,
            "name": name,
            "url": url,
            "events": events,
            "headers": headers or {},
            "max_retries": max_retries,
            "active": active,
            "created": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.webhooks[webhook_id] = webhook
        self._save_webhooks()
        logger.info(f"Added webhook: {name} ({webhook_id})")
        return webhook

    def get_webhooks(self) -> Dict[str, Dict]:
        """Get all registered webhooks."""
        return self.webhooks

    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """Get a specific webhook by ID."""
        return self.webhooks.get(webhook_id)

    def update_webhook(self, webhook_id: str, **kwargs) -> Dict:
        """Update a webhook."""
        if webhook_id not in self.webhooks:
            raise ValueError(f"Webhook '{webhook_id}' not found")

        webhook = self.webhooks[webhook_id]
        for key, value in kwargs.items():
            if key in webhook:
                webhook[key] = value

        self._save_webhooks()
        return webhook

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self._save_webhooks()
            return True
        return False

    def _send_webhook(self, webhook: Dict, payload: Dict) -> Dict:
        """Send a webhook request."""
        result = {"success": False}

        try:
            headers = {"Content-Type": "application/json"}
            headers.update(webhook.get("headers", {}))

            response = requests.post(
                webhook["url"],
                json=payload,
                headers=headers,
                timeout=10
            )

            result["status_code"] = response.status_code
            result["success"] = response.status_code < 400

        except requests.RequestException as e:
            result["error"] = str(e)
            logger.error(f"Webhook request failed: {e}")

        return result

    def trigger_event(self, event_type: str, data: Dict) -> List[Dict]:
        """Trigger webhooks for an event type."""
        results = []

        for webhook_id, webhook in self.webhooks.items():
            if not webhook.get("active", True):
                continue

            if event_type in webhook.get("events", []) or "*" in webhook.get("events", []):
                payload = {
                    "event_type": event_type,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "data": data
                }

                result = self._send_webhook(webhook, payload)
                result["webhook_id"] = webhook_id
                results.append(result)

        return results
