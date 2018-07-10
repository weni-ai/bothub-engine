import logging

from rest_framework import status


logger = logging.getLogger('bothub.health.checks')

CHECK_ACCESSIBLE_API_URL = '/api/repositories/'

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
    from django.test import Client
    logger.info('making request to {}'.format(CHECK_ACCESSIBLE_API_URL))
    client = Client()
    response = client.get(CHECK_ACCESSIBLE_API_URL)
    logger.info('{} status code: {}'.format(
        CHECK_ACCESSIBLE_API_URL,
        response.status_code))
    if response.status_code is status.HTTP_200_OK:
        return True
    return False
