from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Case, Count, F, FloatField, Q, Value, When
from django.db.models.functions import Greatest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CustomUserCreationForm,
    MovieForm,
    ReviewForm,
    UserProfileForm,
)
from .models import (
    Favorite,
    Movie,
    MovieVote,
    Review,
    UserProfile,
    WatchHistory,
    Watchlist,
)

PAGE_SIZE = 12
HOME_PREVIEW_CATEGORIES = ('tarjima_kino', 'hind', 'serial', 'multfilm')
SEARCH_FIELDS = ('title', 'description', 'genre', 'director', 'actors')
VOTE_LIKE = 'like'
VOTE_DISLIKE = 'dislike'
VALID_VOTE_TYPES = {VOTE_LIKE, VOTE_DISLIKE}

CATEGORY_TEMPLATES = {
    'tarjima_kino': 'tarjima_kino.html',
    'premyera': 'premyera.html',
    'hind': 'hind.html',
    'multfilm': 'multfilm.html',
    'serial': 'serial.html',
}

staff_required = user_passes_test(lambda user: user.is_staff)


def _paginate(request, queryset, per_page=PAGE_SIZE):
    """Return the requested page of a queryset."""
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def _filter_movies(query):
    """Return movies matching the query in any searchable field."""
    filters = Q()
    for field in SEARCH_FIELDS:
        filters |= Q(**{f'{field}__icontains': query})
    return Movie.objects.filter(filters).order_by('-rating', '-year')


def _category_previews(categories, limit=PAGE_SIZE):
    """Return the newest movies for each requested category."""
    return {
        category: Movie.objects.filter(category=category).order_by('-created_at')[:limit]
        for category in categories
    }


def _user_vote(user, movie):
    """Return the user's vote type for a movie, or None."""
    if not user.is_authenticated:
        return None
    return (
        MovieVote.objects.filter(user=user, movie=movie)
        .values_list('vote_type', flat=True)
        .first()
    )


def home(request):
    """Landing page with search, category previews, and popular picks."""
    query = request.GET.get('q', '').strip()
    movies = _filter_movies(query) if query else Movie.objects.order_by('-created_at')
    previews = _category_previews(HOME_PREVIEW_CATEGORIES)

    movies_by_category = defaultdict(list)
    for movie in Movie.objects.all()[:30]:
        movies_by_category[movie.category].append(movie)

    context = {
        'movies': _paginate(request, movies),
        'featured_movie': Movie.objects.filter(is_featured=True).first(),
        'movies_by_category': movies_by_category,
        'popular_movies': get_popular_movies(),
        'random_movies': get_random_movies(),
        'query': query,
        'total_count': movies.count(),
        'tarjima_movies': previews['tarjima_kino'],
        'hind_movies': previews['hind'],
        'serial_movies': previews['serial'],
        'multfilm_movies': previews['multfilm'],
    }
    return render(request, 'home.html', context)


def movie_detail(request, slug):
    """Show a single movie together with related titles."""
    movie = get_object_or_404(Movie, slug=slug)
    return render(request, 'movie_detail.html', {
        'movie': movie,
        'movies': Movie.objects.exclude(id=movie.id)[:6],
        'user_vote': _user_vote(request.user, movie),
    })


def register(request):
    """Create a new account and sign the user in."""
    if request.method != 'POST':
        return render(request, 'registration/register.html', {
            'form': CustomUserCreationForm(),
        })

    form = CustomUserCreationForm(request.POST)
    if not form.is_valid():
        return render(request, 'registration/register.html', {'form': form})

    user = form.save()
    login(request, user)
    messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
    return redirect('cinemadia:home')


@login_required
def profile(request):
    """Show and update the current user's profile."""
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('cinemadia:profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'user': user,
        'profile': user_profile,
        'form': form,
        'favorites': Favorite.objects.filter(user=user).select_related('movie')[:6],
        'watchlist': Watchlist.objects.filter(user=user).select_related('movie')[:6],
        'watch_history': WatchHistory.objects.filter(user=user).select_related('movie')[:6],
        'reviews': Review.objects.filter(user=user).select_related('movie')[:5],
        'stats': {
            'favorites_count': Favorite.objects.filter(user=user).count(),
            'watchlist_count': Watchlist.objects.filter(user=user).count(),
            'reviews_count': Review.objects.filter(user=user).count(),
            'watched_count': WatchHistory.objects.filter(user=user).count(),
        },
    }
    return render(request, 'profile.html', context)


def category_view(request, category):
    """Show movies in a single category."""
    movies = Movie.objects.filter(category=category).order_by('-rating', '-year')
    context = {
        'movies': _paginate(request, movies),
        'category': category,
        'category_name': dict(Movie.CATEGORY_CHOICES).get(category, ''),
        'total_count': movies.count(),
    }
    template_name = CATEGORY_TEMPLATES.get(category, 'category.html')
    return render(request, template_name, context)


def genre_view(request, genre):
    """Show movies matching a genre."""
    movies = Movie.objects.filter(genre__icontains=genre).order_by('-rating', '-year')
    return render(request, 'genre.html', {
        'movies': _paginate(request, movies),
        'genre': genre,
        'total_count': movies.count(),
    })


@login_required
@require_POST
def toggle_favorite(request, movie_id):
    """Add a movie to favorites, or remove it when already saved."""
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if created:
        is_favorite = True
        message = "Sevimlilarga qo'shildi"
    else:
        favorite.delete()
        is_favorite = False
        message = "Sevimlilardan o'chirildi"

    return JsonResponse({
        'is_favorite': is_favorite,
        'message': message,
        'favorites_count': Favorite.objects.filter(movie=movie).count(),
    })


@login_required
@require_POST
def toggle_watchlist(request, movie_id):
    """Add a movie to the watchlist, or remove it when already saved."""
    movie = get_object_or_404(Movie, id=movie_id)
    entry, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)

    if created:
        in_watchlist = True
        message = "Ko'rish ro'yxatiga qo'shildi"
    else:
        entry.delete()
        in_watchlist = False
        message = "Ko'rish ro'yxatidan o'chirildi"

    return JsonResponse({'in_watchlist': in_watchlist, 'message': message})


def _recalculate_movie_rating(movie):
    """Sync the movie rating with the average of its reviews."""
    average = Review.objects.filter(movie=movie).aggregate(avg=Avg('rating'))['avg']
    if average is not None:
        Movie.objects.filter(pk=movie.pk).update(rating=round(average, 1))


@login_required
def add_review(request, movie_id):
    """Create or update the current user's review for a movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    review = Review.objects.filter(user=request.user, movie=movie).first()

    if request.method != 'POST':
        return render(request, 'add_review.html', {
            'form': ReviewForm(instance=review),
            'movie': movie,
        })

    form = ReviewForm(request.POST, instance=review)
    if not form.is_valid():
        return render(request, 'add_review.html', {'form': form, 'movie': movie})

    review = form.save(commit=False)
    review.user = request.user
    review.movie = movie
    review.save()
    _recalculate_movie_rating(movie)
    messages.success(request, 'Fikringiz saqlandi!')
    return redirect('cinemadia:movie_detail', slug=movie.slug)


@login_required
def favorites_list(request):
    """List every movie the current user marked as favorite."""
    favorites = Favorite.objects.filter(user=request.user).select_related('movie')
    return render(request, 'favorites.html', {
        'favorites': _paginate(request, favorites),
        'total_count': favorites.count(),
    })


@login_required
def watchlist_view(request):
    """List every movie the current user saved for later."""
    watchlist = Watchlist.objects.filter(user=request.user).select_related('movie')
    return render(request, 'watchlist.html', {
        'watchlist': _paginate(request, watchlist),
        'total_count': watchlist.count(),
    })


VOTE_COUNTER_FIELDS = {
    VOTE_LIKE: 'likes_count',
    VOTE_DISLIKE: 'dislikes_count',
}


def _adjust_vote_counts(movie, changes):
    """Apply signed deltas to vote counters atomically, clamped at zero."""
    updates = {
        VOTE_COUNTER_FIELDS[vote_type]: Greatest(
            F(VOTE_COUNTER_FIELDS[vote_type]) + delta,
            Value(0),
        )
        for vote_type, delta in changes.items()
    }
    Movie.objects.filter(pk=movie.pk).update(**updates)
    movie.refresh_from_db(fields=['likes_count', 'dislikes_count'])


def _vote_response(movie, user_vote):
    return JsonResponse({
        'success': True,
        'likes_count': movie.likes_count,
        'dislikes_count': movie.dislikes_count,
        'user_vote': user_vote,
    })


@login_required
@require_POST
def vote_movie(request, movie_id):
    """Add, switch, or remove the current user's like/dislike vote."""
    vote_type = request.POST.get('vote_type')
    if vote_type not in VALID_VOTE_TYPES:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    movie = get_object_or_404(Movie, id=movie_id)

    with transaction.atomic():
        vote = MovieVote.objects.filter(user=request.user, movie=movie).first()

        if vote is None:
            MovieVote.objects.create(user=request.user, movie=movie, vote_type=vote_type)
            _adjust_vote_counts(movie, {vote_type: 1})
            return _vote_response(movie, vote_type)

        if vote.vote_type == vote_type:
            vote.delete()
            _adjust_vote_counts(movie, {vote_type: -1})
            return _vote_response(movie, None)

        previous_vote = vote.vote_type
        vote.vote_type = vote_type
        vote.save(update_fields=['vote_type'])
        _adjust_vote_counts(movie, {previous_vote: -1, vote_type: 1})
        return _vote_response(movie, vote_type)


def get_popular_movies(limit=10):
    """Rank movies by like ratio plus an engagement boost."""
    total_votes = F('likes_count') + F('dislikes_count')
    popularity = Case(
        When(total_votes=0, then=0.0),
        default=(F('likes_count') * 100.0 / total_votes) + (total_votes / 10.0),
        output_field=FloatField(),
    )
    return (
        Movie.objects.annotate(total_votes=total_votes, popularity_score=popularity)
        .filter(total_votes__gt=0)
        .order_by('-popularity_score')[:limit]
    )


def get_random_movies(limit=15):
    """Return a random selection of movies for the carousel."""
    return Movie.objects.order_by('?')[:limit]


@login_required
@staff_required
def admin_panel(request):
    """Cinemadia platformasi uchun maxsus boshqaruv paneli."""
    user_model = get_user_model()
    category_labels = dict(Movie.CATEGORY_CHOICES)

    top_categories = [
        {
            'key': item['category'],
            'label': category_labels.get(item['category'], item['category'].title()),
            'count': item['count'],
        }
        for item in (
            Movie.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
    ]

    stats_cards = [
        {
            'label': 'Umumiy filmlar',
            'value': Movie.objects.count(),
            'icon': '🎬',
            'accent': 'card-primary',
        },
        {
            'label': 'Premyera filmlar',
            'value': Movie.objects.filter(is_featured=True).count(),
            'icon': '⭐',
            'accent': 'card-accent',
        },
        {
            'label': 'Ro‘yxatdan o‘tgan foydalanuvchilar',
            'value': user_model.objects.count(),
            'icon': '👥',
            'accent': 'card-secondary',
        },
        {
            'label': 'Umumiy sharhlar',
            'value': Review.objects.count(),
            'icon': '💬',
            'accent': 'card-muted',
        },
    ]

    context = {
        'stats_cards': stats_cards,
        'average_rating': (
            Movie.objects.filter(rating__gt=0)
            .aggregate(avg_rating=Avg('rating'))
            .get('avg_rating')
        ),
        'top_categories': top_categories,
        'engagement_stats': {
            'favorites': Favorite.objects.count(),
            'watchlists': Watchlist.objects.count(),
            'history': WatchHistory.objects.count(),
        },
        'latest_movies': Movie.objects.order_by('-created_at')[:6],
        'top_rated_movies': Movie.objects.order_by('-rating', '-likes_count')[:6],
        'recent_reviews': (
            Review.objects.select_related('movie', 'user').order_by('-created_at')[:6]
        ),
        'all_movies': Movie.objects.order_by('-created_at'),
    }
    return render(request, 'admin_standalone.html', context)


@login_required
@staff_required
def admin_movie_form(request):
    """Film qo‘shish yoki tahrirlash uchun alohida sahifa."""
    movie_id = request.GET.get('id') or request.POST.get('id')
    movie = get_object_or_404(Movie, pk=movie_id) if movie_id else None

    if request.method != 'POST':
        return render(request, 'admin_movie_form.html', {
            'form': MovieForm(instance=movie),
            'movie': movie,
        })

    form = MovieForm(request.POST, request.FILES, instance=movie)
    if not form.is_valid():
        messages.error(request, 'Forma ma’lumotlarini tekshiring.')
        return render(request, 'admin_movie_form.html', {'form': form, 'movie': movie})

    saved_movie = form.save()
    action = 'yangilandi' if movie else 'qo‘shildi'
    messages.success(request, f"'{saved_movie.title}' filmi {action}.")
    return redirect('cinemadia:admin_panel')


@login_required
@staff_required
@require_POST
def admin_movie_delete(request, movie_id):
    """Delete a movie and return a JSON result."""
    movie = Movie.objects.filter(pk=movie_id).first()
    if movie is None:
        return JsonResponse({
            'success': False,
            'error': f'ID {movie_id} bilan film topilmadi.',
        }, status=404)

    title = movie.title
    movie.delete()
    return JsonResponse({
        'success': True,
        'message': f"{title} filmi muvaffaqiyatli o‘chirildi.",
    })
