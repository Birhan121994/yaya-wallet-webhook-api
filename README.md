# YaYa Wallet Webhook Integration

This project implements a webhook endpoint using Django to receive real-time updates from YaYa Wallet. The endpoint verifies incoming requests to ensure they originate from YaYa Wallet and prevents replay attacks by checking the timestamps.

## Assumptions

- The webhook payload structure provided in the task is adhered to.
- The server's clock is synchronized using NTP to accurately verify timestamps.
- The application is running in a secure environment (preferably with HTTPS) for production.

## Problem-Solving Approach

1. **Setup Django Project**: Created a new Django project and app to handle webhook requests.I have created two app which handles the task in two approches.The apps are
   - The first app is called webhooks which handles the task using Django built in JsonResponse functionlity which handles api requests.
   - The second app is called webhooks_DRF which handles the task using Django RestFramework which is one of the most popular framework on api related task.
3. **Define Models**: Implemented a model to store transaction data received from the webhook.The database that I have used for these project is the default sqlite database for simplicity. For production purpose use Postgres database.To use postgre database on these project
  download and install PostgreSQL from the official website, download tools like pgadmin, to have gui that allows you to created database tables and other database management tasks.
  Modify the settings.py: Ensure your DATABASES settings in ya_wallet/settings.py match your PostgreSQL setup:
  ```
  python
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ya_wallet',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
4. **Create Webhook Endpoint**: Developed a class-based view to handle POST requests. This view:
   - Extracts and verifies the HMAC SHA256 signature.
   - Checks the validity of the timestamp to prevent replay attacks.
   - Stores transaction data in the database.
5. **Testing**: Utilized Postman to simulate webhook requests and verify the endpoint's behavior under various scenarios (valid requests, invalid signatures, etc.).

## Testing the Solution

To test the solution:

1. Run the development server:
   ```bash
   python manage.py runserver
