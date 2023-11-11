from google.auth.transport import requests
from google.auth import default, compute_engine

def signing_credentials():
    credentials, _ = default()

    auth_request = requests.Request()
    credentials.refresh(auth_request)

    print(credentials.service_account_email)

    return compute_engine.IDTokenCredentials(
        auth_request,
        "",
        service_account_email=credentials.service_account_email
    )
