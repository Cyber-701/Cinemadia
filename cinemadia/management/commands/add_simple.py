from django.core.management.base import BaseCommand
from django.utils.text import slugify

from cinemadia.models import Movie


class Command(BaseCommand):
    help = "Bazaga asosiy toifalar uchun yangi kinolarni qo'shish"

    def handle(self, *args, **options):
        movies_data = [
            {
                "title": "The Translator",
                "description": "Istanbulda yashovchi tarjimonning kutilmagan sarguzashtlarga boy hayoti haqida dramatik hikoya.",
                "year": 2024,
                "genre": "Drama, Sarguzasht",
                "director": "Eren Aksoy",
                "actors": "Burak Özçivit, Hande Erçel, Kaan Urgancıoğlu",
                "duration": "1h 52m",
                "rating": 8.1,
                "is_featured": True,
                "category": "tarjima_kino",
                "poster_url": "https://image.tmdb.org/t/p/w500/oqb8mOktGkrnSsjK8broQm3J3hq.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=Q0CbN8sfihY",
            },
            {
                "title": "Dilwale Returns",
                "description": "Yillar davomida bir-birini ko'rmagan sevishganlar yana uchrashib, katta to'siqlardan o'tishadi.",
                "year": 2023,
                "genre": "Romantika, Komediya",
                "director": "Farah Khan",
                "actors": "Shah Rukh Khan, Kajol Devgan, Varun Dhawan",
                "duration": "2h 14m",
                "rating": 7.9,
                "is_featured": True,
                "category": "hind",
                "poster_url": "https://image.tmdb.org/t/p/w500/1n7ugVxJ0HxJtPkAY68O0gYN2sH.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=7WfFFxjJFr0",
            },
            {
                "title": "Shadow Lines",
                "description": "Maxfiy xizmat agentlari dunyo miqyosidagi fitnalarni fosh qilish uchun kuch birlashtirishlari kerak bo'ladi.",
                "year": 2024,
                "genre": "Triller, Serial",
                "director": "Maggie Kline",
                "actors": "Pedro Pascal, Hayley Atwell, Lee Pace",
                "duration": "48m (1 qism)",
                "rating": 8.6,
                "is_featured": False,
                "category": "serial",
                "poster_url": "https://image.tmdb.org/t/p/w500/5DMrRjGZhzZ1TLWO0edrS7ZV7Z4.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=qh-9V8CvtpI",
            },
            {
                "title": "Cosmic Dreams",
                "description": "Kichik qahramonlar galaktikani saqlab qolish uchun sehrli sayohatga chiqishadi.",
                "year": 2025,
                "genre": "Animatsiya, Fantastika",
                "director": "Nora Singh",
                "actors": "Jacob Tremblay, Millie Bobby Brown, Awkwafina",
                "duration": "1h 37m",
                "rating": 7.8,
                "is_featured": False,
                "category": "multfilm",
                "poster_url": "https://image.tmdb.org/t/p/w500/2fOUeoLhM8GMd7sWXBJgpSDwa9N.jpg",
                "trailer_url": "https://www.youtube.com/watch?v=l4bRmsXTFzo",
            },
        ]

        created_count = 0
        updated_count = 0

        for data in movies_data:
            slug = slugify(data["title"])
            movie, created = Movie.objects.update_or_create(
                slug=slug,
                defaults={
                    **data,
                    "slug": slug,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Yangi kinolar qo'shildi: {created_count}, yangilandi: {updated_count}"
            )
        )
