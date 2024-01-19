import unittest
from unittest.mock import Mock
from django.http import HttpResponse
from openpyxl import Workbook
from ..export import ExportRepositoryLogUseCase


class TestExportRepositoryLogUseCase(unittest.TestCase):

    def setUp(self):
        self.use_case = ExportRepositoryLogUseCase()
        self.mock_repository_logs = [
            Mock(
                nlp_log=Mock(
                    text='text',
                    intent=Mock(
                        name='intent',
                        confidence='confidence'
                    ),
                    entities='entities'
                ), created_at='created_at'
            )
        ]
        for log in self.mock_repository_logs:
            log.nlp_log.intent.name = 'intent_name'

    def test_create_xlsx_workbook(self):
        # Chama a função _create_xlsx_workbook
        result = self.use_case._create_xlsx_workbook(self.mock_repository_logs)
        self.assertIsInstance(result, Workbook)

    def test_create_xlsx_response(self):
        result = self.use_case.create_xlsx_response(self.mock_repository_logs)
        self.assertIsInstance(result, HttpResponse)
        self.assertEqual(
            result['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            result['Content-Disposition'],
            'attachment; filename=repository_logs.xlsx'
        )

    def test_create_xlsx_workbook_with_none(self):

        result = self.use_case._create_xlsx_workbook(None)
        self.assertIsInstance(result, Workbook)

    def test_create_xlsx_response_with_none(self):

        result = self.use_case.create_xlsx_response(None)
        self.assertIsInstance(result, HttpResponse)
        self.assertEqual(
            result['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            result['Content-Disposition'],
            'attachment; filename=repository_logs.xlsx'
        )
