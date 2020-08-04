import io
import re
import uuid
import boto3
import random
import string
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Subquery, IntegerField
from botocore.exceptions import ClientError
from collections import OrderedDict


entity_regex = re.compile(
    r"\[(?P<entity_text>[^\]]+)" r"\]\((?P<entity>[^:)]*?)" r"(?:\:(?P<value>[^)]+))?\)"
)


def cast_supported_languages(i):
    return OrderedDict([x.split(":", 1) if ":" in x else (x, x) for x in i.split("|")])


def cast_empty_str_to_none(value):
    return value or None


def send_bot_data_file_aws(id, bot_data):
    confmat_url = ""

    if all(
        [
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_BUCKET_NAME,
        ]
    ):
        confmat_filename = f"repository_{str(id)}/bot_data_{uuid.uuid4()}.tar.gz"

        botdata = io.BytesIO(bot_data)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        try:
            s3_client.upload_fileobj(
                botdata,
                settings.AWS_BUCKET_NAME,
                confmat_filename,
                ExtraArgs={"ContentType": "application/gzip"},
            )
            confmat_url = "{}/{}/{}".format(
                s3_client.meta.endpoint_url, settings.AWS_BUCKET_NAME, confmat_filename
            )
        except ClientError as e:
            print(e)

    return confmat_url


def unique_slug_generator(validated_data, Repository, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(validated_data.get("name"))[:25:]

    qs_exists = Repository.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr="".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(6)
            ).lower(),
        )
        return unique_slug_generator(validated_data, Repository, new_slug=new_slug)
    return slug


def format_entity(text, entity, start, end):
    """
        Returns the correct formatted text with the correct entities
    """
    return text[0:start] + "[" + text[start:end] + "](" + entity + ")" + text[end:]


def find_entities_in_example(example):
    """Extracts entities from a markdown intent example."""
    entities = []
    offset = 0

    for match in re.finditer(entity_regex, example):
        entity_text = match.groupdict()["entity_text"]
        entity_type = match.groupdict()["entity"]
        if match.groupdict()["value"]:
            entity_value = match.groupdict()["value"]
        else:
            entity_value = entity_text

        start_index = match.start() - offset
        end_index = start_index + len(entity_text)
        offset += len(match.group(0)) - len(entity_text)

        entity = {
            "start": start_index,
            "end": end_index,
            "value": entity_value,
            "entity": entity_type,
        }
        entities.append(entity)

    return entities


def get_without_entity(example):
    """Extract entities and synonyms, and convert to plain text."""
    plain_text = re.sub(entity_regex, lambda m: m.groupdict()["entity_text"], example)
    return plain_text


class CountSubquery(Subquery):
    template = "(SELECT COUNT(1) FROM (%(subquery)s) _count_subquery)"
    output_field = IntegerField()

    def __init__(self, queryset, output_field=None, **extra):
        super().__init__(queryset, output_field, **extra)
