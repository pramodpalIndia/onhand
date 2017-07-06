from django.apps import AppConfig


class ProviderConfig(AppConfig):
    name = 'onhand.subscription'
    verbose_name = 'Provider'


    def ready(self):
        # from onhand.subscription import recurlyonfiguration
        # recurlyonfiguration()
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        # recurly.SUBDOMAIN = 'onhand'
        # recurly.API_KEY = '26eb038a51ec48df9d8809db21456e8b'
        # Set a default currency for your API requests
        # recurly.DEFAULT_CURRENCY = 'USD'
        pass
