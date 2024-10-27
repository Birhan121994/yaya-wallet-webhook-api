import hmac
import json
import hashlib
from decouple import config
from django.views import View
from webhooks.models import Transaction
from django.utils import timezone
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache

# Load the secret key from environment variable

SECRET_KEY = config('SECRET_KEY')
# SECRET_KEY = 'django-insecure-0n8v09g#j1foiskz7=-m1a=igd-1rn#yp8@8$)*l^n$##ay3x0'

@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    def post(self, request):
        try:
            # Get the YAYA-SIGNATURE header
            signature = request.headers.get('YAYA-SIGNATURE')
            if not signature:
                return HttpResponseBadRequest("Missing signature")

            # Get the raw payload
            payload = request.body.decode('utf-8')
            data = json.loads(payload)

            # Prepare the signed payload
            signed_payload = self.prepare_signed_payload(data)


            # Verify the signature
            if not self.verify_signature(signed_payload, signature):
                return HttpResponseBadRequest("Invalid signature")
            
            # Check timestamp to prevent replay attacks
            if not self.is_timestamp_valid(data['timestamp']) and cache.get(data['id']):
                return JsonResponse({"message":"Timestamp is too old"}, status=400)
            cache.set(data['id'], True, timeout=300)


            # Save the transaction to the database
            transaction = Transaction.objects.create(
                transaction_id=data['id'],
                amount=data['amount'],
                currency=data['currency'],
                created_at_time=timezone.datetime.fromtimestamp(data['created_at_time']),
                timestamp=timezone.datetime.fromtimestamp(data['timestamp']),
                cause=data['cause'],
                full_name=data['full_name'],
                account_name=data['account_name'],
                invoice_url=data['invoice_url']
            )
            transaction.save()

            # Return a success response
            return JsonResponse({"status": "success", "transaction_id": transaction.transaction_id}, status=201)

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}")

    def prepare_signed_payload(self, data):
        """Concatenate all values of the payload."""
        return ''.join(str(data[key]) for key in sorted(data.keys()))

    def verify_signature(self, signed_payload, signature):
        """Verify the HMAC SHA256 signature."""
        expected_signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        print(expected_signature)
        return hmac.compare_digest(expected_signature, signature)

    def is_timestamp_valid(self, timestamp):
        """Check if the timestamp is within acceptable range."""
        current_time = timezone.now().timestamp()
        print(current_time)
        return abs(current_time - timestamp) <= 300  # 5 minutes

