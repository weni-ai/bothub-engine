import requests
from celery import shared_task


@shared_task
def migrate_repository_wit(auth_token):
    print('dasdasdas')

    request = requests.get(
        url='https://api.wit.ai/export',
        headers={
            'Authorization': 'Bearer {}'.format(auth_token)
        }
    )



    print(request.json())


    return True
