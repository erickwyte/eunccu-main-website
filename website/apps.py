from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        import website.signals
        from django.db.models.signals import post_migrate
        from .permissions import ensure_user_manager_group_exists

        def create_user_manager_group(sender, **kwargs):
            if sender.name != 'website':
                return
            ensure_user_manager_group_exists()

        post_migrate.connect(create_user_manager_group, sender=self)
