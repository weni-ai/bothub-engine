import json
import requests

from django.conf import settings

from django_elasticsearch_dsl.management.commands import search_index
from django_elasticsearch_dsl.registries import registry
from elasticsearch.exceptions import RequestError


ES_BASE_URL = settings.ELASTICSEARCH_DSL["default"]["hosts"]


class Command(search_index.Command):
    req_content_type = {"content-type": "application/json"}

    def _check_pipeline_ilm(self):
        # Check Pipeline
        pipeline_url = f"{ES_BASE_URL}/_ingest/pipeline/{settings.ELASTICSEARCH_TIMESTAMP_PIPELINE_NAME}"
        pipeline_get = requests.get(pipeline_url)
        if pipeline_get.status_code == 200:
            self.stdout.write(
                f"[{pipeline_get.status_code}] {settings.ELASTICSEARCH_TIMESTAMP_PIPELINE_NAME} Pipeline already exists"
            )
        else:
            pipeline_body = {
                "processors": [
                    {
                        "date": {
                            "field": settings.ES_TIMESTAMP_PIPELINE_FIELD,
                            "formats": ["ISO8601"],
                        },
                    }
                ]
            }
            r = requests.put(
                pipeline_url,
                json.dumps(pipeline_body),
                headers=self.req_content_type,
            )

            self.stdout.write(
                f"[{r.status_code}] {settings.ELASTICSEARCH_TIMESTAMP_PIPELINE_NAME} Pipeline created"
            )

        # Check ILM Policy
        ilm_url = f"{ES_BASE_URL}/_ilm/policy/{settings.ELASTICSEARCH_DELETE_ILM_NAME}"
        ilm_get = requests.get(ilm_url)
        if ilm_get.status_code == 200:
            self.stdout.write(
                f"[{ilm_get.status_code}] {settings.ELASTICSEARCH_DELETE_ILM_NAME} ILM Policy already exists"
            )
        else:
            ilm_body = {
                "policy": {
                    "phases": {
                        "hot": {
                            "min_age": "0ms",
                            "actions": {
                                "rollover": {
                                    "max_age": settings.ELASTICSEARCH_LOGS_ROLLOVER_AGE,  # 1d
                                }
                            },
                        },
                        "delete": {
                            "min_age": settings.ELASTICSEARCH_LOGS_DELETE_AGE,  # 90d
                            "actions": {"delete": {"delete_searchable_snapshot": True}},
                        },
                    }
                }
            }
            r = requests.put(
                ilm_url,
                json.dumps(ilm_body),
                headers=self.req_content_type,
            )
            self.stdout.write(
                f"[{r.status_code}] {settings.ELASTICSEARCH_DELETE_ILM_NAME} ILM Policy created"
            )

    def _check_index_settings(self, index):
        doc_settings_url = f"{ES_BASE_URL}/_component_template/{index}-settings"
        r = requests.get(doc_settings_url)
        if r.status_code == 200:
            self.stdout.write(
                f"[{r.status_code}] {index} Settings template already exists"
            )
        else:
            doc_settings_body = {"template": {"settings": {}}}
            doc_settings_body["template"][
                "settings"
            ] = settings.ELASTICSEARCH_DSL_INDEX_SETTINGS
            doc_settings_body["template"]["settings"][
                "index.default_pipeline"
            ] = settings.ELASTICSEARCH_TIMESTAMP_PIPELINE_NAME
            doc_settings_body["template"]["settings"][
                "index.lifecycle.name"
            ] = settings.ELASTICSEARCH_DELETE_ILM_NAME
            doc_settings_body["template"]["settings"][
                "index.lifecycle.rollover_alias"
            ] = index._name
            r = requests.put(
                doc_settings_url,
                json.dumps(doc_settings_body),
                headers=self.req_content_type,
            )
            self.stdout.write(f"[{r.status_code}] {index} Settings template created")

    def _check_index_mappings(self, index, mapping):
        doc_mapping_url = f"{ES_BASE_URL}/_component_template/{index}-mappings"
        r = requests.get(doc_mapping_url)
        if r.status_code == 200:
            self.stdout.write(
                f"[{r.status_code}] {index} Mappings template already exists"
            )
        else:
            doc_mapping_body = {"template": {"mappings": {}}}
            doc_mapping_body["template"]["mappings"]["_doc"] = mapping
            doc_mapping_body["template"]["mappings"]["_doc"]["properties"][
                "@timestamp"
            ] = {"type": "date"}
            r = requests.put(
                doc_mapping_url,
                json.dumps(doc_mapping_body),
                headers=self.req_content_type,
            )
            self.stdout.write(f"[{r.status_code}] {index} Mappings template created")

    def _check_index_template(self, index):
        doc_index_template_url = f"{ES_BASE_URL}/_index_template/{index}-template"
        r = requests.get(doc_index_template_url)
        if r.status_code == 200:
            self.stdout.write(
                f"[{r.status_code}] {index} Index template already exists"
            )
        else:
            doc_index_template_body = {
                "index_patterns": [f"{index}*"],
                "data_stream": {},
                "composed_of": [f"{index}-mappings", f"{index}-settings"],
                "priority": 500,
            }
            r = requests.put(
                doc_index_template_url,
                json.dumps(doc_index_template_body),
                headers=self.req_content_type,
            )
            self.stdout.write(f"[{r.status_code}] {index} Index template created")

    def _create(self, models, options):
        for index in registry.get_indices(models):
            doc = index._doc_types[0]
            if getattr(doc, "_time_based", None):
                self._check_pipeline_ilm()
                mapping = doc._doc_type.mapping.to_dict()
                self._check_index_settings(index)
                self._check_index_mappings(index, mapping)
                self._check_index_template(index)
            else:
                try:
                    self.stdout.write(f"Creating index '{index._name}'")
                    index.create()
                except RequestError:
                    self.stdout.write(f"Index '{index._name}' already exists")
