from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'onhand.management'
    verbose_name = "Management"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
