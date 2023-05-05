import requests

from django.conf import settings

class KeycloakRESTClient:

    def get_user_token(self, email, password):
        response = requests.post(
            url=settings.OIDC_OP_TOKEN_ENDPOINT,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                "grant_type": "password",
                "username": email,
                "password": password,
                "client_id": settings.OIDC_RP_CLIENT_ID,
                "client_secret": settings.OIDC_RP_CLIENT_SECRET
            }
        )
        token = None
        if response.status_code == 200:
            token = response.json()["access_token"]
        return dict(status_code=response.status_code, token=f"Bearer {token}")

    def get_user_info(self, email, password):
        user_token_response = self.get_user_token(email=email, password=password)
        if user_token_response.get("status_code") == 200:
            formatted_header = {
                "Content-Type": "application/json; charset: utf-8",
                "Authorization": user_token_response.get("token")
            }
            response = requests.get(
                url=settings.OIDC_OP_USER_ENDPOINT,
                headers=formatted_header
            )
            user_response = dict()
            if response.status_code == 200:
                response_json = response.json()
                user_response = dict(
                    status_code=response.status_code,
                    email=response_json.get("email")
                )
            else:
                user_response = dict(status_code=response.status_code, message="cannot get that user")
        else:
            user_response = dict(status_code=user_token_response.get("status_code"), message="cannot get that user")
        return user_response   