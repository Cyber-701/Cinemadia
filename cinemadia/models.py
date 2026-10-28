from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    year = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    actors = models.TextField(help_text="Aktyorlarni vergul bilan ajrating")
    duration = models.CharField(max_length=20)
    rating = models.FloatField(default=0.0)
    is_featured = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('Draft', 'Chiqarmasdan saqlash'),
        ('Published', 'Bugun qo‘yish'),
        ('Scheduled', 'Kelajak sanasiga rejalash'),
    ]

    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='Draft'
    )
    
    # Movie categories
    CATEGORY_CHOICES = [
        ('serial', 'Serial'),
        ('tarjima_kino', "Tarjima kinolar"),
        ('premyera', 'Premyera'),
        ('hind', 'Hind kinolari'),
        ('multfilm', 'Multfilmlar'),
        ('klassika', 'Klassika'),
        ('yangilik', 'Yangilik'),
        ('eng_yaxshi', 'Eng Yaxshi'),
        ('jangari', 'Jangari'),
        ('drama', 'Drama'),
        ('komediya', 'Komediya'),
        ('melodrama', 'Melodrama'),
        ('sarguzasht', 'Sarguzasht'),
        ('qorquv', 'Qo\'rqinchli'),
        ('tarixiy', 'Tarixiy'),
        ('fantastika', 'Fantastika'),
        ('hayotiy', 'Hayotiy'),
        ('triller', 'Triller'),
        ('detektiv', 'Detektiv'),
        ('hujjatli', 'Hujjatli'),
        ('anime', 'Anime'),
        ('kriminal', 'Kriminal'),
        ('fentezi', 'Fentezi'),
        ('afsona', 'Afsona'),
        ('vester', 'Vester'),
        ('musiqiy', 'Musiqiy'),
        ('romantik', 'Romantik'),
        ('oilaviy', 'Oilaviy'),
        ('jangovar', 'Jangovar'),
        ('mistik', 'Mistik'),
        ('ilmiy', 'Ilmiy'),
        ('sport', 'Sport'),
    ]
    
    category = models.CharField(
        'Kategoriya',
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='yangilik'
    )
    
    # Media files
    poster_file = models.ImageField(upload_to='posters/', blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)
    banner_file = models.ImageField(upload_to='banners/', blank=True, null=True, help_text="Katta premyeralar uchun banner rasm")
    banner_url = models.URLField(blank=True, null=True, help_text="Yoki banner URL manzili")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    trailer_file = models.FileField(upload_to='trailers/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    
    # Like/Dislike fields
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_poster(self):
        if self.poster_file:
            return self.poster_file.url
        return self.poster_url
    
    def get_banner(self):
        """Katta premyeralar uchun banner rasmni qaytaradi"""
        if self.banner_file:
            return self.banner_file.url
        return self.banner_url
    
    def get_popularity_score(self):
        """Calculate popularity score based on likes, dislikes, and views"""
        total_votes = self.likes_count + self.dislikes_count
        if total_votes == 0:
            return 0
        
        # Calculate percentage of likes
        like_percentage = (self.likes_count / total_votes) * 100
        
        # Boost score based on total engagement
        engagement_boost = min(total_votes / 10, 50)  # Max 50 point boost
        
        return like_percentage + engagement_boost
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        """Return a slug that does not collide with another movie."""
        base_slug = slugify(self.title) or uuid4().hex[:8]
        candidate = base_slug
        while Movie.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base_slug}-{uuid4().hex[:6]}"
        return candidate
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Film'
        verbose_name_plural = 'Filmlar'


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    favorite_genres = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} profili"


class Favorite(models.Model):
    """User's favorite movies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class Watchlist(models.Model):
    """Movies user wants to watch later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} watchlist - {self.movie.title}"


class Review(models.Model):
    """User reviews for movies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}/10)"


class WatchHistory(models.Model):
    """Track what users have watched"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    watched_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # Percentage watched
    
    class Meta:
        ordering = ['-watched_at']
        verbose_name = 'Ko\'rilgan film'
        verbose_name_plural = 'Ko\'rilgan filmlar'
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"


class MovieVote(models.Model):
    """User votes (like/dislike) for movies"""
    VOTE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_votes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.vote_type})"
   