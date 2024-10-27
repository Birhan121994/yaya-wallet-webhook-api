from django.urls import path
from webhooks.views import WebhookView

urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
]