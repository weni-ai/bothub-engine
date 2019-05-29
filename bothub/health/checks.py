import logging

from decouple import config
from rest_framework import status


logger = logging.getLogger('bothub.health.checks')

CHECK_ACCESSIBLE_API_URL = config(
    'CHECK_ACCESSIBLE_API_URL',
    default=None)


def check_database_connection(**kwargs):
    from django.db import connections
    from django.db.utils import OperationalError
    if len(connections.all()) == 0:
        return False
    logger.info('found {} database connection'.format(len(connections.all())))
    for i, conn in enumerate(connections.all(), 1):
        try:
            conn.cursor()
            logger.info('#{} db connection OKAY'.format(i))
        except OperationalError:
            logger.warning('#{} db connection ERROR'.format(i))
            return False
    return True


def check_accessible_api(request, **kwargs):
    import requests
    if CHECK_ACCESSIBLE_API_URL:
        logger.info('requesting {}'.format(CHECK_ACCESSIBLE_API_URL))
        response = requests.get(CHECK_ACCESSIBLE_API_URL)
    else:
        url = 'http://{}/200/'.format(
            request.META.get('HTTP_HOST'))
        logger.info('requesting to {}'.format(url))
        response = requests.get(url)
    logger.info('{} response status code {}'.format(
        CHECK_ACCESSIBLE_API_URL,
        response.status_code))
    if response.status_code is status.HTTP_200_OK:
        return True
    return False
