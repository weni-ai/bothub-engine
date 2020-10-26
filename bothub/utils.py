import io
import math
import random
import re
import string
import uuid
import boto3
import matplotlib.pyplot as plt
import numpy as np
import requests
from collections import OrderedDict
from botocore.exceptions import ClientError
from django.conf import settings
from django.db.models import IntegerField, Subquery
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

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
            endpoint_url=settings.AWS_ACCESS_ENDPOINT_URL,
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


def score_normal(x, optimal):
    """
        Based on normal distribution,
        score will decay if current value is below or above target
    """

    try:
        slim_const = 2
        result = math.exp(-((x - optimal) ** 2) / (2 * (optimal / slim_const) ** 2))
    except ZeroDivisionError:
        return 100

    return result * 100


def score_cumulated(x, optimal):
    """
        Based on cumulated distribution,
        score will increase as close current value is to the target
    """

    try:
        factor = 10 / optimal
        sigma_func = 1 / (1 + np.exp(-(-5 + x * factor)))
    except ZeroDivisionError:
        return 100

    return sigma_func * 100


def intentions_balance_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return {"score": 0, "recommended": ""}

    train_count = dataset["train_count"]

    scores = []
    for intention in sentences.keys():
        this_size = sentences[intention]
        excl_size = train_count - this_size

        # Mean of sentences/intention excluding this intention
        # It is the optimal target
        excl_mean = excl_size / (intentions_count - 1)
        # print(this_size, excl_mean)
        scores.append(score_normal(this_size, excl_mean))

    try:
        score = sum(scores) / len(scores)
    except ZeroDivisionError:
        return {"score": 0, "recommended": ""}

    return {
        "score": score,
        "recommended": f"The avarage sentences per intention is {int(train_count/intentions_count)}",
    }


def intentions_size_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return {"score": 0, "recommended": ""}

    optimal = int(
        106.6556
        + (19.75708 - 106.6556) / (1 + (intentions_count / 8.791823) ** 1.898546)
    )

    scores = []
    for intention in sentences.keys():
        this_size = sentences[intention]
        if this_size >= optimal:
            scores.append(1.0)
        else:
            scores.append(score_cumulated(this_size, optimal))

    try:
        score = sum(scores) / len(scores)
    except ZeroDivisionError:
        return {"score": 0, "recommended": ""}

    return {"score": score, "recommended": f"{optimal} sentences per intention"}


def evaluate_size_score(dataset):
    intentions = dataset["intentions"]

    intentions_size = len(intentions)
    if intentions_size < 2:
        return {"score": 0, "recommended": ""}

    train_count = dataset["train_count"]
    evaluate_count = dataset["evaluate_count"]

    optimal = int(
        692.4702 + (-1.396326 - 692.4702) / (1 + (train_count / 5646.078) ** 0.7374176)
    )

    if evaluate_count >= optimal:
        score = 1.0
    else:
        score = score_cumulated(evaluate_count, optimal)

    return {"score": score, "recommended": f"{optimal} evaluation sentences"}


def arrange_data(train_data, eval_data):
    """
        :param train_data: list of sentences {"intent";"text"}
        :param eval_data:  list of sentences {"intent";"text"}
        :return: formatted dataset
    """
    dataset = {
        "intentions": [],
        "train_count": len(train_data),
        "train": {},
        "evaluate_count": len(eval_data),
        "evaluate": {},
    }

    for data in train_data:
        if data["intent"] not in dataset["intentions"]:
            dataset["intentions"].append(data["intent"])
            dataset["train"][data["intent"]] = 0

        dataset["train"][data["intent"]] += 1

    for data in eval_data:
        if data["intent"] not in dataset["intentions"]:
            continue
        if data["intent"] not in dataset["evaluate"]:
            dataset["evaluate"][data["intent"]] = 0

        dataset["evaluate"][data["intent"]] += 1

    return dataset


def plot_func(func, optimal):

    x = np.linspace(0, 2 * optimal, 100)
    y = [func(n, optimal=optimal) for n in x]

    plt.plot(x, y)
    plt.plot([optimal, optimal], [0, 100])
    plt.ylabel("score")
    plt.xlabel("distance")
    plt.show()


def request_nlp(auth, nlp_server, route, data):
    try:
        url = f"{nlp_server if nlp_server else settings.BOTHUB_NLP_BASE_URL}"
        url += f"{route}/?"
        header = {
            "Authorization": "Bearer " + auth
        }
        r = requests.post(url, json=data, headers=header)
        data = r.json()
        return data
    except requests.exceptions.ConnectionError:
        raise APIException(
            {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
            code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def is_valid_classifier(value):  # pragma: no cover
    from bothub.common.migrate_classifiers import TYPES

    return value in TYPES.keys()


def validate_classifier(value):  # pragma: no cover
    if not is_valid_classifier(value):
        raise ValidationError(_("{} is not a supported classifier.").format(value))


def classifier_choice():
    from bothub.common.migrate_classifiers import TYPES

    return list(TYPES.keys())


class CountSubquery(Subquery):
    template = "(SELECT COUNT(1) FROM (%(subquery)s) _count_subquery)"
    output_field = IntegerField()

    def __init__(self, queryset, output_field=None, **extra):
        super().__init__(queryset, output_field, **extra)
