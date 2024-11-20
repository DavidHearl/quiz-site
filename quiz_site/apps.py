from django.apps import AppConfig

class QuizSiteConfig(AppConfig):
    name = 'quiz_site'

    def ready(self):
        import quiz_site.signals