import xlsxwriter
from django.db.models import Count, Q

from bothub.common.models import RepositoryTranslatedExample, Repository, RepositoryExample, RepositoryVersion, \
    RepositoryExampleEntity

repository_version = RepositoryVersion.objects.get(
    pk=45, repository='af285b3e-be93-411f-a7d4-38412e7ade37'
)
queryset = RepositoryExample.objects.filter(
    repository_version_language__repository_version=repository_version
)

examples = repository_version.repository.examples(
    queryset=queryset, version_default=repository_version.is_default
).filter(
    repository_version_language__language='pt_br'
).annotate(
    translation_count=Count(
        "translations", filter=Q(translations__language='en')
    )
)
#     .filter(
#     translation_count=0
# )


workbook = xlsxwriter.Workbook('Expenses01.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, 'id')
worksheet.write(0, 1, 'repository_version')
worksheet.write(0, 2, 'language')
worksheet.write(0, 3, 'text')
worksheet.write(0, 4, 'es:text')
worksheet.write(0, 5, 'entities/0/value')
worksheet.write(0, 6, 'es:entities/0/value')

for count, example in enumerate(examples, start=1):
    worksheet.write(count, 0, str(example.pk))
    worksheet.write(count, 1, example.repository_version_language.repository_version.pk)
    worksheet.write(count, 2, example.repository_version_language.language)
    worksheet.write(count, 3, example.text)
    entities = RepositoryExampleEntity.objects.filter(repository_example=example.pk)
    for count, entity in enumerate(entities, start=1):
        worksheet.write(count, 5, entity.entity.value)
    # print(entities)


workbook.close()


