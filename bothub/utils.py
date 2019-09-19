import io
import uuid
import boto3
from decouple import config
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
    aws_access_key_id = config('BOTHUB_ENGINE_AWS_ACCESS_KEY_ID', default='')
    aws_secret_access_key = config(
        'BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY', default='')
    aws_bucket_name = config('BOTHUB_ENGINE_AWS_S3_BUCKET_NAME', default='')
    aws_region_name = config('BOTHUB_ENGINE_AWS_REGION_NAME', 'us-east-1')

    confmat_url = ''

    if all([aws_access_key_id, aws_secret_access_key, aws_bucket_name]):
        confmat_filename = \
            f'repository_{str(id)}/bot_data_{uuid.uuid4()}.tar.gz'

        botdata = io.BytesIO(bot_data)

        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name,
        )
        try:
            s3_client.upload_fileobj(
                botdata,
                aws_bucket_name,
                confmat_filename,
                ExtraArgs={'ContentType': 'application/gzip'}
            )
            confmat_url = '{}/{}/{}'.format(
                s3_client.meta.endpoint_url,
                aws_bucket_name,
                confmat_filename
            )
        except ClientError as e:
            print(e)

    return confmat_url
