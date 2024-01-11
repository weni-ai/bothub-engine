from django.http import HttpResponse

from openpyxl import Workbook


class ExportRepositoryLogUseCase:

    def _create_xlsx_workbook(
            self,
            repository_logs
    ) -> Workbook:

        wb = Workbook()
        ws = wb.active

        ws['A1'] = 'Repository'
        ws['B1'] = 'Date'
        ws['C1'] = 'Action'
        ws['D1'] = 'User'

        row = 2
        for repository_log in repository_logs:
            ws['A{}'.format(row)] = repository_log.repository.name
            ws['B{}'.format(row)] = repository_log.date
            ws['C{}'.format(row)] = repository_log.action
            ws['D{}'.format(row)] = repository_log.user.username
            row += 1

        return wb

    def create_xlsx_response(
            self,
            repository_logs
    ) -> HttpResponse:

        wb = self._create_xlsx_workbook(repository_logs)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=repository_logs.xlsx'
        wb.save(response)

        return response
