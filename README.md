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
6. **Unit Testing**: I also implemented unit test mechanism on the test.py file on the django project by which my project passes all the test cases defined on the project.

### Explanation of Test Cases
   -**test_webhook_success**: Tests the successful scenario where a valid payload with a valid signature is sent. It checks that a new transaction is created in the database.
   -**test_webhook_missing_signature**: Tests the case where the YAYA-SIGNATURE header is missing. It should return a 400 status code.
   -**test_webhook_invalid_signature**: Tests the scenario where an invalid signature is provided. The response should indicate an invalid signature.
   -**test_webhook_timestamp_too_old**: Tests the case where the timestamp in the payload is set to an old value. It checks that the response indicates that the timestamp is too old.
   -**test_webhook_invalid_json**: Tests the scenario where the body of the request is not valid JSON. It should return a 400 status code.

## Testing the Solution

To test the solution:

1. To clone a repository for a Django project, use the following command:
   ```bash
   git clone https://github.com/Birhan121994/yaya-wallet-webhook-api.git
## Steps to follow after cloning the repo
Once users have cloned the repository, they should follow these steps:
1.**Navigate into the project directory:**
   ```bash
   cd ya_wallet_webhook
   ```
2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
4 **Configure the database settings in settings.py as needed (if applicable).**
5.**Run database migrations:**
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser (optional, for accessing the admin interface):**
   ```bash
   python manage.py createsuperuser
7.**Run the development server:**
   ```bash
   python manage.py runserver
   ```
8. **Test the Webhook with Postman:**
   - Open Postman and create a new POST request.
   - Set the URL to http://localhost:8000/api/webhook/ for testing the webhook app api made using JsonResponse and Set the URL to http://localhost:8000/DRF/api/webhook_DRF/ for testing the webhook_DRF app made using Django RestFramework.
   - In the "Headers" tab, add the YAYA-SIGNATURE and YAYA-SIGNATURE-TIMESTAMP header (generate the signature using the provided code in the view and it is printed on the console).
   - In the "Body" tab, set the request type to raw and select JSON. Use the following sample payload:
     ```json
     {
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
     ```
9.**Testing the Webhook using Testcaset:**
   ```bash
   py manage.py test webhooks
   ```
   or for the DRF app
   ```bash
   py manage.py test webhooks_DRF
   ```


