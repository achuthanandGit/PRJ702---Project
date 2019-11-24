from django.core.management.base import BaseCommand
from identify.models import Identify, FishSpotData

class Command(BaseCommand):
    def handle(self, *args, **options):
        Tag.objects.all().delete()
        Post.objects.all().delete()