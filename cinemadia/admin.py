from django.contrib import admin
from django.utils.html import format_html
from .models import Movie, UserProfile, Favorite, Watchlist, Review, WatchHistory


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Film ma'lumotlarini boshqarish (o'zbekcha, tushunarli ko'rinish)."""

    list_display = (
        'title', 'year', 'genre', 'category', 'rating', 'is_featured',
        'favorites_count', 'watchlist_count', 'poster_preview'
    )
    list_filter = ('category', 'genre', 'year', 'is_featured')
    search_fields = ('title', 'director', 'actors', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'poster_preview')
    list_editable = ('is_featured', 'rating')
    list_per_page = 25
    inlines = [ReviewInline]

    fieldsets = (
        ('🎬 Asosiy ma\'lumotlar', {
            'fields': (
                'title', 'slug', 'description',
                ('year', 'genre', 'category'),
                ('director', 'actors'),
                ('duration', 'rating', 'is_featured'),
            )
        }),
        ('📁 Media fayllar', {
            'fields': (
                'poster_preview',
                ('poster_file', 'poster_url'),
                ('video_file', 'video_url', 'trailer_url'),
            ),
            'description': 'Fayl yuklang yoki tashqi URL kiriting.'
        }),
        ('📅 Sana ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def poster_preview(self, obj):
        if obj.get_poster():
            return format_html('<img src="{}" style="height:60px;border-radius:6px"/>', obj.get_poster())
        return '—'
    poster_preview.short_description = 'Poster'

    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'Sevimlilar'

    def watchlist_count(self, obj):
        return obj.in_watchlists.count()
    watchlist_count.short_description = 'Ko\'rish ro\'yxati'

    actions = ['belgilanganlarni_premyera_qilish', 'belgilanganlarni_oddiy_qilish']

    def belgilanganlarni_premyera_qilish(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} ta film premyera sifatida belgilandi.")
    belgilanganlarni_premyera_qilish.short_description = 'Premyera sifatida belgilash'

    def belgilanganlarni_oddiy_qilish(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} ta film oddiy holatga qaytarildi.")
    belgilanganlarni_oddiy_qilish.short_description = 'Premyerani bekor qilish'

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    search_fields = ('user__username', 'movie__title', 'comment')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'progress', 'watched_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('watched_at', 'progress')
    date_hierarchy = 'watched_at'


# Admin panel sarlavhalari (o'zbekcha)
admin.site.site_header = '🎬 CINEMADIA — Admin panel'
admin.site.site_title = 'Cinemadia boshqaruv'
admin.site.index_title = 'Cinemadia boshqaruv paneli'
