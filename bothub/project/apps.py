from django.apps import AppConfig

class ProjectConfig(AppConfig):
    name = 'bothub.project'

    def ready(self):
        from bothub.project.signals import integrate_ai  # noqa: F401
