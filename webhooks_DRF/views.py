import hmac
import hashlib
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decouple import config
from webhooks.models import Transaction

# Load the secret key from environment variable
SECRET_KEY = config('SECRET_KEY')

class WebhookDRFView(APIView):
    def post(self, request):
        try:
            # Get the YAYA-SIGNATURE header
            signature = request.headers.get('YAYA-SIGNATURE')
            if not signature:
                return Response({"error": "Missing signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the raw payload
            payload = request.body.decode('utf-8')
            data = json.loads(payload)

            # Prepare the signed payload
            signed_payload = self.prepare_signed_payload(data)

            # Verify the signature
            if not self.verify_signature(signed_payload, signature):
                return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Check timestamp to prevent replay attacks
            if not self.is_timestamp_valid(data['timestamp']):
                return Response({"error": "Timestamp is too old"}, status=status.HTTP_400_BAD_REQUEST)

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

            # Return a success response
            return Response({"status": "success", "transaction_id": transaction.transaction_id}, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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