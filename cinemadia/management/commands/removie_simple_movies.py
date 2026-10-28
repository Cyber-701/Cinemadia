from django.core.management.base import BaseCommand
from cinemadia.models import Movie

class Command(BaseCommand):
    help = 'Remove excess movies, keeping only the specified number of most recent ones'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of movies to keep')

    def handle(self, *args, **options):
        keep_count = options['count']
        
        # Get total count of movies
        total_movies = Movie.objects.count()
        
        if keep_count >= total_movies:
            self.stdout.write(
                self.style.SUCCESS(f'No movies to remove. Current count: {total_movies}, keeping: {keep_count}')
            )
            return

        # Get IDs of movies to keep (most recent ones)
        movies_to_keep = Movie.objects.order_by('-id')[:keep_count].values_list('id', flat=True)
        
        # Delete all movies not in the keep list
        deleted_count, _ = Movie.objects.exclude(id__in=movies_to_keep).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed {deleted_count} movies. Kept {keep_count} most recent movies.')
        )