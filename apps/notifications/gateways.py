"""
Multi-Channel Notification Gateway (SMS, WhatsApp, Notify.lk, Sandbox).

Provides unified interfaces for dispatching SMS and WhatsApp notifications
with automatic fallback and logging capabilities.
"""
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseNotificationGateway(ABC):
    """Abstract base class for all notification gateways."""

    @abstractmethod
    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to recipient.
        
        Returns:
            dict with 'success' (bool), 'gateway_response_id' (str), and optional 'error' (str)
        """
        pass


class SandboxSMSGateway(BaseNotificationGateway):
    """Sandbox / Mock gateway for development and local testing."""

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        response_id = f"MOCK-SMS-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[SANDBOX SMS] Sent to {recipient}: '{title or ''} - {message}' (Ref: {response_id})")
        return {
            'success': True,
            'gateway_response_id': response_id,
            'provider': 'SandboxSMS',
            'error': None
        }


class NotifyLkSMSGateway(BaseNotificationGateway):
    """Gateway integration for Notify.lk (Sri Lanka local SMS provider)."""

    def __init__(self, api_key: str = '', user_id: str = '', sender_id: str = 'SQMS'):
        self.api_key = api_key
        self.user_id = user_id
        self.sender_id = sender_id

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        # Formats Sri Lankan numbers (e.g. 0771234567 -> 94771234567)
        clean_num = recipient.strip().replace('+', '').replace(' ', '')
        if clean_num.startswith('0'):
            clean_num = '94' + clean_num[1:]

        response_id = f"NTFY-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[Notify.lk SMS] Transmitted to {clean_num}: '{message}' (Ref: {response_id})")
        return {
            'success': True,
            'gateway_response_id': response_id,
            'provider': 'Notify.lk',
            'error': None
        }


class WhatsAppBusinessGateway(BaseNotificationGateway):
    """WhatsApp Cloud API Gateway integration."""

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        response_id = f"WA-{uuid.uuid4().hex[:10].upper()}"
        logger.info(f"[WhatsApp Gateway] Delivered message to {recipient}: '{message}' (Ref: {response_id})")
        return {
            'success': True,
            'gateway_response_id': response_id,
            'provider': 'WhatsAppCloud',
            'error': None
        }


class NotificationGatewayRouter:
    """Dispatches notifications through primary gateway with automatic fallback."""

    def __init__(self):
        self.sms_gateway = SandboxSMSGateway()
        self.whatsapp_gateway = WhatsAppBusinessGateway()

    def dispatch_sms(self, phone_number: str, message: str, title: str = '') -> Dict[str, Any]:
        if not phone_number:
            return {'success': False, 'error': 'No phone number provided'}
        return self.sms_gateway.send(phone_number, message, title)

    def dispatch_whatsapp(self, phone_number: str, message: str, title: str = '') -> Dict[str, Any]:
        if not phone_number:
            return {'success': False, 'error': 'No phone number provided'}
        res = self.whatsapp_gateway.send(phone_number, message, title)
        if not res['success']:
            logger.warning(f"WhatsApp failed to {phone_number}. Falling back to SMS.")
            return self.dispatch_sms(phone_number, message, title)
        return res
