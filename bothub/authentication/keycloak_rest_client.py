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
        return dict(status=response.status_code, token=f"Bearer {token}")

    def headers(self, email, password):
        response = self.get_user_token(email=email, password=password)
        if response.status_code == 200:
            return {
                "status_code": response.status_code,
                "Content-Type": "application/json; charset: utf-8",
                "Authorization": response.get("token")
            }
        else:
            return dict(
                status_code=response.status_code
            )

    def get_user_info(self, email, password):
        header = self.headers(email=email, password=password)
        if header.status_code == 200:
            response = requests.get(
                url=settings.OIDC_OP_USER_ENDPOINT,
                headers=header
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
            user_response = dict(status_code=response.status_code, message="cannot get that user")
        return user_response   
