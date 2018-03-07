from django.contrib import admin

from .models import RepositoryCategory
from .models import Repository
from .models import RepositoryUpdate
from .models import RepositoryExample
from .models import RepositoryExampleEntity
from .models import RepositoryTranslatedExample
from .models import RepositoryTranslatedExampleEntity
from .models import RepositoryAuthorization


@admin.register(RepositoryCategory)
class RepositoryCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    pass


@admin.register(RepositoryUpdate)
class RepositoryUpdateAdmin(admin.ModelAdmin):
    pass


@admin.register(RepositoryExample)
class RepositoryExampleAdmin(admin.ModelAdmin):
    pass


@admin.register(RepositoryExampleEntity)
class RepositoryExampleEntityAdmin(admin.ModelAdmin):
    pass


@admin.register(RepositoryTranslatedExample)
class RepositoryTranslatedExampleAdmin(admin.ModelAdmin):
    pass


@admin.register(RepositoryTranslatedExampleEntity)
class RepositoryTranslatedExampleEntity(admin.ModelAdmin):
    pass


@admin.register(RepositoryAuthorization)
class RepositoryAuthorizationAdmin(admin.ModelAdmin):
    pass
