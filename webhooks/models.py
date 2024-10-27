from django.db import models

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at_time = models.DateTimeField()
    timestamp = models.DateTimeField()
    cause = models.TextField()
    full_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    invoice_url = models.URLField()

    def __str__(self):
        return self.transaction_id
