from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cinemadia'

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('category/<str:category>/', views.category_view, name='category'),
    path('genre/<str:genre>/', views.genre_view, name='genre'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/movies/manage/', views.admin_movie_form, name='admin_movie_form'),
    path('admin-panel/movies/delete/<int:movie_id>/', views.admin_movie_delete, name='admin_movie_delete'),
    
    # User authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='cinemadia:home'), name='logout'),
    
    # User interactions
    path('movie/<int:movie_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('movie/<int:movie_id>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('movie/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('movie/<int:movie_id>/vote/', views.vote_movie, name='vote_movie'),
    
    # User lists
    path('favorites/', views.favorites_list, name='favorites'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
]
