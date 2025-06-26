from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Initialize Python package'

    def handle(self, *args, **kwargs):
        self.stdout.write('Package initialized')
