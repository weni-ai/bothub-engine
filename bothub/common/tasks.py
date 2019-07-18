import json
import requests
import io
import re
import zipfile
from celery import shared_task
from bothub.api.v1.serializers import NewRepositoryExampleEntitySerializer
from bothub.common.models import RepositoryExample
from bothub.common.models import Repository


@shared_task
def migrate_repository_wit(repository, auth_token, language):
    try:
        request_api = requests.get(
            url='https://api.wit.ai/export',
            headers={
                'Authorization': 'Bearer {}'.format(auth_token)
            }
        ).json()

        expressions = ""
        response = requests.get(request_api['uri'])
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            for zipinfo in thezip.infolist():
                with thezip.open(zipinfo) as thefile:
                    if re.search('expressions.*', thefile.name):
                        for line in thefile.readlines():
                            expressions += line.decode('utf-8', 'replace').replace(
                                '\\"', '')

        for data in json.loads(expressions)['data']:
            text = data['text']

            count = 0
            intent_position = None
            while count < len(data['entities']):
                if data['entities'][count]['entity'] == 'intent':
                    intent_position = count
                    break
                count += 1

            if intent_position is None:
                print('Não encontrou a chave entity com o valor intent.')
                continue

            repository_ = Repository.objects.get(uuid=repository)

            repository_update = repository_.current_update(language)
            example = RepositoryExample.objects.create(
                text=str(text.encode('utf-8', 'replace').decode('utf-8')),
                intent=data['entities'][intent_position]['value'],
                repository_update=repository_update

            )

            for entities in data['entities']:
                entity = entities['entity']
                value = entities['value']
                if not entity == 'intent':
                    start = entities['start']
                    end = entities['end']

                    entity_serializer = NewRepositoryExampleEntitySerializer(
                        data={
                            'repository_example': example.pk,
                            "label": value.replace(' ', '_').lower(),
                            "entity": entity.replace(' ', '_').lower(),
                            "start": start,
                            "end": end,
                        }
                    )
                    entity_serializer.is_valid(raise_exception=True)
                    entity_serializer.save()

        return True
    except requests.ConnectionError:
        return False
    except json.JSONDecodeError:
        return False
