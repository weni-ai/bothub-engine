import io
import json
import re
import zipfile

import requests

from bothub.common.migrate_classifiers.classifiers import ClassifierType


class WitType(ClassifierType):
    name = "Wit.ai"
    slug = "wit"

    def migrate(self):
        from bothub.common.models import RepositoryExample
        from bothub.common.models import RepositoryIntent
        from bothub.common.models import RepositoryEntity
        from bothub.common.models import RepositoryExampleEntity

        try:
            request_api = requests.get(
                url="https://api.wit.ai/export",
                headers={"Authorization": "Bearer {}".format(self.auth_token)},
            ).json()

            expressions = ""
            response = requests.get(request_api.get("uri"))
            with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
                for zipinfo in thezip.infolist():
                    with thezip.open(zipinfo) as thefile:
                        if re.search("utterances.*", thefile.name):
                            for line in thefile.readlines():
                                expressions += line.decode("utf-8", "replace").replace(
                                    '\\"', ""
                                )

            for data in json.loads(expressions).get("utterances", []):
                text = str(data.get("text").encode("utf-8", "replace").decode("utf-8"))
                intent_text = data.get("intent")

                if RepositoryExample.objects.filter(
                    text=text,
                    intent__text=intent_text,
                    repository_version_language__repository_version__repository=self.repository_version.repository,
                    repository_version_language__repository_version=self.repository_version,
                    repository_version_language__language=self.language,
                ):
                    continue

                intent, created = RepositoryIntent.objects.get_or_create(
                    text=intent_text, repository_version=self.repository_version
                )
                example_id = RepositoryExample.objects.create(
                    repository_version_language=self.repository_version.get_version_language(
                        language=self.language
                    ),
                    text=text,
                    intent=intent,
                )

                for entities in data.get("entities", []):
                    entity_text = (
                        entities.get("entity").split(":")[0].replace(" ", "_").lower()
                    )
                    start = entities.get("start")
                    end = entities.get("end")

                    entity, created = RepositoryEntity.objects.get_or_create(
                        repository_version=self.repository_version, value=entity_text
                    )
                    RepositoryExampleEntity.objects.create(
                        repository_example=example_id,
                        start=start,
                        end=end,
                        entity=entity,
                    )

            return True
        except requests.ConnectionError:
            return False
        except json.JSONDecodeError:
            return False
