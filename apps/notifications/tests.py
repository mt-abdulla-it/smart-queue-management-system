from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from apps.notifications.gateways import (
    NotificationGatewayRouter,
    SandboxSMSGateway,
    SandboxWhatsAppGateway,
    NotifyLkSMSGateway,
    TwilioSMSGateway,
    TwilioWhatsAppGateway,
    WhatsAppBusinessGateway
)

class NotificationGatewayTestCase(TestCase):

    def test_default_sandbox_gateways(self):
        # With no settings configured, router should fall back to SandboxSMSGateway and SandboxWhatsAppGateway
        router = NotificationGatewayRouter()
        self.assertIsInstance(router.sms_gateway, SandboxSMSGateway)
        self.assertIsInstance(router.whatsapp_gateway, SandboxWhatsAppGateway)

        res_sms = router.dispatch_sms("0771234567", "Hello Test", "Subject")
        self.assertTrue(res_sms['success'])
        self.assertEqual(res_sms['provider'], 'SandboxSMS')

        res_wa = router.dispatch_whatsapp("0771234567", "Hello Test", "Subject")
        self.assertTrue(res_wa['success'])
        self.assertEqual(res_wa['provider'], 'SandboxWhatsApp')

    @override_settings(
        NOTIFY_LK_API_KEY='test_api_key',
        NOTIFY_LK_USER_ID='test_user_id',
        NOTIFY_LK_SENDER_ID='SQMS'
    )
    def test_router_selects_notifylk(self):
        router = NotificationGatewayRouter()
        self.assertIsInstance(router.sms_gateway, NotifyLkSMSGateway)

    @override_settings(
        TWILIO_ACCOUNT_SID='test_sid',
        TWILIO_AUTH_TOKEN='test_token',
        TWILIO_PHONE_NUMBER='+12345'
    )
    def test_router_selects_twilio(self):
        router = NotificationGatewayRouter()
        # Since Notify.lk settings are empty but Twilio is present
        self.assertIsInstance(router.sms_gateway, TwilioSMSGateway)
        self.assertIsInstance(router.whatsapp_gateway, TwilioWhatsAppGateway)

    @override_settings(
        WHATSAPP_PHONE_NUMBER_ID='test_phone_id',
        WHATSAPP_ACCESS_TOKEN='test_access_token'
    )
    def test_router_selects_whatsapp_cloud(self):
        router = NotificationGatewayRouter()
        self.assertIsInstance(router.whatsapp_gateway, WhatsAppBusinessGateway)

    @patch('apps.notifications.gateways._make_http_request')
    def test_twilio_sms_gateway_send(self, mock_http):
        mock_http.return_value = {
            'success': True,
            'status_code': 201,
            'body': '{"sid": "SM123456"}'
        }
        gateway = TwilioSMSGateway(account_sid='sid', auth_token='token', phone_number='+12345')
        res = gateway.send("0771234567", "Hello Twilio")
        self.assertTrue(res['success'])
        self.assertEqual(res['gateway_response_id'], 'SM123456')
        self.assertEqual(res['provider'], 'TwilioSMS')
        mock_http.assert_called_once()

    @patch('apps.notifications.gateways._make_http_request')
    def test_notifylk_sms_gateway_send(self, mock_http):
        mock_http.return_value = {
            'success': True,
            'status_code': 200,
            'body': '{"status": "success", "data": {"message_id": "NTFY123"}}'
        }
        gateway = NotifyLkSMSGateway(api_key='key', user_id='uid')
        res = gateway.send("0771234567", "Hello Sri Lanka")
        self.assertTrue(res['success'])
        self.assertEqual(res['gateway_response_id'], 'NTFY123')
        self.assertEqual(res['provider'], 'Notify.lk')
