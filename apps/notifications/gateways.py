"""
Multi-Channel Notification Gateway (SMS, WhatsApp, Notify.lk, Sandbox).

Provides unified interfaces for dispatching SMS and WhatsApp notifications
with automatic fallback and logging capabilities.
"""
import logging
import uuid
import json
import base64
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


def _make_http_request(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, method: str = 'POST') -> Dict[str, Any]:
    """Helper to perform HTTP requests using standard urllib without external dependencies."""
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        if isinstance(data, dict) and headers.get('Content-Type') == 'application/json':
            req_data = json.dumps(data).encode('utf-8')
        elif isinstance(data, dict):
            req_data = urllib.parse.urlencode(data).encode('utf-8')
        elif isinstance(data, str):
            req_data = data.encode('utf-8')
        else:
            req_data = data

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            return {
                'success': True,
                'status_code': response.status,
                'body': res_body
            }
    except Exception as e:
        logger.error(f"HTTP request to {url} failed: {e}")
        return {
            'success': False,
            'status_code': getattr(e, 'code', 500),
            'body': str(e)
        }


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
    """Sandbox / Mock SMS gateway for development and local testing."""

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        response_id = f"MOCK-SMS-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[SANDBOX SMS] Sent to {recipient}: '{title or ''} - {message}' (Ref: {response_id})")
        return {
            'success': True,
            'gateway_response_id': response_id,
            'provider': 'SandboxSMS',
            'error': None
        }


class SandboxWhatsAppGateway(BaseNotificationGateway):
    """Sandbox / Mock WhatsApp gateway for development and local testing."""

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        response_id = f"MOCK-WA-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[SANDBOX WHATSAPP] Sent to {recipient}: '{title or ''} - {message}' (Ref: {response_id})")
        return {
            'success': True,
            'gateway_response_id': response_id,
            'provider': 'SandboxWhatsApp',
            'error': None
        }


class NotifyLkSMSGateway(BaseNotificationGateway):
    """Gateway integration for Notify.lk (Sri Lanka local SMS provider)."""

    def __init__(self, api_key: str = '', user_id: str = '', sender_id: str = 'SQMS'):
        self.api_key = api_key or getattr(settings, 'NOTIFY_LK_API_KEY', '')
        self.user_id = user_id or getattr(settings, 'NOTIFY_LK_USER_ID', '')
        self.sender_id = sender_id or getattr(settings, 'NOTIFY_LK_SENDER_ID', 'SQMS')

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key or not self.user_id:
            logger.warning("Notify.lk credentials missing. Falling back to sandbox logging.")
            return SandboxSMSGateway().send(recipient, message, title)

        # Formats Sri Lankan numbers (e.g. 0771234567 -> 94771234567)
        clean_num = recipient.strip().replace('+', '').replace(' ', '')
        if clean_num.startswith('0'):
            clean_num = '94' + clean_num[1:]

        url = "https://app.notify.lk/api/v1/send"
        params = {
            'user_id': self.user_id,
            'api_key': self.api_key,
            'sender_id': self.sender_id,
            'to': clean_num,
            'message': message
        }
        
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        res = _make_http_request(full_url, method='GET')
        
        if res['success']:
            try:
                resp_json = json.loads(res['body'])
                if resp_json.get('status') == 'success' or resp_json.get('code') == 200:
                    response_id = resp_json.get('data', {}).get('message_id') or f"NTFY-{uuid.uuid4().hex[:8].upper()}"
                    logger.info(f"[Notify.lk SMS] Transmitted to {clean_num}: '{message}' (Ref: {response_id})")
                    return {
                        'success': True,
                        'gateway_response_id': response_id,
                        'provider': 'Notify.lk',
                        'error': None
                    }
                else:
                    error_msg = resp_json.get('message') or resp_json.get('errors') or 'Unknown error'
                    logger.error(f"[Notify.lk SMS] API returned error: {error_msg}")
                    return {'success': False, 'gateway_response_id': None, 'provider': 'Notify.lk', 'error': str(error_msg)}
            except Exception as parse_err:
                logger.error(f"[Notify.lk SMS] Failed to parse response: {parse_err}")
                return {'success': False, 'gateway_response_id': None, 'provider': 'Notify.lk', 'error': f"Parse error: {parse_err}"}
        else:
            return {'success': False, 'gateway_response_id': None, 'provider': 'Notify.lk', 'error': res['body']}


class TwilioSMSGateway(BaseNotificationGateway):
    """Gateway integration for Twilio SMS."""

    def __init__(self, account_sid: str = '', auth_token: str = '', phone_number: str = ''):
        self.account_sid = account_sid or getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = auth_token or getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.phone_number = phone_number or getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        if not self.account_sid or not self.auth_token or not self.phone_number:
            logger.warning("Twilio credentials missing. Falling back to sandbox logging.")
            return SandboxSMSGateway().send(recipient, message, title)

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        clean_num = recipient.strip()
        if not clean_num.startswith('+'):
            if clean_num.startswith('0'):
                clean_num = '+94' + clean_num[1:]
            else:
                clean_num = '+' + clean_num

        data = {
            'To': clean_num,
            'From': self.phone_number,
            'Body': message
        }
        
        auth_str = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        res = _make_http_request(url, data=data, headers=headers, method='POST')
        if res['success']:
            try:
                resp_json = json.loads(res['body'])
                response_id = resp_json.get('sid')
                logger.info(f"[Twilio SMS] Sent to {clean_num}: '{message}' (Ref: {response_id})")
                return {
                    'success': True,
                    'gateway_response_id': response_id,
                    'provider': 'TwilioSMS',
                    'error': None
                }
            except Exception as parse_err:
                logger.error(f"[Twilio SMS] Failed to parse response: {parse_err}")
                return {'success': False, 'gateway_response_id': None, 'provider': 'TwilioSMS', 'error': f"Parse error: {parse_err}"}
        else:
            return {'success': False, 'gateway_response_id': None, 'provider': 'TwilioSMS', 'error': res['body']}


class TwilioWhatsAppGateway(BaseNotificationGateway):
    """Gateway integration for Twilio WhatsApp Channel."""

    def __init__(self, account_sid: str = '', auth_token: str = '', phone_number: str = ''):
        self.account_sid = account_sid or getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = auth_token or getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.phone_number = phone_number or getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        if not self.account_sid or not self.auth_token or not self.phone_number:
            logger.warning("Twilio WhatsApp credentials missing. Falling back to sandbox logging.")
            return SandboxWhatsAppGateway().send(recipient, message, title)

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        clean_num = recipient.strip()
        if not clean_num.startswith('+'):
            if clean_num.startswith('0'):
                clean_num = '+94' + clean_num[1:]
            else:
                clean_num = '+' + clean_num

        data = {
            'To': f'whatsapp:{clean_num}',
            'From': f'whatsapp:{self.phone_number}',
            'Body': message
        }
        
        auth_str = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        res = _make_http_request(url, data=data, headers=headers, method='POST')
        if res['success']:
            try:
                resp_json = json.loads(res['body'])
                response_id = resp_json.get('sid')
                logger.info(f"[Twilio WhatsApp] Sent to {clean_num}: '{message}' (Ref: {response_id})")
                return {
                    'success': True,
                    'gateway_response_id': response_id,
                    'provider': 'TwilioWhatsApp',
                    'error': None
                }
            except Exception as parse_err:
                logger.error(f"[Twilio WhatsApp] Failed to parse response: {parse_err}")
                return {'success': False, 'gateway_response_id': None, 'provider': 'TwilioWhatsApp', 'error': f"Parse error: {parse_err}"}
        else:
            return {'success': False, 'gateway_response_id': None, 'provider': 'TwilioWhatsApp', 'error': res['body']}


class WhatsAppBusinessGateway(BaseNotificationGateway):
    """WhatsApp Cloud API Gateway integration."""

    def __init__(self, phone_number_id: str = '', access_token: str = ''):
        self.phone_number_id = phone_number_id or getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = access_token or getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')

    def send(self, recipient: str, message: str, title: Optional[str] = None) -> Dict[str, Any]:
        if not self.phone_number_id or not self.access_token:
            logger.warning("WhatsApp Cloud API credentials missing. Falling back to sandbox logging.")
            return SandboxWhatsAppGateway().send(recipient, message, title)

        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        clean_num = recipient.strip().replace('+', '').replace(' ', '')
        if clean_num.startswith('0'):
            clean_num = '94' + clean_num[1:]

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_num,
            "type": "text",
            "text": {
                "body": message
            }
        }

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        res = _make_http_request(url, data=data, headers=headers, method='POST')
        if res['success']:
            try:
                resp_json = json.loads(res['body'])
                response_id = resp_json.get('messages', [{}])[0].get('id')
                logger.info(f"[WhatsApp Cloud API] Delivered message to {clean_num}: '{message}' (Ref: {response_id})")
                return {
                    'success': True,
                    'gateway_response_id': response_id,
                    'provider': 'WhatsAppCloud',
                    'error': None
                }
            except Exception as parse_err:
                logger.error(f"[WhatsApp Cloud API] Failed to parse response: {parse_err}")
                return {'success': False, 'gateway_response_id': None, 'provider': 'WhatsAppCloud', 'error': f"Parse error: {parse_err}"}
        else:
            return {'success': False, 'gateway_response_id': None, 'provider': 'WhatsAppCloud', 'error': res['body']}


class NotificationGatewayRouter:
    """Dispatches notifications through primary gateway with automatic fallback."""

    def __init__(self):
        # Pick SMS gateway dynamically
        self.sms_gateway: BaseNotificationGateway
        if getattr(settings, 'NOTIFY_LK_API_KEY', '') and getattr(settings, 'NOTIFY_LK_USER_ID', ''):
            self.sms_gateway = NotifyLkSMSGateway()
        elif getattr(settings, 'TWILIO_ACCOUNT_SID', '') and getattr(settings, 'TWILIO_AUTH_TOKEN', ''):
            self.sms_gateway = TwilioSMSGateway()
        else:
            self.sms_gateway = SandboxSMSGateway()

        # Pick WhatsApp gateway dynamically
        self.whatsapp_gateway: BaseNotificationGateway
        if getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '') and getattr(settings, 'WHATSAPP_ACCESS_TOKEN', ''):
            self.whatsapp_gateway = WhatsAppBusinessGateway()
        elif getattr(settings, 'TWILIO_ACCOUNT_SID', '') and getattr(settings, 'TWILIO_AUTH_TOKEN', '') and getattr(settings, 'TWILIO_PHONE_NUMBER', ''):
            self.whatsapp_gateway = TwilioWhatsAppGateway()
        else:
            self.whatsapp_gateway = SandboxWhatsAppGateway()

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
