import json
import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

ES_BASE_URL = settings.ELASTICSEARCH_DSL["default"]["hosts"]


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("documents", nargs="+", type=str, help="list of models")

    def _check_pipeline_ilm(self):
        # Check Pipeline
        pipeline_url = (
            f"{ES_BASE_URL}/_ingest/pipeline/{settings.ES_TIMESTAMP_PIPELINE_NAME}"
        )
        pipeline_get = requests.get(pipeline_url)
        if pipeline_get.status_code == 200:
            print("Pipeline already created")
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
            requests.post(pipeline_url, json.dumps(pipeline_body))
            print("Pipeline created")

        # Check ILM Policy
        ilm_url = f"{ES_BASE_URL}/_ilm/policy/{settings.ES_DELETE_ILM_NAME}"
        ilm_get = requests.get(ilm_url)
        if ilm_get.status_code == 200:
            print("ILM Policy already created")
        else:
            ilm_body = {
                "policy": {
                    "phases": {
                        "hot": {
                            "min_age": "0ms",
                            "actions": {
                                "rollover": {
                                    "max_age": "90d",
                                }
                            },
                        },
                        "delete": {
                            "min_age": "30m",
                            "actions": {"delete": {"delete_searchable_snapshot": True}},
                        },
                    }
                }
            }
            requests.post(ilm_url, json.dumps(ilm_body))
            print("ILM Policy created")

    def _check_index_settings(self, index):
        doc_settings_url = f"{ES_BASE_URL}/_component_template/{index}-settings"
        doc_settings_body = {}
        doc_settings_body["template"][
            "settings"
        ] = settings.ELASTICSEARCH_DSL_INDEX_SETTINGS
        doc_settings_body["template"]["settings"][
            "index.default_pipeline"
        ] = settings.ES_TIMESTAMP_PIPELINE_NAME
        doc_settings_body["template"]["settings"][
            "index.lifecycle.name"
        ] = settings.ES_DELETE_ILM_NAME
        doc_settings_body["template"]["settings"][
            "index.lifecycle.rollover_alias"
        ] = index
        requests.post(doc_settings_url, json.dumps(doc_settings_body))
        print(f"{index} Settings template created")

    def _check_index_mappings(self, index, mapping):
        doc_mapping_url = f"{ES_BASE_URL}/_component_template/{index}-mappings"
        doc_mapping_body = {}
        doc_mapping_body["template"]["mappings"]["_doc"] = mapping
        doc_mapping_body["template"]["mappings"]["_doc"]["properties"]["@timestamp"] = {
            "type": "date"
        }
        requests.post(doc_mapping_url, json.dumps(doc_mapping_body))
        print(f"{index} Mappings template created")

    def _check_index_template(self, index):
        doc_index_template_url = f"{ES_BASE_URL}/_component_template/{index}-template"
        doc_index_template_body = {
            "index_patterns": [f"{index}*"],
            "data_stream": {},
            "composed_of": [f"{index}-mappings", f"{index}-settings"],
            "priority": 500,
        }
        requests.post(doc_index_template_url, json.dumps(doc_index_template_body))
        print(f"{index} Index template created")

    def handle(self, *args, **options):
        document_classes = []
        for doc in options["documents"][1:]:
            document_classes.append(import_string(doc))
        document_classes = set(document_classes)
        self._check_pipeline_ilm()

        for doc in document_classes:
            index = doc._index._name
            mapping = doc()._doc_type.mapping.to_dict()
            self._check_index_settings(index)
            self._check_index_mappings(index, mapping)
            self._check_index_template(index)
