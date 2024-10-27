import json
import hmac
import hashlib
import datetime
from decouple import config
from django.urls import reverse
from webhooks.models import Transaction
from django.utils import timezone
from django.test import TestCase, Client
import warnings

class DRFWebhookViewTest(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*naive datetime.*")
        self.client = Client()
        self.url = reverse('webhook')
        self.secret_key = config('SECRET_KEY')
        
        self.valid_payload = {
            "id": "1dd2854e-3a79-4548-ae36-97e4a18ebf81",
            "amount": 100,
            "currency": "ETB",
            "created_at_time": 1673381836,
            "timestamp": 1701272333,
            "cause": "Testing",
            "full_name": "Abebe Kebede",
            "account_name": "abebekebede1",
            "invoice_url": "https://yayawallet.com/en/invoice/xxxx"
        }

    def generate_signature(self, payload):
        signed_payload = ''.join(str(payload[key]) for key in sorted(payload.keys()))
        return hmac.new(
            self.secret_key.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    

    def test_webhook_success(self):
        signature = self.generate_signature(self.valid_payload)
        response = self.client.post(self.url, data=json.dumps(self.valid_payload),
                                     content_type='application/json',
                                     HTTP_YAYA_SIGNATURE=signature)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_id, self.valid_payload['id'])

    def test_webhook_missing_signature(self):
        response = self.client.post(self.url, data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Missing signature")

    def test_webhook_invalid_signature(self):
        invalid_signature = "invalid_signature"
        response = self.client.post(self.url, data=json.dumps(self.valid_payload),
                                     content_type='application/json',
                                     HTTP_YAYA_SIGNATURE=invalid_signature)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid signature")

    def test_webhook_timestamp_too_old(self):
        old_payload = self.valid_payload.copy()
        old_payload['timestamp'] = 0  # Set a very old timestamp
        signature = self.generate_signature(old_payload)
        
        response = self.client.post(self.url, data=json.dumps(old_payload),
                                     content_type='application/json',
                                     HTTP_YAYA_SIGNATURE=signature)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), '{"message": "Timestamp is too old"}')

    def test_webhook_invalid_json(self):
        response = self.client.post(self.url, data="Invalid JSON",
                                     content_type='application/json',
                                     HTTP_YAYA_SIGNATURE="any_signature")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid JSON")
