from django.core.management.base import BaseCommand
from django.template import engines

class Command(BaseCommand):
    help = 'Clear Django template cache'

    def handle(self, *args, **options):
        self.stdout.write('Clearing template cache...')
        try:
            for engine in engines.all():
                if hasattr(engine, 'template_loaders'):
                    for loader in engine.template_loaders:
                        if hasattr(loader, 'get_template_cache'):
                            loader.get_template_cache.clear()
            self.stdout.write(self.style.SUCCESS('Successfully cleared template cache'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear template cache: {e}'))
