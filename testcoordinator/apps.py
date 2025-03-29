from django.apps import AppConfig


class TestCoordinatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testcoordinator'
    
    def ready(self):
        import testcoordinator.signals  # noqa 