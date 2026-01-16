"""
BALE Webhook & Integration System
Event-driven notifications and third-party integrations.
"""
import os
import json
import hmac
import hashlib
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from src.logger import setup_logger

logger = setup_logger("bale_webhooks")


# ==================== EVENT TYPES ====================

class EventType(str, Enum):
    """Webhook event types."""
    # Analysis events
    ANALYSIS_STARTED = "analysis.started"
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    
    # Risk events
    HIGH_RISK_DETECTED = "risk.high_detected"
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    
    # Contract events
    CONTRACT_CREATED = "contract.created"
    CONTRACT_UPDATED = "contract.updated"
    CONTRACT_DELETED = "contract.deleted"
    
    # System events
    SYSTEM_HEALTH_WARNING = "system.health_warning"
    QUOTA_WARNING = "quota.warning"


@dataclass
class WebhookEvent:
    """A webhook event to be delivered."""
    id: str
    type: EventType
    timestamp: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "user_id": self.user_id
        }


@dataclass
class WebhookEndpoint:
    """A registered webhook endpoint."""
    id: str
    url: str
    secret: str
    events: List[EventType]
    active: bool = True
    
    # Metadata
    created_at: str = None
    last_triggered_at: str = None
    failure_count: int = 0


# ==================== SIGNATURE GENERATION ====================

def generate_signature(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_signature(payload: str, secret: str, signature: str) -> bool:
    """Verify webhook signature."""
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(expected, signature)


# ==================== WEBHOOK DISPATCHER ====================

class WebhookDispatcher:
    """
    Manages webhook endpoints and event delivery.
    """
    
    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    def register_endpoint(self, endpoint: WebhookEndpoint):
        """Register a new webhook endpoint."""
        self.endpoints[endpoint.id] = endpoint
        logger.info(f"Registered webhook endpoint: {endpoint.id} -> {endpoint.url}")
    
    def unregister_endpoint(self, endpoint_id: str):
        """Remove a webhook endpoint."""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            logger.info(f"Unregistered webhook endpoint: {endpoint_id}")
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an in-process event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def dispatch(self, event: WebhookEvent):
        """Dispatch an event to all matching endpoints and handlers."""
        # Call in-process handlers
        handlers = self.event_handlers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.type}: {e}")
        
        # Send to webhook endpoints
        matching_endpoints = [
            ep for ep in self.endpoints.values()
            if ep.active and event.type in ep.events
        ]
        
        if matching_endpoints:
            await asyncio.gather(*[
                self._deliver_to_endpoint(event, ep)
                for ep in matching_endpoints
            ], return_exceptions=True)
    
    async def _deliver_to_endpoint(
        self, 
        event: WebhookEvent, 
        endpoint: WebhookEndpoint
    ):
        """Deliver an event to a single endpoint with retries."""
        payload = json.dumps(event.to_dict())
        signature = generate_signature(payload, endpoint.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-BALE-Signature": signature,
            "X-BALE-Event": event.type.value,
            "X-BALE-Delivery": event.id
        }
        
        session = await self._get_session()
        
        for attempt in range(3):  # 3 retries
            try:
                async with session.post(
                    endpoint.url,
                    data=payload,
                    headers=headers
                ) as response:
                    if response.status < 300:
                        endpoint.last_triggered_at = datetime.utcnow().isoformat()
                        endpoint.failure_count = 0
                        logger.info(f"Webhook delivered: {event.type} -> {endpoint.url}")
                        return
                    else:
                        logger.warning(
                            f"Webhook delivery failed: {endpoint.url} "
                            f"returned {response.status}"
                        )
            except Exception as e:
                logger.error(f"Webhook delivery error: {e}")
            
            # Exponential backoff
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
        
        # All retries failed
        endpoint.failure_count += 1
        if endpoint.failure_count >= 5:
            endpoint.active = False
            logger.warning(f"Webhook disabled after failures: {endpoint.url}")


# Global dispatcher instance
dispatcher = WebhookDispatcher()


# ==================== HELPER FUNCTIONS ====================

def emit_event(
    event_type: EventType,
    data: Dict[str, Any],
    user_id: str = None
):
    """
    Synchronously queue an event for dispatch.
    Use in non-async contexts.
    """
    import uuid
    event = WebhookEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        data=data,
        user_id=user_id
    )
    
    # Fire and forget
    asyncio.create_task(dispatcher.dispatch(event))


async def emit_event_async(
    event_type: EventType,
    data: Dict[str, Any],
    user_id: str = None
):
    """Emit an event asynchronously."""
    import uuid
    event = WebhookEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        data=data,
        user_id=user_id
    )
    await dispatcher.dispatch(event)


# ==================== SLACK INTEGRATION ====================

class SlackNotifier:
    """Send notifications to Slack."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    
    async def send(
        self,
        message: str,
        channel: str = None,
        blocks: List[Dict] = None
    ):
        """Send a message to Slack."""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        payload = {"text": message}
        if channel:
            payload["channel"] = channel
        if blocks:
            payload["blocks"] = blocks
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.webhook_url,
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("Slack notification sent")
                    else:
                        logger.warning(f"Slack notification failed: {response.status}")
            except Exception as e:
                logger.error(f"Slack error: {e}")
    
    async def send_risk_alert(
        self,
        contract_name: str,
        risk_score: int,
        clause_summary: str,
        analysis_url: str = None
    ):
        """Send a formatted risk alert."""
        color = "#ef4444" if risk_score > 70 else "#f59e0b" if risk_score > 50 else "#10b981"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⚠️ High Risk Alert: {contract_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Risk Score:*\n{risk_score}%"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{'🔴 Critical' if risk_score > 70 else '🟡 Warning'}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Clause Summary:*\n{clause_summary[:200]}..."
                }
            }
        ]
        
        if analysis_url:
            blocks.append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Analysis"},
                    "url": analysis_url
                }]
            })
        
        await self.send(
            message=f"High risk detected: {contract_name} ({risk_score}%)",
            blocks=blocks
        )


# ==================== EMAIL INTEGRATION ====================

class EmailNotifier:
    """Send email notifications via SMTP or API."""
    
    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = 587,
        smtp_user: str = None,
        smtp_password: str = None
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    
    async def send(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False
    ):
        """Send an email."""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            logger.warning("Email not configured")
            return
        
        # Use aiosmtplib for async email
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(to)
            
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            logger.info(f"Email sent to {to}")
        except ImportError:
            logger.warning("aiosmtplib not installed")
        except Exception as e:
            logger.error(f"Email error: {e}")
    
    async def send_analysis_report(
        self,
        to: List[str],
        contract_name: str,
        risk_score: int,
        verdict: str,
        summary: str
    ):
        """Send a formatted analysis report email."""
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a1a;">BALE Analysis Report</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
                <h3 style="margin-top: 0;">{contract_name}</h3>
                <table style="width: 100%;">
                    <tr>
                        <td><strong>Risk Score:</strong></td>
                        <td style="color: {'#ef4444' if risk_score > 70 else '#f59e0b' if risk_score > 50 else '#10b981'};">
                            {risk_score}%
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Verdict:</strong></td>
                        <td>{verdict}</td>
                    </tr>
                </table>
                <hr style="border: 1px solid #ddd; margin: 20px 0;">
                <h4>Summary</h4>
                <p>{summary}</p>
            </div>
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                Generated by BALE - Binary Adjudication & Litigation Engine
            </p>
        </body>
        </html>
        """
        
        await self.send(
            to=to,
            subject=f"[BALE] Analysis Report: {contract_name} ({risk_score}% risk)",
            body=html_body,
            html=True
        )


# Global instances
slack_notifier = SlackNotifier()
email_notifier = EmailNotifier()
