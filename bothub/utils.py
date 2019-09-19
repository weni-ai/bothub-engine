import io
import uuid
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from collections import OrderedDict


def cast_supported_languages(i):
    return OrderedDict([
        x.split(':', 1) if ':' in x else (x, x) for x in
        i.split('|')
    ])


def cast_empty_str_to_none(value):
    return value or None


def send_bot_data_file_aws(id, bot_data):
    confmat_url = ''

    if all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_BUCKET_NAME]):
        confmat_filename = \
            f'repository_{str(id)}/bot_data_{uuid.uuid4()}.tar.gz'

        botdata = io.BytesIO(bot_data)

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        try:
            s3_client.upload_fileobj(
                botdata,
                settings.AWS_BUCKET_NAME,
                confmat_filename,
                ExtraArgs={'ContentType': 'application/gzip'}
            )
            confmat_url = '{}/{}/{}'.format(
                s3_client.meta.endpoint_url,
                settings.AWS_BUCKET_NAME,
                confmat_filename
            )
        except ClientError as e:
            print(e)

    return confmat_url
