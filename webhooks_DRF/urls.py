from django.urls import path
from webhooks_DRF.views import WebhookDRFView

urlpatterns = [
    path('webhook_DRF/', WebhookDRFView.as_view(), name='webhook_DRF'),
]