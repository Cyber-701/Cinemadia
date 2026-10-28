from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Movie, MovieVote, Review


class MovieTestMixin:
    def create_movie(self, **overrides):
        data = {
            'title': 'Kod Shadow',
            'description': 'Sinov filmi',
            'year': 2025,
            'genre': 'Drama',
            'director': 'Rejissyor',
            'actors': 'Aktyor A, Aktyor B',
            'duration': '120',
            'poster_url': 'https://example.com/poster.jpg',
        }
        data.update(overrides)
        return Movie.objects.create(**data)


class MovieModelTests(MovieTestMixin, TestCase):
    def test_slug_is_generated_from_title(self):
        movie = self.create_movie(title='Kod Shadow')
        self.assertEqual(movie.slug, 'kod-shadow')

    def test_duplicate_titles_get_unique_slugs(self):
        first = self.create_movie()
        second = self.create_movie()

        self.assertNotEqual(first.slug, second.slug)
        self.assertTrue(second.slug.startswith('kod-shadow'))

    def test_get_poster_prefers_uploaded_file(self):
        movie = self.create_movie(poster_file='posters/a.jpg')
        self.assertEqual(movie.get_poster(), '/media/posters/a.jpg')


class VoteViewTests(MovieTestMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='secret123')
        self.movie = self.create_movie()
        self.client.force_login(self.user)
        self.url = reverse('cinemadia:vote_movie', args=[self.movie.id])

    def test_like_creates_vote_and_counts(self):
        response = self.client.post(self.url, {'vote_type': 'like'})

        self.assertEqual(response.json()['user_vote'], 'like')
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.likes_count, 1)

    def test_second_identical_vote_is_removed(self):
        self.client.post(self.url, {'vote_type': 'like'})
        response = self.client.post(self.url, {'vote_type': 'like'})

        self.assertIsNone(response.json()['user_vote'])
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.likes_count, 0)
        self.assertFalse(MovieVote.objects.exists())

    def test_switching_vote_moves_the_counter(self):
        self.client.post(self.url, {'vote_type': 'like'})
        response = self.client.post(self.url, {'vote_type': 'dislike'})

        self.assertEqual(response.json()['user_vote'], 'dislike')
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.likes_count, 0)
        self.assertEqual(self.movie.dislikes_count, 1)

    def test_invalid_vote_type_is_rejected(self):
        response = self.client.post(self.url, {'vote_type': 'maybe'})
        self.assertEqual(response.status_code, 400)


class ReviewViewTests(MovieTestMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='secret123')
        self.movie = self.create_movie()
        self.client.force_login(self.user)
        self.url = reverse('cinemadia:add_review', args=[self.movie.id])

    def test_review_updates_movie_rating(self):
        self.client.post(self.url, {'rating': 8, 'comment': 'Yaxshi'})

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.rating, 8.0)

    def test_repeated_review_updates_instead_of_duplicating(self):
        self.client.post(self.url, {'rating': 8, 'comment': 'Yaxshi'})
        self.client.post(self.url, {'rating': 4, 'comment': 'O‘zgardi'})

        self.assertEqual(Review.objects.filter(movie=self.movie).count(), 1)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.rating, 4.0)


class AccessControlTests(MovieTestMixin, TestCase):
    def setUp(self):
        self.movie = self.create_movie()

    def test_favorites_requires_login(self):
        response = self.client.get(reverse('cinemadia:favorites'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_regular_user_cannot_open_admin_panel(self):
        user = User.objects.create_user('regular', password='secret123')
        self.client.force_login(user)

        response = self.client.get(reverse('cinemadia:admin_panel'))
        self.assertEqual(response.status_code, 302)

    def test_home_page_renders(self):
        response = self.client.get(reverse('cinemadia:home'))
        self.assertEqual(response.status_code, 200)
