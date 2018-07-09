def check_database_connection(**kwargs):
    from django.db import connections
    from django.db.utils import OperationalError
    db_conn = connections['default']
    if not db_conn:
        return False
    try:
        db_conn.cursor()
        return True
    except OperationalError as e:
        return False


def check_accessible_api(request, **kwargs):
    import requests
    HTTP_HOST = request.META.get('HTTP_HOST')
    repositories_url = 'http://{}/api/repositories/'.format(HTTP_HOST)
    request = requests.get(repositories_url)
    try:
        request.raise_for_status()
        return True
    except requests.HTTPError as e:
        return False
